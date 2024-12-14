import re

from django.core import validators
import  six
from django.utils.deconstruct import deconstructible


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    regex = r'^[\d+]+$'
    message = 'Enter a valid username. This value may contain only English letters, ' \
        'numbers, and @/./+/-/_ characters.'
    flags = re.ASCII if six.PY3 else 0


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r'^[\d+]+$'
    message = 'Enter a valid username. This value may contain only letters, ' \
        'numbers, and @/./+/-/_ characters.'
    flags = re.UNICODE if six.PY2 else 0
