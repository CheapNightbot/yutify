from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_security import (
    Security,
    auth_required,
    current_user,
    roles_required,
    send_mail,
)

from app.admin import bp
from app.admin.forms import (
    AddRoleForm,
    AddServiceForm,
    EditRoleForm,
    EditServiceForm,
    ManageUserAccount,
)
from app.models import Role, Service, User


@bp.route("/dashboard")
@auth_required()
@roles_required("admin")
def dashboard():
    return render_template(
        "admin/dashboard.html",
        title="Admin Dashboard",
        active_page="dashboard",
        aside_active="dashboard",
        year=datetime.today().year,
    )


@bp.route("/manage_roles", methods=["GET", "POST"])
@auth_required()
@roles_required("admin")
def manage_roles():
    security: Security = current_app.security
    roles = Role.query.all()
    add_role_form = AddRoleForm()
    edit_role_form = EditRoleForm()

    # Handle adding a new role
    if add_role_form.validate_on_submit() and "add_role" in request.form:
        name = add_role_form.name.data.strip()
        description = add_role_form.description.data.strip()
        permissions = set(add_role_form.permissions.data.split(","))
        permissions = [perm.strip() for perm in permissions]

        security.datastore.create_role(
            name=name, description=description, permissions=sorted(permissions)
        )
        security.datastore.db.session.commit()
        flash(f'Successfully created "{name}" role.', "success")
        return redirect(url_for("admin.manage_roles"))

    # Handle editing an existing role
    if edit_role_form.validate_on_submit() and "edit_role" in request.form:
        role_id = int(edit_role_form.role_id.data)
        role = security.datastore.db.session.get(Role, role_id)
        if not role:
            flash(
                f'"{role_id}" doesn\'t exist in database! You may create it instead of tyring to edit.',
                "error",
            )
            return redirect(url_for("admin.manage_roles"))

        role.name = edit_role_form.name.data.strip()
        role.description = edit_role_form.description.data.strip()
        permissions = set(add_role_form.permissions.data.split(","))
        permissions = [perm.strip() for perm in permissions]
        role.permissions = sorted(permissions)
        security.datastore.db.session.commit()
        flash(f'Successfully updated "{role.name}".', "success")
        return redirect(url_for("admin.manage_roles"))

    # Handle deleting a role
    if edit_role_form.validate_on_submit() and "delete_role" in request.form:
        role_id = int(edit_role_form.role_id.data)
        role = security.datastore.db.session.get(Role, role_id)
        if not role:
            flash(
                f'Can not delete "{role_id}" role. It doesn\'t exist in database!',
                "error",
            )
            return redirect(url_for("admin.manage_roles"))

        if role.name == "admin":
            flash(
                'You can not delete the "admin" role!',
                "error",
            )
            return redirect(url_for("admin.manage_roles"))

        security.datastore.db.session.delete(role)
        security.datastore.db.session.commit()
        flash(f'Successfully deleted "{role.name}" role.', "success")
        return redirect(url_for("admin.manage_roles"))

    return render_template(
        "admin/manage_roles.html",
        title="Manage Roles",
        active_page="dashboard",
        aside_active="manage-roles",
        roles=roles,
        add_role_form=add_role_form,
        edit_role_form=edit_role_form,
        year=datetime.today().year,
    )


