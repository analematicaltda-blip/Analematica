from django.core.exceptions import ValidationError

def validate_positive_amount(value):
    if value < 0:
        raise ValidationError("El monto debe ser positivo.")
