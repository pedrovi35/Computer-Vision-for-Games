"""
🚀 ATIRADOR ESPACIAL - Space Shooter com Mãos
Atire em alienígenas usando gestos das mãos!

Controles: Movimente mãos para mirar | Feche o punho para atirar
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

# Cores espaciais
SPACE_BG = (5, 5, 20)
STAR_COLORS = [(255, 255, 255), (200, 200, 255), (255, 200, 200)]
PLAYER_COLOR = (0, 200, 255)
ENEMY_COLORS = [(255, 50, 50), (255, 150, 0), (150, 50, 255), (50, 255, 150)]
BULLET_COLOR = (255, 255, 0)
POWER_COLOR = (255, 0, 255)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (150, 150, 200)

# Configurações do jogo
PLAYER_SIZE = 60
BULLET_SPEED = 15
ENEMY_SPEED = 3
FIRE_COOLDOWN = 15  # Frames entre tiros

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🚀 Atirador Espacial")
clock = pygame.time.Clock()

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
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.color = random.choice(STAR_COLORS)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 150
        self.size = PLAYER_SIZE
        self.fire_cooldown = 0
        self.health = 100
        self.shield = 0
    
    def update(self, target_x, target_y):
        # Movimento suave
        diff_x = target_x - self.x
        diff_y = target_y - self.y
        self.x += diff_x * 0.3
        self.y += diff_y * 0.3
        
        # Limites
        self.x = max(50, min(SCREEN_WIDTH - 50, self.x))
        self.y = max(200, min(SCREEN_HEIGHT - 50, self.y))
        
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
    
    def draw(self, surface):
        # Escudo
        if self.shield > 0:
            shield_radius = self.size + 15
            s = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*POWER_COLOR, 100), (shield_radius, shield_radius), shield_radius)
            surface.blit(s, (self.x - shield_radius, self.y - shield_radius))
        
        # Nave espacial
        points = [
            (self.x, self.y - self.size // 2),  # Topo
            (self.x - self.size // 2, self.y + self.size // 2),  # Base esquerda
            (self.x, self.y + self.size // 3),  # Centro baixo
            (self.x + self.size // 2, self.y + self.size // 2)  # Base direita
        ]
        
        # Glow
        glow_points = [(x + (x - self.x) * 0.3, y + (y - self.y) * 0.3) for x, y in points]
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.polygon(s, (*PLAYER_COLOR, 80), 
                          [(p[0] - self.x + self.size, p[1] - self.y + self.size) for p in glow_points])
        surface.blit(s, (self.x - self.size, self.y - self.size))
        
        # Nave
        pygame.draw.polygon(surface, PLAYER_COLOR, points)
        pygame.draw.polygon(surface, TEXT_PRIMARY, points, 3)
        
        # Cockpit
        pygame.draw.circle(surface, (100, 200, 255), (int(self.x), int(self.y)), 8)
        
        # Propulsores
        flame_length = 15 + int(5 * abs(math.sin(time.time() * 20)))
        pygame.draw.line(surface, (255, 150, 0), (self.x - 15, self.y + 25), 
                        (self.x - 15, self.y + 25 + flame_length), 3)
        pygame.draw.line(surface, (255, 150, 0), (self.x + 15, self.y + 25), 
                        (self.x + 15, self.y + 25 + flame_length), 3)
    
    def can_fire(self):
        return self.fire_cooldown <= 0
    
    def fire(self):
        if self.can_fire():
            self.fire_cooldown = FIRE_COOLDOWN
            return Bullet(self.x, self.y - self.size // 2)
        return None

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.radius = 5
        self.active = True
        self.trail = []
    
    def update(self):
        self.y -= self.speed
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        return self.y > -20
    
    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(200 * (i / len(self.trail)))
            size = int(self.radius * (0.5 + 0.5 * i / len(self.trail)))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*BULLET_COLOR, alpha), (size, size), size)
            surface.blit(s, (tx - size, ty - size))
        
        # Bala
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, TEXT_PRIMARY, (int(self.x), int(self.y)), self.radius + 2, 2)

class Enemy:
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = -50
        self.size = random.randint(40, 70)
        self.speed = ENEMY_SPEED + random.uniform(-1, 2)
        self.color = random.choice(ENEMY_COLORS)
        self.health = 2
        self.angle = 0
        self.wobble = random.uniform(1, 3)
    
    def update(self):
        self.y += self.speed
        self.angle += self.wobble
        return self.y < SCREEN_HEIGHT + 100 and self.health > 0
    
    def draw(self, surface):
        # Alienígena rotativo
        wobble_x = math.sin(math.radians(self.angle)) * 10
        
        # Glow
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, 80), (self.size, self.size), self.size)
        surface.blit(s, (self.x + wobble_x - self.size, self.y - self.size))
        
        # Corpo
        pygame.draw.circle(surface, self.color, (int(self.x + wobble_x), int(self.y)), 
                          self.size // 2)
        
        # Olhos
        eye_offset = self.size // 4
        pygame.draw.circle(surface, (255, 0, 0), 
                          (int(self.x + wobble_x - eye_offset), int(self.y - 5)), 6)
        pygame.draw.circle(surface, (255, 0, 0), 
                          (int(self.x + wobble_x + eye_offset), int(self.y - 5)), 6)
        
        # Antenas
        antenna_h = 15
        pygame.draw.line(surface, self.color, 
                        (self.x + wobble_x - eye_offset, self.y - self.size // 2),
                        (self.x + wobble_x - eye_offset, self.y - self.size // 2 - antenna_h), 3)
        pygame.draw.circle(surface, (255, 255, 0), 
                          (int(self.x + wobble_x - eye_offset), 
                           int(self.y - self.size // 2 - antenna_h)), 4)
        
        pygame.draw.line(surface, self.color, 
                        (self.x + wobble_x + eye_offset, self.y - self.size // 2),
                        (self.x + wobble_x + eye_offset, self.y - self.size // 2 - antenna_h), 3)
        pygame.draw.circle(surface, (255, 255, 0), 
                          (int(self.x + wobble_x + eye_offset), 
                           int(self.y - self.size // 2 - antenna_h)), 4)
    
    def hit(self):
        self.health -= 1
        return self.health <= 0
    
    def check_collision_bullet(self, bullet):
        dist = math.sqrt((self.x - bullet.x)**2 + (self.y - bullet.y)**2)
        return dist < self.size // 2 + bullet.radius

class Explosion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.particles = []
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'size': random.randint(3, 8)
            })
    
    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.03
        return any(p['life'] > 0 for p in self.particles)
    
    def draw(self, surface):
        for p in self.particles:
            if p['life'] > 0:
                alpha = int(p['life'] * 255)
                s = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, alpha), (p['size'], p['size']), p['size'])
                surface.blit(s, (int(p['x'] - p['size']), int(p['y'] - p['size'])))

# --- Detecção de Gestos ---
def detect_fist(hand_landmarks):
    """Detecta se a mão está fechada (punho)"""
    if not hand_landmarks:
        return False
    
    # Verifica se todos os dedos estão fechados
    finger_tips = [8, 12, 16, 20]
    finger_mids = [6, 10, 14, 18]
    
    fingers_closed = 0
    for tip, mid in zip(finger_tips, finger_mids):
        if hand_landmarks.landmark[tip].y >= hand_landmarks.landmark[mid].y:
            fingers_closed += 1
    
    return fingers_closed >= 3

# --- UI ---
def draw_text(surface, text, font, color, x, y, center=True, shadow=True):
    if shadow:
        text_obj = font.render(text, True, (0, 0, 0))
        rect = text_obj.get_rect(center=(x+2, y+2)) if center else (x+2, y+2)
        surface.blit(text_obj, rect)
    
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(x, y)) if center else (x, y)
    surface.blit(text_obj, rect)

# --- Telas ---
def main_menu():
    stars = [Star() for _ in range(100)]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill(SPACE_BG)
        for star in stars:
            star.update()
            star.draw(screen)
        
        title_y = 150 + int(10 * np.sin(time.time() * 2))
        draw_text(screen, "🚀 ATIRADOR ESPACIAL 🚀", font_title, PLAYER_COLOR, 
                  SCREEN_WIDTH // 2, title_y)
        
        card_x = SCREEN_WIDTH // 2 - 450
        card_y = 300
        s = pygame.Surface((900, 450), pygame.SRCALPHA)
        pygame.draw.rect(s, (20, 20, 40, 230), (0, 0, 900, 450), border_radius=20)
        screen.blit(s, (card_x, card_y))
        pygame.draw.rect(screen, PLAYER_COLOR, (card_x, card_y, 900, 450), 4, border_radius=20)
        
        instructions = [
            "Como Jogar:",
            "",
            "👋 MOVIMENTE suas mãos para MIRAR",
            "✊ FECHE O PUNHO para ATIRAR",
            "👽 Destrua os alienígenas!",
            "💚 Não deixe passar muitos!",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 50
        for i, text in enumerate(instructions):
            if i == 0 or i == 7:
                color = PLAYER_COLOR
                font = font_medium
            else:
                color = TEXT_PRIMARY
                font = font_small
            draw_text(screen, text, font, color, SCREEN_WIDTH // 2, y_offset, True, False)
            y_offset += 60 if i == 0 or i == 6 else 52
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return 0
    
    stars = [Star() for _ in range(150)]
    player = Player()
    bullets = []
    enemies = []
    explosions = []
    
    score = 0
    enemies_escaped = 0
    max_escaped = 10
    frame_count = 0
    
    running = True
    
    while running and enemies_escaped < max_escaped and player.health > 0:
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
        hand_positions = []
        is_firing = False
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Posição do indicador
                index_tip = hand_landmarks.landmark[8]
                hand_x = int(index_tip.x * SCREEN_WIDTH)
                hand_y = int(index_tip.y * SCREEN_HEIGHT)
                hand_positions.append((hand_x, hand_y))
                
                # Verifica punho fechado
                if detect_fist(hand_landmarks):
                    is_firing = True
                    cv2.putText(frame, "FOGO!", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        # Atualiza jogador
        if hand_positions:
            avg_x = sum(p[0] for p in hand_positions) / len(hand_positions)
            avg_y = sum(p[1] for p in hand_positions) / len(hand_positions)
            player.update(avg_x, avg_y)
        else:
            player.update(player.x, player.y)
        
        # Atira
        if is_firing:
            bullet = player.fire()
            if bullet:
                bullets.append(bullet)
        
        # Spawna inimigos
        frame_count += 1
        if frame_count % 60 == 0:
            enemies.append(Enemy())
        
        # Atualiza objetos
        for star in stars:
            star.update()
        
        bullets = [b for b in bullets if b.update()]
        enemies = [e for e in enemies if e.update()]
        explosions = [exp for exp in explosions if exp.update()]
        
        # Colisões
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if enemy.check_collision_bullet(bullet):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if enemy.hit():
                        score += 100
                        explosions.append(Explosion(enemy.x, enemy.y, enemy.color))
                        if enemy in enemies:
                            enemies.remove(enemy)
                    break
        
        # Inimigos que escaparam
        for enemy in enemies[:]:
            if enemy.y > SCREEN_HEIGHT:
                enemies_escaped += 1
                enemies.remove(enemy)
        
        # --- Renderização ---
        screen.fill(SPACE_BG)
        
        for star in stars:
            star.draw(screen)
        
        for explosion in explosions:
            explosion.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
        
        for bullet in bullets:
            bullet.draw(screen)
        
        player.draw(screen)
        
        # HUD
        hud_surf = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (0, 0, 0, 150), (0, 0, SCREEN_WIDTH, 100))
        screen.blit(hud_surf, (0, 0))
        
        draw_text(screen, f"PONTOS: {score}", font_large, TEXT_PRIMARY, 180, 50)
        
        # Barra de vida
        bar_x = SCREEN_WIDTH // 2 - 150
        bar_y = 30
        bar_width = 300
        bar_height = 25
        
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 
                        border_radius=10)
        health_width = int(bar_width * (player.health / 100))
        health_color = (0, 255, 0) if player.health > 50 else (255, 255, 0) if player.health > 25 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height), 
                        border_radius=10)
        draw_text(screen, f"VIDA: {player.health}%", font_small, TEXT_PRIMARY, 
                  SCREEN_WIDTH // 2, 70)
        
        # Escapados
        draw_text(screen, f"ESCAPARAM: {enemies_escaped}/{max_escaped}", font_medium, 
                  (255, 100, 100) if enemies_escaped > 7 else TEXT_SECONDARY, 
                  SCREEN_WIDTH - 200, 50)
        
        # Webcam
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        
        border_color = (255, 0, 0) if is_firing else (0, 255, 0) if hand_positions else (100, 100, 100)
        pygame.draw.rect(screen, border_color, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 4)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    
    return show_results(score, enemies_escaped < max_escaped and player.health > 0)

def show_results(score, won):
    stars = [Star() for _ in range(100)]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill(SPACE_BG)
        for star in stars:
            star.update()
            star.draw(screen)
        
        card_x = SCREEN_WIDTH // 2 - 450
        card_y = 250
        s = pygame.Surface((900, 400), pygame.SRCALPHA)
        pygame.draw.rect(s, (20, 20, 40, 240), (0, 0, 900, 400), border_radius=20)
        screen.blit(s, (card_x, card_y))
        pygame.draw.rect(screen, PLAYER_COLOR, (card_x, card_y, 900, 400), 5, border_radius=20)
        
        if won:
            draw_text(screen, "🎉 VITÓRIA! 🎉", font_title, (0, 255, 0), 
                      SCREEN_WIDTH // 2, card_y + 80)
        else:
            draw_text(screen, "💥 GAME OVER 💥", font_title, (255, 0, 0), 
                      SCREEN_WIDTH // 2, card_y + 80)
        
        draw_text(screen, f"Pontuação Final: {score}", font_large, TEXT_PRIMARY, 
                  SCREEN_WIDTH // 2, card_y + 200)
        
        draw_text(screen, "ESPAÇO para jogar novamente | ESC para sair", 
                  font_small, TEXT_SECONDARY, SCREEN_WIDTH // 2, card_y + 320)
        
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

