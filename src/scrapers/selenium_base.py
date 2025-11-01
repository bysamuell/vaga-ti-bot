from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import undetected_chromedriver as uc

class SeleniumScraper:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o ChromeDriver de forma stealth"""
        try:
            options = uc.ChromeOptions()
            
            # Configurações para evitar detecção
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-application-cache')
            options.add_argument('--media-cache-size=1')
            options.add_argument('--disk-cache-size=1')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            if self.headless:
                options.add_argument('--headless=new')
            
            # Usa undetected-chromedriver para evitar detecção
            self.driver = uc.Chrome(
                options=options,
                service=Service(ChromeDriverManager().install())
            )
            
            # Script para remover webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            print(f"❌ Erro ao configurar driver: {e}")
            self._setup_fallback_driver()
    
    def _setup_fallback_driver(self):
        """Configuração fallback caso undetected-chromedriver falhe"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            if self.headless:
                options.add_argument('--headless=new')
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
        except Exception as e:
            print(f"❌ Erro no fallback driver: {e}")
    
    def human_delay(self, min_seconds=2, max_seconds=5):
        """Delay humanoide entre ações"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def scroll_page(self, scroll_pauses=3):
        """Faz scroll humanoide na página"""
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(scroll_pauses):
            # Scroll aleatório
            scroll_to = random.randint(200, scroll_height // 2)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            self.human_delay(1, 2)
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Aguarda elemento aparecer"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except:
            return None
    
    def find_elements_safe(self, selector, by=By.CSS_SELECTOR):
        """Encontra elementos com tratamento de erro"""
        try:
            return self.driver.find_elements(by, selector)
        except:
            return []
    
    def find_element_safe(self, selector, by=By.CSS_SELECTOR):
        """Encontra elemento com tratamento de erro"""
        try:
            return self.driver.find_element(by, selector)
        except:
            return None
    
    def get_page_source(self):
        """Retorna o HTML da página"""
        return self.driver.page_source
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()