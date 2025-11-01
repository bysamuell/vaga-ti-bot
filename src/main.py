import schedule
import time
from datetime import datetime
from scrapers.linkedin_selenium import LinkedInSeleniumScraper
from scrapers.gupy_selenium import GupySeleniumScraper
from filters.job_filter import JobFilter
from utils.helpers import save_jobs_to_file, load_previous_jobs, get_new_jobs
from utils.discord_notifier import DiscordNotifier
from config.settings import JOB_LEVELS, TECH_KEYWORDS, LOCATION, SCHEDULE_TIMES

class VagasTIBot:
    def __init__(self):
        # Usa Selenium para ambos (mais confiável)
        self.scrapers = {
            'linkedin': LinkedInSeleniumScraper(),
            'gupy': GupySeleniumScraper(),
        }
        self.filter = JobFilter()
        self.notifier = DiscordNotifier()
        
    def run_search(self):
        """Executa busca usando Selenium"""
        print(f"🚀 Iniciando busca Selenium às {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        all_jobs = []
        
        for site_name, scraper in self.scrapers.items():
            print(f"🔍 Buscando vagas no {site_name.capitalize()} (Selenium)...")
            try:
                jobs = scraper.scrape_jobs(JOB_LEVELS, TECH_KEYWORDS, LOCATION)
                all_jobs.extend(jobs)
                print(f"✅ {len(jobs)} vagas encontradas no {site_name.capitalize()}")
            except Exception as e:
                print(f"❌ Erro no {site_name.capitalize()}: {e}")
        
        # Resto do processo...
        filtered_jobs = self.filter.filter_jobs(all_jobs)
        print(f"📊 {len(filtered_jobs)} vagas após filtro")
        
        previous_jobs = load_previous_jobs()
        new_jobs = get_new_jobs(filtered_jobs, previous_jobs)
        
        if filtered_jobs:
            save_jobs_to_file(filtered_jobs)
        
        if new_jobs:
            print(f"🎉 {len(new_jobs)} NOVAS VAGAS! Enviando para Discord...")
            self.notifier.send_jobs(new_jobs)
        else:
            print("📭 Nenhuma vaga nova encontrada.")
            self.notifier.send_jobs([])
        
        print("=" * 60)
    
    def setup_scheduler(self):
        """Configura o agendador"""
        for schedule_time in SCHEDULE_TIMES:
            schedule.every().day.at(schedule_time).do(self.run_search)
            print(f"⏰ Agendada busca às {schedule_time} (horário de Brasília)")
    
    def run(self):
        """Executa o bot"""
        print("🤖 Bot de Vagas de TI (API) Iniciado!")
        print(f"📍 Localização: {LOCATION}")
        print(f"🎯 Níveis: {', '.join(JOB_LEVELS)}")
        print(f"🔧 Área: TI/Technology")
        print(f"⏰ Horários: {', '.join(SCHEDULE_TIMES)}")
        print("=" * 60)
        
        # Busca imediata
        self.run_search()
        
        # Agendador
        self.setup_scheduler()
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    bot = VagasTIBot()
    bot.run()