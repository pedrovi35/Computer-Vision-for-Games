"""
🎨 PINTURA NO AR INCRÍVEL - Desenhe Arte Digital com suas Mãos!
Crie arte digital movimentando suas mãos no ar! Escolha templates ou desenhe livre!

Controles: Dedo indicador para desenhar | Polegar + indicador para ferramentas
"""

# Suprime warnings do TensorFlow/MediaPipe
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings('ignore')

import cv2
import pygame
import sys
import random
import time
import mediapipe as mp
import numpy as np
import math

# --- Configurações ---
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 950
WEBCAM_WIDTH = 300
WEBCAM_HEIGHT = 225
FPS = 60

# Paleta de cores vibrante e moderna
COLORS = {
    "Vermelho": (255, 65, 65),
    "Laranja": (255, 140, 0),
    "Amarelo": (255, 220, 0),
    "Verde": (50, 255, 100),
    "Ciano": (0, 230, 255),
    "Azul": (65, 105, 255),
    "Roxo": (180, 80, 255),
    "Rosa": (255, 105, 180),
    "Marrom": (139, 90, 60),
    "Branco": (255, 255, 255),
    "Cinza": (150, 150, 150),
    "Preto": (20, 20, 20)
}

BG_COLOR = (245, 245, 255)
UI_BG = (45, 45, 65)
UI_ACCENT = (100, 220, 255)
UI_SUCCESS = (80, 255, 150)
UI_WARNING = (255, 180, 80)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (200, 210, 220)

# Configurações de desenho
BRUSH_SIZES = {
    "Fino": 2,
    "Pequeno": 5,
    "Médio": 10,
    "Grande": 18,
    "Enorme": 30
}

# Modos de jogo
MODES = {
    "LIVRE": "free",
    "TEMPLATES": "templates"
}

# Templates de desenho
TEMPLATES = {
    "Coração": [
        "heart", "❤️", 
        "Um lindo coração para expressar amor!"
    ],
    "Estrela": [
        "star", "⭐",
        "Uma estrela brilhante!"
    ],
    "Casa": [
        "house", "🏠",
        "Uma casinha aconchegante!"
    ],
    "Flor": [
        "flower", "🌸",
        "Uma flor colorida e alegre!"
    ],
    "Sol": [
        "sun", "☀️",
        "Um sol radiante!"
    ],
    "Borboleta": [
        "butterfly", "🦋",
        "Uma borboleta delicada!"
    ],
    "Árvore": [
        "tree", "🌳",
        "Uma árvore frondosa!"
    ],
    "Arco-íris": [
        "rainbow", "🌈",
        "Um arco-íris colorido!"
    ]
}

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎨 Pintura no Ar Incrível")
clock = pygame.time.Clock()

# Fontes
font_title = pygame.font.Font(None, 85)
font_large = pygame.font.Font(None, 65)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 38)
font_tiny = pygame.font.Font(None, 30)
font_mini = pygame.font.Font(None, 24)

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# --- Funções de Template ---
def generate_template_points(template_type, width, height):
    """Gera pontos para desenhar templates"""
    cx, cy = width // 2, height // 2
    points = []
    
    if template_type == "heart":
        # Coração
        for t in range(0, 360, 2):
            angle = math.radians(t)
            x = cx + 200 * (16 * math.sin(angle)**3)
            y = cy - 200 * (13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle))
            points.append((x, y))
    
    elif template_type == "star":
        # Estrela de 5 pontas
        for i in range(11):
            angle = math.radians(i * 36 - 90)
            r = 200 if i % 2 == 0 else 80
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((x, y))
    
    elif template_type == "house":
        # Casa
        points = [
            (cx - 150, cy - 50), (cx - 150, cy + 150),  # Parede esquerda
            (cx + 150, cy + 150), (cx + 150, cy - 50),  # Parede direita
            (cx - 150, cy - 50), (cx, cy - 180),  # Telhado esquerdo
            (cx + 150, cy - 50),  # Telhado direito
            (cx - 150, cy - 50),  # Fecha base
        ]
    
    elif template_type == "flower":
        # Flor com pétalas
        for i in range(6):
            angle = math.radians(i * 60)
            # Pétalas
            for t in range(0, 180, 10):
                petal_angle = math.radians(t)
                r = 80 * math.sin(petal_angle)
                x = cx + (120 + r) * math.cos(angle + petal_angle / 2)
                y = cy + (120 + r) * math.sin(angle + petal_angle / 2)
                points.append((x, y))
        # Centro
        for t in range(0, 360, 10):
            angle = math.radians(t)
            x = cx + 40 * math.cos(angle)
            y = cy + 40 * math.sin(angle)
            points.append((x, y))
    
    elif template_type == "sun":
        # Sol com raios
        for t in range(0, 360, 10):
            angle = math.radians(t)
            x = cx + 100 * math.cos(angle)
            y = cy + 100 * math.sin(angle)
            points.append((x, y))
        # Raios
        for i in range(12):
            angle = math.radians(i * 30)
            points.append((cx + 100 * math.cos(angle), cy + 100 * math.sin(angle)))
            points.append((cx + 180 * math.cos(angle), cy + 180 * math.sin(angle)))
            points.append((cx + 100 * math.cos(angle), cy + 100 * math.sin(angle)))
    
    elif template_type == "butterfly":
        # Borboleta
        for side in [-1, 1]:
            for t in range(0, 360, 5):
                angle = math.radians(t)
                r = 100 * (1 + 0.5 * math.sin(2 * angle))
                x = cx + side * r * math.cos(angle)
                y = cy + 150 * math.sin(angle)
                points.append((x, y))
    
    elif template_type == "tree":
        # Árvore
        points = [
            (cx, cy + 150), (cx, cy - 50),  # Tronco
        ]
        # Copa (círculo)
        for t in range(0, 360, 10):
            angle = math.radians(t)
            x = cx + 120 * math.cos(angle)
            y = cy - 50 + 120 * math.sin(angle)
            points.append((x, y))
    
    elif template_type == "rainbow":
        # Arco-íris
        colors_count = 6
        for arc in range(colors_count):
            radius = 200 - arc * 25
            for t in range(0, 180, 5):
                angle = math.radians(t)
                x = cx + radius * math.cos(angle)
                y = cy + 100 + radius * math.sin(angle)
                points.append((x, y))
    
    return points

