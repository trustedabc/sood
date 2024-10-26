from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

class ResumeApiTests(APITestCase):

    def setUp(self):
        self.upload_url = reverse('resume-upload')  # Adjust based on your URL routing
        self.retrieve_url = reverse('retrieve-data')  # Adjust based on your URL routing

    @patch('app.views.process_resume_task.delay')  # Mock the Celery task
    def test_resume_upload_success(self, mock_process_resume):
        """Test the resume upload endpoint with valid files."""
        # Mock the Celery task to simulate successful task initiation
        mock_process_resume.return_value = True

        with open('U:/drive-download-20241009T182740Z-001 - Copy', 'rb') as resume_file:
            response = self.client.post(self.upload_url, {'file': resume_file}, format='multipart')
        
        # Verify that the task was called with the correct arguments
        self.assertTrue(mock_process_resume.called)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertTrue("resumes uploaded and processing started." in response.data["message"])

    @patch('app.views.process_resume_task.delay')  # Mock the Celery task
    def test_resume_upload_no_files(self, mock_process_resume):
        """Test the resume upload endpoint with no files."""
        response = self.client.post(self.upload_url, {}, format='multipart')
        
        # Ensure the Celery task was not called due to no files
        self.assertFalse(mock_process_resume.called)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "No files uploaded.")

    @patch('your_app.mongo_service.MongoClient')  # Mock MongoDB client
    def test_get_resume_data_with_filters(self, mock_mongo_client):
        """Test the retrieval of parsed resumes with filters applied."""

        # Define hardcoded resume data for testing
        mock_parsed_data = [
            {
                'Personal Information': {'Name': 'John Doe', 'Graduation Year': 2020},
                'Experience': [{'Company': 'Company A', 'Years of Experience': 1}],
                'Education': {'Institute': 'XYZ University'}
            },
            {
                'Personal Information': {'Name': 'Jane Doe', 'Graduation Year': 2018},
                'Experience': [{'Company': 'Company B', 'Years of Experience': 3}],
                'Education': {'Institute': 'ABC University'}
            },
            {
                'Personal Information': {'Name': 'Jim Beam', 'Graduation Year': 2019},
                'Experience': [{'Company': 'Company C', 'Years of Experience': 2}],
                'Education': {'Institute': 'XYZ University'}
            }
        ]
        
        # Simulate the behavior of MongoDB's find method returning these hardcoded results
        mock_mongo_client().your_db.resume_data_collection.find.return_value = mock_parsed_data

        # Call the API with filter parameters (e.g., graduation year and experience filters)
        response = self.client.get(self.retrieve_url, {'graduation_year': 2020, 'min_experience': 1}, format='json')
        
        # Check that the status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the response data matches the filtered hardcoded data
        expected_filtered_data = [
            {
                'Personal Information': {'Name': 'John Doe', 'Graduation Year': 2020},
                'Experience': [{'Company': 'Company A', 'Years of Experience': 1}],
                'Education': {'Institute': 'XYZ University'}
            }
        ]
        
        # Assert that the filtered data is returned as expected
        self.assertEqual(response.data, expected_filtered_data)

        # Ensure the mock was called with the right filter arguments
        mock_mongo_client().your_db.resume_data_collection.find.assert_called_with({
            'Personal Information.Graduation Year': 2020,
            'Experience.Years of Experience': {'$gte': 1}
        })
