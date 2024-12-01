from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _


class OnlyDigitsValidator:
    """
    Validate that the password is of a minimum length.
    """

    def __init__(self, only_digits=True):
        self.only_digits = only_digits

    def validate(self, password, user=None):
        if str(password).isdigit() != self.only_digits:
            raise ValidationError(
                _(
                    "This password contains only digits. only_digits=True "
                ),
                code="password_not_only_digits",
                params={"only_digits": self.only_digits},
            )

    def get_help_text(self):
        return _(
            "This password contains only digits. only_digits=True "
        )