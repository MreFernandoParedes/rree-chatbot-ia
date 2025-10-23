def validate_user_data(data):
    errors = {}

    validate_required_field(data, 'Name', errors)
    validate_required_field(data, 'LastName', errors)
    validate_required_field(data, 'Company', errors)
    validate_required_field(data, 'Email', errors)
    validate_required_field(data, 'Password', errors)
    validate_email(data, errors)
    validate_password(data, errors)

    return errors if errors else None


def validate_required_field(data, field_name, errors):
    if field_name in data:
        if not isinstance(data[field_name], str) or not data[field_name].strip():
            errors[field_name] = [f'{field_name} is required and cannot be blank.']
    else:
        errors[field_name] = [f'{field_name} field is missing.']


def validate_email(data, errors):
    if 'Email' in data:
        if not "@" in data['Email']:
            errors['Email'] = ['Email must contain @.']
    else:
        errors['Email'] = ['Email field is missing.']


def validate_password(data, errors):
    if 'Password' in data:
        if not isinstance(data['Password'], str) or len(data['Password']) < 8:
            errors['Password'] = ['Password must be at least 8 characters long.']
    else:
        errors['Password'] = ['Password field is missing.']
