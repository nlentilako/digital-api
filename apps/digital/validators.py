from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value):
    """
    Validate phone number format.
    Expected format: 10-15 digits, may start with country code.
    """
    # Remove any non-digit characters
    digits_only = re.sub(r'\D', '', value)
    
    # Check if it's between 10 and 15 digits
    if len(digits_only) < 10 or len(digits_only) > 15:
        raise ValidationError(
            _('Phone number must be between 10 and 15 digits.'),
            params={'value': value},
        )
    
    # Additional validation could be added for specific country formats
    # For Ghana, phone numbers typically start with 024, 027, 054, 055, 059, etc.
    if not re.match(r'^(\+?233|0)?(24|27|54|55|59|26|23|57)\d{7}$', digits_only):
        # This is a simplified Ghanaian number validation
        # In a real application, you'd want more comprehensive validation
        pass  # We'll allow any 10-15 digit number for now


def validate_ghanaian_phone_number(value):
    """
    Specifically validate Ghanaian phone numbers.
    """
    # Remove any non-digit characters
    digits_only = re.sub(r'\D', '', value)
    
    # Check length (Ghanaian mobile numbers are 10 digits after removing country code)
    if len(digits_only) == 10 and digits_only.startswith('0'):
        # Local format: 024XXXXXXX
        valid_prefixes = ['024', '027', '054', '055', '059', '026', '023', '057']
        if not any(digits_only.startswith(prefix) for prefix in valid_prefixes):
            raise ValidationError(
                _('Invalid Ghanaian phone number prefix.'),
                params={'value': value},
            )
    elif len(digits_only) == 12 and digits_only.startswith('233'):
        # International format: 23324XXXXXXX
        valid_prefixes = ['23324', '23327', '23354', '23355', '23359', '23326', '23323', '23357']
        if not any(digits_only.startswith(prefix) for prefix in valid_prefixes):
            raise ValidationError(
                _('Invalid Ghanaian phone number prefix.'),
                params={'value': value},
            )
    elif len(digits_only) == 9:
        # Short format: 24XXXXXXX
        valid_prefixes = ['24', '27', '54', '55', '59', '26', '23', '57']
        if not any(digits_only.startswith(prefix) for prefix in valid_prefixes):
            raise ValidationError(
                _('Invalid Ghanaian phone number prefix.'),
                params={'value': value},
            )
    else:
        raise ValidationError(
            _('Invalid Ghanaian phone number format.'),
            params={'value': value},
        )


def validate_positive_decimal(value):
    """
    Validate that a decimal value is positive.
    """
    if value <= 0:
        raise ValidationError(
            _('Value must be greater than zero.'),
            params={'value': value},
        )


def validate_denomination(value):
    """
    Validate denomination format for digital products.
    """
    if value is not None and value <= 0:
        raise ValidationError(
            _('Denomination must be greater than zero.'),
            params={'value': value},
        )


def validate_size_format(value):
    """
    Validate size format for data bundles (e.g., '1GB', '500MB').
    """
    if value:
        # Simple validation for size format
        if not re.match(r'^\d+(MB|GB|KB)$', value.upper()):
            raise ValidationError(
                _('Size must be in format like 1GB, 500MB, 1024KB.'),
                params={'value': value},
            )