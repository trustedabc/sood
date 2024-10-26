from rest_framework import serializers
from app.models import Resume
from django.core.exceptions import ValidationError
import json
from drf_yasg import openapi
from drf_yasg.utils import swagger_serializer_method
import re
from resumeparser.settings import logger

class ResumeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    modified_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = (
            'id', 'parsing_status', 'no_of_retries', 
            'parsed_data_id', 'created_at', 'modified_at',
            'storage_path', 'resume_category'
        )

    def create(self, validated_data):
        return Resume.objects.create(**validated_data)

    def create_bulk(self, files):
        resume_objects = [Resume(file=file) for file in files]
        return Resume.bulk_create_resume(resume_objects)
    

class ProficiencySerializer(serializers.Serializer):
    proficient = serializers.ListField(child=serializers.CharField(allow_blank=True), max_length=3, required=False)
    average = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False)


class SkillSerializer(serializers.Serializer):
    languages = ProficiencySerializer(required=False)
    frameworks = ProficiencySerializer(required=False)
    technologies = ProficiencySerializer(required=False)
    total_skill_experience = serializers.DictField(required=False, allow_null=True)
    llm_experience = serializers.CharField(required=False)  
    gen_ai_experience = serializers.CharField(required=False)


class CompanyInformationSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_position_held = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    joining_month_and_year = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    leaving_month_and_year = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    total_duration_in_years = serializers.FloatField(required=False, allow_null=True)  
    company_size_range = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    total_capital_raised = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_faang = serializers.CharField(required=False)  
    has_the_company_raised_capital_in_the_last_5_years = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_startup = serializers.CharField(required=False) 
    industry_type = serializers.CharField(required=False,allow_blank=True,allow_null=True)


class ExperienceSerializer(serializers.Serializer):
    company_information = CompanyInformationSerializer(required=False)
    positions_held_within_the_company = serializers.ListField(child=serializers.DictField(), required=False)
    candidate_company_summary = serializers.CharField(required=False, allow_blank=True,allow_null=True)


