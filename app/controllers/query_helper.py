import re
from datetime import datetime, timedelta
from app.models import Resume
from django.utils import timezone
from bson import ObjectId
from dateutil.relativedelta import relativedelta
from app.constants import TimeFilter
from resumeparser.settings import logger

def full_time_experience_query(params,filter_query):
    if params.get('full_time_experience'):
        filter_query["parsed_data.additional_experience_summary.years_of_full_time_experience_after_graduation"] =  {
                "$gte": float(params['full_time_experience'])
                }

def skills_experience_query(params,filter_query):
    if params.get('skills_experience'):
        skills = split_and_strip(params, "skills_experience")

        skill_queries = []
        for skill in skills:
            skill_name, experience_years = skill.split('|')
            experience_years = float(experience_years)
            skill_query = {
                f"parsed_data.skills.total_skill_experience.{skill_name.lower()}": {
                    "$gte": experience_years
                }
            }
            skill_queries.append(skill_query)

        if skill_queries:
            if "$and" in filter_query:
                filter_query["$and"].append(skill_queries)
            else:
                filter_query["$and"] = skill_queries

def company_type_query(params,filter_query):
    if params.get('company_type') == 'product':
        filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
            "$gt": 0
        }

def product_company_experience_query(params,filter_query):
    if params.get('product_company_experience'):
        filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
            "$gte": float(params['product_company_experience'])
        }

def startup_experience_query(params,filter_query):
    if params.get('startup_experience'):
        filter_query["parsed_data.additional_experience_summary.total_startup_experience"] = {
            "$gte": float(params['startup_experience'])
        }

def degree_type_query(params,filter_query):
    if params.get('degree_type'):
        filter_query["parsed_data.education.degree_level"] = {
            "$regex": f"^{params['degree_type']}$", "$options": "i"
        }

def last_position_held_query(params,filter_query):
    if params.get('last_position_held'):
        filter_query["parsed_data.additional_experience_summary.last_position_held"] = {
            "$regex": f".*{re.escape(params['last_position_held'])}.*",
            "$options": "i"
        }
        
def gen_ai_experience_query(params,filter_query):
     if params.get('gen_ai_experience'):
        filter_query["parsed_data.skills.gen_ai_experience"] = params['gen_ai_experience'].lower() == 'true'

def is_ml_degree_query(params,filter_query):
    if params.get('is_ml_degree'):
        filter_query["parsed_data.education.is_ml_degree"] = params['is_ml_degree'].lower() == 'true'

def is_cs_degree_query(params,filter_query):
    if params.get('is_cs_degree'):
        filter_query["parsed_data.education.is_cs_degree"] = params['is_cs_degree'].lower() == 'true'

def early_stage_startup_experience_query(params,filter_query):
    if params.get('early_stage_startup_experience'):
        filter_query["parsed_data.additional_experience_summary.total_early_stage_startup_experience"] = {
            "$gte": float(params['early_stage_startup_experience'])
        }

def institute_type_query(params, filter_query):
    institute_type = params.get('institute_type')
    if institute_type:
        if institute_type.lower() == "all":
            filter_query["parsed_data.education.institute_type"] = {
                "$in": ["iit", "nit", "iiit", "bits"]
            }
        else:
            filter_query["parsed_data.education.institute_type"] = {
                "$regex": f"^{re.escape(institute_type)}$",
                "$options": "i"
            }


def llm_experience_query(params,filter_query):
    if params.get('llm_experience'):
        filter_query["parsed_data.skills.llm_experience"] = params['llm_experience'].lower() == 'true'

def service_company_experience_query(params,filter_query):
    if params.get('service_company_experience'):
        filter_query["parsed_data.additional_experience_summary.service_company_experience"] = {
            "$gte": float(params['service_company_experience'])
        }

def resume_type_query(params,filter_query):
    if params.get('resume_type'):
        filter_query["parsed_data.resume_type"] = {
            "$regex": f"^{params['resume_type']}$", "$options": "i"
        }

def projects_outside_of_work_query(params,filter_query):
    if params.get('projects_outside_of_work'):
        filter_query["parsed_data.projects_outside_of_work"] = {"$exists": True, "$ne": []}

def skills_and_query(params, filter_query):
    if params.get('skills_and'):
        skills = split_and_strip(params, 'skills_and')
        if skills:
            skill_conditions = []

            for skill in skills:
                skill_conditions.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.average": {"$in": [skill]}},
                        {"parsed_data.skills.languages.average": {"$in": [skill]}},
                        {"parsed_data.skills.technologies.average": {"$in": [skill]}}
                    ]
                })

            if skill_conditions:
                if "$and" in filter_query:
                    filter_query["$and"].extend(skill_conditions)
                else:
                    filter_query["$and"] = skill_conditions

    return filter_query



def proficient_technologies_and_query(params,filter_query):
    if params.get('proficient_technologies_and'):
        proficient_technologies_and = split_and_strip(params, 'proficient_technologies_and')
        if proficient_technologies_and:
            proficient_technologies_condition = []
            for proficient_technology in proficient_technologies_and:
                proficient_technologies_condition.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [proficient_technology]}},
                    ]
                })
            if proficient_technologies_condition:
                if "$and" in filter_query:
                    filter_query["$and"].extend(proficient_technologies_condition)
                else:
                    filter_query["$and"] = proficient_technologies_condition

    return filter_query


