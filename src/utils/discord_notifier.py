import requests
import json
from typing import List, Dict
from datetime import datetime
import time
from config.settings import DISCORD_WEBHOOK_URL

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL
    
    def send_jobs(self, jobs: List[Dict]):
        """Envia vagas para o webhook do Discord"""
        if not self.webhook_url:
            print("❌ Webhook do Discord não configurado")
            print("💡 Configure DISCORD_WEBHOOK_URL no arquivo .env")
            return False
        
        if not jobs:
            message = "📭 Nenhuma vaga nova encontrada na última busca."
            print(message)
            return self._send_simple_message(message)
        
        print(f"📤 Enviando {len(jobs)} vagas para Discord...")
        
        try:
            # Envia um resumo primeiro
            summary_sent = self._send_summary(jobs)
            if not summary_sent:
                print("❌ Falha ao enviar resumo para Discord")
                return False
            
            # Envia cada vaga individualmente
            success_count = 0
            for job in jobs[:8]:  # Limita a 8 vagas
                sent = self._send_job_embed(job)
                if sent:
                    success_count += 1
                time.sleep(1)
            
            if len(jobs) > 8:
                remaining = len(jobs) - 8
                self._send_simple_message(f"📊 ... e mais {remaining} vagas!")
            
            print(f"✅ {success_count}/{len(jobs)} vagas enviadas para Discord")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erro ao enviar para Discord: {e}")
            return False
    
    def _send_simple_message(self, message: str):
        """Envia uma mensagem simples"""
        try:
            data = {"content": message}
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    def _send_summary(self, jobs: List[Dict]):
        """Envia resumo das vagas"""
        try:
            platforms = list(set(job['platform'] for job in jobs))
            
            summary = {
                "content": f"🚀 **{len(jobs)} NOVAS VAGAS DE TI ENCONTRADAS!**",
                "embeds": [
                    {
                        "title": "📊 Resumo da Busca",
                        "color": 0x00ff00,
                        "fields": [
                            {
                                "name": "Total de Vagas",
                                "value": str(len(jobs)),
                                "inline": True
                            },
                            {
                                "name": "Plataformas",
                                "value": ", ".join(platforms),
                                "inline": True
                            },
                            {
                                "name": "Localização",
                                "value": "Salvador, BA",
                                "inline": True
                            }
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                json=summary,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar resumo: {e}")
            return False
    
    def _send_job_embed(self, job: Dict):
        """Envia uma vaga como embed"""
        try:
            title = job['title'][:200] + "..." if len(job['title']) > 200 else job['title']
            
            embed = {
                "embeds": [
                    {
                        "title": f"🏢 {title}",
                        "color": 0x3498db,
                        "fields": [
                            {
                                "name": "Empresa",
                                "value": job.get('company', 'N/A')[:100],
                                "inline": True
                            },
                            {
                                "name": "Localização",
                                "value": job.get('location', 'N/A')[:50],
                                "inline": True
                            },
                            {
                                "name": "Plataforma",
                                "value": job.get('platform', 'N/A'),
                                "inline": True
                            }
                        ],
                        "url": job.get('url', '#'),
                        "footer": {
                            "text": "🤖 Vagas TI Bot - Salvador/BA"
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                json=embed,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar vaga: {e}")
            return False