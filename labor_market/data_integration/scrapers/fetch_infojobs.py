import time
import random
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import logging

class InfoJobsScraper:
    BASE_URL = "https://www.infojobs.net"
    SEARCH_URL = f"{BASE_URL}/jobsearch/search-results/list.xhtml"
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    def __init__(self):
        self.jobs = []
        
        # Lista de User-Agents para rotar
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        
        # Configurar Chrome options
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Comentamos el modo headless para ver qué está pasando
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
        
        # Añadir más opciones para evadir la detección
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Inicializar el driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Modificar el navigator.webdriver para evadir la detección
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        
        # Almacenar URLs ya procesadas para evitar duplicados
        self.processed_urls = set()

    def random_delay(self, min_seconds=2, max_seconds=5):
        """Añade un retraso aleatorio para simular comportamiento humano"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"Esperando {delay:.2f} segundos...")
        time.sleep(delay)

    def simulate_human_behavior(self):
        """Simula comportamiento humano aleatorio"""
        try:
            # Obtener dimensiones de la ventana y viewport
            window_width = self.driver.execute_script("return window.innerWidth;")
            window_height = self.driver.execute_script("return window.innerHeight;")
            viewport_width = self.driver.execute_script("return document.documentElement.clientWidth;")
            viewport_height = self.driver.execute_script("return document.documentElement.clientHeight;")
            
            # Usar las dimensiones más pequeñas para asegurar que estamos dentro de los límites
            safe_width = min(window_width, viewport_width) - 100
            safe_height = min(window_height, viewport_height) - 100
            
            # Simular movimiento del ratón dentro de los límites de la ventana
            action = ActionChains(self.driver)
            
            # Primero mover a una posición segura
            action.move_by_offset(50, 50).perform()
            action.reset_actions()
            
            # Luego hacer movimientos aleatorios
            for _ in range(random.randint(2, 5)):
                try:
                    x = random.randint(0, int(safe_width))
                    y = random.randint(0, int(safe_height))
                    action.move_by_offset(x, y).perform()
                    action.reset_actions()
                    time.sleep(random.uniform(0.1, 0.3))
                except Exception as e:
                    print(f"Error en movimiento del ratón: {str(e)}")
                    action.reset_actions()
                    continue
            
            # Simular scroll aleatorio con límites
            try:
                for _ in range(random.randint(2, 4)):
                    scroll_amount = random.randint(100, 300)
                    current_scroll = self.driver.execute_script("return window.pageYOffset;")
                    max_scroll = self.driver.execute_script("return document.body.scrollHeight - window.innerHeight;")
                    
                    # Asegurar que no nos pasamos del límite
                    if current_scroll + scroll_amount > max_scroll:
                        scroll_amount = max_scroll - current_scroll
                    
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(random.uniform(0.2, 0.5))
                
                # Simular scroll hacia arriba de manera suave
                self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
                time.sleep(random.uniform(0.5, 1.0))
            except Exception as e:
                print(f"Error en scroll: {str(e)}")
                
        except Exception as e:
            print(f"Error en simulate_human_behavior: {str(e)}")
            # Continuar con la ejecución aunque falle la simulación

    def handle_cookie_notice(self):
        """Maneja la notificación de cookies"""
        try:
            print("Buscando notificación de cookies...")
            
            # Intentar diferentes selectores para encontrar el botón de aceptar cookies
            cookie_selectors = [
                "//button[contains(text(), 'Aceptar')]",
                "//button[contains(text(), 'Aceptar todas')]",
                "//button[contains(text(), 'Aceptar cookies')]",
                "//button[contains(@class, 'cookie')]",
                "//button[contains(@class, 'accept')]",
                "//button[contains(@id, 'cookie')]",
                "//button[contains(@id, 'accept')]",
                "//div[contains(@class, 'cookie')]//button",
                "//div[contains(@id, 'cookie')]//button",
                "button#didomi-notice-agree-button",
                "button.didomi-notice-agree-button",
                "button.didomi-components-button",
                "button[aria-label*='Agree']",
                "button[aria-label*='Aceptar']",
                "button.didomi-dismiss-button"
            ]
            
            for selector in cookie_selectors:
                try:
                    if selector.startswith("//"):
                        cookie_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        cookie_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    print(f"Botón de cookies encontrado con selector: {selector}")
                    
                    # Simular comportamiento humano antes de hacer clic
                    action = ActionChains(self.driver)
                    action.move_to_element(cookie_button)
                    action.pause(random.uniform(0.2, 0.5))
                    action.perform()
                    
                    # Hacer clic en el botón
                    cookie_button.click()
                    print("Cookies aceptadas")
                    self.random_delay(1, 3)
                    return True
                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"Error al intentar hacer clic en el botón de cookies con selector {selector}: {e}")
            
            print("No se encontró el botón de aceptar cookies")
            return False
        except Exception as e:
            print(f"Error al manejar la notificación de cookies: {e}")
            return False

    def is_captcha_page(self):
        """
        Verifica si la página actual es una página de captcha.
        
        Returns:
            bool: True si es una página de captcha, False en caso contrario.
        """
        try:
            # Verificar si ya hemos resuelto un captcha en esta sesión
            if hasattr(self, '_captcha_solved') and self._captcha_solved:
                return False
                
            # Verificar múltiples indicadores de captcha
            captcha_indicators = [
                "//iframe[contains(@src, 'captcha')]",
                "//div[contains(@class, 'captcha')]",
                "//div[contains(@class, 'geetest')]",
                "//div[contains(@id, 'captcha')]",
                "//div[contains(@class, 'geetest_radar_tip')]"
            ]
            
            for indicator in captcha_indicators:
                elements = self.driver.find_elements(By.XPATH, indicator)
                if elements and any(elem.is_displayed() for elem in elements):
                    return True
                    
            # Verificar si hay un mensaje de error de captcha
            error_messages = [
                "//div[contains(text(), 'captcha')]",
                "//div[contains(text(), 'robot')]",
                "//div[contains(text(), 'verificación')]",
                "//div[contains(text(), 'verification')]"
            ]
            
            for message in error_messages:
                elements = self.driver.find_elements(By.XPATH, message)
                if elements and any(elem.is_displayed() for elem in elements):
                    return True
                    
            return False
        except Exception as e:
            print(f"Error checking for captcha: {str(e)}")
            return False

    def handle_geetest_captcha(self):
        """Maneja el captcha de GeeTest"""
        try:
            # Buscar el elemento específico de GeeTest
            geetest_element = self.driver.find_element(By.CLASS_NAME, "geetest_radar_tip")
            if geetest_element:
                print("\n" + "="*80)
                print("¡DETECTADO CAPTCHA DE GEETEST!")
                print("Intentando resolver el captcha automáticamente...")
                print("Si falla, por favor resuélvelo manualmente en la ventana del navegador.")
                print("="*80 + "\n")
                
                # Intentar hacer clic en el elemento del captcha de manera "humana"
                try:
                    # Primero, mover el ratón a una posición aleatoria en la página
                    action = ActionChains(self.driver)
                    action.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
                    action.reset_actions()
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # Luego, mover el ratón hacia el elemento del captcha con movimientos naturales
                    action.move_to_element(geetest_element)
                    # Añadir movimientos intermedios para simular un movimiento más natural
                    for _ in range(3):
                        action.move_by_offset(random.randint(-10, 10), random.randint(-10, 10))
                        action.pause(random.uniform(0.1, 0.3))
                    action.perform()
                    action.reset_actions()
                    
                    # Hacer clic en el elemento
                    time.sleep(random.uniform(0.2, 0.5))
                    geetest_element.click()
                    
                    print("Clic realizado en el elemento del captcha.")
                except Exception as e:
                    print(f"Error al intentar hacer clic automáticamente: {e}")
                    print("Por favor, resuelve el captcha manualmente.")
                
                # Esperar a que el usuario resuelva el captcha
                # Verificamos si la URL cambia o si el elemento de captcha desaparece
                original_url = self.driver.current_url
                max_wait_time = 120  # 2 minutos máximo de espera
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    # Verificar si la URL ha cambiado
                    if self.driver.current_url != original_url:
                        print("URL cambiada, captcha probablemente resuelto.")
                        break
                    
                    # Verificar si el elemento de captcha ha desaparecido
                    try:
                        self.driver.find_element(By.CLASS_NAME, "geetest_radar_tip")
                        print("Esperando a que se resuelva el captcha...", end="\r")
                    except NoSuchElementException:
                        print("Elemento de captcha no encontrado, probablemente resuelto.")
                        break
                    
                    time.sleep(2)
                
                print("Continuando con el scraping...")
                self.random_delay(3, 5)
                return True
        except NoSuchElementException:
            # No se encontró el elemento de GeeTest
            return False
        except Exception as e:
            print(f"Error al manejar el captcha: {e}")
            return False

    def handle_captcha(self):
        """
        Maneja la página de captcha esperando resolución manual.
        """
        print("Detectada página de captcha. Esperando resolución...")
        max_wait_time = 300  # 5 minutos máximo de espera
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            if not self.is_captcha_page():
                print("Captcha resuelto correctamente")
                self._captcha_solved = True  # Marcar que hemos resuelto un captcha
                return True
            time.sleep(5)
            print("Esperando resolución manual del captcha...")
            
        print("Tiempo de espera agotado para resolver el captcha")
        return False

    def get_page(self, page=1):
        url = f"{self.SEARCH_URL}?page={page}&sortBy=PUBLICATION_DATE&onlyForeignCountry=false&countryIds=17&sinceDate=ANY"
        print(f"Requesting URL: {url}")
        
        # Cambiar User-Agent antes de cada solicitud
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": random.choice(self.user_agents)
        })
        
        self.driver.get(url)
        print("Página cargada, esperando...")
        self.random_delay(3, 7)  # Espera más tiempo
        
        # Simular comportamiento humano
        self.simulate_human_behavior()
        
        # Verificar si estamos en la página correcta
        print(f"URL actual: {self.driver.current_url}")
        print(f"Título de la página: {self.driver.title}")
        
        # Primero manejar la notificación de cookies
        self.handle_cookie_notice()
        
        # Luego verificar si hay algún elemento de error o captcha
        try:
            # Primero verificar si es un captcha de GeeTest
            if self.handle_geetest_captcha():
                # Si se manejó el captcha, continuamos
                return
            
            # Si no es GeeTest, verificar otros tipos de captcha
            if self.is_captcha_page():
                print("Detectada página de captcha. Esperando resolución...")
                if not self.handle_captcha():
                    print("No se pudo resolver el captcha")
                    return
        except NoSuchElementException:
            print("No se detectó captcha o verificación")

    def scroll_to_element(self, element):
        """Scroll an element into view with improved error handling"""
        try:
            # Verificar si el elemento está en el DOM
            if not element.is_displayed():
                print("Elemento no visible, intentando hacer scroll...")
            
            # Intentar scroll suave primero
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    element
                )
            except:
                # Si falla, intentar scroll directo
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    element
                )
            
            # Verificar si el elemento está realmente visible
            is_visible = self.driver.execute_script("""
                var elem = arguments[0];
                var rect = elem.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            """, element)
            
            if not is_visible:
                print("Elemento no completamente visible después del scroll")
            
            self.random_delay(0.5, 1.5)
            return True
        except Exception as e:
            print(f"Error en scroll_to_element: {str(e)}")
            return False

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            # Ensure element is in viewport
            self.scroll_to_element(element)
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {value}")
            return None
        except Exception as e:
            print(f"Error waiting for element: {e}")
            return None

    def extract_job_details(self, job_element):
        try:
            print("Extracting job details from element...")
            
            # Intentar hacer scroll al elemento con manejo de errores
            if not self.scroll_to_element(job_element):
                print("No se pudo hacer scroll al elemento, continuando de todas formas...")
            
            self.random_delay(0.5, 1.0)
            
            # Wait for and scroll to elements before interacting
            try:
                title_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "job-title"))
                )
                self.scroll_to_element(title_elem)
                title = title_elem.text.strip()
                print(f"Found title: {title}")
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error finding title: {e}")
                return None
            
            try:
                company_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "job-company"))
                )
                self.scroll_to_element(company_elem)
                company = company_elem.text.strip()
                print(f"Found company: {company}")
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error finding company: {e}")
                return None
            
            # Get location with improved error handling
            try:
                location_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferCardContent-description-list-item"))
                )
                self.scroll_to_element(location_elem)
                location = location_elem.text.strip() if location_elem else "Unknown"
            except (TimeoutException, NoSuchElementException):
                location = "Unknown"
            print(f"Found location: {location}")
            
            # Get the job URL with improved error handling
            try:
                # First ensure the title element is in view
                self.scroll_to_element(title_elem)
                self.random_delay(0.5, 1.0)
                
                # Try to find the link element
                link_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#job-title a"))
                )
                self.scroll_to_element(link_elem)
                job_url = link_elem.get_attribute("href")
                
                if not job_url:
                    print("No job URL found")
                    return None
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error finding job URL: {e}")
                return None
            print(f"Found job URL: {job_url}")

            # Verificar si la URL ya ha sido procesada
            if job_url in self.processed_urls:
                print(f"URL ya procesada, saltando: {job_url}")
                return None
            
            # Añadir la URL a las procesadas
            self.processed_urls.add(job_url)

            # Get detailed job information
            job_details = self.get_job_details(job_url)
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                **job_details
            }
        except Exception as e:
            print(f"Error extracting job details: {e}")
            import traceback
            traceback.print_exc()
            return None

    def extract_jobs_from_page(self):
        """
        Extrae todas las ofertas de trabajo de la página actual.
        
        Returns:
            list: Lista de diccionarios con la información de las ofertas de trabajo.
        """
        try:
            print("Extracting jobs from current page...")
            
            # Verificar si estamos en una página de captcha
            if self.is_captcha_page():
                if not self.handle_captcha():
                    return []
            
            # Esperar a que la página se cargue completamente
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Intentar diferentes selectores para los elementos de trabajo
            selectors = [
                (By.CLASS_NAME, "ij-OfferCard"),
                (By.CLASS_NAME, "job-card"),
                (By.XPATH, "//div[contains(@class, 'job-card')]"),
                (By.XPATH, "//div[contains(@class, 'ij-OfferCard')]")
            ]
            
            job_elements = None
            for by, selector in selectors:
                try:
                    job_elements = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_all_elements_located((by, selector))
                    )
                    if job_elements:
                        print(f"Found jobs using selector: {selector}")
                        break
                except:
                    continue
            
            if not job_elements:
                print("No se encontraron elementos de trabajo en la página")
                return []
            
            print(f"Found {len(job_elements)} job elements on the page")
            
            # Extract details from each job element
            page_jobs = []
            for i, job_element in enumerate(job_elements):
                try:
                    print(f"Processing job {i+1}/{len(job_elements)}")
                    
                    # Scroll to the job element
                    self.scroll_to_element(job_element)
                    self.random_delay(0.5, 1.0)
                    
                    job_details = self.extract_job_details(job_element)
                    if job_details:
                        page_jobs.append(job_details)
                except Exception as e:
                    print(f"Error processing job {i+1}: {str(e)}")
                    continue
            
            return page_jobs
            
        except Exception as e:
            print(f"Error extracting jobs from page: {str(e)}")
            return []

    def get_job_details(self, url):
        try:
            print(f"Getting detailed job information from: {url}")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
            print("Página de detalles cargada, esperando...")
            self.random_delay(3, 7)  # Espera más tiempo
            
            # Simular comportamiento humano
            self.simulate_human_behavior()
            
            # Manejar cookies y captcha en la página de detalles
            self.handle_cookie_notice()
            self.handle_geetest_captcha()
            
            details = {}
            
            # Extract description
            try:
                desc_elem = self.driver.find_element(By.CLASS_NAME, "ij-Box.mb-xl.mt-l")
                details['description'] = ' '.join([p.text.strip() for p in desc_elem.find_elements(By.TAG_NAME, "p")])
            except NoSuchElementException:
                details['description'] = 'No description available'
            
            # Extract contract type and schedule
            try:
                contract_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Tipo de contrato')]/following-sibling::dd[1]")
                details['contract_type'] = contract_elem.text.strip()
            except NoSuchElementException:
                details['contract_type'] = 'No contract type available'
            
            # Extract salary
            try:
                salary_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Salario')]/following-sibling::dd[1]")
                details['salary'] = salary_elem.text.strip()
            except NoSuchElementException:
                details['salary'] = 'Salary not available'
            
            # Extract experience
            try:
                exp_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Experiencia mínima')]/following-sibling::dd[1]")
                details['experience'] = exp_elem.text.strip()
            except NoSuchElementException:
                details['experience'] = 'Experience not specified'
            
            # Extract education
            try:
                edu_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Estudios mínimos')]/following-sibling::dd[1]")
                details['education'] = edu_elem.text.strip()
            except NoSuchElementException:
                details['education'] = 'Education not specified'
            
            # Extract vacancies
            try:
                vacancies_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Vacantes')]/following-sibling::dd[1]")
                details['vacancies'] = vacancies_elem.text.strip()
            except NoSuchElementException:
                details['vacancies'] = 'Vacancies not specified'
            
            # Extract people in charge
            try:
                people_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Personas a cargo')]/following-sibling::dd[1]")
                details['people_in_charge'] = people_elem.text.strip()
            except NoSuchElementException:
                details['people_in_charge'] = 'Not specified'
            
            # Extract benefits
            try:
                benefits_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Beneficios sociales')]/following-sibling::dd[1]")
                benefits_list = benefits_elem.find_elements(By.TAG_NAME, "li")
                details['benefits'] = '; '.join([benefit.text.strip() for benefit in benefits_list])
            except NoSuchElementException:
                details['benefits'] = 'No benefits specified'
            
            # Cerrar la pestaña actual y volver a la principal
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            print(f"Extracted details: {details}")
            return details
        except Exception as e:
            print(f"Error getting job details: {e}")
            import traceback
            traceback.print_exc()
            # Asegurarse de volver a la pestaña principal
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            return {}

    def scrape_jobs(self, num_pages=3):
        """
        Extrae ofertas de trabajo de Infojobs.
        
        Args:
            num_pages (int): Número de páginas a extraer. Por defecto es 3.
            
        Returns:
            list: Lista de diccionarios con la información de las ofertas de trabajo.
        """
        try:
            self.jobs = []  # Reiniciar la lista de trabajos
            
            for page in range(1, num_pages + 1):
                print(f"\nProcesando página {page} de {num_pages}...")
                
                # Obtener la página
                self.get_page(page)
                
                # Manejar cookies si es necesario
                if page == 1:
                    self.handle_cookie_notice()
                
                # Simular comportamiento humano
                self.simulate_human_behavior()
                
                # Extraer ofertas de trabajo de la página actual
                page_jobs = self.extract_jobs_from_page()
                if page_jobs:
                    self.jobs.extend(page_jobs)
                
                # Esperar un tiempo aleatorio entre páginas
                if page < num_pages:
                    self.random_delay(3, 6)
            
            print(f"\nSe encontraron {len(self.jobs)} ofertas de trabajo en total.")
            return self.jobs
            
        except Exception as e:
            print(f"Error durante el scraping: {e}")
            return []
        finally:
            # Cerrar el navegador
            try:
                self.driver.quit()
            except:
                pass

    def __del__(self):
        """Cerrar el navegador al finalizar"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except Exception as e:
            print(f"Error al cerrar el navegador: {e}")

# Función para ser llamada desde la aplicación
def fetch_infojobs_jobs(num_pages=3):
    """
    Función para obtener ofertas de trabajo de InfoJobs
    
    Args:
        num_pages (int): Número de páginas a scrapear
        
    Returns:
        list: Lista de diccionarios con la información de las ofertas de trabajo
    """
    try:
        scraper = InfoJobsScraper()
        jobs = scraper.scrape_jobs(num_pages=num_pages)
        return jobs
    except Exception as e:
        logging.error(f"Error al scrapear InfoJobs: {e}")
        return []

if __name__ == "__main__":
    # Si se ejecuta directamente, mostrar los resultados en la consola
    jobs = fetch_infojobs_jobs(num_pages=3)
    print(f"Total de ofertas encontradas: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"\nOferta {i+1}:")
        print(f"Título: {job['title']}")
        print(f"Empresa: {job['company']}")
        print(f"Ubicación: {job['location']}")
        print(f"URL: {job['url']}")
        print("-" * 50)
