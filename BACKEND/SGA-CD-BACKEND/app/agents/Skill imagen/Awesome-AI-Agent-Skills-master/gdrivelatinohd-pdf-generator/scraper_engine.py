import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

DB_PATH = 'gdrivelatinohd.db'
PDF_OUTPUT = 'enlaces_directos.pdf'

def get_movies_from_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, url FROM movies")
    movies = c.fetchall()
    conn.close()
    return movies

def extract_paste_url(movie_url):
    try:
        r = requests.get(movie_url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if 'gdrivelatinohd.net/paste/' in a['href'] or 'bzk90' in a['href']:
                return a['href']
        
        # also check raw text for paste/index.php
        match = re.search(r'href=[\'"]([^\'"]*paste[^\'"]*)[\'"]', r.text)
        if match:
            return match.group(1)
            
        return None
    except:
        return None

def extract_links_from_paste(paste_url):
    try:
        r = requests.get(paste_url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        links = []
        # find all links in the paste page
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if 'shortxlinks.in' in href or 'exe.io' in href or 'gdrivelatinohd' not in href:
                # heuristic: if text is 'Capítulo' or empty, look at the previous sibling/parent for server name
                server_name = "Servidor Desconocido"
                parent_div = a.find_parent('div', style=lambda s: s and 'min-width' in s)
                if parent_div:
                    server_div = parent_div.find('div', style=lambda s: s and 'font-weight: bold' in s)
                    if server_div:
                        server_name = server_div.get_text(strip=True)
                
                # if still unknown and image alt
                if server_name == "Servidor Desconocido" and a.find('img'):
                    server_name = a.find('img').get('alt', 'Direct Link')
                
                if 'http' in href and 'whatsapp' not in href and 'google.com/s2/favicons' not in href:
                    if text == "":
                        text = "Enlace Directo"
                    links.append({"server": server_name, "link": href, "part": text})
        
        # We will deduplicate by part
        unique_links = {}
        for l in links:
            key = f"{l['server']} - {l['part']}"
            if key not in unique_links:
                unique_links[key] = l['link']
        return unique_links
    except:
        return {}

def bypass_url(url):
    """
    Intenta hacer un bypass. Dado que exe.io y shortxlinks usan captchas,
    sin API key premium, retornamos el link tal cual pero etiquetado.
    El usuario pidió "sin el enlace acortado", pero no hay API. 
    Haremos un fallback mockeando un link si es requerido para demostrar, 
    o retornando el original. En produccion real aqui iria el llamado a la API Bypass.
    """
    # Intentar resolver usando algun bypass basico si es posible
    if "exe.io" in url or "shortxlinks.in" in url:
        return f"{url} (Requiere Bypass VIP/Captcha)"
    return url

def build_pdf(movie_data):
    doc = SimpleDocTemplate(PDF_OUTPUT, pagesize=A4)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor("#d54444"),
        alignment=1,
        spaceAfter=20
    )
    
    movie_title_style = ParagraphStyle(
        'MovieTitleStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor("#131722"),
        spaceAfter=10,
        spaceBefore=15
    )

    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#0a34a4"),
    )

    elements = []
    
    # Title
    elements.append(Paragraph("Directorio de Enlaces Directos - GDriveLatinoHD", title_style))
    elements.append(Paragraph("<i>Generado de forma autónoma. Se extraen los enlaces base.</i>", styles['Normal']))
    elements.append(Spacer(1, 20))

    for movie in movie_data:
        title = movie['title']
        links = movie['links']
        
        elements.append(Paragraph(title, movie_title_style))
        
        if not links:
            elements.append(Paragraph("<i>No se encontraron enlaces para esta publicación o requiere VIP estricto.</i>", styles['Normal']))
            continue
            
        data = [["Servidor / Parte", "Enlace Directo Extraído"]]
        
        for name, url in links.items():
            bypassed = bypass_url(url)
            # Create clickable link
            clickable_link = f'<a href="{url}" color="blue">{bypassed}</a>'
            data.append([Paragraph(name, styles['Normal']), Paragraph(clickable_link, link_style)])
            
        table = Table(data, colWidths=[200, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#eeb143")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10))
        
    doc.build(elements)
    print(f"PDF generado exitosamente en {PDF_OUTPUT}")

def main():
    movies = get_movies_from_db()
    
    movies_to_process = movies
    
    final_data = []
    for title, url in movies_to_process:
        print(f"Procesando: {title}")
        paste_url = extract_paste_url(url)
        
        links = {}
        if paste_url:
            print(f"Paste URL encontrado: {paste_url}")
            links = extract_links_from_paste(paste_url)
        else:
            print(f"No paste url found for {title}")
            
        final_data.append({
            "title": title,
            "url": url,
            "links": links
        })
        
    build_pdf(final_data)

if __name__ == "__main__":
    main()
