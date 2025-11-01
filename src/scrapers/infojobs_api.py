from .api_base import ApiBaseScraper
from typing import List, Dict
import base64

class InfoJobsApiScraper(ApiBaseScraper):
    def __init__(self, client_id: str, client_secret: str):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.infojobs.net/api/7/offer"
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """Obtém access token da API do InfoJobs"""
        try:
            # Codifica credenciais para Basic Auth
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(
                'https://www.infojobs.net/oauth/authorize',
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token', '')
            else:
                print(f"❌ Erro ao obter token InfoJobs: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"❌ Erro no auth InfoJobs: {e}")
            return ""
    
    def scrape_jobs(self, job_levels: List[str], tech_keywords: List[str], location: str = "Salvador") -> List[Dict]:
        """Busca vagas usando API oficial do InfoJobs"""
        if not self.access_token:
            print("❌ Access token não disponível para InfoJobs")
            return []
        
        all_jobs = []
        
        for level in job_levels:
            print(f"🔍 Buscando no InfoJobs API: {level}")
            
            jobs = self._search_infojobs_api(level, location)
            if jobs:
                all_jobs.extend(jobs)
                print(f"✅ {len(jobs)} vagas encontradas para '{level}'")
            else:
                print(f"❌ Nenhuma vaga encontrada para '{level}'")
        
        tech_jobs = self.filter_tech_jobs(all_jobs)
        return tech_jobs
    
    def _search_infojobs_api(self, query: str, location: str) -> List[Dict]:
        """Faz busca na API do InfoJobs"""
        jobs = []
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Constrói query de busca
        search_query = f"{query} TI {location}"
        params = {
            'q': search_query,
            'city': location,
            'maxResults': 20
        }
        
        data = self.make_api_request(self.base_url, params, headers)
        
        if data and 'offers' in data:
            for offer in data['offers']:
                job = self._parse_infojobs_offer(offer)
                if job:
                    jobs.append(job)
        
        return jobs
    
    def _parse_infojobs_offer(self, offer: dict) -> Dict:
        """Parse dos dados da vaga do InfoJobs"""
        try:
            title = offer.get('title', '').strip()
            company = offer.get('author', {}).get('name', 'N/A').strip()
            
            # Localização
            city = offer.get('city', 'Salvador')
            location = f"{city}, BA"
            
            # URL
            url = offer.get('link', '#')
            
            # Data
            updated = offer.get('updated', 'Recent')
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'date_posted': updated,
                'platform': 'InfoJobs',
                'url': url,
                'description': offer.get('content', '')
            }
        except Exception as e:
            print(f"❌ Erro ao parsear vaga InfoJobs: {e}")
            return None