import requests
from bs4 import BeautifulSoup
from time import sleep
from django.utils.text import slugify
from data_integration.models import JobOffer, Skill

class TecnoempleoScraper:
    BASE_URL = 'https://www.tecnoempleo.com'
    SEARCH_URL = f'{BASE_URL}/ofertas-trabajo'
    
    def scrape_jobs(self, pages=3):
        jobs = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        for page in range(1, pages + 1):
            try:
                print(f"Scraping Tecnoempleo page {page}...")
                url = f"{self.SEARCH_URL}?pagina={page}"
                print(f"URL: {url}")  # Debug
                
                response = requests.get(url, headers=headers)
                print(f"Status: {response.status_code}")  # Debug
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Buscar ofertas - ajustado a la estructura actual
                    job_listings = soup.select('.job-list .job-item')
                    print(f"Found {len(job_listings)} jobs")  # Debug
                    
                    for listing in job_listings:
                        job = self.parse_job_listing(listing)
                        if job:
                            print(f"Oferta extraída: {job.title}")
                            jobs.append(job)
                
                sleep(2)
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue
        
        return jobs

    def parse_job_listing(self, listing):
        try:
            # Extraer título y URL
            title_elem = listing.select_one('.job-title a')
            if not title_elem:
                print("No title element found")  # Debug
                return None
                
            title = title_elem.text.strip()
            url = title_elem['href']
            if not url.startswith('http'):
                url = self.BASE_URL + url
            
            # Extraer empresa y ubicación
            company = listing.select_one('.company-name').text.strip()
            location = listing.select_one('.location').text.strip()
            
            # Obtener descripción
            description = self.get_job_details(url)
            
            # Extraer salario
            salary_elem = listing.select_one('.salary')
            salary_min, salary_max = self.parse_salary(salary_elem.text.strip() if salary_elem else '')
            
            # Extraer tecnologías/skills
            skills = []
            skills_elem = listing.select_one('.technologies')
            if skills_elem:
                skills_text = [s.strip() for s in skills_elem.text.split(',')]
                for skill_name in skills_text:
                    if skill_name:
                        skill, _ = Skill.objects.get_or_create(name=skill_name)
                        skills.append(skill)
            
            # Crear o actualizar oferta
            job_offer, created = JobOffer.objects.update_or_create(
                external_id=f"tecnoempleo_{slugify(url)}",
                defaults={
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'url': url,
                    'employment_type': 'full_time',
                    'is_active': True,
                    'requirements': description
                }
            )
            
            # Añadir skills
            if skills:
                job_offer.skills.add(*skills)
            
            return job_offer
            
        except Exception as e:
            print(f"Error parsing job listing: {str(e)}")  # Debug detallado
            return None

    def get_job_details(self, url):
        try:
            print(f"Getting details from: {url}")  # Debug
            sleep(1)
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                description = soup.select_one('.job-description')
                return description.text.strip() if description else ''
        except Exception as e:
            print(f"Error getting job details: {e}")
            return ''

    def parse_salary(self, salary_text):
        try:
            # Limpiar y parsear el texto del salario
            salary_text = salary_text.replace('€', '').replace('.', '').strip()
            if '-' in salary_text:
                min_sal, max_sal = salary_text.split('-')
                return int(min_sal.strip()), int(max_sal.strip())
            return 0, 0
        except:
            return 0, 0
