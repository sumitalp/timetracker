from django.conf import settings
from django.core.exceptions import ValidationError


def send_password_set_mail(
    email,
    password_form,
    subject_template_name,
    email_template_name,
    frontend_password_url,
    extra_email_context={},
):
    form = password_form(data={"email": email})
    if not form.is_valid():
        raise ValidationError(form.errors)
    # Set some values to trigger the send_email method.
    extra_email_context["support_email"] = "support@tablechief.com"
    opts = {
        "from_email": getattr(settings, "EMAIL_FROM"),
        "subject_template_name": subject_template_name,
        "email_template_name": email_template_name,
        "domain_override": "/".join(
            [
                getattr(settings, "FRONT_END_URL"),
                getattr(settings, frontend_password_url),
            ]
        ),
        "extra_email_context": extra_email_context,
    }
    form.save(**opts)
