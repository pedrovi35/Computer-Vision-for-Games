"""
🏃 CORREDOR INFINITO PRO - Endless Runner com Visão Computacional
Pule e abaixe usando movimentos corporais! Velocidade progressiva e power-ups!

Controles: Levante os braços para pular | Agache para abaixar
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
WEBCAM_WIDTH = 280
WEBCAM_HEIGHT = 210
FPS = 60

# Cores vibrantes
SKY_COLOR = (135, 206, 250)
GROUND_COLOR = (101, 67, 33)
PLAYER_COLOR = (255, 69, 0)
OBSTACLE_COLOR = (178, 34, 34)
COIN_COLOR = (255, 215, 0)
POWER_COLOR = (147, 51, 234)
SHIELD_COLOR = (0, 200, 255)
MAGNET_COLOR = (255, 0, 255)
SLOW_COLOR = (100, 255, 100)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (200, 200, 200)

# Cores gradiente
GRADIENT_TOP = (255, 153, 204)
GRADIENT_MID = (255, 192, 203)
GRADIENT_BOT = (255, 105, 180)

# Configurações do jogo (velocidade base mais alta)
GRAVITY = 1.5
JUMP_FORCE = -22
PLAYER_SIZE = 60
GROUND_Y = 700
BASE_SPEED = 12  # Velocidade base aumentada
MAX_SPEED = 25  # Velocidade máxima
OBSTACLE_SPAWN_RATE = 75  # Mais frequente

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🏃 Corredor Infinito PRO - Controle Corporal + Power-ups")
clock = pygame.time.Clock()

# Fontes
font_title = pygame.font.Font(None, 90)
font_large = pygame.font.Font(None, 70)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 40)
font_tiny = pygame.font.Font(None, 30)

# MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- Classes ---
class Player:
    def __init__(self):
        self.x = 200
        self.y = GROUND_Y - PLAYER_SIZE
        self.vy = 0
        self.size = PLAYER_SIZE
        self.is_jumping = False
        self.is_ducking = False
        self.animation_frame = 0
        self.trail = []
        
        # Power-ups
        self.has_shield = False
        self.shield_time = 0
        self.has_magnet = False
        self.magnet_time = 0
        self.is_slow_motion = False
        self.slow_motion_time = 0
    
    def update(self, jump_command, duck_command):
        # Pulo mais responsivo (sem cooldown externo)
        if jump_command and not self.is_jumping and not self.is_ducking:
            self.vy = JUMP_FORCE
            self.is_jumping = True
        
        # Agachar mais responsivo
        self.is_ducking = duck_command and not self.is_jumping
        
        # Física com gravidade ajustada
        self.vy += GRAVITY
        self.y += self.vy
        
        # Limite do chão
        if self.y >= GROUND_Y - self.size:
            self.y = GROUND_Y - self.size
            self.vy = 0
            self.is_jumping = False
        
        # Trail mais longo quando está rápido
        self.trail.append((int(self.x + self.size // 2), int(self.y + self.size // 2)))
        trail_length = 15 if not self.is_slow_motion else 10
        if len(self.trail) > trail_length:
            self.trail.pop(0)
        
        # Animação
        self.animation_frame = (self.animation_frame + 0.3) % (2 * math.pi)
        
        # Atualiza power-ups
        if self.shield_time > 0:
            self.shield_time -= 1
            if self.shield_time == 0:
                self.has_shield = False
        
        if self.magnet_time > 0:
            self.magnet_time -= 1
            if self.magnet_time == 0:
                self.has_magnet = False
        
        if self.slow_motion_time > 0:
            self.slow_motion_time -= 1
            if self.slow_motion_time == 0:
                self.is_slow_motion = False
    
    def draw(self, surface):
        # Trail com cores dinâmicas
        for i, (tx, ty) in enumerate(self.trail[:-1]):
            alpha = int(120 * (i / len(self.trail)))
            size = int(self.size * (0.5 + 0.5 * i / len(self.trail)))
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Cor do trail baseada em power-ups
            trail_color = PLAYER_COLOR
            if self.has_shield:
                trail_color = SHIELD_COLOR
            elif self.is_slow_motion:
                trail_color = SLOW_COLOR
            elif self.has_magnet:
                trail_color = MAGNET_COLOR
            
            pygame.draw.circle(s, (*trail_color, alpha), (size // 2, size // 2), size // 2)
            surface.blit(s, (tx - size // 2, ty - size // 2))
        
        # Tamanho baseado em estado
        current_size = self.size if not self.is_ducking else self.size // 2
        y_offset = 0 if not self.is_ducking else self.size // 2
        
        # Pulso de energia mais intenso
        pulse = abs(math.sin(self.animation_frame * 2)) * 10
        
        # Escudo visual
        if self.has_shield:
            shield_pulse = abs(math.sin(self.animation_frame * 3)) * 5
            shield_radius = current_size // 2 + 20 + int(shield_pulse)
            s = pygame.Surface((shield_radius * 2 + 20, shield_radius * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(s, (*SHIELD_COLOR, 100), (shield_radius + 10, shield_radius + 10), shield_radius, 5)
            surface.blit(s, (self.x + current_size // 2 - shield_radius - 10, 
                           self.y + y_offset + current_size // 2 - shield_radius - 10))
        
        # Ímã visual
        if self.has_magnet:
            for angle in range(0, 360, 45):
                rad = math.radians(angle + self.animation_frame * 50)
                px = self.x + current_size // 2 + int(math.cos(rad) * (current_size // 2 + 15))
                py = self.y + y_offset + current_size // 2 + int(math.sin(rad) * (current_size // 2 + 15))
                pygame.draw.circle(surface, MAGNET_COLOR, (px, py), 4)
        
        # Glow mais intenso
        glow_size = current_size + int(pulse) * 2 + 10
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_color = PLAYER_COLOR
        if self.is_slow_motion:
            glow_color = SLOW_COLOR
        
        pygame.draw.circle(glow_surf, (*glow_color, 100), 
                          (glow_size // 2, glow_size // 2), 
                          glow_size // 2)
        surface.blit(glow_surf, (self.x + current_size // 2 - glow_size // 2, 
                                self.y + y_offset + current_size // 2 - glow_size // 2))
        
        # Corpo
        if self.is_ducking:
            # Forma retangular quando agachado
            pygame.draw.rect(surface, PLAYER_COLOR, 
                           (self.x, self.y + y_offset, self.size, current_size), border_radius=10)
            pygame.draw.rect(surface, TEXT_PRIMARY, 
                           (self.x, self.y + y_offset, self.size, current_size), 4, border_radius=10)
        else:
            # Circular normal
            pygame.draw.circle(surface, PLAYER_COLOR, 
                             (int(self.x + current_size // 2), int(self.y + y_offset + current_size // 2)), 
                             current_size // 2)
            pygame.draw.circle(surface, TEXT_PRIMARY, 
                             (int(self.x + current_size // 2), int(self.y + y_offset + current_size // 2)), 
                             current_size // 2, 4)
        
        # Olhos animados
        eye_offset = int(3 * math.sin(self.animation_frame))
        if not self.is_ducking:
            pygame.draw.circle(surface, TEXT_PRIMARY, 
                             (int(self.x + current_size // 2 - 10), 
                              int(self.y + y_offset + current_size // 2 - 5 + eye_offset)), 6)
            pygame.draw.circle(surface, TEXT_PRIMARY, 
                             (int(self.x + current_size // 2 + 10), 
                              int(self.y + y_offset + current_size // 2 - 5 + eye_offset)), 6)

class Obstacle:
    def __init__(self, x, obstacle_type="ground", speed=BASE_SPEED):
        self.x = x
        self.type = obstacle_type  # "ground" ou "air"
        self.width = random.randint(40, 70)
        self.height = random.randint(60, 100) if self.type == "ground" else 50
        self.y = GROUND_Y - self.height if self.type == "ground" else GROUND_Y - 200
        self.speed = speed
        self.passed = False
    
    def update(self, speed_multiplier=1.0):
        self.x -= self.speed * speed_multiplier
        return self.x > -self.width
    
    def draw(self, surface):
        # Gradiente
        for i in range(self.height):
            color_factor = i / self.height
            color = tuple(int(OBSTACLE_COLOR[j] * (1 - color_factor * 0.5)) for j in range(3))
            pygame.draw.line(surface, color, 
                           (self.x, self.y + i), 
                           (self.x + self.width, self.y + i), 1)
        
        # Borda brilhante
        pygame.draw.rect(surface, (150, 0, 0), (self.x, self.y, self.width, self.height), 4, border_radius=8)
        
        # Padrão de perigo
        stripe_width = 10
        for i in range(0, self.width, stripe_width * 2):
            pygame.draw.rect(surface, (255, 255, 0), 
                           (self.x + i, self.y, min(stripe_width, self.width - i), 10))
    
    def check_collision(self, player):
        if player.has_shield:
            return False
        
        player_rect = pygame.Rect(player.x, player.y if not player.is_ducking else player.y + player.size // 2,
                                  player.size, player.size if not player.is_ducking else player.size // 2)
        obstacle_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(obstacle_rect)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.collected = False
        self.rotation = 0
    
    def update(self, speed, speed_multiplier=1.0):
        self.x -= speed * speed_multiplier
        self.rotation += 10
        return self.x > -self.radius * 2 and not self.collected
    
    def draw(self, surface):
        # Glow pulsante mais intenso
        pulse = abs(math.sin(time.time() * 5)) * 12
        s = pygame.Surface((self.radius * 2 + int(pulse) * 2, self.radius * 2 + int(pulse) * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*COIN_COLOR, 120), 
                          (self.radius + int(pulse), self.radius + int(pulse)), 
                          self.radius + int(pulse))
        surface.blit(s, (self.x - self.radius - int(pulse), self.y - self.radius - int(pulse)))
        
        # Moeda
        pygame.draw.circle(surface, COIN_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (218, 165, 32), (int(self.x), int(self.y)), self.radius, 4)
        
        # Símbolo
        font = pygame.font.Font(None, 28)
        text = font.render("$", True, (218, 165, 32))
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text, text_rect)
    
    def check_collection(self, player, magnet_range=0):
        if not self.collected:
            distance = math.sqrt((self.x - (player.x + player.size // 2))**2 + 
                               (self.y - (player.y + player.size // 2))**2)
            
            # Ímã atrai moedas
            if player.has_magnet and distance < magnet_range:
                dx = (player.x + player.size // 2) - self.x
                dy = (player.y + player.size // 2) - self.y
                self.x += dx * 0.15
                self.y += dy * 0.15
            
            if distance < self.radius + player.size // 2 + 10:
                self.collected = True
                return True
        return False

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type  # "shield", "magnet", "slow"
        self.radius = 20
        self.collected = False
        self.rotation = 0
        
        # Cores por tipo
        self.colors = {
            "shield": SHIELD_COLOR,
            "magnet": MAGNET_COLOR,
            "slow": SLOW_COLOR
        }
        
        # Ícones
        self.icons = {
            "shield": "🛡️",
            "magnet": "🧲",
            "slow": "⏱️"
        }
    
    def update(self, speed, speed_multiplier=1.0):
        self.x -= speed * speed_multiplier
        self.rotation += 5
        return self.x > -self.radius * 2 and not self.collected
    
    def draw(self, surface):
        color = self.colors[self.type]
        
        # Glow pulsante
        pulse = abs(math.sin(time.time() * 4)) * 15
        s = pygame.Surface((self.radius * 2 + int(pulse) * 2, self.radius * 2 + int(pulse) * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, 100), 
                          (self.radius + int(pulse), self.radius + int(pulse)), 
                          self.radius + int(pulse))
        surface.blit(s, (self.x - self.radius - int(pulse), self.y - self.radius - int(pulse)))
        
        # Power-up
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, TEXT_PRIMARY, (int(self.x), int(self.y)), self.radius, 4)
        
        # Ícone
        font = pygame.font.Font(None, 30)
        text = font.render(self.icons[self.type], True, TEXT_PRIMARY)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text, text_rect)
    
    def check_collection(self, player):
        if not self.collected:
            distance = math.sqrt((self.x - (player.x + player.size // 2))**2 + 
                               (self.y - (player.y + player.size // 2))**2)
            if distance < self.radius + player.size // 2 + 10:
                self.collected = True
                return True
        return False

# --- Detecção de Pose ---
def detect_jump_and_duck(landmarks):
    if not landmarks:
        return False, False
    
    # Pontos-chave
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value].y
    
    # Pulo: mãos acima dos ombros (mais sensível)
    jump = (left_wrist < left_shoulder - 0.05) and (right_wrist < right_shoulder - 0.05)
    
    # Agachar: cabeça próxima do quadril (mais sensível)
    avg_hip = (left_hip + right_hip) / 2
    duck = nose > avg_hip - 0.15
    
    return jump, duck

# --- Funções UI ---
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

def draw_background(surface, scroll_offset):
    # Gradiente de céu
    for y in range(GROUND_Y):
        factor = y / GROUND_Y
        color = tuple(int(SKY_COLOR[i] * (1 - factor * 0.3)) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
    
    # Chão
    pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    
    # Linha do chão decorativa
    pygame.draw.line(surface, (80, 50, 20), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 5)
    
    # Nuvens paralaxe
    for i in range(5):
        cloud_x = (i * 400 + scroll_offset * 0.2) % (SCREEN_WIDTH + 200) - 100
        cloud_y = 100 + i * 80
        # Nuvem simples
        pygame.draw.ellipse(surface, (255, 255, 255, 150), (cloud_x, cloud_y, 120, 50))
        pygame.draw.ellipse(surface, (255, 255, 255, 150), (cloud_x + 30, cloud_y - 20, 80, 50))

# --- Telas ---
def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill(SKY_COLOR)
        draw_background(screen, time.time() * 50)
        
        # Título
        title_y = 120 + int(15 * np.sin(time.time() * 2))
        draw_text(screen, "🏃 CORREDOR INFINITO 🏃", font_title, PLAYER_COLOR, 
                  SCREEN_WIDTH//2, title_y)
        
        # Card
        card_rect = pygame.Rect(SCREEN_WIDTH//2 - 500, 280, 1000, 450)
        s = pygame.Surface((1000, 450), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 220), (0, 0, 1000, 450), border_radius=20)
        screen.blit(s, card_rect)
        pygame.draw.rect(screen, PLAYER_COLOR, card_rect, 4, border_radius=20)
        
        instructions = [
            "Como Jogar:",
            "",
            "🙌 LEVANTE os braços para PULAR",
            "🙇 AGACHE para ABAIXAR",
            "",
            "🪙 Colete moedas para pontos!",
            "🛡️ Escudo: Protege de 1 obstáculo",
            "🧲 Ímã: Atrai moedas automaticamente",
            "⏱️ Câmera Lenta: Reduz velocidade",
            "",
            "⚡ Velocidade aumenta progressivamente!",
            "🔥 Mantenha combos para mais pontos!",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = 310
        for i, text in enumerate(instructions):
            if i == 0 or i == 13:
                color = PLAYER_COLOR
                font = font_medium
            elif i == 10 or i == 11:
                color = (255, 100, 0)
                font = font_small
            elif i == 6:
                color = SHIELD_COLOR
                font = font_small
            elif i == 7:
                color = MAGNET_COLOR
                font = font_small
            elif i == 8:
                color = SLOW_COLOR
                font = font_small
            else:
                color = TEXT_SECONDARY if i % 2 == 1 and i != 1 and i != 4 and i != 9 and i != 12 else (50, 50, 50)
                font = font_small
            draw_text(screen, text, font, color, SCREEN_WIDTH//2, y_offset, True, False)
            y_offset += 48 if i == 0 or i == 12 else 40
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return 0
    
    player = Player()
    obstacles = []
    coins = []
    powerups = []
    
    score = 0
    distance = 0
    coins_collected = 0
    combo = 0
    max_combo = 0
    frame_count = 0
    game_start_time = time.time()
    scroll_offset = 0
    
    # Sistema de velocidade dinâmica
    current_speed = BASE_SPEED
    speed_level = 1
    
    # Efeitos visuais
    flash_timer = 0
    shake_amount = 0
    
    # Cooldown reduzido
    jump_cooldown = 0
    
    # Partículas de coleta
    particles = []
    
    running = True
    game_over = False
    
    while running and not game_over:
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
        results = pose.process(frame_rgb)
        
        # Detecta pose
        jump_command, duck_command = False, False
        if results.pose_landmarks:
            jump_command, duck_command = detect_jump_and_duck(results.pose_landmarks.landmark)
            
            # Desenha skeleton na webcam
            mp.solutions.drawing_utils.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 255), thickness=2)
            )
        
        # Cooldown reduzido para mais responsividade
        if jump_cooldown > 0:
            jump_cooldown -= 1
            jump_command = False
        elif jump_command:
            jump_cooldown = 15  # Reduzido de 30 para 15
        
        # Atualiza jogo
        player.update(jump_command, duck_command)
        
        # Sistema de velocidade progressiva
        distance_progress = distance // 10
        speed_level = min(1 + distance_progress * 0.1, 2.5)
        current_speed = BASE_SPEED * speed_level
        current_speed = min(current_speed, MAX_SPEED)
        
        # Multiplicador de velocidade (slow motion)
        speed_multiplier = 0.5 if player.is_slow_motion else 1.0
        
        # Spawna obstáculos (mais frequente conforme avança)
        frame_count += 1
        spawn_rate = max(OBSTACLE_SPAWN_RATE - distance // 5, 40)
        
        if frame_count % spawn_rate == 0:
            obstacle_type = "ground" if random.random() < 0.7 else "air"
            obstacles.append(Obstacle(SCREEN_WIDTH, obstacle_type, current_speed))
            
            # Spawna moeda mais frequentemente
            if random.random() < 0.5:
                coin_y = random.randint(GROUND_Y - 250, GROUND_Y - 100)
                coins.append(Coin(SCREEN_WIDTH + 100, coin_y))
        
        # Spawna power-ups raramente
        if frame_count % 300 == 0 and random.random() < 0.5:
            power_type = random.choice(["shield", "magnet", "slow"])
            power_y = random.randint(GROUND_Y - 250, GROUND_Y - 150)
            powerups.append(PowerUp(SCREEN_WIDTH + 150, power_y, power_type))
        
        # Atualiza obstáculos, moedas e power-ups
        obstacles = [obs for obs in obstacles if obs.update(speed_multiplier)]
        coins = [coin for coin in coins if coin.update(current_speed, speed_multiplier)]
        powerups = [pwup for pwup in powerups if pwup.update(current_speed, speed_multiplier)]
        
        # Checa colisões com obstáculos
        for obs in obstacles:
            if obs.check_collision(player):
                if player.has_shield:
                    # Escudo absorve o hit
                    player.has_shield = False
                    player.shield_time = 0
                    obstacles.remove(obs)
                    flash_timer = 10
                    shake_amount = 15
                    score += 100  # Bônus por usar escudo
                else:
                    game_over = True
            elif not obs.passed and obs.x + obs.width < player.x:
                obs.passed = True
                score += 10 * int(speed_level)
                distance += 1
                combo += 1
                max_combo = max(max_combo, combo)
        
        # Checa coleta de moedas (com ímã)
        magnet_range = 200 if player.has_magnet else 0
        for coin in coins:
            if coin.check_collection(player, magnet_range):
                score += 50 + (combo * 5)
                coins_collected += 1
                flash_timer = 5
                # Adiciona partículas
                for _ in range(5):
                    particles.append({
                        'x': coin.x,
                        'y': coin.y,
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-5, -2),
                        'life': 20,
                        'color': COIN_COLOR
                    })
        
        # Checa coleta de power-ups
        for pwup in powerups:
            if pwup.check_collection(player):
                if pwup.type == "shield":
                    player.has_shield = True
                    player.shield_time = 300  # 5 segundos
                elif pwup.type == "magnet":
                    player.has_magnet = True
                    player.magnet_time = 360  # 6 segundos
                elif pwup.type == "slow":
                    player.is_slow_motion = True
                    player.slow_motion_time = 240  # 4 segundos
                
                flash_timer = 8
                score += 25
        
        # Atualiza partículas
        for particle in particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3
            particle['life'] -= 1
            if particle['life'] <= 0:
                particles.remove(particle)
        
        scroll_offset += current_speed * speed_multiplier
        
        # --- Renderização ---
        # Screen shake
        shake_x = random.randint(-shake_amount, shake_amount) if shake_amount > 0 else 0
        shake_y = random.randint(-shake_amount, shake_amount) if shake_amount > 0 else 0
        shake_amount = max(0, shake_amount - 1)
        
        screen.fill(SKY_COLOR)
        
        # Efeito de câmera lenta no fundo
        if player.is_slow_motion:
            bg_tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(bg_tint, (*SLOW_COLOR, 30), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(bg_tint, (0, 0))
        
        draw_background(screen, scroll_offset)
        
        # Desenha partículas
        for particle in particles:
            alpha = int(255 * (particle['life'] / 20))
            s = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(s, (*particle['color'], alpha), (4, 4), 4)
            screen.blit(s, (particle['x'] + shake_x, particle['y'] + shake_y))
        
        # Desenha objetos
        for coin in coins:
            coin.draw(screen)
        
        for pwup in powerups:
            pwup.draw(screen)
        
        for obs in obstacles:
            obs.draw(screen)
        
        player.draw(screen)
        
        # Flash de coleta
        if flash_timer > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(flash_surf, (255, 255, 255, 30), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(flash_surf, (0, 0))
            flash_timer -= 1
        
        # HUD melhorado
        hud_surf = pygame.Surface((SCREEN_WIDTH, 140), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (0, 0, 0, 140), (0, 0, SCREEN_WIDTH, 140))
        screen.blit(hud_surf, (0, 0))
        
        draw_text(screen, f"PONTOS: {score}", font_large, TEXT_PRIMARY, 200, 50)
        draw_text(screen, f"🪙 {coins_collected}", font_medium, COIN_COLOR, SCREEN_WIDTH//2 - 100, 50)
        draw_text(screen, f"DISTÂNCIA: {distance}m", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH - 220, 50)
        
        # Barra de velocidade
        speed_text = f"VELOCIDADE: {int(current_speed)}km/h"
        speed_color = (255, 100, 0) if speed_level > 1.5 else TEXT_SECONDARY
        draw_text(screen, speed_text, font_small, speed_color, SCREEN_WIDTH//2 + 120, 50)
        
        # Combo counter
        if combo > 0:
            combo_text = f"COMBO x{combo}!"
            combo_color = (255, 215, 0) if combo > 5 else TEXT_PRIMARY
            draw_text(screen, combo_text, font_medium, combo_color, SCREEN_WIDTH//2, 110)
        
        # Indicadores de power-ups ativos
        powerup_x = 50
        powerup_y = 160
        if player.has_shield:
            time_left = player.shield_time // 60
            pygame.draw.rect(screen, SHIELD_COLOR, (powerup_x, powerup_y, 60, 60), border_radius=10)
            draw_text(screen, "🛡️", font_small, TEXT_PRIMARY, powerup_x + 30, powerup_y + 20, True, False)
            draw_text(screen, f"{time_left}s", font_tiny, TEXT_PRIMARY, powerup_x + 30, powerup_y + 48, True, False)
            powerup_x += 80
        
        if player.has_magnet:
            time_left = player.magnet_time // 60
            pygame.draw.rect(screen, MAGNET_COLOR, (powerup_x, powerup_y, 60, 60), border_radius=10)
            draw_text(screen, "🧲", font_small, TEXT_PRIMARY, powerup_x + 30, powerup_y + 20, True, False)
            draw_text(screen, f"{time_left}s", font_tiny, TEXT_PRIMARY, powerup_x + 30, powerup_y + 48, True, False)
            powerup_x += 80
        
        if player.is_slow_motion:
            time_left = player.slow_motion_time // 60
            pygame.draw.rect(screen, SLOW_COLOR, (powerup_x, powerup_y, 60, 60), border_radius=10)
            draw_text(screen, "⏱️", font_small, TEXT_PRIMARY, powerup_x + 30, powerup_y + 20, True, False)
            draw_text(screen, f"{time_left}s", font_tiny, TEXT_PRIMARY, powerup_x + 30, powerup_y + 48, True, False)
        
        # Indicadores de controle melhorados
        control_x = 150
        control_y = SCREEN_HEIGHT - 120
        
        # Indicador de pulo
        jump_color = (0, 255, 0) if jump_command else (80, 80, 80)
        pygame.draw.rect(screen, jump_color, (control_x, control_y - 60, 90, 90), border_radius=12)
        if jump_color != (80, 80, 80):
            pygame.draw.rect(screen, TEXT_PRIMARY, (control_x, control_y - 60, 90, 90), 4, border_radius=12)
        draw_text(screen, "🙌", font_medium, TEXT_PRIMARY, control_x + 45, control_y - 25, True, False)
        draw_text(screen, "PULAR", font_tiny, TEXT_PRIMARY, control_x + 45, control_y + 40, True, False)
        
        # Indicador de agachar
        duck_color = (255, 100, 0) if duck_command else (80, 80, 80)
        pygame.draw.rect(screen, duck_color, (control_x + 120, control_y - 60, 90, 90), border_radius=12)
        if duck_color != (80, 80, 80):
            pygame.draw.rect(screen, TEXT_PRIMARY, (control_x + 120, control_y - 60, 90, 90), 4, border_radius=12)
        draw_text(screen, "🙇", font_medium, TEXT_PRIMARY, control_x + 165, control_y - 25, True, False)
        draw_text(screen, "AGACHAR", font_tiny, TEXT_PRIMARY, control_x + 165, control_y + 40, True, False)
        
        # Webcam
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        
        border_color = (0, 255, 0) if results.pose_landmarks else (255, 0, 0)
        pygame.draw.rect(screen, border_color, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 5, border_radius=8)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    
    game_time = time.time() - game_start_time
    return show_results(score, distance, coins_collected, game_time, max_combo)

def show_results(score, distance, coins, game_time, max_combo):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill(SKY_COLOR)
        draw_background(screen, 0)
        
        card_rect = pygame.Rect(SCREEN_WIDTH//2 - 550, 120, 1100, 680)
        s = pygame.Surface((1100, 680), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 240), (0, 0, 1100, 680), border_radius=20)
        screen.blit(s, card_rect)
        pygame.draw.rect(screen, PLAYER_COLOR, card_rect, 6, border_radius=20)
        
        draw_text(screen, "🏁 CORRIDA FINALIZADA! 🏁", font_title, PLAYER_COLOR, 
                  SCREEN_WIDTH//2, 220)
        
        # Estatísticas detalhadas
        y_pos = 330
        draw_text(screen, f"🏆 PONTUAÇÃO FINAL: {score}", font_large, (50, 50, 50), 
                  SCREEN_WIDTH//2, y_pos)
        y_pos += 80
        
        draw_text(screen, f"📏 Distância Percorrida: {distance}m", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH//2, y_pos)
        y_pos += 70
        
        draw_text(screen, f"🪙 Moedas Coletadas: {coins}", font_medium, COIN_COLOR, 
                  SCREEN_WIDTH//2, y_pos)
        y_pos += 70
        
        draw_text(screen, f"🔥 Combo Máximo: x{max_combo}", font_medium, (255, 165, 0), 
                  SCREEN_WIDTH//2, y_pos)
        y_pos += 70
        
        draw_text(screen, f"⏱️ Tempo de Jogo: {int(game_time)}s", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH//2, y_pos)
        y_pos += 90
        
        # Avaliação de desempenho
        if score > 1000:
            rank = "🌟 LENDÁRIO! 🌟"
            rank_color = (255, 215, 0)
        elif score > 500:
            rank = "🔥 INCRÍVEL! 🔥"
            rank_color = (255, 100, 0)
        elif score > 250:
            rank = "✨ ÓTIMO! ✨"
            rank_color = (0, 200, 255)
        else:
            rank = "💪 BOM TRABALHO! 💪"
            rank_color = (100, 200, 100)
        
        draw_text(screen, rank, font_large, rank_color, SCREEN_WIDTH//2, y_pos)
        
        draw_text(screen, "ESPAÇO para jogar novamente | ESC para sair", 
                  font_small, (100, 100, 100), SCREEN_WIDTH//2, 730)
        
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

