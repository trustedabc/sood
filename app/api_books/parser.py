import requests
import json
import os
from resumeparser.settings import logger
from app.serializers import ParsedResumeSerializer

def extract_info_from_resume(resume_text):
    prompt_str = """
Extract the following information from the resume and provide it in a JSON format as specified below. Ensure that you don't add leading commas, brackets anywhere in the response.

{
    "personal_information": {
        "name": "<string: name of the candidate>",
        "email": "<string: email of the candidate>",
        "mobile": "<string: mobile no. of the candidate>",
        "city": "<string: city where the candidate lives>",
        "country": "<string: country where the candidate lives>",
        "linkedin": "<linkedin URL or None>",
        "github": "<github URL or None>"
    },
    "resume_type": "<string: type of resume options: [backend_engineer, frontend_engineer, full_stack_engineer, devops_engineer, qa_engineer, test_engineer, ai_engineer, machine_learning_engineer, data_scientist, tech_lead, director, engineering_manager, ml_research_engineer, ml_ops_engineer, computer_vision_engineer, natural_language_processing_(NLP)_engineer, reinforcement_learning_engineer]>",
    "title": "<string: give appropriate descriptive title to the candidate according to his/her profile>",
    "skills": {
        "languages": {
            "proficient": [
                "<string: name of the language proficient in lowercase letter (e.g. python)>",
                "Can have multiple proficient languages, at max 3"
            ],
            "average": [
                "<string: name of the language average in lowercase letter (e.g. python)>"
            ]
        },
        "frameworks": {
            "proficient": [
                "<string: name of the frameworks proficient in lowercase letter (e.g. django)>",
                "Can have multiple proficient frameworks, at max 3"
            ],
            "average": [
                "<string: name of the framework average in lowercase letter (e.g. django)>"
            ]
        },
        "technologies": {
            "proficient": [
                "<string: name of the technologies proficient in lowercase letter (e.g. github)>",
                "Can have multiple proficient technologies, at max 3"
            ],
            "average": [
                "<string: name of the technologies average in lowercase letter (e.g. github)>"
            ]
        },
        "total_skill_experience": {
            "<string: name of the skill>": <float: no. of years of experience>,
            "<string: name of the skill>": <float: no. of years of experience>,
            "Can have multiple skills"
        },
        "llm_experience": <string: [true, false]>,
        "gen_ai_experience": <string: [true, false]>
    },
    "education": [
        {
            "school_name": "<string: name of the college/school>",
            "degree_name": "<string: name of the degree>",
            "city": "<string: city where the school is located>",
            "country": "<string: country where the school is located>",
            "year_of_start": <int: starting year of the degree>,
            "year_of_graduation": <int: year of graduation>,
            "duration_in_years": <int: total no. of years of degree>,
            "mode": "<string: [offline, online]>",
            "degree_level": "<string: [masters, bachelors]>",
            "is_cs_degree": <string: [true, false]>,
            "is_ml_degree": <string: [true, false]>,
            "institute_type": "<string: [other, iit, nit, iiit]>"
        }
    ],
    "experience": [
        {
            "company_information": {
                "name": "<string: name of the company>",
                "last_position_held": "<string: last position role>",
                "city": "<string: city where company is located>",
                "country": "<string: country where company is located>",
                "joining_month_and_year": "<string: joining_month joining_year>",
                "leaving_month_and_year": "<string: leaving_month leaving_year>",
                "total_duration_in_years": <float: total years worked in this company>,
                "company_size_range": "<string: [>50,50-200,200-500,500-1000,1000<]>",
                "total_capital_raised": "<string: total capital raised by the company>",
                "company_type": "<string: [service, product]>",
                "is_faang": <string: [true, false]>,
                "has_the_company_raised_capital_in_the_last_5_years": "<string: [Yes, No]>",
                "is_startup": <string: [true, false]>,
                "industry_type": <string: [fintech, healthtech,edtech,proptech,insurtech,greentech,agritech,foodtech,hft,legaltech,marttech,hrtech,retailtech,cybersecurity,autotech,govtech,deeptech]>
            },
            "candidate_company_summary": "<string: Summary of the work done by the candidate at the company>",
            "positions_held_within_the_company": [
                {
                    "position_name": "<string: position name>",
                    "position_starting_date": "<string: starting_month starting_year>",
                    "position_ending_date": "<string: ending_month ending_year>",
                    "projects": [
                        {
                            "project_name": "<string: project_name>",
                            "project_description": "<string: project_description>"
                        }
                    ]
                }
            ]
        }
    ],
    "projects_outside_of_work": [
        {
            "project_name": "<string: project name (outside company work)>",
            "project_description": "<string: project description>"
        }
    ],
    "additional_experience_summary": {
        "last_position_held": "<string: last position held in the last company>",
        "years_of_full_time_experience_after_graduation": <float: no. of years of experience after graduation>,
        "total_startup_experience": <float: no. of years of experience in startups>,
        "total_early_stage_startup_experience": <float: no. of years of experience in early-stage startups>,
        "product_company_experience": <float: no. of years of experience in product-based companies>,
        "service_company_experience": <float: no. of years of experience in service-based companies>,
        "gen_ai_experience": <string: [true, false]>
    },
    "achievements_awards": {
        "summary_of_achievements_awards": [
            "List each achievement of the candidate (e.g., great projects, awards, coding platform ranks, etc.)"
        ],
        "position_blurbs": [
            "List each position blurb of the candidate"
        ]
    },
    "overall_summary_of_candidate": "<string: Overall summary of the candidate>"
    """




    url = os.getenv("SERVER_URL")
    headers = {
        'Content-Type': 'application/json',
        'api-key': os.getenv('API_KEY')
    }

    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": prompt_str + "\n\n" + resume_text
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 3500
    })

    try:
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            json_data = response.json()
            response_content = json_data.get('choices', [{}])[0].get('message', {}).get('content', None)

            response_content = response_content.replace("```json", "").replace("```", "").strip()

            try:
                response_dict = json.loads(response_content) 
            except json.JSONDecodeError as e:
                logger.error(f"JSON decoding error: {e} - Response content: {response_content}")
                return None

            serializer = ParsedResumeSerializer(data=response_dict)

            if serializer.is_valid():
                logger.info("Information extracted and validated successfully.")
                return serializer.data  
            else:
                logger.error(f"Validation errors: {serializer.errors}",exc_info=True)
                return None

        else:
            logger.error(f"Error in API response: {response.status_code}")
            return None

    except requests.RequestException as e:
        logger.error(f"API request error: {e}", exc_info=True)
        return None




