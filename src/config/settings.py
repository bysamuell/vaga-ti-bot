import os
from dotenv import load_dotenv

load_dotenv()

# Configurações de busca
JOB_LEVELS = ["auxiliar", "estágio", "estagio", "assistente", "junior", "trainer", "jr"]
TECH_KEYWORDS = ["ti", "tecnologia", "tecnológico", "tecnologica", "tecnologicos", 
                "tecnológica", "tecnológica", "tecnologia da informação", "tecnologia da informacao",
                "tecnologia da informaçao", "sistemas", "informática", "informatica",
                "programação", "programacao", "desenvolvedor", "developer", "software",
                "dados", "data", "suporte", "infraestrutura", "redes", "devops"]

LOCATION = "Salvador, Bahia"

# Horários de execução (horário de Brasília)
SCHEDULE_TIMES = ["09:00", "12:00", "15:00", "19:00"]

# Webhook do Discord
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

# Configurações dos sites
SITES = {
    "linkedin": {
        "enabled": True,
        "base_url": "https://www.linkedin.com/jobs/search/",
    },
    "gupy": {
        "enabled": True,
        "base_url": "https://portal.gupy.io/job-search/",
    },
    "infojobs": {
        "enabled": True,
        "base_url": "https://www.infojobs.com.br/",
    }
}