def skills_or_query(params, filter_query):
    if params.get('skills_or'):
        skills = split_and_strip(params, 'skills_or')
        if skills:
            skill_conditions = []

            for skill in skills:
                skill_conditions.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.average": {"$in": [skill]}},
                        {"parsed_data.skills.languages.average": {"$in": [skill]}},
                        {"parsed_data.skills.technologies.average": {"$in": [skill]}}
                    ]
                })

            if skill_conditions:
                if "$or" in filter_query:
                    filter_query["$or"].extend(skill_conditions)
                else:
                    filter_query["$or"] = skill_conditions

    return filter_query



def proficient_technologies_or_query(params,filter_query):
    if params.get('proficient_technologies_or'):
        proficient_technologies_or = split_and_strip(params, 'proficient_technologies_or')
        if proficient_technologies_or:
            proficient_technologies_condition = []
            for proficient_technology in proficient_technologies_or:
                proficient_technologies_condition.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [proficient_technology]}},
                    ]
                })
            if proficient_technologies_condition:
                if "$or" in filter_query:
                    filter_query["$or"].extend(proficient_technologies_condition)
                else:
                    filter_query["$or"] = proficient_technologies_condition

    return filter_query

def time_filter(filter_query, time_threshold):
    parsed_data_ids = Resume.time_filter_resumes_id(time_threshold)
    
    valid_object_ids = []
    
    for id in parsed_data_ids:
        try:
            if ObjectId.is_valid(id):
                valid_object_ids.append(ObjectId(id))
            else:
                logger.info(f"Invalid ObjectId: {id} - Skipping")
        except errors.InvalidId:
            logger.error(f"Error with ObjectId: {id} - Skipping",exc_info=True)
    
    filter_query["_id"] = {"$in": valid_object_ids}

def one_hour_filter(params, filter_query):
    if params.get('time_filter') == TimeFilter.ONE_HOUR:
        time_threshold = timezone.now() - timedelta(hours=1)
        time_filter(filter_query,time_threshold)
    

def six_hour_filter(params, filter_query):
    if params.get('time_filter') == TimeFilter.SIX_HOUR:
        time_threshold = timezone.now() - timedelta(hours=6)
        time_filter(filter_query,time_threshold)


def tweleve_hour_filter(params, filter_query):
    if params.get('time_filter') == TimeFilter.TWELEVE_HOUR:
        time_threshold = timezone.now() - timedelta(hours=12)
        time_filter(filter_query,time_threshold)


def one_day_filter(params, filter_query):
    if params.get('time_filter') == TimeFilter.ONE_DAY:
        time_threshold = timezone.now() - timedelta(days=1)
        time_filter(filter_query,time_threshold)


def one_week_filter(params, filter_query):
    if params.get("time_filter") == TimeFilter.ONE_WEEK:
        time_threshold = timezone.now() - timedelta(days=7)
        time_filter(filter_query,time_threshold)

def two_week_filter(params, filter_query):
    if params.get("time_filter") == TimeFilter.TWO_WEEK:
        time_threshold = timezone.now() - timedelta(days=14)
        time_filter(filter_query,time_threshold)

def three_week_filter(params, filter_query):
    if params.get("time_filter") == TimeFilter.THREE_WEEK:
        time_threshold = timezone.now() - timedelta(days=21)
        time_filter(filter_query,time_threshold)
    
def forty_five_days_filter(params, filter_query):
    if params.get("time_filter") == TimeFilter.FORTY_FIVE_DAYS:
        time_threshold = timezone.now() - timedelta(days=45)
        time_filter(filter_query,time_threshold)

def one_month_filter(params, filter_query):
    if params.get("time_filter") == TimeFilter.ONE_MONTH:
        time_threshold = timezone.now() - relativedelta(months=1)
        time_filter(filter_query,time_threshold)

def two_month_filter(params, filter_query):
    if params.get("time_filter") == TimeFilter.TWO_MONTH:
        time_threshold = timezone.now() - relativedelta(months=2)
        time_filter(filter_query,time_threshold)

def three_month_filter(params, filter_query):
    if params.get("time_filter") == TimeFilter.THREE_MONTH:
        time_threshold = timezone.now() - relativedelta(months=3)
        time_filter(filter_query,time_threshold)

def industry_type_filter(params, filter_query):
    if params.get('industry_type'):
        industry_type = params['industry_type']
        
        filter_query["parsed_data.experience.company_information.industry_type"] = {
            "$regex": f"^{re.escape(industry_type)}$",  
            "$options": "i"
        }

def company_size_filter(params, filter_query):
    if params.get('company_size'):
        company_size = params['company_size']
        filter_query["parsed_data.experience.company_information.company_size_range"] = {
            "$regex": f"^{re.escape(company_size)}$",  
            "$options": "i"
        }

def split_and_strip(params, key):
        if key in params:
            return [tech.strip() for tech in params[key].split(',')]
        return []
