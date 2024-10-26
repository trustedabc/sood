from django.db import models, IntegrityError, DatabaseError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from resumeparser.settings import logger
import uuid
from app.exceptions import ResumeNotFoundError, ResumeProcessingError, ResumeTextExtractionError, ResumeParsingError, ResumeSaveError
from uuid import UUID
import os

class Resume(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='resumes/') #TODO: Remove the file field in future
    storage_path = models.CharField(max_length=255, blank=True, null=True)
    parsing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    no_of_retries = models.IntegerField(default=0)
    parsed_data_id = models.CharField(max_length=200, editable=False)
    resume_category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume {self.id} - {self.parsing_status}"

    @classmethod
    def get(cls, resume_id):
        try:
            resume = Resume.objects.get(id=resume_id)
            return resume
        except ObjectDoesNotExist:
            logger.warning(f"Resume {resume_id} not found.", exc_info=True)
            raise ResumeNotFoundError(resume_id) 
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching resume {resume_id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Unexpected error: {str(e)}")

    def update(self, **kwargs):
        valid_fields = ['storage_path', 'parsing_status', 'no_of_retries', 'parsed_data_id', 'resume_category']
        updated = False

        try:
            for field, value in kwargs.items():
                if field in valid_fields and value is not None:
                    setattr(self, field, value)
                    updated = True

            if updated:
                self.save()
                logger.info(f"Resume {self.id} updated successfully.")
        except IntegrityError as e:
            logger.error(f"Database integrity error when updating resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Database integrity error: {str(e)}")
        except DatabaseError as e:
            logger.error(f"Database error when updating resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Database error: {str(e)}")
        except ValidationError as e:
            logger.error(f"Validation error when updating resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while updating resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Unexpected error: {str(e)}")

    def get_file_location(self):
        try:
            if self.storage_path:
                return self.storage_path
            else:
                logger.warning(f"No file or storage path available for Resume {self.id}.")
                return None
        except Exception as e:
            logger.error(f"An unexpected error occurred when retrieving file location for Resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Unexpected error: {str(e)}")

    def set_file_location(self):
        try:
            if self.file.path:
                self.storage_path = self.file.path
                self.save()
            else:
                logger.warning(f"No file exists for Resume {self.id}")
        except ValueError as e:
            logger.error(f"Error accessing file path for Resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Error accessing file path: {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while setting file location for Resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Unexpected error: {str(e)}")
    
    def update_retry(self):
        try:
            self.no_of_retries += 1
            self.save()
        except Exception as e:
            logger.error(f"An unexpected error occurred while updating retry count for Resume {self.id}: {str(e)}", exc_info=True)
            raise ResumeProcessingError(f"Unexpected error: {str(e)}")
    
    @classmethod
    def get_all(cls,resume_ids):
        return Resume.objects.filter(id__in=[UUID(resume_id) for resume_id in resume_ids])

    @classmethod
    def bulk_create_resume(cls,resume_objects):
        return Resume.objects.bulk_create(resume_objects)

    def delete_file(self):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
                logger.info(f"File deleted : {self.file.path}")

    def time_filter_resumes_id(time_threshold):
        resumes = Resume.objects.filter(modified_at__gte=time_threshold) 
        return [resume.parsed_data_id for resume in resumes]