class EducationSerializer(serializers.Serializer):
    school_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    degree_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    year_of_start = serializers.IntegerField(required=False, allow_null=True)  
    year_of_graduation = serializers.IntegerField(required=False, allow_null=True) 
    duration_in_years = serializers.IntegerField(required=False, allow_null=True)  
    mode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    degree_level = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_cs_degree = serializers.CharField(required=False)  
    is_ml_degree = serializers.CharField(required=False)
    institute_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ParsedResumeSerializer(serializers.Serializer):
    personal_information = serializers.DictField(required=False, allow_null=True)
    resume_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    skills = SkillSerializer(required=False)
    education = EducationSerializer(many=True, required=False)
    experience = ExperienceSerializer(many=True, required=False)
    projects_outside_of_work = serializers.ListField(child=serializers.DictField(), required=False)
    additional_experience_summary = serializers.DictField(required=False, allow_null=True)
    achievements_awards = serializers.DictField(required=False, allow_null=True)
    overall_summary_of_candidate = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    def try_fix_json_string(self, json_string):
        try:
            json_string = re.sub(r',\s*([\]}])', r'\1', json_string) 
            json_string = json_string.replace("'", '"')  
            json_string = re.sub(r'([{,]\s*)(\w+)\s*:', r'\1"\2":', json_string)
            
            if not json_string.startswith(('{', '[')):
                json_string = '{' + json_string + '}'
            
            return json.loads(json_string)
        
        except json.JSONDecodeError as e:
            logger.info(f"Unable to fix json: {json_string}")
            return None

    def fix_json(self, data):
     
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self.fix_json(value)  
            elif isinstance(value, list):
                data[key] = [self.fix_json(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str):
                if value.isdigit():
                    data[key] = int(value)
                else:
                    data[key] = value.lower()
            elif isinstance(value, bool):
                data[key] = str(value).lower()
        return data

    def validate(self, data):
        if isinstance(data, str):
            data = self.try_fix_json_string(data)
            if data is None:
                raise serializers.ValidationError("Invalid JSON format.")

        fixed_data = self.fix_json(data)

        return super().validate(fixed_data)

    def to_internal_value(self, data):
        try:
            fixed_data = self.fix_json(data)
            return super().to_internal_value(fixed_data)
        except ValueError as e:
            logger.error(f"ValueError during data processing: {e}",exc_info=True)
            raise serializers.ValidationError("Invalid data structure provided.")
        except Exception as e:
            logger.error(f"Error during data fixing: {e}",exc_info=True)
            raise serializers.ValidationError("Unexpected error occurred while processing data.")

class ResumeFilterSerializer(serializers.Serializer):
    COMPANY_SIZE_CHOICES = [
    ('<50', 'Less than 50 employees'),
    ('50-200', '50 to 200 employees'),
    ('200-500', '200 to 500 employees'),
    ('500-1000', '500 to 1000 employees'),
    ('>1000', 'More than 1000 employees')
    ]
    skills_experience = serializers.CharField(required=False, allow_null=True,help_text="Search the candidate with his/her skills and the years of experience. Ex - Skill Name|No. of years of experience. i.e python|5,django|6")
    skills_and = serializers.CharField(required=False, allow_null=True,help_text="Search for the candidate with all the skills mentioned. Skill 1, Skills 2, Skill 3. Ex. python,django,html,css")
    proficient_technologies_and = serializers.CharField(required=False, allow_null=True,help_text="Search for the candidate with any of the skill mentioned. Skill 1, Skills 2, Skill 3. Ex. python,django,html,css")
    full_time_experience = serializers.FloatField(required=False, allow_null=True,help_text="Full time experience of working industry after graduation. ex. 3")
    company_type = serializers.CharField(required=False, allow_null=True,help_text = "Type of company service or product. Ex. product or service")
    product_company_experience = serializers.FloatField(required=False, allow_null=True,help_text="Product company experience. ex. 3")
    startup_experience = serializers.FloatField(required=False, allow_null=True,help_text="Startup experience. ex. 3")
    degree_type = serializers.CharField(required=False, allow_null=True,help_text="Type of degree bachelors or masters. Ex. bachelors or masters")
    last_position_held = serializers.CharField(required=False, allow_null=True,help_text="Name of the last position held. Ex. Senior Data Scientist")
    gen_ai_experience = serializers.CharField(required=False, allow_null=True,help_text="Does the candidate have gen ai experience. true or false")
    is_cs_degree = serializers.CharField(required=False, allow_null=True,help_text="Does the candidate have a CS Degree. true or false")
    is_ml_degree = serializers.CharField(required=False, allow_null=True,help_text="Does the candidate have a ML Degree. true or false")
    early_stage_startup_experience = serializers.FloatField(required=False, allow_null=True,help_text="Early age startup experience. Ex. 3")
    institute_type = serializers.CharField(required=False, allow_null=True,help_text="Institute from where the candidate passout. Ex. others or iit or nit or iiit or bits or all")
    llm_experience = serializers.CharField(required=False, allow_null=True,help_text="Does the candidate have a LLM Experience. true or false")
    service_company_experience = serializers.FloatField(required=False, allow_null=True,help_text="No. of years of experience in service based company. ex. 3")
    resume_type = serializers.CharField(required=False, allow_null=True,help_text="Type of resume. Ex. backend_engineer or front_engineer or full_stack_developer or data_scientist")
    projects_outside_of_work = serializers.CharField(required=False, allow_null=True,help_text="Does the candidate have projects outside his job profile. true or false")
    time_filter = serializers.CharField(required=False, allow_null=True,help_text="Filter resume of a particular time period. Ex. one_hour or six_hour or tweleve_hour or one_day or seven_day or one_month")
    skills_or = serializers.CharField(required=False, allow_null=True,help_text="Search for candidate with particular skills with OR Query. ex. python,django")
    proficient_technologies_or = serializers.CharField(required=False, allow_null=True, help_text="Search for candidate with proficient skills with OR Query. ex. python,django")
    format_type = serializers.CharField(required=False,allow_null=True,help_text="In which format you want the filtered data. Ex. csv")
    industry_type = serializers.CharField(required=False,allow_null=True,help_text="Type of the industry of candidate . Ex - fintech, healthtech, edtech, proptech, insurtech, greentech, agritech, foodtech, hft, legaltech, marttech, hrtech, retailtech, cybersecurity, autotech, govtech, deeptech")
    company_size = serializers.ChoiceField(choices=COMPANY_SIZE_CHOICES,required=False,help_text="Search for the candidate with company choices")


def get_serializer_parameters(serializer):
    parameters = []
    for field_name, field in serializer.get_fields().items():
        if field.read_only:
            continue
        param_type = openapi.TYPE_STRING
        
        
        if isinstance(field, serializers.BooleanField):
            param_type = openapi.TYPE_BOOLEAN
        elif isinstance(field, serializers.IntegerField):
            param_type = openapi.TYPE_INTEGER
        elif isinstance(field, serializers.FloatField):
            param_type = openapi.TYPE_NUMBER
        elif isinstance(field, serializers.FileField):
            param_type = openapi.TYPE_FILE  

        parameters.append(openapi.Parameter(
            field_name,
            openapi.IN_FORM,  
            description=field.help_text or '', 
            type=param_type,
            required=field.required
        ))
        
    return parameters