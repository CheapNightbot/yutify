from datetime import datetime
from time import time

from authlib.oauth2 import OAuth2Error
from flask import abort, flash, redirect, render_template, request, url_for
from flask_security import auth_required, current_user
from werkzeug.security import gen_salt

from app.extensions import db
from app.models import OAuth2Client, User
from app.oauth import bp
from app.oauth.forms import CreateClientForm, DeleteClientForm, EditClientForm
from app.oauth.oauth2 import authorization


@bp.route("/dashboard", methods=["GET", "POST"])
@bp.route("/dashboard/<client_id>", methods=["GET", "POST"])
@auth_required()
def dashboard(client_id=None):
    user = User.query.get(current_user.id)

    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []

    if client_id:
        client = [client for client in clients if client.client_id == client_id]
        if not client:
            abort(404)
        edit_req_form = EditClientForm()
        delete_req_form = DeleteClientForm()

        if edit_req_form.validate_on_submit() and "edit" in request.form:
            return redirect(url_for("oauth.edit_client", client_id=client_id))

        if delete_req_form.validate_on_submit() and "delete" in request.form:
            client = client[0]
            # Delete all tokens for this client (cascade delete for authorized apps)
            from app.models import OAuth2Token

            OAuth2Token.query.filter_by(client_id=client.client_id).delete()
            db.session.delete(client)
            db.session.commit()
            flash(
                f"Successfully deleted {client.client_metadata['client_name']}!",
                "success",
            )
            return redirect(url_for("oauth.dashboard"))

        return render_template(
            "oauth/client_info.html",
            user=user,
            client=client[0],
            title="Developer Dashboard",
            active_page="dev_dashboard",
            year=datetime.today().year,
            edit_req_form=edit_req_form,
            delete_req_form=delete_req_form,
        )

    return render_template(
        "oauth/dashboard.html",
        user=user,
        clients=clients,
        title="Developer Dashboard",
        active_page="dev_dashboard",
        year=datetime.today().year,
    )


@bp.route("/dashboard/create", methods=["GET", "POST"])
def create_client():
    if not current_user.is_authenticated:
        abort(401)

    user = User.query.get(current_user.id)
    create_client_form = CreateClientForm()
    if create_client_form.validate_on_submit():
        client_id = gen_salt(24)
        client_id_issued_at = int(time())
        client = OAuth2Client(
            client_id=client_id,
            client_id_issued_at=client_id_issued_at,
            user_id=user.id,
        )

        client_metadata = {
            "client_name": create_client_form.client_name.data,
            "client_description": create_client_form.client_description.data,
            "client_uri": create_client_form.client_uri.data,
            "grant_types": ["authorization_code"],
            "redirect_uris": [
                data.get("redirect_uri")
                for data in create_client_form.redirect_uris.data
            ],
            "response_types": ["code"],
            "scope": "profile",
            "token_endpoint_auth_method": "client_secret_basic",
        }
        client.set_client_metadata(client_metadata)
        client.client_secret = gen_salt(48)

        db.session.add(client)
        db.session.commit()
        flash(
            f'Successfully created "{create_client_form.client_name.data}"!', "success"
        )
        return redirect(url_for("oauth.dashboard", client_id=client_id))

    return render_template(
        "oauth/create_client.html",
        title="Developer Dashboard",
        active_page="create_client",
        create_client_form=create_client_form,
        year=datetime.today().year,
    )


@bp.route("/dashboard/<client_id>/edit", methods=["GET", "POST"])
@auth_required()
def edit_client(client_id):
    user = User.query.get(current_user.id)
    client = OAuth2Client.query.filter_by(client_id=client_id).first()
    if not client or client.user_id != user.id:
        abort(404)

    client_metadata = client.client_metadata.copy()
    redirect_uris_data = [
        {"redirect_uri": uri} for uri in client_metadata.get("redirect_uris", [])
    ]

    if request.method == "GET":
        edit_client_form = CreateClientForm(
            client_name=client_metadata.get("client_name", ""),
            client_description=client_metadata.get("client_description", ""),
            client_uri=client_metadata.get("client_uri", ""),
            redirect_uris=redirect_uris_data,
        )
    else:
        edit_client_form = CreateClientForm()

    if edit_client_form.validate_on_submit():
        client.set_client_metadata(
            {
                "client_name": edit_client_form.client_name.data,
                "client_description": edit_client_form.client_description.data,
                "client_uri": edit_client_form.client_uri.data,
                "grant_types": ["authorization_code"],
                "redirect_uris": [
                    data.get("redirect_uri")
                    for data in edit_client_form.redirect_uris.data
                ],
                "response_types": ["code"],
                "scope": "profile",
                "token_endpoint_auth_method": "client_secret_basic",
            }
        )
        db.session.commit()
        flash("Successfully updated the App information!", "success")
        return redirect(url_for("oauth.dashboard", client_id=client_id))

    return render_template(
        "oauth/edit_client.html",
        client=client,
        title="Developer Dashboard",
        active_page="dev_dashboard",
        year=datetime.today().year,
        edit_client_form=edit_client_form,
    )


@bp.route("/oauth/authorize", methods=["GET", "POST"])
def authorize():
    user = User.query.get(current_user.id)
    # if user log status is not true (Auth server), then to log it in
    if not user:
        return redirect(url_for("security.login", next=request.url))
    if request.method == "GET":
        try:
            grant = authorization.get_consent_grant(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template("oauth/authorize.html", user=user, grant=grant)
    if not user and "username" in request.form:
        username = request.form.get("username")
        user = User.query.filter_by(username=username).first()
    if request.form.get("confirm"):
        grant_user = user
    else:
        grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)


@bp.route("/oauth/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()


@bp.route("/oauth/revoke", methods=["POST"])
def revoke_token():
    return authorization.create_endpoint_response("revocation")
