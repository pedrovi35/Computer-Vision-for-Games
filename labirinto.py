"""
🧩 LABIRINTO - Controlado por Posição do Rosto
Mova seu rosto para controlar o jogador pelo labirinto!

Controles: Mova seu rosto na direção desejada para guiar o personagem
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

# Cores vibrantes
DARK_BG = (10, 15, 25)
WALL_COLOR = (45, 55, 72)
PATH_COLOR = (20, 25, 35)
CARD_BG = (30, 34, 42)
PLAYER_COLOR = (52, 211, 153)  # Verde água
START_COLOR = (59, 130, 246)  # Azul
END_COLOR = (251, 191, 36)  # Amarelo
ACCENT_PURPLE = (168, 85, 247)
ACCENT_PINK = (236, 72, 153)
ACCENT_GREEN = (16, 185, 129)
ACCENT_CYAN = (6, 182, 212)
ACCENT_RED = (239, 68, 68)
ACCENT_YELLOW = (245, 158, 11)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (148, 163, 184)

# Configurações do jogo
CELL_SIZE = 60
MAZE_COLS = 19
MAZE_ROWS = 13
PLAYER_SPEED = 5

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🧩 Labirinto - Controle por Rosto")
clock = pygame.time.Clock()

# Fontes
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

# --- Gerador de Labirinto ---
class MazeGenerator:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def generate(self):
        """Gera labirinto usando algoritmo de backtracking"""
        stack = []
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = 0
        stack.append((start_x, start_y))
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            
            # Verifica vizinhos não visitados
            for dx, dy in [(0, -2), (2, 0), (0, 2), (-2, 0)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.cols - 1 and 0 < ny < self.rows - 1:
                    if self.grid[ny][nx] == 1:
                        neighbors.append((nx, ny, dx//2, dy//2))
            
            if neighbors:
                nx, ny, mx, my = random.choice(neighbors)
                self.grid[ny][nx] = 0
                self.grid[y + my][x + mx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Garante entrada e saída
        self.grid[1][0] = 0  # Entrada
        self.grid[self.rows - 2][self.cols - 1] = 0  # Saída
        
        return self.grid

# --- Classes ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.radius = CELL_SIZE // 3
        self.trail = []
        self.max_trail = 30
    
    def move(self, dx, dy, maze):
        """Move o jogador suavemente"""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Verifica colisão com paredes
        cell_x = int(new_x // CELL_SIZE)
        cell_y = int(new_y // CELL_SIZE)
        
        if 0 <= cell_x < MAZE_COLS and 0 <= cell_y < MAZE_ROWS:
            if maze[cell_y][cell_x] == 0:
                self.x = new_x
                self.y = new_y
                
                # Adiciona ao rastro
                self.trail.append((int(self.x), int(self.y)))
                if len(self.trail) > self.max_trail:
                    self.trail.pop(0)
    
    def draw(self, surface, offset_x, offset_y):
        """Desenha o jogador com efeito brilhante"""
        draw_x = int(offset_x + self.x)
        draw_y = int(offset_y + self.y)
        
        # Rastro
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = int(self.radius * (0.5 + 0.5 * i / len(self.trail)))
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*PLAYER_COLOR, alpha), (size, size), size)
            surface.blit(s, (offset_x + tx - size, offset_y + ty - size))
        
        # Brilho
        for i in range(3):
            size = self.radius + (3-i) * 8
            alpha = 50 + int(30 * abs(math.sin(time.time() * 3)))
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*PLAYER_COLOR, alpha), (size, size), size)
            surface.blit(s, (draw_x - size, draw_y - size))
        
        # Corpo principal
        pygame.draw.circle(surface, PLAYER_COLOR, (draw_x, draw_y), self.radius)
        pygame.draw.circle(surface, TEXT_PRIMARY, (draw_x, draw_y), self.radius - 5)
        pygame.draw.circle(surface, PLAYER_COLOR, (draw_x, draw_y), self.radius - 10)
        
        # Olhos
        eye_offset = 5
        pygame.draw.circle(surface, TEXT_PRIMARY, (draw_x - eye_offset, draw_y - 3), 3)
        pygame.draw.circle(surface, TEXT_PRIMARY, (draw_x + eye_offset, draw_y - 3), 3)

# --- Funções de UI ---
def draw_rounded_rect(surface, color, rect, radius=20):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_text(surface, text, font, color, x, y, center=True):
    text_obj = font.render(text, True, (0, 0, 0))
    if center:
        rect = text_obj.get_rect(center=(x+2, y+2))
    else:
        rect = (x+2, y+2)
    surface.blit(text_obj, rect)
    
    text_obj = font.render(text, True, color)
    if center:
        rect = text_obj.get_rect(center=(x, y))
    else:
        rect = (x, y)
    surface.blit(text_obj, rect)

def draw_card(surface, x, y, width, height, color=(30, 34, 42)):
    draw_rounded_rect(surface, color, (x, y, width, height), 20)
    pygame.draw.rect(surface, (50, 54, 62), (x, y, width, height), 3, border_radius=20)

def draw_maze(surface, maze, offset_x, offset_y, player):
    """Desenha o labirinto com efeitos visuais"""
    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            x = offset_x + col * CELL_SIZE
            y = offset_y + row * CELL_SIZE
            
            if maze[row][col] == 1:
                # Parede com gradiente
                color_variation = int(10 * math.sin(col + row))
                wall_color = tuple(max(0, min(255, c + color_variation)) for c in WALL_COLOR)
                pygame.draw.rect(surface, wall_color, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(surface, (60, 70, 87), (x, y, CELL_SIZE, CELL_SIZE), 1)
            else:
                # Caminho
                pygame.draw.rect(surface, PATH_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
    
    # Entrada
    start_x = offset_x + 0 * CELL_SIZE
    start_y = offset_y + 1 * CELL_SIZE
    pygame.draw.rect(surface, START_COLOR, (start_x, start_y, CELL_SIZE, CELL_SIZE))
    draw_text(surface, "🏁", font_small, TEXT_PRIMARY, 
              start_x + CELL_SIZE//2, start_y + CELL_SIZE//2)
    
    # Saída
    end_x = offset_x + (MAZE_COLS - 1) * CELL_SIZE
    end_y = offset_y + (MAZE_ROWS - 2) * CELL_SIZE
    
    # Efeito pulsante na saída
    pulse = abs(math.sin(time.time() * 3)) * 10
    s = pygame.Surface((CELL_SIZE + int(pulse*2), CELL_SIZE + int(pulse*2)), pygame.SRCALPHA)
    pygame.draw.rect(s, (*END_COLOR, 100), (0, 0, CELL_SIZE + int(pulse*2), CELL_SIZE + int(pulse*2)))
    surface.blit(s, (end_x - int(pulse), end_y - int(pulse)))
    
    pygame.draw.rect(surface, END_COLOR, (end_x, end_y, CELL_SIZE, CELL_SIZE))
    draw_text(surface, "🏆", font_small, TEXT_PRIMARY, 
              end_x + CELL_SIZE//2, end_y + CELL_SIZE//2)

def detect_face_movement(face_landmarks, frame_width, frame_height, center_x, center_y):
    """Detecta movimento do rosto na tela para controle em 4 direções"""
    if not face_landmarks:
        return 0, 0
    
    # Ponto do nariz (centro do rosto)
    nose = face_landmarks.landmark[1]
    
    # Posição atual do nariz em pixels
    nose_x = nose.x * frame_width
    nose_y = nose.y * frame_height
    
    # Calcula diferença do centro calibrado
    diff_x = nose_x - center_x
    diff_y = nose_y - center_y
    
    # Define zonas mortas (deadzone) para evitar tremores
    deadzone = 30  # pixels
    sensitivity = 0.3  # Multiplicador de sensibilidade
    
    # Movimento horizontal
    dx = 0
    if abs(diff_x) > deadzone:
        dx = (diff_x - deadzone * (1 if diff_x > 0 else -1)) * sensitivity
    
    # Movimento vertical (invertido porque Y cresce para baixo)
    dy = 0
    if abs(diff_y) > deadzone:
        dy = -(diff_y - deadzone * (1 if diff_y > 0 else -1)) * sensitivity
    
    return dx, dy

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
        draw_text(screen, "🧩 LABIRINTO 🧩", font_title, ACCENT_PURPLE, 
                  SCREEN_WIDTH//2, title_y)
        
        # Subtítulo
        draw_text(screen, "Controle por Posição do Rosto", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH//2, title_y + 70)
        
        # Card de instruções
        card_x = SCREEN_WIDTH//2 - 500
        card_y = 300
        draw_card(screen, card_x, card_y, 1000, 450)
        
        instructions = [
            "Como Jogar:",
            "",
            "👤 Posicione seu rosto na webcam",
            "⬅️➡️  MOVA seu rosto para ESQUERDA/DIREITA",
            "⬆️⬇️  MOVA para CIMA/BAIXO",
            "🏁 Comece no ponto azul",
            "🏆 Chegue até o troféu dourado!",
            "",
            "DICA: Mova suavemente seu rosto!",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 40
        for i, text in enumerate(instructions):
            # Título, dica e último item em destaque
            if i == 0:
                color = TEXT_PRIMARY
                font = font_medium
            elif i == 8 or i == 10:  # DICA e botão
                color = ACCENT_YELLOW if i == 8 else TEXT_PRIMARY
                font = font_small
            else:
                color = TEXT_SECONDARY
                font = font_small
            
            draw_text(screen, text, font, color, SCREEN_WIDTH//2, y_offset, True)
            y_offset += 50 if i == 0 or i == 7 or i == 9 else 40
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    """Loop principal do jogo"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return False
    
    # Gera labirinto
    maze_gen = MazeGenerator(MAZE_COLS, MAZE_ROWS)
    maze = maze_gen.generate()
    
    # Cria jogador
    player = Player(CELL_SIZE // 2, CELL_SIZE * 1.5)
    
    # Posição do labirinto na tela
    maze_width = MAZE_COLS * CELL_SIZE
    maze_height = MAZE_ROWS * CELL_SIZE
    maze_offset_x = (SCREEN_WIDTH - maze_width) // 2
    maze_offset_y = (SCREEN_HEIGHT - maze_height) // 2 + 50
    
    # Tempo
    start_time = time.time()
    
    # Calibração do centro do rosto
    calibration_frames = 30
    calibration_counter = 0
    center_face_x = 0
    center_face_y = 0
    calibrated = False
    
    running = True
    won = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # Reinicia
                    maze = maze_gen.generate()
                    player = Player(CELL_SIZE // 2, CELL_SIZE * 1.5)
                    start_time = time.time()
                    won = False
        
        # Captura frame
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        
        h, w = frame.shape[:2]
        
        # Detecta movimentos do rosto
        dx, dy = 0, 0
        face_detected = False
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_detected = True
                
                # Calibração inicial - captura posição central
                if not calibrated:
                    nose = face_landmarks.landmark[1]
                    center_face_x += nose.x * w
                    center_face_y += nose.y * h
                    calibration_counter += 1
                    
                    if calibration_counter >= calibration_frames:
                        center_face_x /= calibration_frames
                        center_face_y /= calibration_frames
                        calibrated = True
                    
                    # Mostra mensagem de calibração
                    cv2.putText(frame, f"CALIBRANDO... {calibration_counter}/{calibration_frames}", 
                               (w//2 - 150, h//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                else:
                    # Detecta movimento
                    dx, dy = detect_face_movement(face_landmarks, w, h, center_face_x, center_face_y)
                    
                    # Desenha indicadores na webcam
                    nose = face_landmarks.landmark[1]
                    nose_x = int(nose.x * w)
                    nose_y = int(nose.y * h)
                    
                    # Círculo no nariz
                    cv2.circle(frame, (nose_x, nose_y), 10, (0, 255, 0), -1)
                    
                    # Centro calibrado
                    cv2.circle(frame, (int(center_face_x), int(center_face_y)), 5, (255, 255, 0), -1)
                    cv2.circle(frame, (int(center_face_x), int(center_face_y)), 30, (255, 255, 0), 2)
                    
                    # Linhas de direção
                    if abs(dx) > 1 or abs(dy) > 1:
                        end_x = int(nose_x + dx * 3)
                        end_y = int(nose_y - dy * 3)
                        cv2.arrowedLine(frame, (nose_x, nose_y), (end_x, end_y), 
                                       (0, 255, 255), 3, tipLength=0.3)
                    
                    # Texto de instrução
                    cv2.putText(frame, "Mova seu rosto", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Mostra valores de movimento
                    move_text = f"X:{dx:.1f} Y:{dy:.1f}"
                    cv2.putText(frame, move_text, (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # Sem rosto detectado - reseta calibração
            h, w = frame.shape[:2]
            cv2.putText(frame, "ROSTO NAO DETECTADO", (w//2 - 150, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            calibrated = False
            calibration_counter = 0
            center_face_x = 0
            center_face_y = 0
            dx, dy = 0, 0
        
        # Move jogador
        if not won and face_detected and calibrated:
            player.move(dx, dy, maze)
            
            # Verifica vitória
            end_cell_x = MAZE_COLS - 1
            end_cell_y = MAZE_ROWS - 2
            player_cell_x = int(player.x // CELL_SIZE)
            player_cell_y = int(player.y // CELL_SIZE)
            
            if player_cell_x == end_cell_x and player_cell_y == end_cell_y:
                won = True
                finish_time = time.time() - start_time
        
        # --- Renderização ---
        screen.fill(DARK_BG)
        
        # HUD superior
        hud_height = 80
        draw_card(screen, 20, 20, SCREEN_WIDTH - 40, hud_height, (25, 29, 37))
        
        # Título
        draw_text(screen, "🧩 LABIRINTO", font_large, ACCENT_PURPLE, 200, 60)
        
        # Tempo
        if not won:
            elapsed = time.time() - start_time
            draw_text(screen, f"⏱️  {int(elapsed)}s", font_medium, TEXT_SECONDARY, 
                      SCREEN_WIDTH - 200, 60)
        else:
            draw_text(screen, f"🏆 {int(finish_time)}s", font_medium, END_COLOR, 
                      SCREEN_WIDTH - 200, 60)
        
        # Instruções
        if not calibrated:
            draw_text(screen, "Aguarde calibração...", font_small, ACCENT_YELLOW, 
                     SCREEN_WIDTH//2, 60)
        else:
            draw_text(screen, "Mova seu rosto para controlar", font_small, TEXT_SECONDARY, 
                     SCREEN_WIDTH//2, 60)
        
        # Desenha labirinto
        draw_maze(screen, maze, maze_offset_x, maze_offset_y, player)
        
        # Desenha jogador
        player.draw(screen, maze_offset_x, maze_offset_y)
        
        # Mensagem de vitória
        if won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            card_x = SCREEN_WIDTH//2 - 400
            card_y = SCREEN_HEIGHT//2 - 200
            draw_card(screen, card_x, card_y, 800, 400, CARD_BG)
            
            draw_text(screen, "🎉 PARABÉNS! 🎉", font_title, END_COLOR, 
                      SCREEN_WIDTH//2, card_y + 100)
            draw_text(screen, f"Tempo: {int(finish_time)} segundos", font_large, TEXT_PRIMARY, 
                      SCREEN_WIDTH//2, card_y + 200)
            draw_text(screen, "R para recomeçar  |  ESC para sair", font_medium, TEXT_SECONDARY, 
                      SCREEN_WIDTH//2, card_y + 300)
        
        # Indicador de movimento (visual grande na tela)
        if face_detected and calibrated and not won:
            indicator_x = 150
            indicator_y = SCREEN_HEIGHT - 200
            
            # Card do indicador
            draw_card(screen, indicator_x - 80, indicator_y - 80, 160, 160, (25, 29, 37))
            
            # Círculo central
            pygame.draw.circle(screen, TEXT_SECONDARY, (indicator_x, indicator_y), 40, 2)
            pygame.draw.circle(screen, ACCENT_GREEN, (indicator_x, indicator_y), 10)
            
            # Setas de direção
            if abs(dx) > 1 or abs(dy) > 1:
                end_x = indicator_x + int(dx * 2)
                end_y = indicator_y - int(dy * 2)
                pygame.draw.line(screen, ACCENT_CYAN, (indicator_x, indicator_y), (end_x, end_y), 5)
                pygame.draw.circle(screen, ACCENT_CYAN, (end_x, end_y), 8)
            
            # Texto
            draw_text(screen, "Movimento", font_tiny, TEXT_SECONDARY, indicator_x, indicator_y - 100, True)
        
        # Webcam
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        
        # Borda colorida baseada em detecção
        border_color = ACCENT_GREEN if face_detected else ACCENT_RED
        pygame.draw.rect(screen, border_color, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 4)
        
        # Status da detecção
        status_text = "✓ Rosto OK" if face_detected else "✗ Posicione seu rosto"
        status_color = ACCENT_GREEN if face_detected else ACCENT_RED
        draw_text(screen, status_text, font_tiny, status_color, 
                  webcam_x + WEBCAM_WIDTH//2, webcam_y - 20, True)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    return True

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

