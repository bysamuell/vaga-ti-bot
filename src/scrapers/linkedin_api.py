from .api_base import ApiBaseScraper
from typing import List, Dict
import urllib.parse
from datetime import datetime, timedelta

class LinkedInApiScraper(ApiBaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    
    def scrape_jobs(self, job_levels: List[str], tech_keywords: List[str], location: str = "Salvador, Bahia") -> List[Dict]:
        """Busca vagas usando API não oficial do LinkedIn"""
        all_jobs = []
        
        # Keywords de busca otimizadas
        search_keywords = [
            "estágio ti",
            "junior ti", 
            "assistente ti",
            "auxiliar ti",
            "estagio tecnologia",
            "junior tecnologia",
            "assistente tecnologia",
            "auxiliar tecnologia"
        ]
        
        for keyword in search_keywords:
            print(f"🔍 Buscando no LinkedIn API: {keyword}")
            
            jobs = self._search_linkedin_api(keyword, location)
            if jobs:
                all_jobs.extend(jobs)
                print(f"✅ {len(jobs)} vagas encontradas para '{keyword}'")
            else:
                print(f"❌ Nenhuma vaga encontrada para '{keyword}'")
        
        # Filtra vagas de TI
        tech_jobs = self.filter_tech_jobs(all_jobs)
        return self._remove_duplicates(tech_jobs)
    
    def _search_linkedin_api(self, keyword: str, location: str, limit: int = 25) -> List[Dict]:
        """Faz busca na API do LinkedIn"""
        jobs = []
        
        params = {
            'keywords': keyword,
            'location': location,
            'f_TPR': 'r86400',  # Últimas 24 horas
            'start': 0
        }
        
        try:
            # A API retorna HTML mesmo, mas é mais estável
            response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                jobs = self._parse_linkedin_html(response.text)
            else:
                print(f"❌ LinkedIn API retornou status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na API LinkedIn: {e}")
        
        return jobs
    
    def _parse_linkedin_html(self, html: str) -> List[Dict]:
        """Parse do HTML retornado pela API"""
        from bs4 import BeautifulSoup
        
        jobs = []
        soup = BeautifulSoup(html, 'html.parser')
        
        job_cards = soup.find_all('li')
        
        for card in job_cards:
            try:
                job = self._extract_job_from_card(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                continue
        
        return jobs
    
    def _extract_job_from_card(self, card) -> Dict:
        """Extrai dados de um card de vaga"""
        # Título
        title_elem = card.find('h3', class_='base-search-card__title')
        if not title_elem:
            return None
            
        title = title_elem.get_text(strip=True)
        
        # Empresa
        company_elem = card.find('h4', class_='base-search-card__subtitle')
        company = company_elem.get_text(strip=True) if company_elem else 'N/A'
        
        # Localização
        location_elem = card.find('span', class_='job-search-card__location')
        location = location_elem.get_text(strip=True) if location_elem else 'Salvador, Bahia'
        
        # Data
        date_elem = card.find('time')
        date_posted = date_elem.get('datetime') if date_elem else 'Recent'
        
        # URL
        link_elem = card.find('a', class_='base-card__full-link')
        url = link_elem.get('href') if link_elem else '#'
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'date_posted': date_posted,
            'platform': 'LinkedIn',
            'url': url,
            'description': ''  # API não retorna descrição
        }
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove vagas duplicadas"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            identifier = f"{job['title']}_{job['company']}"
            if identifier not in seen:
                seen.add(identifier)
                unique_jobs.append(job)
        
        return unique_jobs