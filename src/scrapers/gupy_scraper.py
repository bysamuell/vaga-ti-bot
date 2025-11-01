from .selenium_base import SeleniumScraper
from bs4 import BeautifulSoup
from typing import List, Dict
import urllib.parse
import time
import random

class GupyScraper(SeleniumScraper):
    def __init__(self):
        super().__init__(headless=True)
    
    def scrape_jobs(self, job_levels: List[str], tech_keywords: List[str], location: str = "salvador") -> List[Dict]:
        """Scraping da Gupy usando Selenium"""
        jobs = []
        
        try:
            search_queries = [
                "estágio TI",
                "junior TI", 
                "assistente TI",
                "auxiliar TI"
            ]
            
            for query in search_queries:
                print(f"🔍 Buscando na Gupy (Selenium): {query}")
                query_jobs = self._search_gupy(query, location)
                jobs.extend(query_jobs)
                print(f"📝 Encontradas {len(query_jobs)} vagas para '{query}'")
                
                self.human_delay(2, 4)
                
        except Exception as e:
            print(f"❌ Erro no Gupy Scraper: {e}")
        finally:
            self.close()
            
        return jobs
    
    def _search_gupy(self, query: str, location: str) -> List[Dict]:
        """Faz busca individual na Gupy"""
        jobs = []
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://portal.gupy.io/job-search?jobName={encoded_query}&city={location}"
            
            print(f"🌐 Acessando: {url}")
            self.driver.get(url)
            
            self.human_delay(3, 5)
            self.scroll_page()
            
            # Aguarda resultados
            self.wait_for_element('[data-testid="job-card"]', timeout=10)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            jobs = self._extract_jobs_from_html(soup)
            
        except Exception as e:
            print(f"❌ Erro na busca da Gupy: {e}")
            
        return jobs
    
    def _extract_jobs_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai vagas do HTML da Gupy"""
        jobs = []
        
        job_selectors = [
            '[data-testid="job-card"]',
            '.sc-d984c23f',
            '[class*="job-card"]'
        ]
        
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                print(f"✅ Encontrados {len(job_elements)} elementos na Gupy")
                for job_elem in job_elements:
                    try:
                        job = self._extract_gupy_job(job_elem)
                        if job:
                            jobs.append(job)
                    except:
                        continue
                break
        
        return jobs
    
    def _extract_gupy_job(self, job_elem) -> Dict:
        """Extrai dados de vaga da Gupy"""
        title_selectors = ['h2', '[data-testid="job-card-title"]']
        company_selectors = ['p', '[data-testid*="company"]']
        location_selectors = ['span', '[data-testid*="location"]']
        
        title = self._extract_text(job_elem, title_selectors)
        company = self._extract_text(job_elem, company_selectors)
        location = self._extract_text(job_elem, location_selectors, "Salvador, BA")
        url = self._extract_gupy_url(job_elem)
        
        if not title:
            return None
            
        return {
            'title': title,
            'company': company,
            'location': location,
            'date_posted': 'Recent',
            'platform': 'Gupy',
            'url': url
        }
    
    def _extract_text(self, element, selectors, default="N/A"):
        """Extrai texto usando múltiplos seletores"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return default
    
    def _extract_gupy_url(self, job_elem):
        """Extrai URL da Gupy"""
        link = job_elem.select_one('a[href*="/job/"]')
        if link and link.get('href'):
            href = link.get('href')
            if href.startswith('/'):
                return f"https://portal.gupy.io{href}"
            return href
        return "#"