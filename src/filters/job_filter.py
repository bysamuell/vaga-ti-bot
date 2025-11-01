import re
from datetime import datetime, timedelta
from typing import List, Dict

class JobFilter:
    def __init__(self):
        self.keywords = ["auxiliar", "estágio", "estagio", "assistente", "junior", "trainer", "jr"]
        self.exclude_keywords = ["sênior", "senior", "pleno", "especialista", "coordinator", "manager"]
        
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filtra as vagas baseado nos critérios definidos"""
        filtered_jobs = []
        
        for job in jobs:
            if self._meets_criteria(job):
                filtered_jobs.append(job)
                
        return filtered_jobs
    
    def _meets_criteria(self, job: Dict) -> bool:
        """Verifica se a vaga atende aos critérios"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        
        # Verifica se contém palavras-chave inclusivas
        has_inclusive_keyword = any(keyword in title or keyword in description 
                                  for keyword in self.keywords)
        
        # Verifica se NÃO contém palavras-chave exclusivas
        has_exclusive_keyword = any(keyword in title or keyword in description 
                                  for keyword in self.exclude_keywords)
        
        # Verifica se é recente (últimas 24h)
        is_recent = self._is_recent(job.get('date_posted'))
        
        return has_inclusive_keyword and not has_exclusive_keyword and is_recent
    
    def _is_recent(self, date_string: str) -> bool:
        """Verifica se a vaga foi postada nas últimas 24 horas"""
        if not date_string:
            return True  # Assume recente se não há data
            
        # Padrões comuns de datas
        patterns = [
            r'(\d+)\s*(horas?|h)\s*',
            r'(\d+)\s*(dias?|d)\s*',
            r'(\d+)/(\d+)/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_string.lower())
            if match:
                if 'hora' in pattern or 'h' in pattern:
                    hours = int(match.group(1))
                    return hours <= 24
                elif 'dia' in pattern or 'd' in pattern:
                    days = int(match.group(1))
                    return days == 0
                    
        return True  # Assume recente se não consegue parsear