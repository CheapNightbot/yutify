from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_security import (
    auth_required,
    current_user,
    permissions_required,
    Security,
)

from app.admin import bp
from app.admin.forms import (
    AddRoleForm,
    AddServiceForm,
    EditRoleForm,
    EditServiceForm,
    EditUserRoles,
)
from app.models import Role, Service, User


@bp.route("/dashboard")
@auth_required()
@permissions_required("admin-read", "admin-write")
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
@permissions_required("admin-read", "admin-write")
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
                f'Can not delete"{role_id}" role. It doesn\'t exist in database!',
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
@permissions_required("admin-read", "admin-write")
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


@bp.route("/manage_users/", methods=["GET", "POST"])
@bp.route("/manage_users/<username>")
@auth_required()
@permissions_required("admin-read", "admin-write")
def manage_users(username: str = None):
    security: Security = current_app.security
    roles = Role.query.all()
    users = User.query.all()
    edit_user_form = EditUserRoles()

    edit_user_form.roles.choices = [role.name for role in roles]

    # Handle editing a user's roles
    if edit_user_form.validate_on_submit() and "edit_user" in request.form:
        user_id = int(edit_user_form.user_id.data)
        user = security.datastore.find_user(id=user_id)
        if not user:
            flash(f"Invalid user. This user doesn't exist in database!", "error")
            return redirect(url_for("admin.manage_users"))

        new_roles = [role for role in roles if role.name in edit_user_form.roles.data]
        if user == current_user and "admin" not in new_roles:
            flash(
                f'You can not remove your "admin" role! Please ask another admin to do it for you.',
                "error",
            )
            return redirect(url_for("admin.manage_users"))

        user.roles = new_roles
        security.datastore.db.session.commit()
        flash(f'Successfully updated roles for "{user.name}".', "success")
        return redirect(url_for("admin.manage_users"))

    return render_template(
        "admin/manage_users.html",
        title="Manage Users",
        active_page="dashboard",
        aside_active="manage-users",
        users=users,
        edit_user_form=edit_user_form,
        year=datetime.today().year,
    )
