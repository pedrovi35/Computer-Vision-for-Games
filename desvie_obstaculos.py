"""
🚗 DESVIE DOS OBSTÁCULOS - Controle por Rosto
Desvie lateralmente dos obstáculos movendo seu rosto!

Controles: Mova seu rosto para esquerda/direita
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
WEBCAM_WIDTH = 300
WEBCAM_HEIGHT = 225
FPS = 60

# Cores vibrantes
SKY_TOP = (25, 25, 112)
SKY_BOT = (135, 206, 250)
ROAD_COLOR = (50, 50, 50)
LANE_COLOR = (255, 255, 255)
PLAYER_COLOR = (255, 69, 0)
OBSTACLE_COLORS = [(220, 20, 60), (255, 140, 0), (75, 0, 130), (255, 20, 147)]
COIN_COLOR = (255, 215, 0)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (200, 200, 220)

# Configurações do jogo
NUM_LANES = 3
LANE_WIDTH = 200
PLAYER_SIZE = 70
OBSTACLE_SPEED = 12

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🚗 Desvie dos Obstáculos")
clock = pygame.time.Clock()

font_title = pygame.font.Font(None, 90)
font_large = pygame.font.Font(None, 70)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 40)
font_tiny = pygame.font.Font(None, 30)

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- Classes ---
class Player:
    def __init__(self):
        self.lane = 1  # Começa no meio
        self.target_lane = 1
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 200
        self.size = PLAYER_SIZE
        self.invincible_time = 0
        self.trail = []
    
    def update(self, target_lane):
        self.target_lane = max(0, min(NUM_LANES - 1, target_lane))
        
        # Movimento suave
        target_x = SCREEN_WIDTH // 2 - LANE_WIDTH + self.target_lane * LANE_WIDTH
        diff = target_x - self.x
        self.x += diff * 0.2
        
        # Atualiza lane atual
        if abs(diff) < 10:
            self.lane = self.target_lane
        
        # Trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 15:
            self.trail.pop(0)
        
        # Invencibilidade
        if self.invincible_time > 0:
            self.invincible_time -= 1
    
    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail[:-1]):
            alpha = int(150 * (i / len(self.trail)))
            size = int(self.size * (0.4 + 0.6 * i / len(self.trail)))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*PLAYER_COLOR, alpha), (size, size), size)
            surface.blit(s, (tx - size, ty - size))
        
        # Blink se invencível
        if self.invincible_time > 0 and self.invincible_time % 10 < 5:
            return
        
        # Corpo - formato de carro
        car_width = self.size
        car_height = self.size * 1.5
        
        # Sombra
        pygame.draw.ellipse(surface, (0, 0, 0, 100), 
                           (self.x - car_width // 2, self.y + car_height, 
                            car_width, 20))
        
        # Corpo principal
        pygame.draw.rect(surface, PLAYER_COLOR, 
                        (self.x - car_width // 2, self.y, car_width, car_height), 
                        border_radius=15)
        
        # Janelas
        pygame.draw.rect(surface, (100, 150, 255), 
                        (self.x - car_width // 2 + 5, self.y + 10, car_width - 10, 25), 
                        border_radius=8)
        pygame.draw.rect(surface, (100, 150, 255), 
                        (self.x - car_width // 2 + 5, self.y + 50, car_width - 10, 30), 
                        border_radius=8)
        
        # Detalhes
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x - 15), int(self.y + 5)), 5)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x + 15), int(self.y + 5)), 5)
        
        # Borda
        pygame.draw.rect(surface, TEXT_PRIMARY, 
                        (self.x - car_width // 2, self.y, car_width, car_height), 
                        3, border_radius=15)

class Obstacle:
    def __init__(self, lane):
        self.lane = lane
        self.x = SCREEN_WIDTH // 2 - LANE_WIDTH + lane * LANE_WIDTH
        self.y = -100
        self.width = 60
        self.height = 80
        self.speed = OBSTACLE_SPEED
        self.color = random.choice(OBSTACLE_COLORS)
        self.passed = False
    
    def update(self):
        self.y += self.speed
        return self.y < SCREEN_HEIGHT + 100
    
    def draw(self, surface):
        # Obstáculo como carro/objeto
        pygame.draw.rect(surface, self.color, 
                        (self.x - self.width // 2, self.y, self.width, self.height), 
                        border_radius=10)
        
        # Detalhes
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.x - self.width // 2 + 5, self.y + 5, self.width - 10, 20), 
                        border_radius=5)
        
        pygame.draw.rect(surface, TEXT_PRIMARY, 
                        (self.x - self.width // 2, self.y, self.width, self.height), 
                        2, border_radius=10)
    
    def check_collision(self, player):
        if abs(self.lane - player.lane) < 0.3 and abs(self.y - player.y) < 80:
            if player.invincible_time <= 0:
                return True
        return False

class Coin:
    def __init__(self, lane):
        self.lane = lane
        self.x = SCREEN_WIDTH // 2 - LANE_WIDTH + lane * LANE_WIDTH
        self.y = -50
        self.radius = 20
        self.speed = OBSTACLE_SPEED
        self.collected = False
        self.rotation = 0
    
    def update(self):
        self.y += self.speed
        self.rotation += 10
        return self.y < SCREEN_HEIGHT + 50 and not self.collected
    
    def draw(self, surface):
        # Glow
        pulse = abs(math.sin(time.time() * 5)) * 8
        s = pygame.Surface((self.radius * 2 + int(pulse) * 2, self.radius * 2 + int(pulse) * 2), 
                          pygame.SRCALPHA)
        pygame.draw.circle(s, (*COIN_COLOR, 100), 
                          (self.radius + int(pulse), self.radius + int(pulse)), 
                          self.radius + int(pulse))
        surface.blit(s, (self.x - self.radius - int(pulse), self.y - self.radius - int(pulse)))
        
        # Moeda
        pygame.draw.circle(surface, COIN_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (218, 165, 32), (int(self.x), int(self.y)), self.radius, 3)
        
        # Símbolo
        text = font_small.render("★", True, (218, 165, 32))
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text, text_rect)
    
    def check_collection(self, player):
        if not self.collected and abs(self.lane - player.lane) < 0.5:
            if abs(self.y - player.y) < 60:
                self.collected = True
                return True
        return False

# --- Detecção de Rosto ---
def detect_face_position(face_landmarks, frame_width):
    """Detecta posição horizontal do rosto na tela"""
    if not face_landmarks:
        return 1  # Centro
    
    # Ponto do nariz (centro do rosto)
    nose = face_landmarks.landmark[1]
    
    # Posição horizontal normalizada (0.0 a 1.0)
    face_x = nose.x
    
    # Divide a tela em 3 zonas com margem maior para facilitar
    # Esquerda: 0.0 - 0.35
    # Centro: 0.35 - 0.65
    # Direita: 0.65 - 1.0
    
    if face_x < 0.35:
        return 0  # Esquerda
    elif face_x > 0.65:
        return 2  # Direita
    else:
        return 1  # Centro

# --- UI ---
def draw_text(surface, text, font, color, x, y, center=True, shadow=True):
    if shadow:
        text_obj = font.render(text, True, (0, 0, 0))
        rect = text_obj.get_rect(center=(x+2, y+2)) if center else (x+2, y+2)
        surface.blit(text_obj, rect)
    
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(x, y)) if center else (x, y)
    surface.blit(text_obj, rect)

def draw_road(surface, scroll_offset):
    """Desenha a pista com animação"""
    # Céu gradiente
    for y in range(250):
        factor = y / 250
        color = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * factor) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
    
    # Estrada
    road_x = int(SCREEN_WIDTH // 2 - LANE_WIDTH * 1.5)
    road_width = int(LANE_WIDTH * NUM_LANES)
    pygame.draw.rect(surface, ROAD_COLOR, (road_x, 250, road_width, SCREEN_HEIGHT - 250))
    
    # Linhas das pistas
    line_height = 40
    line_gap = 60
    
    for lane in range(1, NUM_LANES):
        lane_x = int(road_x + lane * LANE_WIDTH)
        start_y = int(250 - (int(scroll_offset) % (line_height + line_gap)))
        for y in range(start_y, SCREEN_HEIGHT, line_height + line_gap):
            pygame.draw.rect(surface, LANE_COLOR, (lane_x - 3, y, 6, line_height))
    
    # Bordas da estrada
    pygame.draw.rect(surface, (255, 255, 0), (road_x - 5, 250, 5, SCREEN_HEIGHT - 250))
    pygame.draw.rect(surface, (255, 255, 0), (road_x + road_width, 250, 5, SCREEN_HEIGHT - 250))

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
        
        screen.fill(SKY_BOT)
        draw_road(screen, time.time() * 100)
        
        # Título
        title_y = 150 + int(10 * np.sin(time.time() * 2))
        draw_text(screen, "🚗 DESVIE DOS OBSTÁCULOS 🚗", font_title, TEXT_PRIMARY, 
                  SCREEN_WIDTH // 2, title_y)
        
        # Card
        card_x = SCREEN_WIDTH // 2 - 450
        card_y = 320
        s = pygame.Surface((900, 400), pygame.SRCALPHA)
        pygame.draw.rect(s, (30, 30, 40, 230), (0, 0, 900, 400), border_radius=20)
        screen.blit(s, (card_x, card_y))
        pygame.draw.rect(screen, PLAYER_COLOR, (card_x, card_y, 900, 400), 4, border_radius=20)
        
        instructions = [
            "Como Jogar:",
            "",
            "🔄 MOVA seu rosto para ESQUERDA/CENTRO/DIREITA",
            "🚗 Desvie dos obstáculos coloridos!",
            "⭐ Colete estrelas douradas!",
            "💥 3 vidas para sobreviver",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 45
        for i, text in enumerate(instructions):
            if i == 0 or i == 7:
                color = PLAYER_COLOR
                font = font_medium
            else:
                color = TEXT_PRIMARY
                font = font_small
            draw_text(screen, text, font, color, SCREEN_WIDTH // 2, y_offset, True, False)
            y_offset += 55 if i == 0 or i == 6 else 48
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    print("🎮 Iniciando jogo...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Erro ao abrir câmera")
            print("⚠️ Verifique se sua webcam está conectada e não está sendo usada por outro programa")
            input("Pressione ENTER para voltar ao menu...")
            return 0
        print("✅ Câmera inicializada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar câmera: {e}")
        input("Pressione ENTER para voltar ao menu...")
        return 0
    
    player = Player()
    obstacles = []
    coins = []
    
    score = 0
    lives = 3
    distance = 0
    coins_collected = 0
    frame_count = 0
    scroll_offset = 0
    
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
        results = face_mesh.process(frame_rgb)
        
        # Detecta posição da cabeça
        head_position = 0
        face_detected = False
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_detected = True
                h, w = frame.shape[:2]
                
                # Detecta posição do rosto
                target_lane = detect_face_position(face_landmarks, w)
                
                player.update(target_lane)
                
                # Desenha indicador visual na webcam
                nose = face_landmarks.landmark[1]
                nose_x = int(nose.x * w)
                nose_y = int(nose.y * h)
                center_y = h // 2
                
                # Desenha círculo no nariz
                cv2.circle(frame, (nose_x, nose_y), 10, (0, 255, 0), -1)
                
                # Desenha linhas de zona
                zone_left = int(w * 0.35)
                zone_right = int(w * 0.65)
                cv2.line(frame, (zone_left, 0), (zone_left, h), (255, 255, 0), 2)
                cv2.line(frame, (zone_right, 0), (zone_right, h), (255, 255, 0), 2)
                
                # Texto da pista
                lane_text = ["<< ESQUERDA", "CENTRO", "DIREITA >>"][target_lane]
                lane_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)][target_lane]
                cv2.putText(frame, lane_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, lane_color, 2)
        else:
            player.update(1)  # Volta para o centro
        
        # Spawna obstáculos e moedas
        frame_count += 1
        if frame_count % 60 == 0:
            lane = random.randint(0, NUM_LANES - 1)
            obstacles.append(Obstacle(lane))
        
        if frame_count % 120 == 0 and random.random() < 0.6:
            lane = random.randint(0, NUM_LANES - 1)
            coins.append(Coin(lane))
        
        # Atualiza objetos
        obstacles = [obs for obs in obstacles if obs.update()]
        coins = [coin for coin in coins if coin.update()]
        
        # Checa colisões
        for obs in obstacles:
            if obs.check_collision(player):
                lives -= 1
                player.invincible_time = 60
                obstacles.remove(obs)
                if lives <= 0:
                    game_over = True
            elif not obs.passed and obs.y > player.y:
                obs.passed = True
                score += 10
                distance += 1
        
        for coin in coins:
            if coin.check_collection(player):
                score += 50
                coins_collected += 1
        
        scroll_offset += OBSTACLE_SPEED
        
        # --- Renderização ---
        screen.fill(SKY_BOT)
        draw_road(screen, scroll_offset)
        
        # Desenha objetos
        for coin in coins:
            coin.draw(screen)
        
        for obs in obstacles:
            obs.draw(screen)
        
        player.draw(screen)
        
        # HUD
        hud_surf = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (0, 0, 0, 150), (0, 0, SCREEN_WIDTH, 120))
        screen.blit(hud_surf, (0, 0))
        
        draw_text(screen, f"PONTOS: {score}", font_large, TEXT_PRIMARY, 200, 60)
        
        # Vidas
        lives_x = SCREEN_WIDTH // 2
        draw_text(screen, "VIDAS:", font_medium, TEXT_SECONDARY, lives_x - 60, 60)
        for i in range(lives):
            pygame.draw.circle(screen, PLAYER_COLOR, (lives_x + 20 + i * 45, 60), 15)
        
        draw_text(screen, f"⭐ {coins_collected}", font_medium, COIN_COLOR, 
                  SCREEN_WIDTH - 150, 60)
        
        # Indicador de pista
        if face_detected:
            indicator_y = SCREEN_HEIGHT - 150
            for i in range(NUM_LANES):
                lane_x = SCREEN_WIDTH // 2 - LANE_WIDTH + i * LANE_WIDTH
                color = PLAYER_COLOR if i == player.target_lane else (100, 100, 100)
                pygame.draw.circle(screen, color, (lane_x, indicator_y), 15)
        
        # Webcam
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        
        border_color = (0, 255, 0) if face_detected else (255, 0, 0)
        pygame.draw.rect(screen, border_color, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 4)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    
    return show_results(score, distance, coins_collected)

def show_results(score, distance, coins):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        screen.fill(SKY_BOT)
        draw_road(screen, 0)
        
        card_x = SCREEN_WIDTH // 2 - 450
        card_y = 200
        s = pygame.Surface((900, 500), pygame.SRCALPHA)
        pygame.draw.rect(s, (30, 30, 40, 240), (0, 0, 900, 500), border_radius=20)
        screen.blit(s, (card_x, card_y))
        pygame.draw.rect(screen, PLAYER_COLOR, (card_x, card_y, 900, 500), 5, border_radius=20)
        
        draw_text(screen, "🏁 CORRIDA FINALIZADA! 🏁", font_title, PLAYER_COLOR, 
                  SCREEN_WIDTH // 2, card_y + 80)
        
        draw_text(screen, f"Pontuação: {score}", font_large, TEXT_PRIMARY, 
                  SCREEN_WIDTH // 2, card_y + 200)
        draw_text(screen, f"Distância: {distance}m", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH // 2, card_y + 280)
        draw_text(screen, f"Estrelas: {coins} ⭐", font_medium, COIN_COLOR, 
                  SCREEN_WIDTH // 2, card_y + 350)
        
        draw_text(screen, "ESPAÇO para jogar novamente | ESC para sair", 
                  font_small, TEXT_SECONDARY, SCREEN_WIDTH // 2, card_y + 440)
        
        pygame.display.flip()
        clock.tick(FPS)

# --- Main ---
if __name__ == "__main__":
    print("🚗 Iniciando Desvie dos Obstáculos...")
    try:
        while True:
            if main_menu():
                result = game_loop()
                if not result:
                    break
            else:
                break
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione ENTER para sair...")
    finally:
        print("👋 Encerrando jogo...")
        pygame.quit()
        sys.exit()