# --- Classe de Desenho ---
class DrawingCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.fill(BG_COLOR)
        self.history = []
        self.current_stroke = []
        self.template_surface = None
    
    def add_point(self, x, y, color, size):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.current_stroke.append((x, y, color, size))
            pygame.draw.circle(self.surface, color, (int(x), int(y)), size)
    
    def end_stroke(self):
        if self.current_stroke:
            self.history.append(self.current_stroke.copy())
            self.current_stroke = []
    
    def undo(self):
        if self.history:
            self.history.pop()
            self.redraw()
    
    def clear(self):
        self.history = []
        self.current_stroke = []
        self.surface.fill(BG_COLOR)
    
    def redraw(self):
        self.surface.fill(BG_COLOR)
        for stroke in self.history:
            for i, (x, y, color, size) in enumerate(stroke):
                pygame.draw.circle(self.surface, color, (int(x), int(y)), size)
                if i > 0:
                    prev_x, prev_y, prev_color, prev_size = stroke[i-1]
                    pygame.draw.line(self.surface, color, (prev_x, prev_y), (x, y), size * 2)
    
    def set_template(self, template_type):
        """Define um template para guiar o desenho"""
        self.template_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.template_surface.fill((0, 0, 0, 0))
        
        points = generate_template_points(template_type, self.width, self.height)
        
        if len(points) > 1:
            # Desenha o contorno do template
            for i in range(len(points) - 1):
                pygame.draw.line(self.template_surface, (150, 150, 150, 100), 
                               (int(points[i][0]), int(points[i][1])),
                               (int(points[i+1][0]), int(points[i+1][1])), 3)
            # Desenha pontos
            for point in points:
                pygame.draw.circle(self.template_surface, (100, 200, 255, 120), 
                                 (int(point[0]), int(point[1])), 5)
    
    def clear_template(self):
        """Remove o template"""
        self.template_surface = None
    
    def save_image(self):
        filename = f"pintura_{int(time.time())}.png"
        pygame.image.save(self.surface, filename)
        return filename

class Tool:
    """Classe para ferramentas de desenho"""
    def __init__(self, name, icon, tool_type):
        self.name = name
        self.icon = icon
        self.type = tool_type  # "brush" ou "eraser"
        self.selected = False

