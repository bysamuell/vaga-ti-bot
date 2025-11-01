from .selenium_base import SeleniumScraper
from bs4 import BeautifulSoup
from typing import List, Dict
import urllib.parse
import time
import random
from selenium.webdriver.common.by import By

class GupySeleniumScraper(SeleniumScraper):
    def __init__(self):
        super().__init__(headless=True)
    
    def scrape_jobs(self, job_levels: List[str], tech_keywords: List[str], location: str = "salvador") -> List[Dict]:
        """Scraping direto do site da Gupy"""
        jobs = []
        
        try:
            # Buscas mais específicas para Salvador
            search_queries = [
                "estágio",
                "estagio", 
                "junior",
                "assistente",
                "auxiliar"
            ]
            
            for query in search_queries:
                print(f"🔍 Buscando na Gupy: {query}")
                query_jobs = self._search_gupy_site(query, location)
                jobs.extend(query_jobs)
                print(f"📝 {len(query_jobs)} vagas encontradas para '{query}'")
                
                self.human_delay(2, 4)
                
        except Exception as e:
            print(f"❌ Erro no Gupy Scraper: {e}")
        finally:
            self.close()
            
        # Filtra apenas vagas de TI
        return self._filter_tech_jobs(jobs)
    
    def _search_gupy_site(self, query: str, location: str) -> List[Dict]:
        """Faz busca direto no site da Gupy com melhor estratégia"""
        jobs = []
        
        try:
            # URL mais genérica para buscar todas as vagas
            encoded_query = urllib.parse.quote(query)
            url = f"https://portal.gupy.io/job-search?jobName={encoded_query}"
            
            print(f"🌐 Acessando Gupy: {url}")
            self.driver.get(url)
            
            # Aguarda carregamento
            self.human_delay(4, 6)
            
            # Tenta mudar para Salvador se possível
            self._try_set_salvador_location()
            
            # Faz scroll para carregar mais vagas
            self.scroll_page(scroll_pauses=3)
            
            # Pega o HTML
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            jobs = self._extract_gupy_jobs(soup)
            
            # Filtra por Salvador localmente
            jobs = [job for job in jobs if self._is_in_salvador(job)]
            
        except Exception as e:
            print(f"❌ Erro na busca da Gupy: {e}")
            
        return jobs
    
    def _try_set_salvador_location(self):
        """Tenta definir localização como Salvador"""
        try:
            # Tenta encontrar e clicar no seletor de localização
            location_selectors = [
                'button[data-testid*="location"]',
                'button[aria-label*="local"]',
                '[class*="location"] button',
                'input[placeholder*="local"]'
            ]
            
            for selector in location_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    elements[0].click()
                    self.human_delay(1, 2)
                    
                    # Tenta digitar Salvador
                    input_selectors = [
                        'input[type="text"]',
                        'input[placeholder*="Cidade"]',
                        'input[data-testid*="search"]'
                    ]
                    
                    for input_selector in input_selectors:
                        inputs = self.driver.find_elements(By.CSS_SELECTOR, input_selector)
                        if inputs:
                            inputs[0].clear()
                            inputs[0].send_keys("Salvador")
                            self.human_delay(1, 2)
                            
                            # Tenta selecionar da lista
                            salvador_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Salvador')]")
                            if salvador_options:
                                salvador_options[0].click()
                                self.human_delay(2, 3)
                            break
                    break
        except Exception as e:
            print(f"⚠️ Não foi possível definir localização: {e}")
    
    def _extract_gupy_jobs(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai vagas do HTML da Gupy com seletores melhorados"""
        jobs = []
        
        # Seletores mais abrangentes
        job_selectors = [
            'div[data-testid="job-card"]',
            '[data-testid*="job-card"]',
            'a[href*="/job/"]',
            '.sc-be4b7f4c-0',
            '[class*="job-card"]',
            'div[class*="sc-"]'  # Seletores genéricos da Gupy
        ]
        
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                print(f"✅ Encontrados {len(job_elements)} elementos na Gupy")
                for job_elem in job_elements[:15]:  # Limita para performance
                    try:
                        job = self._parse_gupy_job_element(job_elem)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        continue
                break
        
        return jobs
    
    def _parse_gupy_job_element(self, job_elem) -> Dict:
        """Parseia um elemento de vaga da Gupy"""
        # Título
        title_selectors = ['h2', '[data-testid*="title"]', 'strong', 'span[class*="title"]']
        title = self._extract_text_safe(job_elem, title_selectors)
        
        if not title:
            return None
            
        # Empresa
        company_selectors = ['p', '[data-testid*="company"]', 'span[class*="company"]']
        company = self._extract_text_safe(job_elem, company_selectors, "Empresa não informada")
        
        # Localização
        location_selectors = ['span', '[data-testid*="location"]', 'div[class*="location"]']
        location = self._extract_text_safe(job_elem, location_selectors, "Salvador, BA")
        
        # URL
        url = self._extract_gupy_url(job_elem)
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'date_posted': 'Recent',
            'platform': 'Gupy',
            'url': url
        }
    
    def _extract_text_safe(self, element, selectors, default="N/A"):
        """Extrai texto com segurança"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return default
    
    def _extract_gupy_url(self, job_elem):
        """Extrai URL da vaga na Gupy"""
        link_selectors = ['a', '[href*="/job/"]']
        for selector in link_selectors:
            link = job_elem.select_one(selector)
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('/'):
                    return f"https://portal.gupy.io{href}"
                return href
        return "#"
    
    def _is_in_salvador(self, job: Dict) -> bool:
        """Filtra apenas vagas em Salvador com critérios mais flexíveis"""
        location = job['location'].lower()
        salvador_indicators = ['salvador', 'ssa', 'bahia', 'ba']
        
        # Se não tem localização, assume que pode ser de Salvador
        if location == 'salvador, ba' or location == 'n/a':
            return True
            
        return any(indicator in location for indicator in salvador_indicators)
    
    def _filter_tech_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filtra vagas de TI"""
        tech_keywords = [
            'ti', 't.i', 'tecnologia', 'tecnológico', 'sistema', 'informática',
            'programação', 'desenvolvedor', 'software', 'dados', 'data',
            'suporte', 'infraestrutura', 'redes', 'devops', 'developer',
            'analista', 'technology', 'systems', 'it', 'dev', 'computação'
        ]
        
        filtered_jobs = []
        for job in jobs:
            title = job['title'].lower()
            if any(keyword in title for keyword in tech_keywords):
                filtered_jobs.append(job)
        
        return filtered_jobs