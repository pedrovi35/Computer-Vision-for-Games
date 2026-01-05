"""
🧱 QUEBRA BLOCOS - Breakout com Visão Computacional
Use suas mãos para controlar a plataforma e destruir todos os blocos!

Controles: Movimente suas mãos horizontalmente
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

# Cores vibrantes estilo neon
DARK_BG = (10, 10, 20)
NEON_PINK = (255, 20, 147)
NEON_CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (191, 64, 191)
NEON_ORANGE = (255, 140, 0)
NEON_YELLOW = (255, 255, 0)
NEON_BLUE = (30, 144, 255)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (160, 160, 200)

# Configurações do jogo
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 20
BALL_RADIUS = 12
BALL_SPEED = 8
BLOCK_ROWS = 6
BLOCK_COLS = 14
BLOCK_WIDTH = 90
BLOCK_HEIGHT = 30
POWERUP_CHANCE = 0.15

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🧱 Quebra Blocos - Controle por Mãos")
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
class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 15
        self.trail = []
        self.glow_intensity = 0
    
    def update(self, target_x):
        # Suaviza movimento
        diff = target_x - self.x
        self.x += diff * 0.3
        
        # Limites
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        
        # Trail
        self.trail.append(int(self.x + self.width // 2))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Glow pulsante
        self.glow_intensity = abs(math.sin(time.time() * 3)) * 20
    
    def draw(self, surface):
        # Trail
        for i, tx in enumerate(self.trail[:-1]):
            alpha = int(255 * (i / len(self.trail)))
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*NEON_CYAN, alpha), (0, 0, self.width, self.height), border_radius=10)
            surface.blit(s, (tx - self.width // 2, self.y))
        
        # Glow
        glow_surf = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*NEON_CYAN, int(50 + self.glow_intensity)), 
                        (20, 20, self.width, self.height), border_radius=10)
        surface.blit(glow_surf, (self.x - 20, self.y - 20))
        
        # Corpo principal
        pygame.draw.rect(surface, NEON_CYAN, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(surface, TEXT_PRIMARY, (self.x, self.y, self.width, self.height), 3, border_radius=10)
        
        # Detalhe central
        center_x = self.x + self.width // 2
        pygame.draw.circle(surface, TEXT_PRIMARY, (center_x, self.y + self.height // 2), 5)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.choice([-1, 1]) * BALL_SPEED * 0.7
        self.vy = -BALL_SPEED
        self.radius = BALL_RADIUS
        self.trail = []
        self.color = NEON_PINK
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 15:
            self.trail.pop(0)
        
        # Colisão com paredes
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.vx *= -1
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        
        if self.y - self.radius <= 150:  # Topo (abaixo do HUD)
            self.vy *= -1
            self.y = 150 + self.radius
    
    def draw(self, surface):
        # Trail com gradiente
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = int(self.radius * (0.3 + 0.7 * i / len(self.trail)))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (tx - size, ty - size))
        
        # Glow
        for i in range(3):
            size = self.radius + (3 - i) * 8
            alpha = 30 + int(20 * abs(math.sin(time.time() * 4)))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (self.x - size, self.y - size))
        
        # Corpo
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, TEXT_PRIMARY, (int(self.x), int(self.y)), self.radius - 3)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius - 6)
        
        # Brilho central
        pygame.draw.circle(surface, TEXT_PRIMARY, (int(self.x - 3), int(self.y - 3)), 3)
    
    def check_paddle_collision(self, paddle):
        if (self.y + self.radius >= paddle.y and 
            self.y + self.radius <= paddle.y + paddle.height and
            self.x >= paddle.x and self.x <= paddle.x + paddle.width):
            
            # Ângulo baseado em onde acertou a plataforma
            hit_pos = (self.x - paddle.x) / paddle.width
            angle = (hit_pos - 0.5) * 2  # -1 a 1
            
            self.vy = -abs(self.vy)
            self.vx = angle * BALL_SPEED
            
            # Garante velocidade mínima
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed < BALL_SPEED * 0.8:
                factor = BALL_SPEED * 0.8 / speed
                self.vx *= factor
                self.vy *= factor
            
            return True
        return False

class Block:
    def __init__(self, x, y, color, row):
        self.x = x
        self.y = y
        self.width = BLOCK_WIDTH
        self.height = BLOCK_HEIGHT
        self.color = color
        self.hp = row + 1  # Mais HP nas fileiras superiores
        self.max_hp = self.hp
        self.pulse = 0
        self.hit_animation = 0
    
    def hit(self):
        self.hp -= 1
        self.hit_animation = 1.0
        return self.hp <= 0
    
    def update(self):
        self.pulse = abs(math.sin(time.time() * 2 + self.x * 0.01)) * 10
        if self.hit_animation > 0:
            self.hit_animation -= 0.05
    
    def draw(self, surface):
        if self.hit_animation > 0:
            # Animação de acerto
            scale = 1 + self.hit_animation * 0.2
            offset = (self.width * (scale - 1)) / 2
            
            s = pygame.Surface((int(self.width * scale), int(self.height * scale)), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, int(255 * (1 - self.hit_animation))), 
                           (0, 0, int(self.width * scale), int(self.height * scale)), border_radius=8)
            surface.blit(s, (self.x - offset, self.y - offset))
        
        # Glow pulsante
        pulse_size = int(self.pulse)
        if pulse_size > 0:
            s = pygame.Surface((self.width + pulse_size * 2, self.height + pulse_size * 2), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, 40), 
                           (0, 0, self.width + pulse_size * 2, self.height + pulse_size * 2), border_radius=8)
            surface.blit(s, (self.x - pulse_size, self.y - pulse_size))
        
        # Corpo do bloco
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=8)
        
        # Barra de HP
        if self.hp < self.max_hp:
            hp_width = (self.width - 10) * (self.hp / self.max_hp)
            pygame.draw.rect(surface, (50, 50, 50), (self.x + 5, self.y + 5, self.width - 10, 5), border_radius=2)
            pygame.draw.rect(surface, TEXT_PRIMARY, (self.x + 5, self.y + 5, int(hp_width), 5), border_radius=2)
        
        # Borda brilhante
        pygame.draw.rect(surface, TEXT_PRIMARY, (self.x, self.y, self.width, self.height), 2, border_radius=8)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
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
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

# --- Funções UI ---
def draw_rounded_rect(surface, color, rect, radius=15):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_text(surface, text, font, color, x, y, center=True, shadow=True):
    if shadow:
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

def draw_card(surface, x, y, width, height, color=(20, 20, 40)):
    draw_rounded_rect(surface, color, (x, y, width, height), 20)
    pygame.draw.rect(surface, NEON_CYAN, (x, y, width, height), 2, border_radius=20)

# --- Telas ---
def main_menu():
    particles = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # Adiciona partículas de fundo
        if random.random() < 0.1:
            particles.append(Particle(random.randint(0, SCREEN_WIDTH), 
                                    random.randint(0, SCREEN_HEIGHT),
                                    random.choice([NEON_CYAN, NEON_PINK, NEON_PURPLE])))
        
        particles = [p for p in particles if p.update()]
        
        screen.fill(DARK_BG)
        
        # Partículas
        for p in particles:
            p.draw(screen)
        
        # Título animado
        title_y = 150 + int(20 * np.sin(time.time() * 2))
        draw_text(screen, "🧱 QUEBRA BLOCOS 🧱", font_title, NEON_CYAN, 
                  SCREEN_WIDTH//2, title_y)
        
        # Efeito neon no título
        title_surface = pygame.Surface((SCREEN_WIDTH, 150), pygame.SRCALPHA)
        glow = int(50 + 30 * abs(math.sin(time.time() * 3)))
        pygame.draw.rect(title_surface, (*NEON_CYAN, glow), 
                        (SCREEN_WIDTH//2 - 400, 0, 800, 100), border_radius=50)
        screen.blit(title_surface, (0, title_y - 50))
        
        # Card de instruções
        card_x = SCREEN_WIDTH//2 - 500
        card_y = 320
        draw_card(screen, card_x, card_y, 1000, 400)
        
        instructions = [
            "Como Jogar:",
            "",
            "👋 Movimente suas mãos HORIZONTALMENTE",
            "🎯 Controle a plataforma com precisão",
            "🧱 Destrua todos os blocos!",
            "💎 Blocos superiores têm mais HP",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 40
        for i, text in enumerate(instructions):
            color = NEON_CYAN if i == 0 or i == 7 else TEXT_SECONDARY
            font = font_medium if i == 0 or i == 7 else font_small
            draw_text(screen, text, font, color, SCREEN_WIDTH//2, y_offset, True)
            y_offset += 55 if i == 0 or i == 6 else 48
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return 0
    
    # Inicialização
    paddle = Paddle()
    balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200)]
    blocks = []
    particles = []
    
    # Cria blocos
    colors = [NEON_PINK, NEON_PURPLE, NEON_BLUE, NEON_GREEN, NEON_YELLOW, NEON_ORANGE]
    start_x = (SCREEN_WIDTH - BLOCK_COLS * BLOCK_WIDTH) // 2
    start_y = 180
    
    for row in range(BLOCK_ROWS):
        for col in range(BLOCK_COLS):
            x = start_x + col * BLOCK_WIDTH
            y = start_y + row * BLOCK_HEIGHT
            blocks.append(Block(x, y, colors[row], row))
    
    # Estado do jogo
    score = 0
    lives = 3
    combo = 0
    max_combo = 0
    game_start_time = time.time()
    hand_positions = []
    
    running = True
    while running and lives > 0 and len(blocks) > 0:
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
        target_x = paddle.x + paddle.width // 2
        if results.multi_hand_landmarks:
            positions = []
            for hand_landmarks in results.multi_hand_landmarks:
                # Pega posição da palma
                wrist = hand_landmarks.landmark[0]
                hand_x = int(wrist.x * SCREEN_WIDTH)
                positions.append(hand_x)
            
            # Usa média das posições
            target_x = sum(positions) / len(positions)
        
        # Atualiza jogo
        paddle.update(target_x)
        
        for ball in balls:
            ball.update()
            
            # Colisão com paddle
            if ball.check_paddle_collision(paddle):
                combo += 1
                max_combo = max(max_combo, combo)
            
            # Colisão com blocos
            for block in blocks[:]:
                if (ball.x + ball.radius > block.x and 
                    ball.x - ball.radius < block.x + block.width and
                    ball.y + ball.radius > block.y and 
                    ball.y - ball.radius < block.y + block.height):
                    
                    # Determina lado da colisão
                    if abs(ball.y - block.y) < abs(ball.y - (block.y + block.height)):
                        ball.vy *= -1
                    else:
                        ball.vx *= -1
                    
                    if block.hit():
                        blocks.remove(block)
                        points = (block.max_hp * 10) * (1 + combo * 0.1)
                        score += int(points)
                        combo += 1
                        max_combo = max(max_combo, combo)
                        
                        # Partículas
                        for _ in range(20):
                            particles.append(Particle(block.x + block.width // 2, 
                                                    block.y + block.height // 2, 
                                                    block.color))
                    break
            
            # Perdeu bola
            if ball.y > SCREEN_HEIGHT:
                balls.remove(ball)
                if len(balls) == 0:
                    lives -= 1
                    combo = 0
                    if lives > 0:
                        balls.append(Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200))
        
        # Atualiza blocos e partículas
        for block in blocks:
            block.update()
        
        particles = [p for p in particles if p.update()]
        
        # --- Renderização ---
        screen.fill(DARK_BG)
        
        # Grade de fundo neon
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, (20, 20, 40), (i, 0), (i, SCREEN_HEIGHT), 1)
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, (20, 20, 40), (0, i), (SCREEN_WIDTH, i), 1)
        
        # HUD
        draw_card(screen, 20, 20, SCREEN_WIDTH - 40, 110, (15, 15, 30))
        
        # Pontuação
        draw_text(screen, f"PONTOS: {score}", font_large, NEON_CYAN, 200, 75)
        
        # Vidas
        lives_x = SCREEN_WIDTH // 2
        draw_text(screen, "VIDAS:", font_medium, TEXT_SECONDARY, lives_x - 60, 75)
        for i in range(lives):
            pygame.draw.circle(screen, NEON_PINK, (lives_x + 20 + i * 40, 75), 12)
        
        # Combo
        if combo > 1:
            combo_text = f"COMBO x{combo}! 🔥"
            combo_color = NEON_ORANGE if combo < 5 else NEON_PINK
            draw_text(screen, combo_text, font_medium, combo_color, SCREEN_WIDTH - 200, 75)
        
        # Desenha partículas (atrás)
        for particle in particles:
            particle.draw(screen)
        
        # Desenha blocos
        for block in blocks:
            block.draw(screen)
        
        # Desenha bolas
        for ball in balls:
            ball.draw(screen)
        
        # Desenha paddle
        paddle.draw(screen)
        
        # Webcam pequena
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        pygame.draw.rect(screen, NEON_PURPLE, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 3)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Determina resultado
    won = len(blocks) == 0
    game_time = time.time() - game_start_time
    
    return show_results(score, max_combo, won, game_time)

def show_results(score, max_combo, won, game_time):
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
        
        card_x = SCREEN_WIDTH//2 - 500
        card_y = 150
        draw_card(screen, card_x, card_y, 1000, 600)
        
        if won:
            draw_text(screen, "🎉 VITÓRIA! 🎉", font_title, NEON_GREEN, 
                      SCREEN_WIDTH//2, card_y + 100)
        else:
            draw_text(screen, "💀 GAME OVER 💀", font_title, NEON_RED, 
                      SCREEN_WIDTH//2, card_y + 100)
        
        draw_text(screen, f"Pontuação: {score}", font_large, NEON_CYAN, 
                  SCREEN_WIDTH//2, card_y + 230)
        draw_text(screen, f"Combo Máximo: {max_combo}x", font_medium, NEON_ORANGE, 
                  SCREEN_WIDTH//2, card_y + 320)
        draw_text(screen, f"Tempo: {int(game_time)}s", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH//2, card_y + 390)
        
        draw_text(screen, "ESPAÇO para jogar novamente | ESC para sair", 
                  font_small, TEXT_SECONDARY, SCREEN_WIDTH//2, card_y + 520)
        
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

