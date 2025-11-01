import requests
import time
import random
from typing import List, Dict
from fake_useragent import UserAgent

class ApiBaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Configura sessão para requests API"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Referer': 'https://www.linkedin.com/',
            'Origin': 'https://www.linkedin.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
    
    def make_api_request(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """Faz requisição para API com tratamento de erro"""
        try:
            # Delay entre requests
            time.sleep(random.uniform(1, 3))
            
            # Rotaciona User-Agent
            if headers:
                headers['User-Agent'] = self.ua.random
            else:
                headers = {'User-Agent': self.ua.random}
            
            response = self.session.get(
                url, 
                params=params, 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API retornou status {response.status_code} para {url}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição API: {e}")
            return None
    
    def filter_tech_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filtra vagas de TI"""
        tech_keywords = [
            'ti', 't.i', 'tecnologia', 'tecnológico', 'sistema', 'informática',
            'programação', 'desenvolvedor', 'software', 'dados', 'data',
            'suporte', 'infraestrutura', 'redes', 'devops', 'developer',
            'analista', 'technology', 'systems', 'it', 'dev', 'computação',
            'programador', 'software', 'aplicação', 'aplicacoes', 'system',
            'database', 'banco de dados', 'sql', 'frontend', 'backend',
            'fullstack', 'mobile', 'web', 'site', 'aplicativo'
        ]
        
        filtered_jobs = []
        for job in jobs:
            title = job.get('title', '').lower()
            description = job.get('description', '').lower()
            
            # Verifica se é vaga de TI
            is_tech_job = any(keyword in title for keyword in tech_keywords)
            
            # Verifica nível (estágio, junior, etc.)
            levels = ['estágio', 'estagio', 'junior', 'jr', 'assistente', 'auxiliar', 'trainer']
            is_desired_level = any(level in title for level in levels)
            
            if is_tech_job and is_desired_level:
                filtered_jobs.append(job)
        
        return filtered_jobs