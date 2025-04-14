import requests
from bs4 import BeautifulSoup
from time import sleep
from django.utils.text import slugify
from data_integration.models import JobOffer, Skill
import logging

class TecnoempleoScraper:
    BASE_URL = 'https://www.tecnoempleo.com'
    SEARCH_URL = f'{BASE_URL}/busqueda-empleo.php'
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.tecnoempleo.com/',
        }
        self.session.headers.update(self.headers)
    
    def scrape_jobs(self, pages=3):
        jobs = []
        
        for page in range(1, pages + 1):
            try:
                print(f"Inspeccionando página {page} de Tecnoempleo...")
                url = f"{self.SEARCH_URL}?pagina={page}"
                print(f"URL completa: {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Debug: Print the first part of the HTML
                print("Estructura HTML encontrada:")
                print(soup.prettify()[:500])
                
                # Imprimir más información de depuración
                print("Buscando ofertas de trabajo...")
                
                # Intentar encontrar el contenedor principal de ofertas
                main_container = soup.select_one('.container-fluid') or soup.select_one('.container')
                if main_container:
                    print(f"Contenedor principal encontrado: {main_container.get('class')}")
                    
                    # Buscar elementos que puedan contener ofertas
                    job_listings = []
                    
                    # Intentar diferentes selectores basados en la estructura actual
                    selectors = [
                        '.card',  # Bootstrap cards
                        '.job-card',  # Clase común para tarjetas de trabajo
                        '.job-item',  # Elementos de trabajo
                        '.search-result',  # Resultados de búsqueda
                        '.job-listing',  # Listados de trabajo
                        '.job-offer',  # Ofertas de trabajo
                        '.oferta',  # Oferta en español
                        'article',  # Artículos HTML
                        '.list-group-item',  # Elementos de lista de Bootstrap
                        '.row .col',  # Columnas de Bootstrap
                    ]
                    
                    for selector in selectors:
                        elements = main_container.select(selector)
                        if elements:
                            print(f"Encontrados {len(elements)} elementos con selector: {selector}")
                            job_listings.extend(elements)
                    
                    # Si no se encontraron elementos con los selectores, intentar buscar por estructura
                    if not job_listings:
                        print("No se encontraron elementos con los selectores predefinidos. Buscando por estructura...")
                        
                        # Buscar elementos que contengan enlaces a ofertas de trabajo
                        links = main_container.select('a[href*="/oferta-trabajo/"]')
                        if links:
                            print(f"Encontrados {len(links)} enlaces a ofertas de trabajo")
                            # Crear elementos de trabajo a partir de los enlaces
                            for link in links:
                                # Buscar el contenedor padre más cercano que pueda ser una oferta
                                parent = link.find_parent(['div', 'article', 'li'])
                                if parent:
                                    job_listings.append(parent)
                
                print(f"Encontradas {len(job_listings)} ofertas")
                
                if not job_listings:
                    print("No se encontraron ofertas. Verificando estructura HTML...")
                    # Debug: Print all div classes to help identify the correct selector
                    all_divs = soup.find_all('div', class_=True)
                    print("Clases de div encontradas:")
                    for div in all_divs[:10]:  # Print first 10 to avoid flooding
                        print(f"- {div.get('class')}")
                    
                    # Buscar enlaces que puedan ser ofertas de trabajo
                    all_links = soup.find_all('a', href=True)
                    print(f"Encontrados {len(all_links)} enlaces en total")
                    for link in all_links[:10]:  # Mostrar los primeros 10 enlaces
                        print(f"- {link.get('href')}: {link.text.strip()}")
                
                for listing in job_listings:
                    job = self.parse_job_listing(listing)
                    if job:
                        print(f"Oferta extraída: {job.title}")
                        jobs.append(job)
                
                sleep(3)  # Increased delay between requests
                
            except requests.exceptions.RequestException as e:
                print(f"Error de red al acceder a la página {page}: {str(e)}")
                sleep(5)  # Longer delay after an error
                continue
            except Exception as e:
                print(f"Error inesperado en la página {page}: {str(e)}")
                continue
        
        return jobs

    def parse_job_listing(self, listing):
        try:
            # Buscar enlaces que puedan ser títulos de ofertas
            links = listing.select('a[href*="/oferta-trabajo/"]')
            if not links:
                links = listing.select('a')
            
            if not links:
                print("No se encontraron enlaces en el elemento")
                return None
            
            # Usar el primer enlace encontrado
            title_elem = links[0]
            title = title_elem.text.strip()
            url = title_elem['href']
            
            if not title:
                print("El título está vacío")
                return None
                
            if not url.startswith('http'):
                url = self.BASE_URL + url
            
            # Buscar empresa y ubicación en el texto del elemento
            listing_text = listing.get_text()
            
            # Intentar extraer empresa
            company = "Empresa no especificada"
            company_selectors = ['.company', '.empresa', '.company-name', '.employer']
            for selector in company_selectors:
                company_elem = listing.select_one(selector)
                if company_elem:
                    company = company_elem.text.strip()
                    break
            
            # Intentar extraer ubicación
            location = "Ubicación no especificada"
            location_selectors = ['.location', '.ubicacion', '.place', '.city']
            for selector in location_selectors:
                location_elem = listing.select_one(selector)
                if location_elem:
                    location = location_elem.text.strip()
                    break
            
            # Si no se encontró ubicación, intentar extraerla del texto
            if location == "Ubicación no especificada":
                # Buscar patrones comunes de ubicación
                import re
                location_patterns = [
                    r'([A-Za-záéíóúÁÉÍÓÚñÑ\s]+,\s*[A-Za-záéíóúÁÉÍÓÚñÑ\s]+)',
                    r'([A-Za-záéíóúÁÉÍÓÚñÑ\s]+)',
                ]
                for pattern in location_patterns:
                    matches = re.findall(pattern, listing_text)
                    if matches:
                        location = matches[0]
                        break
            
            # Obtener descripción
            description = self.get_job_details(url)
            
            # Intentar extraer salario
            salary_min, salary_max = 0, 0
            salary_selectors = ['.salary', '.salario', '.remuneracion', '.wage']
            for selector in salary_selectors:
                salary_elem = listing.select_one(selector)
                if salary_elem:
                    salary_text = salary_elem.text.strip()
                    salary_min, salary_max = self.parse_salary(salary_text)
                    break
            
            # Extraer habilidades/tecnologías
            skills = []
            skills_selectors = ['.technologies', '.tecnologias', '.skills', '.tags']
            for selector in skills_selectors:
                skills_elem = listing.select_one(selector)
                if skills_elem:
                    skills_text = [s.strip() for s in skills_elem.text.split(',')]
                    for skill_name in skills_text:
                        if skill_name:
                            skill, _ = Skill.objects.get_or_create(name=skill_name)
                            skills.append(skill)
                    break
            
            # Si no se encontraron habilidades, intentar extraerlas del texto
            if not skills:
                # Buscar palabras clave comunes de tecnologías
                tech_keywords = ['Python', 'Java', 'JavaScript', 'PHP', 'C#', 'C++', 'Ruby', 'Go', 'Swift', 'Kotlin', 
                                'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel', 
                                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 
                                'GCP', 'Linux', 'Git', 'CI/CD', 'DevOps', 'Agile', 'Scrum', 'Jira', 'Confluence']
                
                for keyword in tech_keywords:
                    if keyword.lower() in listing_text.lower():
                        skill, _ = Skill.objects.get_or_create(name=keyword)
                        skills.append(skill)
            
            # Crear o actualizar oferta de trabajo
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
            
            if skills:
                job_offer.skills.add(*skills)
            
            return job_offer
            
        except Exception as e:
            print(f"Error al procesar la oferta: {str(e)}")
            return None

    def get_job_details(self, url):
        try:
            print(f"Obteniendo detalles de: {url}")
            sleep(2)  # Increased delay
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Intentar diferentes selectores para la descripción
            description_selectors = [
                '.job-description', 
                '.descripcion', 
                '.description',
                '.job-details',
                '.detalles',
                '.details',
                '.content',
                '.job-content',
                'article',
                'main'
            ]
            
            for selector in description_selectors:
                description_elem = soup.select_one(selector)
                if description_elem:
                    return description_elem.text.strip()
            
            # Si no se encontró con los selectores, intentar extraer el texto principal
            main_content = soup.select_one('main') or soup.select_one('article') or soup.select_one('.container')
            if main_content:
                return main_content.text.strip()
            
            return ''
        except Exception as e:
            print(f"Error al obtener detalles del trabajo: {e}")
            return ''

    def parse_salary(self, salary_text):
        try:
            # Clean and parse salary text
            salary_text = salary_text.replace('€', '').replace('.', '').strip()
            if '-' in salary_text:
                min_sal, max_sal = salary_text.split('-')
                return int(min_sal.strip()), int(max_sal.strip())
            elif salary_text:
                # If there's only one number, use it as both min and max
                amount = int(salary_text.strip())
                return amount, amount
            return 0, 0
        except:
            return 0, 0
