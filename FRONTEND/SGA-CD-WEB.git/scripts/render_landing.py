"""Build the published landing while retaining the original source template."""
from pathlib import Path
import hashlib
import re
import subprocess

def render(source: Path, published: Path):
    html=(source/'index.html').read_text()
    sections=list(re.finditer(r'<section\b[^>]*id="([^"]+)"[\s\S]*?</section>',html))
    order=['carrusel-moderno','admin-territorial-control','presentacion','partners','hero',
           'monitor-vivo','carrusel-destacados','funcionalidades','faq','planes','oferta-lanzamiento','registro']
    blocks={match.group(1):match.group() for match in sections}
    if len(sections)!=12 or set(blocks)!=set(order):
        raise ValueError('La estructura de secciones cambió; no se publicó nada')
    # Move whole sections, keeping their IDs, content and existing handlers.
    for match,name in reversed(list(zip(sections,order))):
        html=html[:match.start()]+blocks[name]+html[match.end():]
    button=re.search(r'<button\b[^>]*class="[^"]*mobile-menu-btn[\s\S]*?</button>',html)
    if not button:
        raise ValueError('No se encontró el menú móvil')
    menu=button.group()
    html=html[:button.start()]+html[button.end():]
    html=html.replace('</header>',menu+'\n</header>',1)
    html=html.replace('href="#hero" class="nav-icon-link"', 'href="#carrusel-moderno" class="nav-icon-link"',1)
    html=html.replace('href="#monitor-vivo" class="nav-icon-link"', 'href="#admin-territorial-control" class="nav-icon-link"',1)
    markup=subprocess.check_output(['node',str(Path(__file__).with_name('render_carousel.cjs')),str(source/'js/components/modern_carousel.js')],text=True)
    marker='<div id="modern-carousel-container"></div>'
    if html.count(marker)!=1:
        raise ValueError('Contenedor de carrusel inesperado')
    html=html.replace(marker,'<div id="modern-carousel-container" role="region" aria-label="Galería de imágenes SGA-CD">'+markup+'</div>')
    html=html.replace('</head>','<link rel="stylesheet" href="css/sky-theme.css">\n</head>',1)
    def version(match):
        name=match.group(2)
        # Environment configuration is never copied from the repository.
        path=(published if name=='js/config.js' else source)/name
        if not path.is_file():
            raise ValueError('Falta recurso: '+name)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        return match.group(1)+name+'?v='+digest+'"'
    return re.sub(r'((?:src|href)=")((?:js|css)/[^"?]+\.(?:js|css))"',version,html).encode()
