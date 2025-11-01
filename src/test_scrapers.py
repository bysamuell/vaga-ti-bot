# test_scrapers.py
try:
    from scrapers.gupy_selenium import GupySeleniumScraper
    print("✅ GupySeleniumScraper importado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao importar GupySeleniumScraper: {e}")

try:
    from scrapers.linkedin_selenium import LinkedInSeleniumScraper
    print("✅ LinkedInSeleniumScraper importado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao importar LinkedInSeleniumScraper: {e}")