def decorate_csv(resumes):
    for data in resumes:
        parsed_data = data['parsed_data']
        if isinstance(parsed_data['skills']['total_skill_experience'], dict):
            converted_experience = {}
            
            for skill, experience in parsed_data['skills']['total_skill_experience'].items():
                experience_str = convert_to_years_months(experience)
                converted_experience[skill] = experience_str
            
            parsed_data['skills']['total_skill_experience'] = converted_experience
        
        parsed_data['additional_experience_summary']['years_of_full_time_experience_after_graduation'] = convert_to_years_months(parsed_data['additional_experience_summary']['years_of_full_time_experience_after_graduation'])
        parsed_data['additional_experience_summary']['total_startup_experience'] = convert_to_years_months(parsed_data['additional_experience_summary']['total_startup_experience'])
        parsed_data['additional_experience_summary']['total_early_stage_startup_experience'] = convert_to_years_months(parsed_data['additional_experience_summary']['total_early_stage_startup_experience'])
        parsed_data['additional_experience_summary']['product_company_experience'] = convert_to_years_months(parsed_data['additional_experience_summary']['product_company_experience'])
        parsed_data['additional_experience_summary']['service_company_experience'] = convert_to_years_months(parsed_data['additional_experience_summary']['service_company_experience'])
        
        
        
    
def convert_to_years_months(value: float) -> str:
    if value is None:
        value = 0
    years = int(value)
    months = round((value - years) * 12)

    year_str = "year" if years == 1 else "years"
    month_str = "month" if months == 1 else "months"

    if years > 0 and months > 0:
        return f"{years} {year_str} {months} {month_str}"
    elif years > 0:
        return f"{years} {year_str}"
    else:
        return f"{months} {month_str}"
