from .selenium_base import SeleniumScraper
from bs4 import BeautifulSoup
from typing import List, Dict
import urllib.parse
import time
import random

class LinkedInScraper(SeleniumScraper):
    def __init__(self):
        super().__init__(headless=True)  # Headless=True para GitHub Actions
    
    def scrape_jobs(self, job_levels: List[str], tech_keywords: List[str], location: str = "Salvador, Bahia") -> List[Dict]:
        """Scraping do LinkedIn usando Selenium"""
        jobs = []
        
        try:
            search_queries = [
                "estágio TI",
                "junior TI", 
                "assistente TI",
                "auxiliar TI",
                "tecnologia",
                "programação"
            ]
            
            for query in search_queries:
                print(f"🔍 Buscando no LinkedIn (Selenium): {query}")
                query_jobs = self._search_linkedin(query, location)
                jobs.extend(query_jobs)
                print(f"📝 Encontradas {len(query_jobs)} vagas para '{query}'")
                
                # Delay entre buscas
                self.human_delay(3, 6)
                
        except Exception as e:
            print(f"❌ Erro no LinkedIn Scraper: {e}")
        finally:
            self.close()
            
        return self._remove_duplicates(jobs)
    
    def _search_linkedin(self, query: str, location: str) -> List[Dict]:
        """Faz busca individual no LinkedIn"""
        jobs = []
        
        try:
            # Constrói URL de busca
            encoded_query = urllib.parse.quote(query)
            encoded_location = urllib.parse.quote(location)
            url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&location={encoded_location}&f_TPR=r86400"
            
            print(f"🌐 Acessando: {url}")
            self.driver.get(url)
            
            # Aguarda carregamento
            self.human_delay(3, 5)
            
            # Faz scroll para carregar mais vagas
            self.scroll_page()
            
            # Aguarda resultados
            self.wait_for_element(".jobs-search__results-list", timeout=10)
            
            # Pega HTML da página
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            jobs = self._extract_jobs_from_html(soup)
            
        except Exception as e:
            print(f"❌ Erro na busca do LinkedIn: {e}")
            
        return jobs
    
    def _extract_jobs_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai vagas do HTML"""
        jobs = []
        
        # Seletores atualizados para LinkedIn
        job_selectors = [
            ".jobs-search__results-list li",
            ".job-search-card",
            "[data-entity-urn*='jobPosting']",
            ".base-card",
            ".job-card-container"
        ]
        
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                print(f"✅ Encontrados {len(job_elements)} elementos com selector: {selector}")
                for job_elem in job_elements:
                    try:
                        job = self._extract_job_data(job_elem)
                        if job and self._is_relevant_job(job):
                            jobs.append(job)
                    except Exception as e:
                        continue
                break  # Usa o primeiro selector que funcionar
        
        return jobs
    
    def _extract_job_data(self, job_elem) -> Dict:
        """Extrai dados de uma vaga individual"""
        # Seletores flexíveis
        title_selectors = [
            ".base-search-card__title",
            ".job-card-list__title",
            "h3",
            ".job-card-title"
        ]
        
        company_selectors = [
            ".base-search-card__subtitle",
            ".job-card-container__company-name",
            "h4"
        ]
        
        location_selectors = [
            ".job-search-card__location",
            ".job-card-container__metadata-item"
        ]
        
        link_selectors = [
            ".base-card__full-link",
            "a.job-card-container__link"
        ]
        
        title = self._extract_text(job_elem, title_selectors)
        company = self._extract_text(job_elem, company_selectors)
        location = self._extract_text(job_elem, location_selectors, "Salvador, Bahia")
        url = self._extract_url(job_elem, link_selectors)
        
        if not title:
            return None
            
        return {
            'title': title,
            'company': company,
            'location': location,
            'date_posted': 'Recent',
            'platform': 'LinkedIn',
            'url': url
        }
    
    def _extract_text(self, element, selectors, default="N/A"):
        """Extrai texto usando múltiplos seletores"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return default
    
    def _extract_url(self, element, selectors):
        """Extrai URL usando múltiplos seletores"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get('href'):
                href = found.get('href')
                if href.startswith('/'):
                    return f"https://www.linkedin.com{href}"
                return href
        return "#"
    
    def _is_relevant_job(self, job: Dict) -> bool:
        """Filtra vagas relevantes de TI"""
        tech_keywords = [
            'ti', 't.i', 'tecnologia', 'tecnológico', 'sistema', 'informática',
            'programação', 'desenvolvedor', 'software', 'dados', 'data',
            'suporte', 'infraestrutura', 'redes', 'devops', 'developer',
            'analista', 'technology', 'systems', 'it', 'dev', 'computação'
        ]
        
        title = job['title'].lower()
        return any(keyword in title for keyword in tech_keywords)
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicatas"""
        seen = set()
        unique = []
        for job in jobs:
            identifier = f"{job['title']}_{job['company']}"
            if identifier not in seen:
                seen.add(identifier)
                unique.append(job)
        return unique