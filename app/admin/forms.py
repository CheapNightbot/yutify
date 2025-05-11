from flask_security.forms import Form
from wtforms import (
    BooleanField,
    HiddenField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    URLField,
    widgets,
)
from wtforms.validators import DataRequired, Length


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddRoleForm(Form):
    name = StringField(
        "Role Name",
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Role Name", "form": "add_role_form"},
    )
    description = StringField(
        "Role Description",
        validators=[Length(max=200)],
        render_kw={"placeholder": "Role Description", "form": "add_role_form"},
    )
    permissions = StringField(
        "Role Permissions",
        validators=[DataRequired()],
        render_kw={"placeholder": "Role Permissions", "form": "add_role_form"},
    )
    add_role = SubmitField("Add Role", render_kw={"form": "add_role_form"})


class EditRoleForm(Form):
    role_id = HiddenField(name="role_id")
    name = StringField(
        "Role Name",
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Role Name", "readonly": ""},
    )
    description = StringField(
        "Role Description",
        validators=[Length(max=200)],
        render_kw={"readonly": ""},
    )
    permissions = StringField(
        "Role Permissions", validators=[DataRequired()], render_kw={"readonly": ""}
    )
    edit_role = SubmitField("Save")
    delete_role = SubmitField("Delete")


class AddServiceForm(Form):
    name = StringField(
        "Service Name",
        validators=[DataRequired(), Length(min=1, max=64)],
        render_kw={"placeholder": "Service Name", "form": "add_service_form"},
    )
    url = URLField(
        "Service URL",
        render_kw={"placeholder": "Service URL", "form": "add_service_form"},
    )
    is_private = BooleanField("It's Private?", render_kw={"form": "add_service_form"})
    add_service = SubmitField("Add Service", render_kw={"form": "add_service_form"})


class EditServiceForm(Form):
    service_id = HiddenField(name="service_id")
    name = StringField(
        "Service Name",
        validators=[DataRequired(), Length(min=1, max=64)],
        render_kw={"placeholder": "Service Name", "readonly": ""},
    )
    url = URLField(
        "Service URL",
        render_kw={"placeholder": "Service URL", "readonly": ""},
    )
    is_private = BooleanField("It's Private?", render_kw={"disabled": ""})
    edit_service = SubmitField("Save")
    delete_service = SubmitField("Delete")


class ManageUserAccount(Form):
    user_id = HiddenField(name="user_id")
    roles = MultiCheckboxField("Roles")
    notify_deletion = BooleanField(
        "Send email to notify user about their account deletion?"
    )
    reason_for_deletion = TextAreaField("Reason")
    edit_user = SubmitField("Save")
    delete_user = SubmitField("Delete")