@bp.route("/manage_services", methods=["GET", "POST"])
@auth_required()
@roles_required("admin")
def manage_services():
    security: Security = current_app.security
    services = Service.query.all()
    add_service_form = AddServiceForm()
    edit_service_form = EditServiceForm()

    # Handle adding a new service
    if add_service_form.validate_on_submit() and "add_service" in request.form:
        name = add_service_form.name.data.strip()
        url = add_service_form.url.data.strip()
        is_private = add_service_form.is_private.data

        new_service = Service(name=name, url=url, is_private=is_private)
        security.datastore.db.session.add(new_service)
        security.datastore.db.session.commit()
        flash(f'Successfully added "{name}" to services.', "success")
        return redirect(url_for("admin.manage_services"))

    # Handle editing an existing service
    if edit_service_form.validate_on_submit() and "edit_service" in request.form:
        service_id = int(edit_service_form.service_id.data)
        service = security.datastore.db.session.get(Service, service_id)
        if not service:
            flash(
                f'"{edit_service_form.name.data}" doesn\'t exist in database! You may create it instead of tyring to edit.',
                "error",
            )
            return redirect(url_for("admin.manage_services"))

        service.name = edit_service_form.name.data.strip()
        service.url = edit_service_form.url.data.strip()
        service.is_private = edit_service_form.is_private.data
        security.datastore.db.session.commit()
        flash(f'Successfully updated "{service.name}" service.', "success")
        return redirect(url_for("admin.manage_services"))

    # Handle deleting a service
    if edit_service_form.validate_on_submit() and "delete_service" in request.form:
        service_id = int(edit_service_form.service_id.data)
        service = security.datastore.db.session.get(Service, service_id)
        if not service:
            flash(
                f'Can not delete"{edit_service_form.name.data}" service. It doesn\'t exist in database!',
                "error",
            )
            return redirect(url_for("admin.manage_services"))

        security.datastore.db.session.delete(service)
        security.datastore.db.session.commit()
        flash(f'Successfully deleted "{service.name}" service.', "success")
        return redirect(url_for("admin.manage_services"))

    return render_template(
        "admin/manage_services.html",
        title="Manage Services",
        active_page="dashboard",
        aside_active="manage-services",
        services=services,
        add_service_form=add_service_form,
        edit_service_form=edit_service_form,
        year=datetime.today().year,
    )


@bp.route("/manage_users", methods=["GET", "POST"])
@auth_required()
@roles_required("admin")
def manage_users():
    security: Security = current_app.security
    roles = Role.query.all()
    users = User.query.order_by(User.id).all()
    manage_user_account_form = ManageUserAccount()

    manage_user_account_form.roles.choices = [role.name for role in roles]

    # Handle editing a user's roles
    if manage_user_account_form.validate_on_submit() and "edit_user" in request.form:
        user_id = int(manage_user_account_form.user_id.data)
        user = security.datastore.find_user(id=user_id)
        if not user:
            flash(f"Invalid user. This user doesn't exist in database!", "error")
            return redirect(url_for("admin.manage_users"))

        new_roles = [
            role for role in roles if role.name in manage_user_account_form.roles.data
        ]
        if user == current_user and "admin" not in new_roles:
            flash(
                f'You can not remove your "admin" role! Please ask another admin to do it for you.',
                "error",
            )
            return redirect(url_for("admin.manage_users"))
        msg = "Successfully updated roles"
        user.roles = new_roles
        if manage_user_account_form.reset_tf.data:
            security.datastore.tf_reset(user)
            msg += " and reset 2FA"
        security.datastore.db.session.commit()
        flash(
            f'{msg} for "{user.name}".',
            "success"
            )
        return redirect(url_for("admin.manage_users"))

    # Handle deleting a user's account
    if manage_user_account_form.validate_on_submit() and "delete_user" in request.form:
        user_id = int(manage_user_account_form.user_id.data)
        if user_id == current_user.id:
            settings_page = f"<a href=\"{url_for('user.user_settings', username=current_user.username)}\">Settings</a>"
            flash(
                f"For deleting your own account, please visit your {settings_page} page!",
                "error",
            )
            return redirect(url_for("admin.manage_users"))
        user = security.datastore.find_user(id=user_id)
        if not user:
            flash(f"Invalid user. This user doesn't exist in database!", "error")
            return redirect(url_for("admin.manage_users"))

        notify_user = manage_user_account_form.notify_deletion.data
        reason_for_deletion = manage_user_account_form.reason_for_deletion.data
        if notify_user:
            send_mail(
                subject="[yutify] Account Deletion Notice!",
                recipient=user.email,
                template="notify_account_delete",
                user=user,
                admin_delete=True,
                reason_for_deletion=(
                    reason_for_deletion.strip() if reason_for_deletion else None
                ),
            )
        security.datastore.delete_user(user=user)
        security.datastore.db.session.commit()
        msg = (
            f'Successfully deleted user "@{user.username}"! And they have been notified with email.'
            if notify_user
            else f'Successfully deleted user with username "{user.username}"!'
        )
        flash(msg, "success")
        return redirect(url_for("admin.manage_users"))

    return render_template(
        "admin/manage_users.html",
        title="Manage Users",
        active_page="dashboard",
        aside_active="manage-users",
        users=users,
        manage_user_account_form=manage_user_account_form,
        year=datetime.today().year,
    )
