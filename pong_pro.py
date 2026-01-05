"""
🎮 PONG PRO - Edição Premium
Versão PREMIUM com visual neon cyberpunk e 5 níveis progressivos!

Controles: Rastreamento de olho pela webcam
Características:
• Visual neon moderno com efeitos especiais
• Sistema de 5 níveis (Iniciante a Lendário)
• Efeitos de partículas em colisões
• IA progressiva por nível
• Sistema de pausa e progressão
"""

# Suprime warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings('ignore')

import cv2
import mediapipe as mp
import pygame
import sys
import math
import random
import time

# --- Configurações ---
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60

# Cores Neon Cyberpunk
NEON_PINK = (255, 16, 240)
NEON_CYAN = (0, 255, 255)
NEON_PURPLE = (191, 64, 191)
NEON_BLUE = (64, 156, 255)
NEON_GREEN = (57, 255, 20)
NEON_ORANGE = (255, 128, 0)
NEON_RED = (255, 0, 64)
NEON_YELLOW = (255, 255, 0)

DARK_BG = (10, 10, 25)
DARKER_BG = (5, 5, 15)

# Configurações do jogo
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 120
BALL_SIZE = 20

# Sistema de níveis (MAIS DIFÍCIL!)
LEVELS = {
    1: {
        "name": "INICIANTE",
        "color": NEON_GREEN,
        "ai_speed": 7,
        "ai_error": 25,
        "ball_speed": 8,
        "win_score": 5,
        "particles": 10,
        "speed_increase": 0.15  # Aumento de velocidade por ponto
    },
    2: {
        "name": "INTERMEDIÁRIO",
        "color": NEON_CYAN,
        "ai_speed": 9,
        "ai_error": 20,
        "ball_speed": 10,
        "win_score": 7,
        "particles": 15,
        "speed_increase": 0.18
    },
    3: {
        "name": "AVANÇADO",
        "color": NEON_PURPLE,
        "ai_speed": 11,
        "ai_error": 15,
        "ball_speed": 12,
        "win_score": 10,
        "particles": 20,
        "speed_increase": 0.20
    },
    4: {
        "name": "EXPERT",
        "color": NEON_ORANGE,
        "ai_speed": 13,
        "ai_error": 10,
        "ball_speed": 14,
        "win_score": 12,
        "particles": 25,
        "speed_increase": 0.22
    },
    5: {
        "name": "LENDÁRIO",
        "color": NEON_PINK,
        "ai_speed": 15,
        "ai_error": 5,
        "ball_speed": 16,
        "win_score": 15,
        "particles": 30,
        "speed_increase": 0.25
    }
}

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎮 PONG PRO - Edição Premium")
clock = pygame.time.Clock()

font_title = pygame.font.Font(None, 100)
font_large = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 45)
font_tiny = pygame.font.Font(None, 35)

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- Classes ---
class Particle:
    """Partícula para efeitos visuais"""
    def __init__(self, x, y, color, speed=5):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = 60
        self.max_life = 60
        self.size = random.randint(3, 8)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, int(self.size * (self.life / self.max_life)))
        return self.life > 0
    
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))

class Paddle:
    """Raquete com efeitos neon"""
    def __init__(self, x, y, color, is_player=False):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color
        self.is_player = is_player
        self.trail = []
        self.glow_intensity = 0
    
    def update_position(self, y):
        """Atualiza posição suavemente"""
        self.trail.append(self.rect.centery)
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        self.rect.centery = y
        
        # Limites da tela
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    def move_ai(self, ball_y, ai_speed, ai_error):
        """Movimento da IA"""
        target_y = ball_y + random.randint(-ai_error, ai_error)
        
        if self.rect.centery < target_y - 10:
            self.rect.y += ai_speed
        elif self.rect.centery > target_y + 10:
            self.rect.y -= ai_speed
        
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    def draw(self, surface):
        """Desenha raquete com efeito neon"""
        # Brilho externo
        for i in range(3):
            glow_size = (3 - i) * 8
            s = pygame.Surface((self.rect.width + glow_size * 2, 
                               self.rect.height + glow_size * 2), pygame.SRCALPHA)
            glow_rect = pygame.Rect(0, 0, self.rect.width + glow_size * 2, 
                                   self.rect.height + glow_size * 2)
            alpha = 50 - i * 15
            pygame.draw.rect(s, (*self.color, alpha), glow_rect, border_radius=10)
            surface.blit(s, (self.rect.x - glow_size, self.rect.y - glow_size))
        
        # Corpo principal
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        
        # Borda brilhante
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3, border_radius=5)

