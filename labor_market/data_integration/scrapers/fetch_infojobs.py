import requests
from bs4 import BeautifulSoup
from time import sleep
from django.utils.text import slugify
from data_integration.models import JobOffer, Skill

class InfojobsScraper:
    BASE_URL = 'https://www.infojobs.net'
    
    def scrape_jobs(self, pages=3):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for page in range(1, pages + 1):
            try:
                sleep(2)  # Delay entre peticiones
                url = f"{self.BASE_URL}/trabajo?page={page}"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='ij-OfferCard')
                    
                    for card in job_cards:
                        job = self.parse_job_card(card)
                        if job:
                            print(f"Oferta extraída de InfoJobs: {job.title}")
                            
            except Exception as e:
                print(f"Error scraping InfoJobs page {page}: {e}")
                continue

    def parse_job_card(self, card):
        try:
            title_elem = card.find('h2', class_='ij-OfferCard-title')
            title = title_elem.text.strip()
            url = self.BASE_URL + title_elem.find('a')['href']
            
            company = card.find('span', class_='ij-OfferCard-companyName').text.strip()
            location = card.find('span', class_='ij-OfferCard-location').text.strip()
            
            salary_elem = card.find('span', class_='ij-OfferCard-salaryRange')
            salary_min, salary_max = self.parse_salary(salary_elem.text if salary_elem else '')
            
            description = self.get_job_details(url)
            
            job_offer, created = JobOffer.objects.update_or_create(
                external_id=f"infojobs_{slugify(url)}",
                defaults={
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'url': url,
                    'employment_type': 'full_time',
                    'is_active': True
                }
            )
            
            return job_offer
            
        except Exception as e:
            print(f"Error parsing InfoJobs card: {e}")
            return None

    def get_job_details(self, url):
        try:
            sleep(1)
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                description = soup.find('div', class_='ij-DetailOffer-description')
                return description.text.strip() if description else ''
        except Exception as e:
            print(f"Error getting InfoJobs details: {e}")
            return ''

    def parse_salary(self, salary_text):
        try:
            if not salary_text:
                return 0, 0
            # Limpiar y parsear el texto del salario
            salary_text = salary_text.replace('€', '').replace('.', '').strip()
            if '-' in salary_text:
                min_sal, max_sal = salary_text.split('-')
                return int(min_sal.strip()), int(max_sal.strip())
            return 0, 0
        except:
            return 0, 0
