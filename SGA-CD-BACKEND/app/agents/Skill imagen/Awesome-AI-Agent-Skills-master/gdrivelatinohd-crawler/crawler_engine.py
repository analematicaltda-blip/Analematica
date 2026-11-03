import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

class GDriveLatinoHDCrawler:
    def __init__(self, start_page=1, max_pages=3):
        self.base_url = "https://gdrivelatinohd.net"
        self.start_page = start_page
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        self.results = []
        
    def run(self):
        print(f"[*] Iniciando rastreo masivo (Max Páginas: {self.max_pages})...")
        for page in range(self.start_page, self.start_page + self.max_pages):
            url = f"{self.base_url}/page/{page}/" if page > 1 else f"{self.base_url}/"
            print(f"[*] Rastreado Página {page} -> {url}")
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 404:
                    print("[!] Fin de la paginación alcanzado (404).")
                    break
                elif response.status_code != 200:
                    print(f"[!] Error HTTP {response.status_code}. Pausando...")
                    time.sleep(5)
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extraer enlaces de películas
                # Asumimos que los enlaces principales están en elementos <a> con título y href
                # pero nos saltamos los del navbar.
                movie_links = []
                for a in soup.find_all('a', href=True, title=True):
                    href = a['href']
                    if 'gdrivelatinohd.net' in href and '/page/' not in href and '/tag/' not in href and '/category/' not in href:
                        if href not in movie_links:
                            movie_links.append(href)
                            
                print(f"[+] Encontrados {len(movie_links)} aportes en la página {page}.")
                
                for movie_url in movie_links:
                    self.extract_movie_links(movie_url)
                    time.sleep(1) # Anti-ban
                    
            except Exception as e:
                print(f"[-] Error al procesar página {page}: {e}")
                
            time.sleep(2) # Anti-ban
            
        self.export_excel()
            
    def extract_movie_links(self, url):
        print(f"    -> Analizando: {url}")
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('h1', class_='titHead')
            title_text = title.text.strip() if title else url.split('/')[-2]
            
            # Buscar los enlaces al paste (son <a> no iframe)
            paste_links = soup.find_all('a', href=lambda s: s and '/paste/' in s)
            if not paste_links:
                print(f"       [-] No se encontraron enlaces de Paste.")
                return
                
            for paste_a in paste_links:
                paste_url = paste_a['href']
                if not paste_url.startswith('http'):
                    paste_url = f"https:{paste_url}" if paste_url.startswith('//') else f"{self.base_url}{paste_url}"
                    
                # Consultar la página del Paste
                paste_resp = self.session.get(paste_url, timeout=10)
                paste_soup = BeautifulSoup(paste_resp.text, 'html.parser')
                
                # Buscar enlaces acortados
                links = paste_soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if 'shortxlinks.in' in href or 'exe.io' in href or 'shrink' in href:
                        server_name = link.text.strip() if link.text.strip() else "Enlace Acortado"
                        self.results.append({
                            'Título': title_text,
                            'URL Publicación': url,
                            'Servidor / Parte': server_name,
                            'Enlace Extraído (Acortador)': href
                        })
                    
        except Exception as e:
            print(f"       [-] Error analizando post: {e}")

    def export_excel(self):
        print("\n[*] Generando archivo Excel...")
        if not self.results:
            print("[!] No se encontraron resultados.")
            return
            
        df = pd.DataFrame(self.results)
        df.to_excel('Catalogo_GDriveLatino.xlsx', index=False)
        print(f"[+] Archivo 'Catalogo_GDriveLatino.xlsx' generado con éxito con {len(self.results)} registros.")

if __name__ == "__main__":
    crawler = GDriveLatinoHDCrawler(max_pages=1) # Solo 1 página por ser piloto
    crawler.run()
