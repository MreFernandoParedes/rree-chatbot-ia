def validate_chat_data(data):
    errors = {}
    validate_required_field(data, 'userEmail', errors)
    validate_required_field(data, 'chatQuestion', errors)
    validate_required_field(data, 'chatAnswer', errors)
    validate_email(data, errors)
    return errors if errors else None


def validate_required_field(data, field_name, errors):
    if field_name in data:
        if not isinstance(data[field_name], str) or not data[field_name].strip():
            errors[field_name] = [f'{field_name} is required and cannot be blank.']
    else:
        errors[field_name] = [f'{field_name} field is missing.']


def validate_email(data, errors):
    if 'userEmail' in data:
        if not isinstance(data['userEmail'], str) or not data['userEmail'].strip():
            errors['userEmail'] = ['userEmail must be a non-empty string.']
    else:
        errors['userEmail'] = ['userEmail field is missing.']
