from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import random
import cloudscraper
from fake_useragent import UserAgent
from urllib.parse import urlencode

class BaseScraper(ABC):
    def __init__(self):
        self.ua = UserAgent()
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        self.setup_headers()
    
    def setup_headers(self):
        """Configura headers realistas"""
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        self.scraper.headers.update(self.headers)
    
    @abstractmethod
    def scrape_jobs(self) -> list:
        pass
    
    def make_request(self, url: str, params: dict = None) -> BeautifulSoup:
        """Faz requisição com proteção anti-bot"""
        try:
            # Delay humanoide entre requests
            time.sleep(random.uniform(2, 5))
            
            # Rotação de User-Agent
            self.headers['User-Agent'] = self.ua.random
            self.scraper.headers.update(self.headers)
            
            response = self.scraper.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Verifica se não foi bloqueado
            if self._is_blocked(response.text):
                print("❌ Site bloqueou o acesso. Tentando contornar...")
                return None
                
            return BeautifulSoup(response.content, 'html.parser')
            
        except Exception as e:
            print(f"❌ Erro na requisição para {url}: {e}")
            return None
    
    def _is_blocked(self, html: str) -> bool:
        """Verifica se foi bloqueado por anti-bot"""
        blocked_indicators = [
            "access denied", "captcha", "cloudflare", "bot detected",
            "blocked", "forbidden", "automated traffic"
        ]
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in blocked_indicators)
    
    def smart_find_element(self, soup: BeautifulSoup, selectors: list):
        """Tenta múltiplos seletores até encontrar o elemento"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
        return None
    
    def smart_find_all(self, soup: BeautifulSoup, selectors: list):
        """Tenta múltiplos seletores até encontrar elementos"""
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                return elements
        return []
    
    def extract_text_safe(self, element, default="N/A"):
        """Extrai texto com segurança"""
        if element:
            text = element.get_text(strip=True)
            return text if text else default
        return default
    
    def extract_attr_safe(self, element, attr, default="N/A"):
        """Extrai atributo com segurança"""
        if element and element.get(attr):
            return element.get(attr)
        return default