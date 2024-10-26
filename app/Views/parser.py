from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from app.tasks import process_resume_task
from app.serializers import ResumeSerializer, ResumeFilterSerializer
from app.models import Resume
from app.controllers import ResumeController
from resumeparser.settings import logger
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from app.serializers import get_serializer_parameters




@swagger_auto_schema(
    method='post',
    manual_parameters=get_serializer_parameters(ResumeSerializer()), 
    responses={
        201: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="3 resumes uploaded and processing started."),
                }
            )
        ),
        400: openapi.Response(
            description='Bad request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, example="No files uploaded.")
                }
            )
        )
    }
)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def resume_upload_view(request):
    
    resume_files = request.FILES.getlist('file')
        
    if not resume_files:
        return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ResumeSerializer()
    created_resumes = serializer.create_bulk(resume_files) 
    for resume in created_resumes:
        process_resume_task.delay(resume.id)

    logger.info(f"{len(resume_files)} Resume has been passed to the celery task for background processing: ")
    return Response(
        {"message": f"{len(resume_files)} resumes uploaded and processing started."},
        status=status.HTTP_201_CREATED
    )
        


validation_error_response = openapi.Response(
    description="Validation Error",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'errors': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=openapi.Schema(type=openapi.TYPE_STRING),
                description="Detailed error messages for each invalid field"
            )
        },
        required=['errors']
    )
)

server_error_response = openapi.Response(
    description="Server Error",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Error message describing what went wrong"
            ),
            'details': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Optional additional details for debugging purposes"
            )
        },
        required=['error']
    )
)

success_response = openapi.Response(
    description="Successful Response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'data': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of filtered resumes"
            ),
        }
    )
)


@swagger_auto_schema(
    method='get',
    query_serializer=ResumeFilterSerializer(),
    responses={
        200: success_response,  
        400: validation_error_response,  
        500: server_error_response 
    }
)
@api_view(['GET'])
def retrieve_data_view(request):
    try:
        serializer = ResumeFilterSerializer(data=request.query_params)

        if serializer.is_valid():
            params = serializer.validated_data
            
            result = ResumeController.filter_resume(params, request)
            return result  

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as e:
        return Response({"error": "Validation error", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def retrieve_resume_category(request):
    try:
        categories = Resume.objects.values_list('resume_category', flat=True).distinct()
        categories_list = list(categories)
        return Response({"resume_categories": categories_list}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": "An error occurred while retrieving resume categories", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )