from resumeparser.settings import logger
from celery import shared_task
from app.models import Resume
from app.controllers import ResumeController
from celery.exceptions import MaxRetriesExceededError
from app.constants import StatusMessages
from app.exceptions import ResumeProcessingError


@shared_task(bind=True, max_retries=3)
def process_resume_task(self, resume_id):
    try:
        if not resume_id:
            logger.error("No resume IDs provided for processing.", exc_info=True)
            return

        logger.info(f'Processing resume: {resume_id}')

        result = ResumeController.process_resume(resume_id)

        if result.get('message') != StatusMessages.SUCCESS:
            logger.error(f'Resume processing failed for: {resume_id}', exc_info=True)
            raise ResumeProcessingError(f'Resume processing failed for {resume_id}')
        
        logger.info(f'Resume processed successfully: {resume_id}')

        return {"message": f"Resume processing completed successfully for {resume_id}"}

    except ResumeProcessingError as exc:
        logger.error(f'Error processing resumes: {exc}', exc_info=True)
        
        retry_intervals = [600, 1200, 1800]
        retry_count = self.request.retries
        retry_countdown = retry_intervals[retry_count] if retry_count < len(retry_intervals) else retry_intervals[-1]

        logger.exception(f'Retrying in {retry_countdown // 60} minutes...', exc_info=True)
        self.retry(exc=exc, countdown=retry_countdown)

    except MaxRetriesExceededError:
        logger.error(f'Max retries exceeded for resumes', exc_info=True)
        Resume.get(resume_id).update(parsing_status="failed")