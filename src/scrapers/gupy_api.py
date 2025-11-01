from .api_base import ApiBaseScraper
from typing import List, Dict
import urllib.parse

class GupyApiScraper(ApiBaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.gupy.io/api/v1/jobs"
    
    def scrape_jobs(self, job_levels: List[str], tech_keywords: List[str], location: str = "salvador") -> List[Dict]:
        """Busca vagas usando API oficial da Gupy"""
        all_jobs = []
        
        search_queries = [
            "estágio", "estagio", "junior", "assistente", "auxiliar"
        ]
        
        for query in search_queries:
            print(f"🔍 Buscando na Gupy API: {query}")
            
            jobs = self._search_gupy_api(query, location)
            if jobs:
                all_jobs.extend(jobs)
                print(f"✅ {len(jobs)} vagas encontradas para '{query}'")
            else:
                print(f"❌ Nenhuma vaga encontrada para '{query}'")
        
        # Filtra vagas de TI
        tech_jobs = self.filter_tech_jobs(all_jobs)
        return tech_jobs
    
    def _search_gupy_api(self, query: str, location: str) -> List[Dict]:
        """Faz busca na API da Gupy"""
        jobs = []
        
        params = {
            'jobName': query,
            'city': location,
            'limit': 50,
            'offset': 0
        }
        
        data = self.make_api_request(self.base_url, params)
        
        if data and 'data' in data:
            for job_data in data['data']:
                job = self._parse_gupy_job(job_data)
                if job:
                    jobs.append(job)
        
        return jobs
    
    def _parse_gupy_job(self, job_data: dict) -> Dict:
        """Parse dos dados da vaga da Gupy"""
        try:
            title = job_data.get('name', '').strip()
            company = job_data.get('company', {}).get('name', 'N/A').strip()
            
            # Localização
            city = job_data.get('city', 'Salvador')
            state = job_data.get('state', 'BA')
            location = f"{city}, {state}"
            
            # URL
            job_id = job_data.get('id')
            url = f"https://portal.gupy.io/job/{job_id}" if job_id else "#"
            
            # Data de publicação
            published_date = job_data.get('publishedDate', 'Recent')
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'date_posted': published_date,
                'platform': 'Gupy',
                'url': url,
                'description': job_data.get('description', '')
            }
        except Exception as e:
            print(f"❌ Erro ao parsear vaga Gupy: {e}")
            return None