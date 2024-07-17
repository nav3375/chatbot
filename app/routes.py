import pandas as pd
from flask import Blueprint, request, jsonify

main = Blueprint('main', __name__)

# Load the datasets
skill_mapping_data = pd.read_csv('data/cleneddata - Copy.csv')
courses_data = pd.read_csv('data/coursera_course_dataset_v3.csv')

def parse_skills(skill_string):
    return set(skill.strip().lower() for skill in skill_string.split(',') if skill.strip())

skill_mapping = {row['Job Title']: parse_skills(row['Extracted Skills']) for _, row in skill_mapping_data.iterrows()}

def extract_skills_from_input(input_skills):
    return parse_skills(input_skills)

def recommend_courses(missing_skills, courses_data, max_recommendations=10):
    skills_column = 'Skills'

    def skill_in_course(course_skills, missing_skills):
        if pd.isna(course_skills):
            return False
        course_skills_list = [skill.strip().lower() for skill in course_skills.split(',')]
        matched_skills = set(course_skills_list).intersection(set(missing_skills))
        return len(matched_skills), matched_skills

    courses_data['RelevanceScore'] = courses_data[skills_column].apply(lambda x: skill_in_course(x, missing_skills)[0])
    courses_data['MatchedSkills'] = courses_data[skills_column].apply(lambda x: skill_in_course(x, missing_skills)[1])

    recommended_courses = courses_data[courses_data['RelevanceScore'] > 0]
    recommended_courses = recommended_courses[recommended_courses['Ratings'] >= 4.0]
    recommended_courses = recommended_courses.sort_values(by=['RelevanceScore', 'Ratings'], ascending=False)
    recommended_courses = recommended_courses.head(max_recommendations)

    columns_to_select = ['Title', 'course_url', 'RelevanceScore', 'MatchedSkills', 'Organization', 'Ratings', 'Difficulty', 'Type', 'Duration']
    return recommended_courses[columns_to_select]

@main.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    job_title = data.get('job_title')
    input_skills = data.get('skills')

    if not job_title or not input_skills:
        return jsonify({'error': 'Missing job title or skills'}), 400

    cv_skills = extract_skills_from_input(input_skills)
    required_skills = skill_mapping.get(job_title, [])
    missing_skills = list(set(required_skills) - set(cv_skills))

    if not missing_skills:
        return jsonify({'message': 'You have all the required skills!'}), 200

    recommended_courses = recommend_courses(missing_skills, courses_data)
    return jsonify(recommended_courses.to_dict(orient='records'))
