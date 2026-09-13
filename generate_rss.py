import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from playwright.sync_api import sync_playwright

urls = [
    "https://www.bolivar.com.bo/Noticias",
]

fg = FeedGenerator()
fg.title("RSS Bolívar")
fg.link(href="https://www.bolivar.com.bo")
fg.description("Feed generado automáticamente con GitHub Actions y Playwright")

print("Iniciando navegador headless para renderizar JavaScript...")
total_entries = 0
seen_links = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for url in urls:
        print(f"Cargando (con JS): {url}")
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Error al cargar {url}: {e}")
            continue

        soup = BeautifulSoup(page.content(), "html.parser")
        found_count = 0

        for a in soup.find_all("a", href=True):
            link = a.get("href")
            title = a.get_text(strip=True)
            
            if "/noticias/" in link and len(title) > 15:
                full_link = urljoin("https://www.aciprensa.com", link)
                
                if full_link not in seen_links:
                    seen_links.add(full_link)
                    
                    fe = fg.add_entry()
                    fe.title(title)
                    fe.link(href=full_link)
                    total_entries += 1
                    found_count += 1
                    
                    if found_count >= 5:
                        break

    browser.close()

rss_file_path = "rss.xml"
fg.rss_file(rss_file_path)
print(f"RSS generado en {rss_file_path} con {total_entries} entradas únicas")

if os.path.exists(rss_file_path):
    print("rss.xml existe y está listo para commit")
else:
    print("Error: rss.xml no se creó")
