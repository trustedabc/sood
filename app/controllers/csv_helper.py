import json

def personal_info_headers(headers):
    headers += ['Name', 'Email', 'Mobile','Github','LinkedIn', 'City', 'Country', 'Title']

def skills_headers(headers):
    headers += [f'Language{i+1}' for i in range(5)]
    headers += [f'Framework{i+1}' for i in range(5)]
    headers += [f'Technology{i+1}' for i in range(5)]
    headers += ['LLM Experience', 'Gen AI Experience']
    for i in range(5):
        headers += [f'Skill_Experience_{i+1}', f'Skill_Experience_Years_{i+1}']

def education_headers(headers):
    for i in range(5):
        headers += [f'School_Name{i+1}', f'Degree_Name{i+1}', f'City{i+1}', f'Country{i+1}', 
                    f'Year_Of_Start{i+1}', f'Year_Of_Graduation{i+1}', f'Duration_In_Years{i+1}', 
                    f'Degree_Level{i+1}',f'Is Cs Degree{i+1}',f'Is ML Degree{i+1}',f'Institute Type{i+1}']

def experience_headers(headers):
    for i in range(5):
        headers += [f'Company_Name{i+1}', f'Position_Held{i+1}', f'City{i+1}', f'Country{i+1}', 
                    f'Joining_Date{i+1}', f'Leaving_Date{i+1}', f'Total_Duration{i+1}',f'Company Size Range{i+1}',
                    f'Total Capital Raised{i+1}',f'Company Type{i+1}',f'Is Faang{i+1}',
                        f'has_the_company_raised_capital_in_the_last_5_years{i+1}',
                        f'Is Startup{i+1}',f'Industry Type{i+1}']

def project_headers(headers):
    for i in range(5):
        headers += [f'Project_Name{i+1}', f'Project_Description{i+1}']

def additional_experience_summary_headers(headers):
    headers += [
            'Last_Position_Held', 'Years_Of_Full_Time_Experience', 'Total_Startup_Experience', 
            'Total_Early_Stage_Startup_Experience', 'Product_Company_Experience', 
            'Service_Company_Experience', 'Gen_AI_Experience'
        ]

def overall_summary_headers(headers):
    headers.append('Overall_Summary')

def parsed_data_header(headers):
    headers.append('Parsed Data')

def personal_info_data(parsed_data,row):
    personal_info = parsed_data.get('personal_information', {})
    row += [
        personal_info.get('name', ''),
        personal_info.get('email', ''),
        personal_info.get('mobile', ''),
        personal_info.get('github', ''),
        personal_info.get('linkedin', ''),
        personal_info.get('city', ''),
        personal_info.get('country', ''),
        parsed_data.get('title', '')
    ]

def skills_data(parsed_data, row):
    for skill_type in ['languages', 'frameworks', 'technologies']:
        skills = parsed_data.get('skills', {}).get(skill_type, {})
        proficient = skills.get('proficient', [])
        average = skills.get('average', [])
        combined = proficient[:5] + average[:5 - len(proficient)] 
        row += combined + [''] * (5 - len(combined))  

    row += [
        parsed_data.get('skills', {}).get('llm_experience', False),
        parsed_data.get('skills', {}).get('gen_ai_experience', False)
    ]

    total_skill_experience = parsed_data.get('skills', {}).get('total_skill_experience', {})
    
    top_5_skills = list(total_skill_experience.items())[:5]

    for skill, exp in top_5_skills:
        row += [skill, exp]  
    row += [''] * (5 - len(top_5_skills)) * 2 




def educations_data(parsed_data,row):
    educations = parsed_data.get('education', [])[:5]
    educations = educations + [{}] * (5 - len(educations))  
    for edu in educations:
        row += [
            edu.get('school_name', ''),
            edu.get('degree_name', ''),
            edu.get('city', ''),
            edu.get('country', ''),
            edu.get('year_of_start', ''),
            edu.get('year_of_graduation', ''),
            edu.get('duration_in_years', ''),
            edu.get('degree_level', ''),
            edu.get('is_cs_degree'),
            edu.get('is_ml_degree'),
            edu.get('institute_type')
        ]

def experience_data(parsed_data,row):
    experiences = parsed_data.get('experience', [])[:5]  
    experiences = experiences + [{}] * (5 - len(experiences))  
    for exp in experiences:
        company_info = exp.get('company_information', {})
        position = exp.get('positions_held_within_the_company', [{}])[0]
        row += [
            company_info.get('name', ''),
            position.get('position_name', ''),
            company_info.get('city', ''),
            company_info.get('country', ''),
            company_info.get('joining_month_and_year', ''),
            company_info.get('leaving_month_and_year', ''),
            company_info.get('total_duration_in_years', ''),
            company_info.get('company_size_range'),
            company_info.get('total_capital_raised'),
            company_info.get('company_type'),
            company_info.get('is_faang'),
            company_info.get('has_the_company_raised_capital_in_the_last_5_years?'),
            company_info.get('is_startup'),
            company_info.get('industry_type')
        ]

def project_data(parsed_data,row):
    projects = parsed_data.get('projects_outside_of_work', [])[:5]  
    projects = projects + [{}] * (5 - len(projects)) 
    for project in projects:
        row += [
            project.get('project_name', ''),
            project.get('project_description', '')
        ]

def additional_experience_summary_data(parsed_data,row):
    additional_experience = parsed_data.get('additional_experience_summary', {})
    row += [
        additional_experience.get('last_position_held', ''),
        additional_experience.get('years_of_full_time_experience_after_graduation', ''),
        additional_experience.get('total_startup_experience', ''),
        additional_experience.get('total_early_stage_startup_experience', ''),
        additional_experience.get('product_company_experience', ''),
        additional_experience.get('service_company_experience', ''),
        additional_experience.get('gen_ai_experience', '')
    ]

def overall_summary_data(parsed_data,row):
    row.append(parsed_data.get('overall_summary_of_candidate', ''))

def json_data(parsed_data,row):
    row.append(json.dumps(parsed_data))


 