class Ball:
    """Bola com efeitos e rastro"""
    def __init__(self, level_config):
        self.base_speed = level_config["ball_speed"]
        self.speed_multiplier = 1.0
        self.reset(level_config)
        self.trail = []
        self.particles = []
    
    def reset(self, level_config):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SIZE, BALL_SIZE)
        self.speed = self.base_speed * self.speed_multiplier
        angle = random.choice([random.uniform(-math.pi/4, math.pi/4),
                              random.uniform(3*math.pi/4, 5*math.pi/4)])
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.color = level_config["color"]
    
    def increase_speed(self, amount):
        """Aumenta a velocidade da bola progressivamente"""
        self.speed_multiplier += amount
        # Limita o aumento máximo
        self.speed_multiplier = min(self.speed_multiplier, 2.5)
        
        # Atualiza velocidades mantendo a direção
        magnitude = math.sqrt(self.vx**2 + self.vy**2)
        if magnitude > 0:
            self.vx = (self.vx / magnitude) * self.base_speed * self.speed_multiplier
            self.vy = (self.vy / magnitude) * self.base_speed * self.speed_multiplier
    
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Trail
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 20:
            self.trail.pop(0)
        
        # Colisão com topo/fundo
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy *= -1
            return "wall"
        
        return None
    
    def create_particles(self, num_particles, color):
        """Cria partículas na posição da bola"""
        for _ in range(num_particles):
            self.particles.append(Particle(self.rect.centerx, self.rect.centery, 
                                         color, speed=random.randint(3, 8)))
    
    def update_particles(self):
        """Atualiza partículas"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface):
        """Desenha bola com efeitos"""
        # Partículas
        for particle in self.particles:
            particle.draw(surface)
        
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(200 * (i / len(self.trail)))
            size = int(BALL_SIZE // 2 * (0.3 + 0.7 * i / len(self.trail)))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (tx - size, ty - size))
        
        # Brilho externo
        for i in range(4):
            glow_size = BALL_SIZE // 2 + (4 - i) * 6
            alpha = 80 - i * 20
            s = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (glow_size, glow_size), glow_size)
            surface.blit(s, (self.rect.centerx - glow_size, self.rect.centery - glow_size))
        
        # Corpo
        pygame.draw.circle(surface, self.color, self.rect.center, BALL_SIZE // 2)
        pygame.draw.circle(surface, (255, 255, 255), self.rect.center, BALL_SIZE // 2, 2)

# --- Funções Auxiliares ---
def draw_text(surface, text, font, color, x, y, center=True, glow=True):
    """Desenha texto com efeito neon"""
    if glow:
        # Brilho
        for i in range(3):
            offset = (3 - i) * 2
            alpha = 100 - i * 30
            s = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            text_obj = font.render(text, True, (*color, alpha))
            if center:
                rect = text_obj.get_rect(center=(x, y))
            else:
                rect = (x - offset, y - offset)
            s.blit(text_obj, rect)
            surface.blit(s, (0, 0))
    
    # Texto principal
    text_obj = font.render(text, True, color)
    if center:
        rect = text_obj.get_rect(center=(x, y))
    else:
        rect = (x, y)
    surface.blit(text_obj, rect)

def draw_gradient_rect(surface, x, y, width, height, color1, color2, vertical=True):
    """Desenha retângulo com gradiente"""
    if vertical:
        for i in range(height):
            factor = i / height
            color = tuple(int(color1[j] + (color2[j] - color1[j]) * factor) for j in range(3))
            pygame.draw.line(surface, color, (x, y + i), (x + width, y + i))
    else:
        for i in range(width):
            factor = i / width
            color = tuple(int(color1[j] + (color2[j] - color1[j]) * factor) for j in range(3))
            pygame.draw.line(surface, color, (x + i, y), (x + i, y + height))

def detect_eye_position(face_landmarks, frame_height):
    """Detecta posição vertical do olho"""
    if not face_landmarks:
        return SCREEN_HEIGHT // 2
    
    # Usa landmark do olho direito
    right_eye = face_landmarks.landmark[159]
    
    # Mapeia posição Y do olho para altura da tela
    eye_y = right_eye.y * frame_height
    screen_y = int(eye_y / frame_height * SCREEN_HEIGHT)
    
    return screen_y

# --- Telas ---
def main_menu():
    """Menu principal com visual cyberpunk"""
    angle = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # Background animado
        screen.fill(DARK_BG)
        
        # Grid cibernético
        grid_color = (30, 30, 60)
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, grid_color, (i, 0), (i, SCREEN_HEIGHT), 1)
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, grid_color, (0, i), (SCREEN_WIDTH, i), 1)
        
        # Título animado
        angle += 0.05
        title_y = 150 + int(20 * math.sin(angle))
        
        draw_text(screen, "PONG PRO", font_title, NEON_PINK, 
                 SCREEN_WIDTH // 2, title_y)
        draw_text(screen, "EDIÇÃO PREMIUM", font_medium, NEON_CYAN, 
                 SCREEN_WIDTH // 2, title_y + 80)
        
        # Card de informações
        card_x = SCREEN_WIDTH // 2 - 500
        card_y = 350
        
        # Fundo do card com borda neon
        s = pygame.Surface((1000, 400), pygame.SRCALPHA)
        pygame.draw.rect(s, (20, 20, 40, 230), (0, 0, 1000, 400), border_radius=20)
        screen.blit(s, (card_x, card_y))
        
        # Borda brilhante
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.rect(screen, (*NEON_PURPLE, alpha), 
                           (card_x - i * 2, card_y - i * 2, 1000 + i * 4, 400 + i * 4), 
                           3, border_radius=20)
        
        # Informações
        info_y = card_y + 40
        
        draw_text(screen, "🎮 5 NÍVEIS PROGRESSIVOS", font_small, NEON_CYAN, 
                 SCREEN_WIDTH // 2, info_y, glow=False)
        info_y += 60
        
        # Níveis
        level_texts = [
            ("1. INICIANTE", NEON_GREEN),
            ("2. INTERMEDIÁRIO", NEON_CYAN),
            ("3. AVANÇADO", NEON_PURPLE),
            ("4. EXPERT", NEON_ORANGE),
            ("5. LENDÁRIO", NEON_PINK)
        ]
        
        for i, (text, color) in enumerate(level_texts):
            x = card_x + 150 + (i % 3) * 280
            y = info_y + (i // 3) * 50
            draw_text(screen, text, font_tiny, color, x, y, center=False, glow=False)
        
        info_y += 130
        draw_text(screen, "👁️  Controle: Movimento dos OLHOS", font_small, NEON_YELLOW, 
                 SCREEN_WIDTH // 2, info_y, glow=False)
        
        info_y += 60
        draw_text(screen, "✨ Visual Neon • Efeitos de Partículas • IA Progressiva", 
                 font_tiny, (150, 150, 180), SCREEN_WIDTH // 2, info_y, glow=False)
        
        # Botão start pulsante
        pulse = abs(math.sin(time.time() * 3)) * 20
        draw_text(screen, "PRESSIONE ESPAÇO PARA COMEÇAR", font_small, 
                 NEON_GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        
        pygame.display.flip()
        clock.tick(FPS)

def level_intro(level_num):
    """Tela de introdução do nível"""
    level = LEVELS[level_num]
    start_time = time.time()
    duration = 2  # segundos
    
    while time.time() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        screen.fill(DARK_BG)
        
        # Círculo expandindo
        elapsed = time.time() - start_time
        radius = int(300 * (elapsed / duration))
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        alpha = int(100 * (1 - elapsed / duration))
        pygame.draw.circle(s, (*level["color"], alpha), (radius, radius), radius, 5)
        screen.blit(s, (SCREEN_WIDTH // 2 - radius, SCREEN_HEIGHT // 2 - radius))
        
        # Informações do nível
        draw_text(screen, f"NÍVEL {level_num}", font_title, level["color"], 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        draw_text(screen, level["name"], font_large, (255, 255, 255), 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, f"Vença {level['win_score']} pontos!", font_medium, level["color"], 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return True

def game_loop(current_level):
    """Loop principal do jogo"""
    print(f"🎮 Iniciando Nível {current_level}...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return False, current_level
    
    print("✅ Câmera inicializada!")
    
    # Configura janela da webcam separada
    window_name = "👁️ PONG PRO - Webcam"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 400, 300)
    cv2.moveWindow(window_name, SCREEN_WIDTH + 50, 100)  # Posiciona ao lado direito da tela do jogo
    
    level_config = LEVELS[current_level]
    
    # Objetos do jogo
    player_paddle = Paddle(50, SCREEN_HEIGHT // 2, level_config["color"], is_player=True)
    ai_paddle = Paddle(SCREEN_WIDTH - 70, SCREEN_HEIGHT // 2, NEON_RED)
    ball = Ball(level_config)
    
    player_score = 0
    ai_score = 0
    total_rallies = 0  # Contador de rebatidas para aumentar velocidade
    
    paused = False
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    paused = not paused
        
        if not paused:
            # Captura frame
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)
            
            h, w = frame.shape[:2]
            face_detected = False
            
            # Detecta posição do olho
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    face_detected = True
                    
                    # Posição do olho
                    eye_y = detect_eye_position(face_landmarks, h)
                    player_paddle.update_position(eye_y)
                    
                    # Indicador visual
                    right_eye = face_landmarks.landmark[159]
                    eye_x = int(right_eye.x * w)
                    eye_y_frame = int(right_eye.y * h)
                    
                    cv2.circle(frame, (eye_x, eye_y_frame), 10, (0, 255, 0), -1)
                    cv2.circle(frame, (eye_x, eye_y_frame), 15, (0, 255, 255), 3)
                    
                    # Desenha linha indicando posição
                    cv2.line(frame, (0, eye_y_frame), (w, eye_y_frame), (0, 255, 255), 2)
                    
                    # Status
                    cv2.putText(frame, "OLHO DETECTADO", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, f"Nivel: {current_level} - {level_config['name']}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"Velocidade: {ball.speed_multiplier:.1f}x", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            else:
                cv2.putText(frame, "PROCURANDO ROSTO...", (w//2 - 150, h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.putText(frame, "Posicione seu rosto na camera", (w//2 - 200, h//2 + 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Exibe webcam em janela separada
            cv2.imshow(window_name, frame)
            
            # IA
            ai_paddle.move_ai(ball.rect.centery, level_config["ai_speed"], 
                            level_config["ai_error"])
            
            # Bola
            collision = ball.update()
            ball.update_particles()
            
            if collision == "wall":
                ball.create_particles(level_config["particles"] // 2, level_config["color"])
            
            # Colisões com raquetes
            if ball.rect.colliderect(player_paddle.rect):
                ball.vx = abs(ball.vx)
                ball.vy += random.uniform(-2, 2)
                ball.create_particles(level_config["particles"], level_config["color"])
                total_rallies += 1
                # Aumenta velocidade a cada rebatida
                ball.increase_speed(level_config["speed_increase"])
            
            if ball.rect.colliderect(ai_paddle.rect):
                ball.vx = -abs(ball.vx)
                ball.vy += random.uniform(-2, 2)
                ball.create_particles(level_config["particles"], NEON_RED)
                total_rallies += 1
                # Aumenta velocidade a cada rebatida
                ball.increase_speed(level_config["speed_increase"])
                # IA também fica mais rápida
                if total_rallies % 3 == 0:  # A cada 3 rebatidas
                    ai_paddle.rect.height = max(60, ai_paddle.rect.height - 2)  # Raquete da IA fica menor
            
            # Pontuação
            if ball.rect.left <= 0:
                ai_score += 1
                ball.reset(level_config)
                ball.create_particles(level_config["particles"] * 2, NEON_RED)
            
            if ball.rect.right >= SCREEN_WIDTH:
                player_score += 1
                ball.reset(level_config)
                ball.create_particles(level_config["particles"] * 2, level_config["color"])
            
            # Verifica vitória/derrota
            if player_score >= level_config["win_score"]:
                cap.release()
                cv2.destroyAllWindows()
                return True, current_level + 1  # Próximo nível
            
            if ai_score >= level_config["win_score"]:
                cap.release()
                cv2.destroyAllWindows()
                return False, current_level  # Mesma fase
            
            # --- Renderização ---
            screen.fill(DARK_BG)
            
            # Grid de fundo
            for i in range(0, SCREEN_WIDTH, 100):
                alpha = 20
                pygame.draw.line(screen, (30, 30, 60), (i, 0), (i, SCREEN_HEIGHT), 1)
            for i in range(0, SCREEN_HEIGHT, 100):
                pygame.draw.line(screen, (30, 30, 60), (0, i), (SCREEN_WIDTH, i), 1)
            
            # Linha central
            for i in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.line(screen, level_config["color"], 
                               (SCREEN_WIDTH // 2, i), (SCREEN_WIDTH // 2, i + 20), 3)
            
            # Objetos
            player_paddle.draw(screen)
            ai_paddle.draw(screen)
            ball.draw(screen)
            
            # HUD
            hud_height = 100
            s = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
            pygame.draw.rect(s, (10, 10, 25, 200), (0, 0, SCREEN_WIDTH, hud_height))
            screen.blit(s, (0, 0))
            
            # Placar
            draw_text(screen, str(player_score), font_large, level_config["color"], 
                     SCREEN_WIDTH // 4, 50)
            draw_text(screen, str(ai_score), font_large, NEON_RED, 
                     SCREEN_WIDTH * 3 // 4, 50)
            
            # Informações do nível
            draw_text(screen, f"NÍVEL {current_level}: {level_config['name']}", 
                     font_small, level_config["color"], SCREEN_WIDTH // 2, 30, glow=False)
            draw_text(screen, f"Primeiro a {level_config['win_score']}", 
                     font_tiny, (150, 150, 180), SCREEN_WIDTH // 2, 70, glow=False)
            
            # Indicador de velocidade (parte inferior)
            speed_text = f"VELOCIDADE: {ball.speed_multiplier:.1f}x"
            speed_color = NEON_GREEN if ball.speed_multiplier < 1.5 else NEON_YELLOW if ball.speed_multiplier < 2.0 else NEON_RED
            draw_text(screen, speed_text, font_tiny, speed_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, glow=False)
            
            # Indicador de status da detecção (sem webcam embutida)
            status_x = SCREEN_WIDTH - 200
            status_y = 130
            status_color = NEON_GREEN if face_detected else NEON_RED
            status_text = "👁️ OLHO OK" if face_detected else "❌ SEM DETECÇÃO"
            draw_text(screen, status_text, font_tiny, status_color, status_x, status_y, glow=False)
            
            # Dica
            draw_text(screen, "Webcam à direita →", font_tiny, (150, 150, 180), 
                     status_x, status_y + 30, glow=False)
        
        else:
            # Tela de pausa
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "PAUSADO", font_title, NEON_CYAN, 
                     SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, "ESPAÇO para continuar", font_medium, (255, 255, 255), 
                     SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        
        pygame.display.flip()
        clock.tick(FPS)
        
        # Verifica se fechou a janela da webcam
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
    
    cap.release()
    cv2.destroyAllWindows()
    return False, current_level

def victory_screen(level):
    """Tela de vitória do nível"""
    level_config = LEVELS[level - 1]  # Level que acabou de vencer
    
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
        
        # Efeito de vitória
        for i in range(5):
            angle = time.time() * 2 + i * math.pi * 2 / 5
            x = SCREEN_WIDTH // 2 + int(200 * math.cos(angle))
            y = SCREEN_HEIGHT // 2 + int(200 * math.sin(angle))
            size = 30 + int(10 * abs(math.sin(time.time() * 3 + i)))
            pygame.draw.circle(screen, level_config["color"], (x, y), size)
        
        draw_text(screen, "🏆 VITÓRIA! 🏆", font_title, level_config["color"], 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        
        if level <= 5:
            draw_text(screen, f"Nível {level - 1} Completo!", font_large, (255, 255, 255), 
                     SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "ESPAÇO para próximo nível", font_medium, NEON_CYAN, 
                     SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        else:
            draw_text(screen, "VOCÊ COMPLETOU TODOS OS NÍVEIS!", font_large, NEON_PINK, 
                     SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "VOCÊ É LENDÁRIO!", font_medium, NEON_YELLOW, 
                     SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        pygame.display.flip()
        clock.tick(FPS)

def defeat_screen(level):
    """Tela de derrota"""
    level_config = LEVELS[level]
    
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
        
        draw_text(screen, "DERROTA", font_title, NEON_RED, 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        draw_text(screen, "Tente novamente!", font_large, (255, 255, 255), 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "ESPAÇO para tentar de novo | ESC para menu", font_medium, 
                 NEON_CYAN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        pygame.display.flip()
        clock.tick(FPS)

# --- Main ---
if __name__ == "__main__":
    print("🎮 PONG PRO - Edição Premium")
    print("=" * 50)
    
    try:
        current_level = 1
        
        while True:
            if not main_menu():
                break
            
            # Loop de níveis
            while current_level <= 5:
                # Introdução do nível
                if not level_intro(current_level):
                    break
                
                # Joga o nível
                won, next_level = game_loop(current_level)
                
                if won:
                    # Vitória
                    if not victory_screen(next_level):
                        break
                    current_level = next_level
                    
                    if current_level > 5:
                        # Completou todos os níveis!
                        current_level = 1
                        break
                else:
                    # Derrota
                    if not defeat_screen(current_level):
                        break
                    # Tenta o mesmo nível novamente
            
            # Reset para o menu
            current_level = 1
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
        print("👋 Obrigado por jogar!")
        sys.exit()
