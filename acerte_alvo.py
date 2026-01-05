"""
🎯 ACERTE O ALVO - Whack-a-Mole com Visão Computacional
Use suas mãos para acertar os alvos que aparecem na tela!

Controles: Movimente suas mãos para controlar os cursores
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
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
WEBCAM_WIDTH = 320
WEBCAM_HEIGHT = 240
FPS = 60

# Cores modernas
DARK_BG = (15, 15, 25)
CARD_BG = (30, 34, 42)
ACCENT_PURPLE = (156, 39, 176)
ACCENT_PINK = (233, 30, 99)
ACCENT_CYAN = (0, 188, 212)
ACCENT_ORANGE = (255, 152, 0)
ACCENT_GREEN = (76, 175, 80)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (160, 160, 180)

# Configurações do jogo
TARGET_LIFETIME = 2.0  # Segundos que o alvo fica visível
TARGET_SIZE = 80
CURSOR_SIZE = 30
HIT_DISTANCE = 60
GAME_DURATION = 60  # Segundos

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎯 Acerte o Alvo")
clock = pygame.time.Clock()

# Fontes
font_title = pygame.font.Font(None, 90)
font_large = pygame.font.Font(None, 70)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 40)
font_tiny = pygame.font.Font(None, 30)

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# --- Classes ---
class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawn_time = time.time()
        self.size = 0
        self.max_size = TARGET_SIZE
        self.alive = True
        self.hit = False
        self.color = random.choice([ACCENT_PURPLE, ACCENT_PINK, ACCENT_CYAN, ACCENT_ORANGE])
        self.points = random.randint(10, 50)
        self.pulse = 0
    
    def update(self):
        """Atualiza o alvo"""
        age = time.time() - self.spawn_time
        
        # Animação de crescimento
        if self.size < self.max_size:
            self.size = min(self.max_size, self.size + 5)
        
        # Pulso
        self.pulse = abs(math.sin(time.time() * 5)) * 10
        
        # Verifica se expirou
        if age >= TARGET_LIFETIME and not self.hit:
            self.alive = False
        
        return self.alive
    
    def draw(self, surface):
        """Desenha o alvo"""
        if self.hit:
            # Animação de explosão
            size = int(self.size * 1.5)
            alpha_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*self.color, 100), (size, size), size)
            surface.blit(alpha_surface, (self.x - size, self.y - size))
            return
        
        # Círculo pulsante
        pulse_size = int(self.size + self.pulse)
        
        # Anel externo
        pygame.draw.circle(surface, (*self.color, 50), (self.x, self.y), pulse_size, 3)
        
        # Círculo principal
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)
        
        # Círculo interno
        pygame.draw.circle(surface, TEXT_PRIMARY, (self.x, self.y), self.size - 10, 3)
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size - 20)
        
        # Centro
        pygame.draw.circle(surface, TEXT_PRIMARY, (self.x, self.y), 8)
        
        # Pontos
        points_text = font_small.render(str(self.points), True, TEXT_PRIMARY)
        points_rect = points_text.get_rect(center=(self.x, self.y - self.size - 25))
        surface.blit(points_text, points_rect)
    
    def check_hit(self, cursor_x, cursor_y):
        """Verifica se o cursor acertou o alvo"""
        distance = math.sqrt((self.x - cursor_x)**2 + (self.y - cursor_y)**2)
        if distance <= HIT_DISTANCE and not self.hit:
            self.hit = True
            return self.points
        return 0

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.life = 1.0
        self.color = color
        self.size = random.randint(3, 8)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Gravidade
        self.life -= 0.02
        return self.life > 0
    
    def draw(self, surface):
        alpha = int(self.life * 255)
        color_with_alpha = (*self.color, alpha)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x), int(self.y)))

# --- Funções de UI ---
def draw_rounded_rect(surface, color, rect, radius=20):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_text(surface, text, font, color, x, y, center=True):
    text_obj = font.render(text, True, (0, 0, 0))
    if center:
        rect = text_obj.get_rect(center=(x+3, y+3))
    else:
        rect = (x+3, y+3)
    surface.blit(text_obj, rect)
    
    text_obj = font.render(text, True, color)
    if center:
        rect = text_obj.get_rect(center=(x, y))
    else:
        rect = (x, y)
    surface.blit(text_obj, rect)

def draw_card(surface, x, y, width, height, color=CARD_BG):
    draw_rounded_rect(surface, color, (x, y, width, height), 20)
    pygame.draw.rect(surface, (50, 54, 62), (x, y, width, height), 3, border_radius=20)

def draw_cursor(surface, x, y, color=ACCENT_CYAN):
    """Desenha cursor da mão"""
    # Anel pulsante
    pulse = abs(math.sin(time.time() * 8)) * 8
    pygame.draw.circle(surface, (*color, 100), (x, y), int(CURSOR_SIZE + pulse), 2)
    
    # Círculo principal
    pygame.draw.circle(surface, color, (x, y), CURSOR_SIZE)
    pygame.draw.circle(surface, TEXT_PRIMARY, (x, y), CURSOR_SIZE - 5, 3)
    pygame.draw.circle(surface, color, (x, y), CURSOR_SIZE - 10)
    
    # Centro brilhante
    pygame.draw.circle(surface, TEXT_PRIMARY, (x, y), 5)

# --- Telas ---
def main_menu():
    """Menu principal"""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill(DARK_BG)
        
        # Título animado
        title_y = 120 + int(15 * np.sin(time.time() * 2))
        draw_text(screen, "🎯 ACERTE O ALVO 🎯", font_title, ACCENT_ORANGE, 
                  SCREEN_WIDTH//2, title_y)
        
        # Card de instruções
        card_x = SCREEN_WIDTH//2 - 450
        card_y = 280
        draw_card(screen, card_x, card_y, 900, 450)
        
        instructions = [
            "Como Jogar:",
            "",
            "👋 Movimente suas mãos para controlar os cursores",
            "🎯 Acerte os alvos que aparecem na tela",
            "⭐ Alvos maiores valem mais pontos!",
            "⏱️  Você tem 60 segundos",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 50
        for i, text in enumerate(instructions):
            color = TEXT_PRIMARY if i == 0 or i == 7 else TEXT_SECONDARY
            font = font_medium if i == 0 or i == 7 else font_small
            draw_text(screen, text, font, color, SCREEN_WIDTH//2, y_offset, True)
            y_offset += 60 if i == 0 or i == 6 else 50
        
        # Animação de alvos no fundo
        for i in range(5):
            x = 100 + i * 250 + int(20 * np.sin(time.time() * 2 + i))
            y = 800 + int(10 * np.cos(time.time() * 3 + i))
            color = [ACCENT_PURPLE, ACCENT_PINK, ACCENT_CYAN, ACCENT_ORANGE, ACCENT_GREEN][i]
            pygame.draw.circle(screen, (*color, 100), (x, y), 30)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    """Loop principal do jogo"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return
    
    # Estado do jogo
    score = 0
    combo = 0
    max_combo = 0
    targets = []
    particles = []
    cursors = []
    
    game_start_time = time.time()
    last_spawn_time = 0
    spawn_interval = 1.0
    
    running = True
    while running:
        current_time = time.time()
        time_left = max(0, GAME_DURATION - (current_time - game_start_time))
        
        if time_left <= 0:
            running = False
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Captura frame
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Detecta mãos
        cursors = []
        if results.multi_hand_landmarks:
            h, w = frame.shape[:2]
            for hand_landmarks in results.multi_hand_landmarks:
                # Pega posição do dedo indicador
                index_finger = hand_landmarks.landmark[8]
                cursor_x = int(index_finger.x * SCREEN_WIDTH)
                cursor_y = int(index_finger.y * SCREEN_HEIGHT)
                cursors.append((cursor_x, cursor_y))
        
        # Spawna novos alvos
        if current_time - last_spawn_time >= spawn_interval:
            margin = 100
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = random.randint(200, SCREEN_HEIGHT - margin)
            targets.append(Target(x, y))
            last_spawn_time = current_time
            
            # Aumenta dificuldade
            if len(targets) > 5:
                spawn_interval = max(0.5, spawn_interval - 0.05)
        
        # Atualiza alvos
        targets = [t for t in targets if t.update()]
        
        # Verifica colisões
        hit_this_frame = False
        for cursor_x, cursor_y in cursors:
            for target in targets:
                points = target.check_hit(cursor_x, cursor_y)
                if points > 0:
                    score += points * (1 + combo * 0.1)
                    combo += 1
                    max_combo = max(max_combo, combo)
                    hit_this_frame = True
                    
                    # Cria partículas
                    for _ in range(15):
                        particles.append(Particle(target.x, target.y, target.color))
        
        if not hit_this_frame:
            combo = 0
        
        # Remove alvos acertados
        targets = [t for t in targets if not t.hit or (time.time() - t.spawn_time < 0.3)]
        
        # Atualiza partículas
        particles = [p for p in particles if p.update()]
        
        # --- Renderização ---
        screen.fill(DARK_BG)
        
        # Grade decorativa
        for i in range(0, SCREEN_WIDTH, 100):
            pygame.draw.line(screen, (30, 34, 42), (i, 0), (i, SCREEN_HEIGHT), 1)
        for i in range(0, SCREEN_HEIGHT, 100):
            pygame.draw.line(screen, (30, 34, 42), (0, i), (SCREEN_WIDTH, i), 1)
        
        # HUD superior
        hud_height = 120
        draw_card(screen, 20, 20, SCREEN_WIDTH - 40, hud_height, (25, 29, 37))
        
        # Pontuação
        draw_text(screen, f"PONTOS: {int(score)}", font_large, ACCENT_CYAN, 200, 80)
        
        # Combo
        if combo > 0:
            combo_color = ACCENT_ORANGE if combo < 5 else ACCENT_PINK
            draw_text(screen, f"COMBO x{combo}! 🔥", font_medium, combo_color, 600, 80)
        
        # Tempo
        time_color = ACCENT_GREEN if time_left > 20 else (ACCENT_ORANGE if time_left > 10 else ACCENT_PINK)
        draw_text(screen, f"⏱️  {int(time_left)}s", font_large, time_color, SCREEN_WIDTH - 200, 80)
        
        # Desenha partículas (atrás)
        for particle in particles:
            particle.draw(screen)
        
        # Desenha alvos
        for target in targets:
            target.draw(screen)
        
        # Desenha cursores
        colors = [ACCENT_CYAN, ACCENT_PINK]
        for i, (cx, cy) in enumerate(cursors):
            draw_cursor(screen, cx, cy, colors[i % 2])
        
        # Webcam (pequena)
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        pygame.draw.rect(screen, ACCENT_PURPLE, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 3)
        
        # Instruções
        if current_time - game_start_time < 5:
            draw_text(screen, "👋 Movimente suas mãos!", font_medium, TEXT_SECONDARY, 
                      SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Tela de resultado
    return show_results(int(score), max_combo)

def show_results(score, max_combo):
    """Mostra resultados finais"""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill(DARK_BG)
        
        # Card de resultados
        card_x = SCREEN_WIDTH//2 - 450
        card_y = 150
        draw_card(screen, card_x, card_y, 900, 600)
        
        # Título
        draw_text(screen, "🎉 JOGO FINALIZADO! 🎉", font_title, ACCENT_ORANGE, 
                  SCREEN_WIDTH//2, card_y + 80)
        
        # Pontuação
        draw_text(screen, "PONTUAÇÃO FINAL", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH//2, card_y + 200)
        draw_text(screen, str(score), font_title, ACCENT_CYAN, 
                  SCREEN_WIDTH//2, card_y + 280)
        
        # Combo máximo
        draw_text(screen, f"Combo Máximo: {max_combo}x", font_medium, ACCENT_PINK, 
                  SCREEN_WIDTH//2, card_y + 380)
        
        # Avaliação
        if score >= 1000:
            rating = "🏆 INCRÍVEL! 🏆"
            rating_color = ACCENT_ORANGE
        elif score >= 500:
            rating = "⭐ EXCELENTE! ⭐"
            rating_color = ACCENT_CYAN
        elif score >= 250:
            rating = "👍 BOM! 👍"
            rating_color = ACCENT_GREEN
        else:
            rating = "💪 CONTINUE PRATICANDO!"
            rating_color = TEXT_SECONDARY
        
        draw_text(screen, rating, font_large, rating_color, 
                  SCREEN_WIDTH//2, card_y + 470)
        
        # Instruções
        draw_text(screen, "ESPAÇO para jogar novamente  |  ESC para sair", 
                  font_small, TEXT_SECONDARY, SCREEN_WIDTH//2, card_y + 580)
        
        pygame.display.flip()
        clock.tick(FPS)

# --- Main ---
if __name__ == "__main__":
    try:
        while True:
            if main_menu():
                if not game_loop():
                    break
            else:
                break
    finally:
        pygame.quit()
        sys.exit()

