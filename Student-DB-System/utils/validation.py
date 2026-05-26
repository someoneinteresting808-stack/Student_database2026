import re

def validate_login_fields(username, password):
    if not username or not username.strip():
        return False, "Username field is required"
    if not password or not password.strip():
        return False, "Password field is required"
    return True, ""

def validate_student_fields(student_id, name, email, phone, department, year_level, username=None, password=None, is_creation=True):
    if not student_id or not student_id.strip():
        return False, "Student ID is required"
    if not name or not name.strip():
        return False, "Full Name is required"
    if not email or not email.strip():
        return False, "Email is required"
    if "@" not in email:
        return False, "Invalid email address format (missing '@')"
    if not phone or not phone.strip():
        return False, "Phone Number is required"
    if not phone.replace("-", "").replace("+", "").strip().isdigit():
        return False, "Phone Number must contain only digits"
    if not department or not department.strip():
        return False, "Department is required"
    if not year_level or not year_level.strip():
        return False, "Year level is required"
    if is_creation:
        if not username or not username.strip():
            return False, "Student account Username is required"
        if not password or not password.strip():
            return False, "Student account Password is required"
    return True, ""

def validate_grade_fields(subject_name, score_str):
    if not subject_name or not subject_name.strip():
        return False, "Subject name is required"
    if not score_str or not score_str.strip():
        return False, "Score is required"
    try:
        score = float(score_str)
        if score < 0 or score > 100:
            return False, "Subject score must be between 0 and 100"
    except ValueError:
        return False, "Subject score must be a number"
    return True, ""
