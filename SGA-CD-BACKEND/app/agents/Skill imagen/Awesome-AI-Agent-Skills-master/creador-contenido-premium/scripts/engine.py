from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap
import numpy as np

def aplicar_grano_lujo(imagen, intensidad=10):
    data = np.array(imagen)
    noise = np.random.normal(0, intensidad, data.shape)
    data = np.clip(data + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(data)

def crear_slide_premium(index, titulo, descripcion, output_path):
    width, height = 1080, 1080
    # Paleta de Lujo: Crema, Negro Carbón y Oro Viejo
    bg = (252, 250, 245)
    fg = (18, 18, 20)
    oro = (170, 140, 90)
    
    img = Image.new('RGB', (width, height), bg)
    draw = ImageDraw.Draw(img)
    
    try:
        # Fuentes Serif (Estilo Editorial)
        t_font = ImageFont.truetype("georgia.ttf", 95)
        d_font = ImageFont.truetype("arial.ttf", 36)
        m_font = ImageFont.truetype("arial.ttf", 22)
    except:
        t_font = ImageFont.load_default()
        d_font = ImageFont.load_default()
        m_font = ImageFont.load_default()

    # Layout Asimétrico
    margin = 80
    draw.rectangle([margin, 40, margin+60, 44], fill=oro)
    draw.text((width - 150, 60), f"0{index}", font=t_font, fill=oro)
    
    # Título
    wrapped_title = textwrap.fill(titulo.upper(), width=12)
    draw.text((margin, 200), wrapped_title, font=t_font, fill=fg)
    
    # Descripción
    wrapped_desc = textwrap.fill(descripcion, width=40)
    draw.text((margin, 700), wrapped_desc, font=d_font, fill=fg)
    
    # Footer en Español
    draw.text((margin, 960), "CONTENIDO PREMIUM // SISTEMA CLAUDE", font=m_font, fill=fg)
    draw.text((width-450, 960), "DIRECCIÓN DE ARTE 2026", font=m_font, fill=oro)

    # Elemento visual minimalista
    if index % 2 == 0:
        draw.line([(600, 250), (900, 250)], fill=oro, width=2)
    else:
        draw.ellipse([750, 300, 900, 450], outline=oro, width=1)

    # Finalizado con textura
    img = aplicar_grano_lujo(img)
    img = img.filter(ImageFilter.SHARPEN)
    img.save(output_path)
    print(f"✅ Slide {index} guardado en: {output_path}")

def generar_carrusel(tema, slides_info, folder_name):
    if not os.path.exists(folder_name): os.makedirs(folder_name)
    for i, info in enumerate(slides_info):
        path = os.path.join(folder_name, f"slide_{i+1}.png")
        crear_slide_premium(i+1, info['titulo'], info['desc'], path)
    print(f"\n🚀 Carrusel '{tema}' completado con éxito.")

if __name__ == "__main__":
    # Ejemplo de uso interno
    pass
