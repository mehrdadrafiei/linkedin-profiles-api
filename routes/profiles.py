from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from config.fields import (
    PROFILE_PROJECTION,
    EXPERIENCE_PROJECTION,
    EDUCATION_PROJECTION
)

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/profiles', methods=['GET'])
def get_profiles():
    db = current_app.db
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    skip = (page - 1) * per_page
    total = db.profiles.count_documents({})
    
    profiles = list(db.profiles.find(
        {},
        PROFILE_PROJECTION
    ).skip(skip).limit(per_page))
    
    for profile in profiles:
        profile['_id'] = str(profile['_id'])
    
    return jsonify({
        'data': profiles,
        'page': page,
        'per_page': per_page,
        'total': total
    })

@profiles_bp.route('/profiles/<profile_id>', methods=['GET'])
def get_profile_details(profile_id):
    db = current_app.db
    
    profile = db.profiles.find_one(
        {'_id': ObjectId(profile_id)},
        PROFILE_PROJECTION
    )
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    experiences = list(db.experiences.find(
        {'profile': ObjectId(profile_id)},
        EXPERIENCE_PROJECTION
    ))
    
    educations = list(db.educations.find(
        {'profile': ObjectId(profile_id)},
        EDUCATION_PROJECTION
    ))
    
    # Convert ObjectIds to strings
    profile['_id'] = str(profile['_id'])
    for exp in experiences:
        exp['_id'] = str(exp['_id']),
        exp['profile'] = str(exp['profile'])
    for edu in educations:
        edu['_id'] = str(edu['_id'])
        edu['profile'] = str(edu['profile'])
    
    return jsonify({
        'profile': profile,
        'experiences': experiences,
        'educations': educations
    })

@profiles_bp.route('/profiles/search', methods=['GET'])
def search_profiles():
    db = current_app.db
    query = request.args.get('query', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    skip = (page - 1) * per_page
    
    # Build search queries for each collection
    profiles_query = {
        '$or': [
            {'location': {'$regex': query, '$options': 'i'}},
            {'position': {'$regex': query, '$options': 'i'}},
            {'open_to_work': query.lower() == 'true' if query.lower() in ['true', 'false'] else None}
        ]
    }
    
    experiences_query = {
        '$or': [
            {'work_at': {'$regex': query, '$options': 'i'}},
            {'role': {'$regex': query, '$options': 'i'}}
        ]
    }
    
    educations_query = {
        '$or': [
            {'university_name': {'$regex': query, '$options': 'i'}},
            {'field_of_study': {'$regex': query, '$options': 'i'}}
        ]
    }
    
    # Remove None values from the profiles query
    profiles_query['$or'] = [item for item in profiles_query['$or'] if item[list(item.keys())[0]] is not None]
    
    # Step 1: Find matching profiles
    matching_profiles = list(db.profiles.find(
        profiles_query,
        PROFILE_PROJECTION
    ).skip(skip).limit(per_page))
    
    # Step 2: Find matching experiences and get associated profile IDs
    matching_experiences = list(db.experiences.find(experiences_query))
    experience_profile_ids = [exp['profile'] for exp in matching_experiences]
    
    # Step 3: Find matching educations and get associated profile IDs
    matching_educations = list(db.educations.find(educations_query))
    education_profile_ids = [edu['profile'] for edu in matching_educations]
    
    # Combine all unique profile IDs
    unique_profile_ids = set(experience_profile_ids + education_profile_ids)
    
    # Step 4: Fetch profiles for the combined IDs
    if unique_profile_ids:
        object_ids = [ObjectId(pid) for pid in unique_profile_ids]
        additional_profiles = list(db.profiles.find(
            {'_id': {'$in': object_ids}},
            PROFILE_PROJECTION
        ))
        matching_profiles.extend(additional_profiles)
    
    # Remove duplicates (if any)
    unique_profiles = {profile['_id']: profile for profile in matching_profiles}.values()
    
    # Convert ObjectIds to strings
    for profile in unique_profiles:
        profile['_id'] = str(profile['_id'])
    
    # Get total count of matching profiles
    total = len(unique_profiles)
    
    # Apply pagination
    paginated_profiles = list(unique_profiles)[skip:skip + per_page]
    
    return jsonify({
        'data': paginated_profiles,
        'page': page,
        'per_page': per_page,
        'total': total,
        'query': query
    })