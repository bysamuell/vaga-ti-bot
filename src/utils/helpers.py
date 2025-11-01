import json
from datetime import datetime
from typing import List, Dict

def save_jobs_to_file(jobs: List[Dict], filename: str = "vagas_encontradas.json"):
    """Salva as vagas encontradas em um arquivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

def load_previous_jobs(filename: str = "vagas_encontradas.json") -> List[Dict]:
    """Carrega vagas anteriores do arquivo"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_new_jobs(current_jobs: List[Dict], previous_jobs: List[Dict]) -> List[Dict]:
    """Retorna apenas as vagas novas"""
    previous_titles = {job['title'] + job['company'] for job in previous_jobs}
    return [job for job in current_jobs if job['title'] + job['company'] not in previous_titles]

def format_jobs_for_display(jobs: List[Dict]) -> str:
    """Formata as vagas para exibição"""
    if not jobs:
        return "Nenhuma vaga nova encontrada."
    
    output = f"🚀 {len(jobs)} NOVAS VAGAS ENCONTRADAS!\n\n"
    
    for i, job in enumerate(jobs, 1):
        output += f"📌 VAGA {i}:\n"
        output += f"🏢 Empresa: {job.get('company', 'N/A')}\n"
        output += f"📝 Cargo: {job.get('title', 'N/A')}\n"
        output += f"📍 Local: {job.get('location', 'N/A')}\n"
        output += f"🕒 Data: {job.get('date_posted', 'N/A')}\n"
        output += f"🌐 Plataforma: {job.get('platform', 'N/A')}\n"
        output += f"🔗 Link: {job.get('url', '#')}\n"
        output += "─" * 50 + "\n\n"
    
    return output