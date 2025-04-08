from django.conf import settings
from data_integration.models import JobOffer, Skill
from linkedin import linkedin  # Cambiar la importación

class LinkedInJobsFetcher:
    def __init__(self):
        self.application = linkedin.LinkedInApplication(
            token=settings.LINKEDIN_ACCESS_TOKEN
        )
    
    def fetch_jobs(self):
        try:
            # Usar la API correcta de LinkedIn
            params = {
                'start': 0,
                'count': 20,
                'format': 'json'
            }
            jobs = self.application.search_job(params)
            
            if 'jobs' in jobs:
                for job in jobs['jobs']['values']:
                    self.save_job(job)
                    
        except Exception as e:
            print(f"Error fetching LinkedIn jobs: {e}")

    def save_job(self, job_data):
        try:
            job_offer, created = JobOffer.objects.update_or_create(
                external_id=f"linkedin_{job_data.get('id')}",
                defaults={
                    'title': job_data.get('position', {}).get('title', ''),
                    'company': job_data.get('company', {}).get('name', ''),
                    'location': job_data.get('location', {}).get('name', ''),
                    'description': job_data.get('description', ''),
                    'url': job_data.get('referral', {}).get('url', ''),
                    'employment_type': 'full_time',
                    'is_active': True
                }
            )
            return job_offer
        except Exception as e:
            print(f"Error saving LinkedIn job: {e}")
            return None
