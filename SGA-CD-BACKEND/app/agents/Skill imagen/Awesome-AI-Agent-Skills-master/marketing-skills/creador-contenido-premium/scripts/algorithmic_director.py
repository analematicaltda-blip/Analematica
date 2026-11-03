import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

class AlgorithmicDirector:
    """
    Motor híbrido: Algoritmos Generativos + Dirección de Arte 2026.
    Fusión de 'algorithmic-art' y 'creador-contenido-premium'.
    """
    def __init__(self, width=1080, height=1080):
        self.width = width
        self.height = height
        self.palettes = [
            [(20, 20, 22), (255, 255, 255), (0, 255, 150)],  # Cyber Mint
            [(245, 245, 240), (40, 40, 45), (255, 80, 0)],    # Safety Orange
            [(30, 30, 40), (220, 220, 230), (100, 100, 255)], # Deep Periwinkle
            [(10, 10, 10), (180, 180, 180), (255, 255, 255)], # Monochrome Master
            [(45, 25, 20), (240, 230, 220), (200, 150, 100)]  # Terra Cotta
        ]

    def _generate_noise_field(self, intensity=20):
        # Ruido sub-píxel para Hyper-Physicality
        noise = np.random.normal(0, intensity, (self.height, self.width, 3)).astype(np.int16)
        return noise

    def _draw_organic_brutalism(self, draw, color):
        # Fusión Algorítmica: Grillas industriales + Atractores extraños
        # 1. Grilla Rígida (Máquina)
        for i in range(0, self.width, 120):
            alpha = random.randint(20, 60)
            draw.line([(i, 0), (i, self.height)], fill=color + (alpha,), width=1)
            draw.line([(0, i), (self.width, i)], fill=color + (alpha,), width=1)
        
        # 2. Caminata Aleatoria / Atractores (Organismo)
        points = []
        x, y = self.width // 2, self.height // 2
        for _ in range(1000):
            x += random.uniform(-30, 30)
            y += random.uniform(-30, 30)
            x = max(0, min(self.width, x))
            y = max(0, min(self.height, y))
            points.append((x, y))
        
        if len(points) > 1:
            draw.line(points, fill=color + (100,), width=2)

    def create_artifact(self, index, title, description, output_path):
        bg, fg, accent = self.palettes[index % len(self.palettes)]
        
        # Base de la imagen
        img = Image.new('RGBA', (self.width, self.height), bg + (255,))
        draw = ImageDraw.Draw(img)
        
        # Capa Algorítmica (Fondo dinámico)
        self._draw_organic_brutalism(draw, accent)
        
        # Capa Editorial (Tipografía)
        try:
            t_font = ImageFont.truetype("georgia.ttf", 110)
            d_font = ImageFont.truetype("arial.ttf", 36)
            m_font = ImageFont.truetype("arial.ttf", 18)
        except:
            t_font = ImageFont.load_default()
            d_font = ImageFont.load_default()
            m_font = ImageFont.load_default()

        # Layout High-End (MC-Dean + Anthropic)
        margin = 100
        draw.text((margin, 60), f"ALGO_DIRECTOR_2026 // NODE_{index:03d}", font=m_font, fill=accent)
        
        wrapped_title = textwrap.fill(title.upper(), width=10)
        draw.text((margin, 200), wrapped_title, font=t_font, fill=fg)
        
        wrapped_desc = textwrap.fill(description, width=40)
        draw.text((margin, 750), wrapped_desc, font=d_font, fill=fg)
        
        # Firma técnica
        draw.text((self.width - 400, 1020), "GENERATIVE ARTIFACT // ELITE EDITION", font=m_font, fill=accent)

        # Post-procesado físico (Hiper-Fisicidad)
        data = np.array(img).astype(np.int16)
        noise = np.zeros_like(data)
        noise_vals = self._generate_noise_field(intensity=15)
        noise[:, :, :3] = noise_vals
        data = np.clip(data + noise, 0, 255).astype(np.uint8)
        
        final_img = Image.fromarray(data).convert('RGB')
        final_img = final_img.filter(ImageFilter.SHARPEN)
        final_img.save(output_path)
        print(f"🎨 Artefacto Algorítmico {index} generado: {output_path}")

def main():
    director = AlgorithmicDirector()
    output_dir = "hybrid_algorithmic_2026"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    slides = [
        {"title": "Generative Soul", "description": "En 2026, el diseño no se dibuja, se programa. Algoritmos de caminata aleatoria crean el 'alma' biológica de la pieza."},
        {"title": "Organic Grid", "description": "La tensión perfecta. Una grilla industrial brutalista siendo colonizada por procesos matemáticos naturales."},
        {"title": "Sub-Pixel Life", "description": "Hiper-fisicidad mediante ruido sub-píxel. Cada punto de luz tiene un peso táctil que puedes sentir en la mirada."},
        {"title": "Liquid Data", "description": "La información fluye como un organismo. Usamos atractores matemáticos para guiar el ojo hacia el insight fundamental."},
        {"title": "Elite Synthesis", "description": "La unión final. Buen gusto editorial + poder algorítmico. El estándar definitivo para la creación de contenido."}
    ]
    
    for i, slide in enumerate(slides):
        director.create_artifact(i+1, slide["title"], slide["description"], os.path.join(output_dir, f"artifact_{i+1}.jpg"))

if __name__ == "__main__":
    main()