class ColorButton:
    def __init__(self, x, y, color, name, size=40):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.size = size
        self.selected = False
        self.hover = False
    
    def draw(self, surface):
        # Glow animado se selecionado
        if self.selected:
            pulse = 1.0 + 0.1 * math.sin(time.time() * 5)
            glow_size = int((self.size // 2 + 12) * pulse)
            glow_surf = pygame.Surface((glow_size * 2 + 10, glow_size * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, 80), 
                             (glow_size + 5, glow_size + 5), glow_size)
            surface.blit(glow_surf, (self.x + self.size // 2 - glow_size - 5, 
                                     self.y + self.size // 2 - glow_size - 5))
        
        # Botão
        pygame.draw.circle(surface, self.color, 
                          (self.x + self.size // 2, self.y + self.size // 2), 
                          self.size // 2)
        
        # Borda
        border_color = UI_ACCENT if self.selected else (180, 180, 180)
        border_width = 3 if self.selected else 2
        pygame.draw.circle(surface, border_color, 
                          (self.x + self.size // 2, self.y + self.size // 2), 
                          self.size // 2, border_width)
        
        # Nome (tooltip)
        if self.hover or self.selected:
            text = font_mini.render(self.name, True, TEXT_PRIMARY)
            text_rect = text.get_rect(center=(self.x + self.size // 2, self.y + self.size + 18))
            
            # Fundo do tooltip
            bg_rect = text_rect.inflate(12, 6)
            s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(s, (30, 30, 40, 220), (0, 0, bg_rect.width, bg_rect.height), 
                           border_radius=8)
            surface.blit(s, bg_rect)
            surface.blit(text, text_rect)
    
    def is_clicked(self, pos):
        dx = pos[0] - (self.x + self.size // 2)
        dy = pos[1] - (self.y + self.size // 2)
        return dx * dx + dy * dy <= (self.size // 2) ** 2
    
    def check_hover(self, pos):
        dx = pos[0] - (self.x + self.size // 2)
        dy = pos[1] - (self.y + self.size // 2)
        self.hover = dx * dx + dy * dy <= (self.size // 2) ** 2

class Button:
    """Botão retangular moderno"""
    def __init__(self, x, y, width, height, text, icon=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.hover = False
        self.active = False
    
    def draw(self, surface, selected=False):
        # Cor de fundo
        if selected:
            bg_color = UI_SUCCESS
        elif self.hover:
            bg_color = (70, 70, 90)
        else:
            bg_color = UI_BG
        
        # Botão
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*bg_color, 240), (0, 0, self.rect.width, self.rect.height), 
                        border_radius=12)
        surface.blit(s, self.rect)
        
        # Borda
        border_color = UI_ACCENT if selected else (100, 100, 120)
        border_width = 3 if selected else 2
        pygame.draw.rect(surface, border_color, self.rect, border_width, border_radius=12)
        
        # Texto e ícone
        full_text = f"{self.icon} {self.text}" if self.icon else self.text
        text_surf = font_small.render(full_text, True, TEXT_PRIMARY)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

# --- Detecção de Gestos ---
def detect_drawing_gesture(hand_landmarks):
    """Detecta se está desenhando (indicador levantado)"""
    if not hand_landmarks:
        return False, None
    
    # Pontos dos dedos
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    index_pip = hand_landmarks.landmark[6]
    
    # Indicador levantado
    index_up = index_tip.y < index_pip.y
    
    # Outros dedos baixos (simplificado)
    middle_down = middle_tip.y > index_pip.y
    
    # Posição do indicador
    pos_x = index_tip.x
    pos_y = index_tip.y
    
    # Está desenhando: indicador levantado, outros baixos
    is_drawing = index_up and middle_down
    
    return is_drawing, (pos_x, pos_y)

# --- Funções UI ---
def draw_text(surface, text, font, color, x, y, center=True):
    text_obj = font.render(text, True, color)
    if center:
        rect = text_obj.get_rect(center=(x, y))
    else:
        rect = (x, y)
    surface.blit(text_obj, rect)

def draw_ui_panel(surface, x, y, width, height, title=""):
    # Painel
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(s, (*UI_BG, 230), (0, 0, width, height), border_radius=15)
    surface.blit(s, (x, y))
    pygame.draw.rect(surface, UI_ACCENT, (x, y, width, height), 3, border_radius=15)
    
    # Título
    if title:
        draw_text(surface, title, font_small, UI_ACCENT, x + width // 2, y + 25)

# --- Telas ---
def main_menu():
    """Menu principal com opções de modo - UI/UX INCRÍVEL"""
    particles = []
    stars = []
    
    class MenuParticle:
        def __init__(self):
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.size = random.randint(3, 12)
            self.color = random.choice(list(COLORS.values()))
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-2, 2)
            self.alpha = random.randint(120, 255)
            self.pulse_speed = random.uniform(2, 5)
            self.pulse_offset = random.uniform(0, math.pi * 2)
        
        def update(self):
            self.x += self.vx
            self.y += self.vy
            if self.x < 0 or self.x > SCREEN_WIDTH:
                self.vx *= -1
                self.x = max(0, min(SCREEN_WIDTH, self.x))
            if self.y < 0 or self.y > SCREEN_HEIGHT:
                self.vy *= -1
                self.y = max(0, min(SCREEN_HEIGHT, self.y))
        
        def draw(self, surf, time_val):
            pulse = 1.0 + 0.3 * math.sin(time_val * self.pulse_speed + self.pulse_offset)
            current_size = int(self.size * pulse)
            current_alpha = min(255, int(self.alpha * pulse))  # Limita a 255
            
            s = pygame.Surface((current_size * 3, current_size * 3), pygame.SRCALPHA)
            # Glow externo
            pygame.draw.circle(s, (*self.color, max(0, current_alpha // 3)), 
                             (current_size * 1.5, current_size * 1.5), current_size * 1.5)
            # Partícula principal
            pygame.draw.circle(s, (*self.color, current_alpha), 
                             (current_size * 1.5, current_size * 1.5), current_size)
            surf.blit(s, (int(self.x) - current_size * 1.5, int(self.y) - current_size * 1.5))
    
    class Star:
        def __init__(self):
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.size = random.randint(1, 3)
            self.brightness = random.randint(100, 255)
            self.twinkle_speed = random.uniform(1, 3)
            self.twinkle_offset = random.uniform(0, math.pi * 2)
        
        def draw(self, surf, time_val):
            twinkle = 0.5 + 0.5 * math.sin(time_val * self.twinkle_speed + self.twinkle_offset)
            alpha = int(self.brightness * twinkle)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (self.size, self.size), self.size)
            surf.blit(s, (int(self.x) - self.size, int(self.y) - self.size))
    
    # Cria estrelas de fundo
    for _ in range(150):
        stars.append(Star())
    
    # Cria partículas coloridas
    for _ in range(100):
        particles.append(MenuParticle())
    
    # Botões de modo
    free_button = Button(SCREEN_WIDTH // 2 - 250, 400, 200, 90, "Livre [L]", "✏️")
    templates_button = Button(SCREEN_WIDTH // 2 + 50, 400, 200, 90, "Templates [T]", "🎨")
    
    buttons = [free_button, templates_button]
    
    # Efeitos de UI
    start_time = time.time()
    
    while True:
        current_time = time.time()
        time_elapsed = current_time - start_time
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_l:
                    return "free"
                elif event.key == pygame.K_t:
                    return "templates"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if free_button.is_clicked(mouse_pos):
                    return "free"
                if templates_button.is_clicked(mouse_pos):
                    return "templates"
        
        # Update hover
        for btn in buttons:
            btn.check_hover(mouse_pos)
        
        # === FUNDO PRETO COM GRADIENTE ===
        screen.fill((0, 0, 0))
        
        # Gradiente radial sutil do centro
        for i in range(5):
            alpha = 15 - i * 3
            radius = 600 + i * 100
            center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(s, (20, 20, 40, alpha), center, radius)
            screen.blit(s, (0, 0))
        
        # Estrelas cintilantes
        for star in stars:
            star.draw(screen, time_elapsed)
        
        # Partículas coloridas animadas
        for p in particles:
            p.update()
            p.draw(screen, time_elapsed)
        
        # === TÍTULO ESPETACULAR ===
        title_y = 80
        colors_list = list(COLORS.values())
        title_text = "🎨 PINTURA NO AR INCRÍVEL 🎨"
        offset_wave = time_elapsed * 2
        
        # Sombra do título
        for i, char in enumerate(title_text):
            color_idx = (i + int(offset_wave * 2)) % len(colors_list)
            wave_offset = int(15 * math.sin(i * 0.5 + offset_wave))
            char_surf = font_title.render(char, True, (0, 0, 0))
            char_x = SCREEN_WIDTH // 2 - len(title_text) * 18 + i * 36
            screen.blit(char_surf, (char_x + 3, title_y + wave_offset + 3))
        
        # Título com cores
        for i, char in enumerate(title_text):
            color_idx = (i + int(offset_wave * 2)) % len(colors_list)
            color = colors_list[color_idx]
            wave_offset = int(15 * math.sin(i * 0.5 + offset_wave))
            
            # Glow do caractere
            glow_surf = font_title.render(char, True, color)
            glow_surf.set_alpha(100)
            char_x = SCREEN_WIDTH // 2 - len(title_text) * 18 + i * 36
            screen.blit(glow_surf, (char_x - 2, title_y + wave_offset - 2))
            screen.blit(glow_surf, (char_x + 2, title_y + wave_offset + 2))
            
            # Caractere principal
            char_surf = font_title.render(char, True, color)
            screen.blit(char_surf, (char_x, title_y + wave_offset))
        
        # Subtítulo com glow
        subtitle_text = "Crie Arte Digital com suas Mãos!"
        glow_color = (100, 220, 255, 150)
        for offset in [(0, 0), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            s = pygame.Surface((700, 50), pygame.SRCALPHA)
            subtitle = font_small.render(subtitle_text, True, glow_color)
            s.blit(subtitle, (0, 0))
            screen.blit(s, (SCREEN_WIDTH // 2 - 350 + offset[0], 190 + offset[1]))
        draw_text(screen, subtitle_text, font_small, (255, 255, 255), 
                 SCREEN_WIDTH // 2, 200)
        
        # === CARD PRINCIPAL COM EFEITOS ===
        card_x = SCREEN_WIDTH // 2 - 450
        card_y = 260
        card_width = 900
        card_height = 480
        
        # Sombra do card
        shadow_surf = pygame.Surface((card_width + 20, card_height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, card_width + 20, card_height + 20), 
                        border_radius=20)
        screen.blit(shadow_surf, (card_x - 10, card_y - 10))
        
        # Card com gradiente
        card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        for i in range(card_height):
            alpha = 200 + int(30 * (i / card_height))
            color = (25 + i // 20, 25 + i // 20, 45 + i // 15, alpha)
            pygame.draw.line(card_surf, color, (0, i), (card_width, i))
        screen.blit(card_surf, (card_x, card_y))
        
        # Borda animada do card
        border_pulse = 1.0 + 0.2 * math.sin(time_elapsed * 3)
        border_color = tuple(min(255, int(c * border_pulse)) for c in UI_ACCENT)
        pygame.draw.rect(screen, border_color, (card_x, card_y, card_width, card_height), 
                        4, border_radius=20)
        
        # Título do card
        draw_text(screen, "✨ Escolha Seu Modo ✨", font_large, UI_ACCENT, 
                 SCREEN_WIDTH // 2, card_y + 50)
        
        # Linha decorativa
        line_y = card_y + 90
        for i in range(400):
            alpha = int(150 * (1 - abs(i - 200) / 200))
            color = (*UI_ACCENT, alpha)
            pygame.draw.circle(screen, color, (SCREEN_WIDTH // 2 - 200 + i, line_y), 2)
        
        # Botões com efeitos
        for btn in buttons:
            # Glow nos botões
            if btn.hover:
                glow_surf = pygame.Surface((btn.rect.width + 30, btn.rect.height + 30), pygame.SRCALPHA)
                pulse = 1.0 + 0.3 * math.sin(time_elapsed * 5)
                glow_alpha = int(80 * pulse)
                pygame.draw.rect(glow_surf, (*UI_ACCENT, glow_alpha), 
                               (0, 0, btn.rect.width + 30, btn.rect.height + 30), 
                               border_radius=15)
                screen.blit(glow_surf, (btn.rect.x - 15, btn.rect.y - 15))
            btn.draw(screen)
        
        # === FEATURES COM ÍCONES ===
        features_y = card_y + 200
        
        features_left = [
            ("✏️", "Desenho Livre", "Criatividade sem limites"),
            ("🎨", "12 Cores", "Paleta vibrante"),
            ("🖌️", "5 Tamanhos", "Do fino ao enorme"),
        ]
        
        features_right = [
            ("🖼️", "8 Templates", "Guias prontos"),
            ("🧹", "Borracha", "Correções fáceis"),
            ("💾", "Salvar PNG", "Suas obras salvas"),
        ]
        
        # Features da esquerda
        for i, (icon, title, desc) in enumerate(features_left):
            y = features_y + i * 70
            x = card_x + 100
            
            # Ícone
            icon_surf = font_large.render(icon, True, UI_ACCENT)
            screen.blit(icon_surf, (x, y))
            
            # Texto
            draw_text(screen, title, font_small, TEXT_PRIMARY, x + 80, y + 10, center=False)
            draw_text(screen, desc, font_mini, TEXT_SECONDARY, x + 80, y + 35, center=False)
        
        # Features da direita
        for i, (icon, title, desc) in enumerate(features_right):
            y = features_y + i * 70
            x = card_x + card_width // 2 + 50
            
            # Ícone
            icon_surf = font_large.render(icon, True, UI_SUCCESS)
            screen.blit(icon_surf, (x, y))
            
            # Texto
            draw_text(screen, title, font_small, TEXT_PRIMARY, x + 80, y + 10, center=False)
            draw_text(screen, desc, font_mini, TEXT_SECONDARY, x + 80, y + 35, center=False)
        
        # === FOOTER COM ATALHOS ===
        footer_y = SCREEN_HEIGHT - 80
        
        # Painel de atalhos
        shortcut_panel = pygame.Surface((700, 60), pygame.SRCALPHA)
        pygame.draw.rect(shortcut_panel, (20, 20, 40, 220), (0, 0, 700, 60), border_radius=15)
        pygame.draw.rect(shortcut_panel, UI_ACCENT, (0, 0, 700, 60), 3, border_radius=15)
        screen.blit(shortcut_panel, (SCREEN_WIDTH // 2 - 350, footer_y))
        
        # Atalhos
        draw_text(screen, "⌨️ ATALHOS RÁPIDOS", font_small, UI_ACCENT, 
                 SCREEN_WIDTH // 2, footer_y + 15)
        draw_text(screen, "[L] Livre  •  [T] Templates  •  [ESC] Sair", 
                 font_tiny, TEXT_PRIMARY, SCREEN_WIDTH // 2, footer_y + 40)
        
        pygame.display.flip()
        clock.tick(FPS)

def select_template_menu():
    """Menu de seleção de templates"""
    templates_list = list(TEMPLATES.items())
    buttons = []
    
    # Cria botões para cada template
    cols = 4
    button_width = 160
    button_height = 120
    spacing = 20
    start_x = SCREEN_WIDTH // 2 - (cols * (button_width + spacing)) // 2
    start_y = 250
    
    for i, (name, data) in enumerate(templates_list):
        row = i // cols
        col = i % cols
        x = start_x + col * (button_width + spacing)
        y = start_y + row * (button_height + spacing)
        btn = Button(x, y, button_width, button_height, name, data[1])
        btn.template_id = data[0]
        buttons.append(btn)
    
    # Botão de voltar
    back_button = Button(50, SCREEN_HEIGHT - 100, 150, 60, "Voltar", "←")
    free_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100, 150, 60, "Livre [L]", "✏️")
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_l:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(mouse_pos):
                    return "back"
                if free_button.is_clicked(mouse_pos):
                    return None
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        return btn.template_id
        
        # Update hover
        for btn in buttons + [back_button, free_button]:
            btn.check_hover(mouse_pos)
        
        screen.fill(BG_COLOR)
        
        # Gradiente de fundo
        for i in range(SCREEN_HEIGHT):
            alpha = int(100 * (i / SCREEN_HEIGHT))
            color = (240 + alpha // 10, 240 + alpha // 10, 255)
            pygame.draw.line(screen, color, (0, i), (SCREEN_WIDTH, i))
        
        # Título
        draw_text(screen, "🎨 Escolha um Template 🎨", font_title, UI_ACCENT, 
                 SCREEN_WIDTH // 2, 100)
        
        draw_text(screen, "Selecione um desenho para começar a pintar!", 
                 font_small, TEXT_SECONDARY, SCREEN_WIDTH // 2, 170)
        
        # Botões de templates
        for btn in buttons:
            btn.draw(screen)
        
        # Botões de navegação
        back_button.draw(screen)
        free_button.draw(screen)
        
        # Dica
        draw_text(screen, "💡 Pressione [L] para ir direto ao modo Livre!", 
                 font_tiny, UI_WARNING, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        
        pygame.display.flip()
        clock.tick(FPS)

def drawing_app(mode="free", template=None):
    """Aplicativo de desenho melhorado com ferramentas"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return
    
    # Canvas de desenho
    canvas_width = SCREEN_WIDTH - 280
    canvas_height = SCREEN_HEIGHT - 20
    canvas_x = 10
    canvas_y = 10
    canvas = DrawingCanvas(canvas_width, canvas_height)
    
    # Se tem template, define
    if template:
        canvas.set_template(template)
    
    # UI - Cores (mais compacto)
    color_buttons = []
    colors_list = list(COLORS.items())
    cols = 3
    start_y = 120
    for i, (name, color) in enumerate(colors_list):
        row = i // cols
        col = i % cols
        x = SCREEN_WIDTH - 250 + col * 50
        y = start_y + row * 55
        btn = ColorButton(x, y, color, name, size=38)
        color_buttons.append(btn)
    
    color_buttons[0].selected = True  # Vermelho selecionado
    current_color = color_buttons[0].color
    
    # Ferramentas: Pincel e Borracha
    current_tool = "brush"  # "brush" ou "eraser"
    
    # Tamanhos de pincel
    brush_sizes_list = list(BRUSH_SIZES.items())
    current_brush_idx = 2  # Médio
    current_brush_size = brush_sizes_list[current_brush_idx][1]
    
    # Botões de ferramenta
    tool_buttons = {
        "brush": Button(SCREEN_WIDTH - 250, 50, 110, 50, "Pincel", "✏️"),
        "eraser": Button(SCREEN_WIDTH - 130, 50, 110, 50, "Borracha", "🧹")
    }
    
    # Botões de ação
    clear_btn = Button(SCREEN_WIDTH - 250, canvas_height - 180, 230, 45, "Limpar Tudo", "🗑️")
    undo_btn = Button(SCREEN_WIDTH - 250, canvas_height - 125, 230, 45, "Desfazer", "↶")
    save_btn = Button(SCREEN_WIDTH - 250, canvas_height - 70, 230, 45, "Salvar", "💾")
    
    # Estado
    is_drawing_active = False
    last_pos = None
    cursor_trail = []
    show_save_message = False
    save_message_time = 0
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    canvas.clear()
                    if template:
                        canvas.set_template(template)
                elif event.key == pygame.K_u:
                    canvas.undo()
                elif event.key == pygame.K_s:
                    filename = canvas.save_image()
                    print(f"✅ Imagem salva: {filename}")
                    show_save_message = True
                    save_message_time = current_time
                elif event.key == pygame.K_UP:
                    current_brush_idx = min(len(brush_sizes_list) - 1, current_brush_idx + 1)
                    current_brush_size = brush_sizes_list[current_brush_idx][1]
                elif event.key == pygame.K_DOWN:
                    current_brush_idx = max(0, current_brush_idx - 1)
                    current_brush_size = brush_sizes_list[current_brush_idx][1]
                elif event.key == pygame.K_b:
                    current_tool = "brush"
                elif event.key == pygame.K_e:
                    current_tool = "eraser"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Verifica cliques nos botões
                if tool_buttons["brush"].is_clicked(mouse_pos):
                    current_tool = "brush"
                elif tool_buttons["eraser"].is_clicked(mouse_pos):
                    current_tool = "eraser"
                elif clear_btn.is_clicked(mouse_pos):
                    canvas.clear()
                    if template:
                        canvas.set_template(template)
                elif undo_btn.is_clicked(mouse_pos):
                    canvas.undo()
                elif save_btn.is_clicked(mouse_pos):
                    filename = canvas.save_image()
                    print(f"✅ Imagem salva: {filename}")
                    show_save_message = True
                    save_message_time = current_time
                
                # Verifica cliques em cores
                for btn in color_buttons:
                    if btn.is_clicked(mouse_pos):
                        for b in color_buttons:
                            b.selected = False
                        btn.selected = True
                        current_color = btn.color
                        current_tool = "brush"  # Muda para pincel ao selecionar cor
        
        # Update hover
        for btn in color_buttons:
            btn.check_hover(mouse_pos)
        for btn in tool_buttons.values():
            btn.check_hover(mouse_pos)
        for btn in [clear_btn, undo_btn, save_btn]:
            btn.check_hover(mouse_pos)
        
        # Captura frame
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Detecta gestos
        is_drawing, hand_pos = False, None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                is_drawing, hand_pos = detect_drawing_gesture(hand_landmarks)
                
                if hand_pos:
                    # Converte para coordenadas do canvas
                    canvas_pos_x = hand_pos[0] * canvas_width
                    canvas_pos_y = hand_pos[1] * canvas_height
                    
                    cursor_trail.append((canvas_pos_x, canvas_pos_y))
                    if len(cursor_trail) > 12:
                        cursor_trail.pop(0)
                    
                    if is_drawing:
                        # Decide cor baseado na ferramenta
                        draw_color = BG_COLOR if current_tool == "eraser" else current_color
                        draw_size = current_brush_size * 2 if current_tool == "eraser" else current_brush_size
                        
                        if last_pos:
                            # Desenha linha entre pontos para suavidade
                            steps = 5
                            for step in range(steps):
                                t = step / steps
                                x = last_pos[0] + (canvas_pos_x - last_pos[0]) * t
                                y = last_pos[1] + (canvas_pos_y - last_pos[1]) * t
                                canvas.add_point(x, y, draw_color, draw_size)
                        else:
                            canvas.add_point(canvas_pos_x, canvas_pos_y, draw_color, draw_size)
                        last_pos = (canvas_pos_x, canvas_pos_y)
                        is_drawing_active = True
                    else:
                        if last_pos and is_drawing_active:
                            canvas.end_stroke()
                            is_drawing_active = False
                        last_pos = None
                else:
                    if last_pos and is_drawing_active:
                        canvas.end_stroke()
                        is_drawing_active = False
                    last_pos = None
                    cursor_trail = []
        else:
            if last_pos and is_drawing_active:
                canvas.end_stroke()
                is_drawing_active = False
            last_pos = None
            cursor_trail = []
        
        # --- Renderização ---
        screen.fill((35, 35, 50))
        
        # Canvas com template
        screen.blit(canvas.surface, (canvas_x, canvas_y))
        
        # Desenha template por cima se existir
        if canvas.template_surface:
            screen.blit(canvas.template_surface, (canvas_x, canvas_y))
        
        # Borda do canvas
        pygame.draw.rect(screen, UI_ACCENT, (canvas_x, canvas_y, canvas_width, canvas_height), 4)
        
        # Cursor virtual com trail
        if cursor_trail:
            for i, (cx, cy) in enumerate(cursor_trail):
                alpha = int(255 * (i / len(cursor_trail)))
                size = int(current_brush_size * (0.5 + 0.5 * i / len(cursor_trail)))
                if current_tool == "eraser":
                    size = int(size * 1.5)
                s = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
                
                if is_drawing:
                    cursor_color = (255, 100, 100) if current_tool == "eraser" else current_color
                    pygame.draw.circle(s, (*cursor_color, alpha), (size + 2, size + 2), size)
                else:
                    pygame.draw.circle(s, (255, 255, 255, alpha), (size + 2, size + 2), size)
                screen.blit(s, (canvas_x + cx - size - 2, canvas_y + cy - size - 2))
            
            # Cursor principal
            cx, cy = cursor_trail[-1]
            display_size = current_brush_size * 2 if current_tool == "eraser" else current_brush_size
            cursor_color = (255, 80, 80) if current_tool == "eraser" else current_color if is_drawing else (255, 255, 255)
            
            pygame.draw.circle(screen, cursor_color, 
                             (int(canvas_x + cx), int(canvas_y + cy)), 
                             display_size + 3)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(canvas_x + cx), int(canvas_y + cy)), 
                             display_size + 3, 2)
        
        # Painel lateral
        panel_x = SCREEN_WIDTH - 260
        
        # Botões de ferramentas
        for tool_name, btn in tool_buttons.items():
            btn.draw(screen, selected=(tool_name == current_tool))
        
        # Seção de cores
        draw_text(screen, "🎨 Cores", font_small, UI_ACCENT, panel_x + 125, 95)
        for btn in color_buttons:
            btn.draw(screen)
        
        # Tamanho do pincel
        brush_panel_y = 390
        draw_ui_panel(screen, panel_x, brush_panel_y, 250, 130, "TAMANHO")
        
        brush_name, brush_size = brush_sizes_list[current_brush_idx]
        draw_text(screen, brush_name, font_small, TEXT_PRIMARY, panel_x + 125, brush_panel_y + 55)
        
        # Preview do pincel/borracha
        preview_color = (220, 220, 220) if current_tool == "eraser" else current_color
        preview_size = brush_size * 2 if current_tool == "eraser" else brush_size
        pygame.draw.circle(screen, preview_color, (panel_x + 125, brush_panel_y + 95), 
                         min(preview_size, 35))
        pygame.draw.circle(screen, TEXT_PRIMARY, (panel_x + 125, brush_panel_y + 95), 
                         min(preview_size, 35), 2)
        
        # Dica de tamanho
        draw_text(screen, "↑↓ Alterar", font_mini, TEXT_SECONDARY, 
                 panel_x + 125, brush_panel_y + 115)
        
        # Botões de ação
        clear_btn.draw(screen)
        undo_btn.draw(screen)
        save_btn.draw(screen)
        
        # Mensagem de salvamento
        if show_save_message and current_time - save_message_time < 2:
            msg_surf = pygame.Surface((300, 70), pygame.SRCALPHA)
            pygame.draw.rect(msg_surf, (50, 200, 100, 230), (0, 0, 300, 70), border_radius=15)
            msg_surf.blit(font_small.render("✅ Salvo!", True, TEXT_PRIMARY), (100, 20))
            screen.blit(msg_surf, (SCREEN_WIDTH // 2 - 150, 20))
        
        # Webcam
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 20
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 15
        screen.blit(frame_surface, (webcam_x, webcam_y))
        
        # Borda da webcam com estado
        border_color = UI_SUCCESS if is_drawing else UI_ACCENT
        pygame.draw.rect(screen, border_color, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 4)
        
        # Status
        if is_drawing:
            status_icon = "🧹" if current_tool == "eraser" else "✏️"
            status_text = f"{status_icon} Desenhando"
            status_color = UI_WARNING if current_tool == "eraser" else UI_SUCCESS
        else:
            status_text = "👋 Levante o indicador"
            status_color = TEXT_SECONDARY
        
        status_bg = pygame.Surface((WEBCAM_WIDTH, 30), pygame.SRCALPHA)
        pygame.draw.rect(status_bg, (30, 30, 40, 200), (0, 0, WEBCAM_WIDTH, 30))
        screen.blit(status_bg, (webcam_x, webcam_y - 30))
        draw_text(screen, status_text, font_tiny, status_color, 
                 webcam_x + WEBCAM_WIDTH // 2, webcam_y - 15)
        
        # Atalhos de teclado
        shortcuts = ["B-Pincel", "E-Borracha", "C-Limpar", "U-Desfazer", "S-Salvar"]
        shortcut_y = 15
        for shortcut in shortcuts:
            draw_text(screen, shortcut, font_mini, TEXT_SECONDARY, 80, shortcut_y, center=False)
            shortcut_y += 22
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()

# --- Main ---
if __name__ == "__main__":
    try:
        while True:
            # Menu principal
            mode = main_menu()
            
            if mode is None:  # Sair
                break
            
            if mode == "free":
                # Modo desenho livre
                drawing_app(mode="free", template=None)
            
            elif mode == "templates":
                # Menu de templates
                while True:
                    template = select_template_menu()
                    
                    if template == "back":  # Volta pro menu principal
                        break
                    elif template is None:  # Modo livre
                        drawing_app(mode="free", template=None)
                    else:  # Template selecionado
                        drawing_app(mode="templates", template=template)
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
        sys.exit()

