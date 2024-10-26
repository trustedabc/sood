

class ResumeProcessingError(Exception):
    """Base class for exceptions related to resume processing."""
    pass

class ResumeNotFoundError(ResumeProcessingError):
    def __init__(self, resume_id):
        self.message = f"Resume with ID {resume_id} not found."
        super().__init__(self.message)

class InvalidPDFError(ResumeProcessingError):
    def __init__(self, pdf_path):
        self.message = f"The file {pdf_path} is not a valid PDF."
        super().__init__(self.message)

class ExtractionError(ResumeProcessingError):
    pass

class ResumeTextExtractionError(ExtractionError):
    def __init__(self, pdf_path, **kwargs):
        self.message = kwargs.get('message', f"Failed to extract text from the PDF at {pdf_path}.")
        super().__init__(self.message)

class ResumeParsingError(ExtractionError):
    def __init__(self, resume_text, **kwargs):
        self.message = kwargs.get('message', "Failed to parse data from the resume.")
        self.resume_text = resume_text  
        super().__init__(self.message)

class DatabaseSaveError(ResumeProcessingError):
    """Exception raised for errors while saving to the database."""
    pass

class ResumeSaveError(DatabaseSaveError):
    def __init__(self, error_code=None, **kwargs):
        self.message = kwargs.get('message', "Failed to save resume data to the database.")
        self.error_code = error_code  
        super().__init__(self.message)
