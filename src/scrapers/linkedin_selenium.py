from .selenium_base import SeleniumScraper
from bs4 import BeautifulSoup
from typing import List, Dict
import urllib.parse
import time
import random
from selenium.webdriver.common.by import By

class LinkedInSeleniumScraper(SeleniumScraper):
    def __init__(self):
        super().__init__(headless=True)
    
    def scrape_jobs(self, job_levels: List[str], tech_keywords: List[str], location: str = "Salvador, Bahia") -> List[Dict]:
        """Scraping do LinkedIn com busca mais inteligente"""
        jobs = []
        
        try:
            # Buscas mais genéricas para evitar bloqueio
            search_queries = [
                "estágio",
                "estagio",
                "junior", 
                "assistente",
                "auxiliar"
            ]
            
            for query in search_queries:
                print(f"🔍 Buscando no LinkedIn: {query}")
                query_jobs = self._search_linkedin_smart(query, location)
                jobs.extend(query_jobs)
                print(f"📝 {len(query_jobs)} vagas encontradas para '{query}'")
                
                # Delay maior para evitar rate limiting
                self.human_delay(5, 8)
                
        except Exception as e:
            print(f"❌ Erro no LinkedIn Scraper: {e}")
        finally:
            self.close()
            
        # Filtra vagas de TI e de Salvador
        return self._filter_relevant_jobs(jobs)
    
    def _search_linkedin_smart(self, query: str, location: str) -> List[Dict]:
        """Busca inteligente no LinkedIn com filtro de tempo"""
        jobs = []
        
        try:
            # URL com filtro de tempo (últimas 24 horas)
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location)
            url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&location={encoded_location}&f_TPR=r86400"
            
            print(f"🌐 Acessando LinkedIn: {url}")
            self.driver.get(url)
            
            # Aguarda mais tempo para carregar
            self.human_delay(5, 7)
            
            # Verifica se há resultados
            if self._no_results_found():
                print("📭 Nenhum resultado encontrado para esta busca")
                return []
                
            # Scroll mais humanoide
            self._human_like_scroll()
            
            # Pega o HTML
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            jobs = self._extract_linkedin_jobs(soup)
            
            # Filtra por data no código também (backup)
            jobs = self._filter_recent_jobs(jobs)
            
        except Exception as e:
            print(f"❌ Erro na busca do LinkedIn: {e}")
            
        return jobs
    
    def _no_results_found(self) -> bool:
        """Verifica se não há resultados"""
        no_results_selectors = [
            '.jobs-search__no-results',
            '.results__container--no-results',
            '.search-no-results',
            'h1[class*="no-results"]'
        ]
        
        for selector in no_results_selectors:
            element = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if element:
                return True
        return False
    
    def _human_like_scroll(self):
        """Scroll mais humanoide para evitar detecção"""
        scroll_actions = random.randint(2, 4)
        for i in range(scroll_actions):
            # Scroll de tamanhos variados
            scroll_pixels = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            self.human_delay(1, 2)
    
    def _extract_linkedin_jobs(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai vagas do LinkedIn com seletores mais flexíveis"""
        jobs = []
        
        # Múltiplos seletores tentativos
        job_selectors = [
            'li.jobs-search-results__list-item',
            'div.job-search-card',
            'div.base-card',
            '[data-entity-urn*="jobPosting"]',
            '.occludable-update'
        ]
        
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                print(f"✅ Encontrados {len(job_elements)} elementos no LinkedIn")
                for job_elem in job_elements[:15]:  # Limita para performance
                    try:
                        job = self._parse_linkedin_job(job_elem)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        continue
                break
        
        return jobs
    
    def _parse_linkedin_job(self, job_elem) -> Dict:
        """Parseia um elemento de vaga do LinkedIn"""
        # Título
        title_selectors = [
            'h3.base-search-card__title',
            '.job-card-list__title', 
            'span.job-card-title',
            'h3'
        ]
        title = self._extract_text_safe(job_elem, title_selectors)
        
        if not title:
            return None
            
        # Empresa
        company_selectors = [
            'h4.base-search-card__subtitle',
            '.job-card-container__primary-description',
            'h4'
        ]
        company = self._extract_text_safe(job_elem, company_selectors, "Empresa não informada")
        
        # Localização
        location_selectors = [
            'span.job-search-card__location',
            '.job-card-container__metadata-item'
        ]
        location = self._extract_text_safe(job_elem, location_selectors, "Salvador, Bahia")
        
        # URL
        url = self._extract_linkedin_url(job_elem)
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'date_posted': 'Recent',
            'platform': 'LinkedIn',
            'url': url
        }
    
    def _extract_text_safe(self, element, selectors, default="N/A"):
        """Extrai texto com segurança"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return default
    
    def _extract_linkedin_url(self, job_elem):
        """Extrai URL do LinkedIn"""
        url_selectors = [
            'a.base-card__full-link',
            'a.job-card-container__link',
            'a[href*="/jobs/view"]'
        ]
        
        for selector in url_selectors:
            link = job_elem.select_one(selector)
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('/'):
                    return f"https://www.linkedin.com{href}"
                return href
        return "#"
    
    def _filter_recent_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filtra vagas recentes (últimas 24h)"""
        from datetime import datetime, timedelta
        import re
        
        recent_jobs = []
        
        for job in jobs:
            date_text = job.get('date_posted', '').lower()
            
            # Verifica padrões de data recente
            if any(pattern in date_text for pattern in ['hora', 'hour', 'now', 'recent']):
                recent_jobs.append(job)
            elif 'dia' in date_text or 'day' in date_text:
                # Extrai número de dias
                match = re.search(r'(\d+)\s*(dia|day)', date_text)
                if match:
                    days_ago = int(match.group(1))
                    if days_ago <= 1:  # 1 dia ou menos
                        recent_jobs.append(job)
                else:
                    # Se não consegue extrair, mantém por segurança
                    recent_jobs.append(job)
            else:
                # Se não tem informação de data, mantém (evita perder vagas)
                recent_jobs.append(job)
        
        print(f"📅 {len(recent_jobs)} vagas das últimas 24h")
        return recent_jobs
    
    def _filter_relevant_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filtra vagas relevantes: TI + Salvador"""
        tech_keywords = [
            'ti', 't.i', 'tecnologia', 'tecnológico', 'sistema', 'informática',
            'programação', 'desenvolvedor', 'software', 'dados', 'data',
            'suporte', 'infraestrutura', 'redes', 'devops', 'developer',
            'analista', 'technology', 'systems', 'it', 'dev', 'computação'
        ]
        
        filtered_jobs = []
        for job in jobs:
            title = job['title'].lower()
            location = job['location'].lower()
            
            # Verifica se é de TI E está em Salvador
            is_tech = any(keyword in title for keyword in tech_keywords)
            is_salvador = 'salvador' in location or 'ba' in location or 'bahia' in location
            
            if is_tech and is_salvador:
                filtered_jobs.append(job)
        
        return filtered_jobs