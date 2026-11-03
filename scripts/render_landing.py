"""Build the published landing while retaining the original source template."""
from pathlib import Path
import hashlib
import re
import subprocess

def render(source: Path, published: Path):
    html=(source/'index.html').read_text()
    block=re.search(r'<section\b[^>]*id="admin-territorial-control"[\s\S]*?</section>',html)
    if not block:
        raise ValueError('No se encontró el panel territorial')
    section=block.group()
    html=html[:block.start()]+html[block.end():]
    carousel=re.search(r'<section\b[^>]*id="carrusel-moderno"[\s\S]*?</section>',html)
    if not carousel:
        raise ValueError('No se encontró el carrusel principal')
    html=html[:carousel.end()]+'\n'+section+html[carousel.end():]
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
