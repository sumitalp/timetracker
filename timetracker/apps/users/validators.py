from django.core.validators import RegexValidator


class FirstNameRegexValidator(RegexValidator):
    regex = r"^[a-zA-Z ]*$"
    message = "First Name has to be letters only"
    code = "first_name_invalid"


class SurnameRegexValidator(RegexValidator):
    regex = r"^[a-zA-Z]*$"
    message = "Surname has to be letters without any space"
    code = "surname_invalid"
