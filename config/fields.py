# Profile fields projection
PROFILE_PROJECTION = {
    '_id': 1,
    'name': 1,
    'position': 1,
    'location': 1,
    'open_to_work': 1,
    'about': 1,
    'url': 1
}

# Experience fields projection
EXPERIENCE_PROJECTION = {
    'profile': 1,
    'company_page': 1,
    'role': 1,
    'work_at': 1,
    'duration': 1,
    'location': 1,
    'role_summery': 1
}

# Education fields projection
EDUCATION_PROJECTION = {
    'profile': 1,
    'university_url': 1,
    'university_name': 1,
    'degree': 1,
    'field_of_study': 1,
    'start_date': 1,
    'end_date': 1,
}