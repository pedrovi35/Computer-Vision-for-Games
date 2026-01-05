"""
🕺 SIMON DIZ - Jogo de Poses Corporais
Copie as poses que o Simon mostrar!

Controles: Use seu corpo inteiro para fazer as poses
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
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480
FPS = 30

# Cores vibrantes
DARK_BG = (15, 20, 35)
CARD_BG = (35, 40, 55)
ACCENT_BLUE = (59, 130, 246)
ACCENT_GREEN = (16, 185, 129)
ACCENT_RED = (239, 68, 68)
ACCENT_YELLOW = (245, 158, 11)
ACCENT_PURPLE = (168, 85, 247)
ACCENT_PINK = (236, 72, 153)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (148, 163, 184)

# Configurações do jogo
POSE_DURATION = 5  # Segundos para fazer a pose
MAX_ROUNDS = 10

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🕺 Simon Diz - Jogo de Poses")
clock = pygame.time.Clock()

# Fontes
font_title = pygame.font.Font(None, 90)
font_large = pygame.font.Font(None, 70)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 40)
font_tiny = pygame.font.Font(None, 30)

# MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- Definição de Poses ---
POSES = {
    "T": {
        "name": "Letra T",
        "emoji": "🙆",
        "description": "Braços na horizontal",
        "check": lambda lm: check_t_pose(lm)
    },
    "Y": {
        "name": "Letra Y",
        "emoji": "🙌",
        "description": "Braços para cima em V",
        "check": lambda lm: check_y_pose(lm)
    },
    "squat": {
        "name": "Agachamento",
        "emoji": "🧘",
        "description": "Agache com braços para frente",
        "check": lambda lm: check_squat(lm)
    },
    "warrior": {
        "name": "Guerreiro",
        "emoji": "🧘‍♂️",
        "description": "Uma perna para trás, braços abertos",
        "check": lambda lm: check_warrior(lm)
    },
    "star": {
        "name": "Estrela",
        "emoji": "⭐",
        "description": "Pernas e braços abertos",
        "check": lambda lm: check_star(lm)
    },
    "flamingo": {
        "name": "Flamingo",
        "emoji": "🦩",
        "description": "Uma perna levantada",
        "check": lambda lm: check_flamingo(lm)
    },
    "airplane": {
        "name": "Avião",
        "emoji": "✈️",
        "description": "Inclinado com braços abertos",
        "check": lambda lm: check_airplane(lm)
    },
    "dab": {
        "name": "Dab",
        "emoji": "💪",
        "description": "Dab clássico!",
        "check": lambda lm: check_dab(lm)
    }
}

# --- Funções de Detecção de Poses ---
def get_angle(a, b, c):
    """Calcula ângulo entre três pontos"""
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(math.degrees(radians))
    if angle > 180:
        angle = 360 - angle
    return angle

def check_t_pose(landmarks):
    """Verifica pose em T"""
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    
    left_angle = get_angle(left_wrist, left_elbow, left_shoulder)
    right_angle = get_angle(right_wrist, right_elbow, right_shoulder)
    
    # Braços devem estar retos (próximo de 180°) e na horizontal
    return left_angle > 160 and right_angle > 160 and left_wrist[1] < left_elbow[1] + 0.1

def check_y_pose(landmarks):
    """Verifica pose em Y"""
    nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
            landmarks[mp_pose.PoseLandmark.NOSE.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    
    # Mãos devem estar acima da cabeça
    return left_wrist[1] < nose[1] and right_wrist[1] < nose[1]

def check_squat(landmarks):
    """Verifica agachamento"""
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    
    angle = get_angle(left_hip, left_knee, left_ankle)
    # Joelho dobrado (menos de 120°)
    return angle < 120

def check_warrior(landmarks):
    """Verifica pose do guerreiro"""
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y
    
    # Uma perna mais atrás e braços abertos
    return abs(left_ankle - right_ankle) > 0.15 and left_wrist < 0.7 and right_wrist < 0.7

def check_star(landmarks):
    """Verifica pose em estrela"""
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x
    
    # Pernas e braços bem abertos
    leg_spread = abs(left_ankle - right_ankle)
    arm_spread = abs(left_wrist - right_wrist)
    return leg_spread > 0.3 and arm_spread > 0.6

def check_flamingo(landmarks):
    """Verifica pose de flamingo"""
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y
    
    # Uma perna levantada
    return abs(left_ankle - right_ankle) > 0.2 or abs(left_knee - right_knee) > 0.15

def check_airplane(landmarks):
    """Verifica pose de avião"""
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value].y
    hip = (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y + 
           landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2
    
    # Corpo inclinado para frente
    return nose < hip - 0.1

def check_dab(landmarks):
    """Verifica dab"""
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
            landmarks[mp_pose.PoseLandmark.NOSE.value].y]
    
    # Uma mão perto do rosto
    distance = math.sqrt((left_wrist[0] - nose[0])**2 + (left_wrist[1] - nose[1])**2)
    return distance < 0.2

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
    pygame.draw.rect(surface, (55, 60, 75), (x, y, width, height), 3, border_radius=20)

def draw_progress_bar(surface, x, y, width, height, progress, color=ACCENT_BLUE):
    # Fundo
    draw_rounded_rect(surface, (30, 35, 50), (x, y, width, height), 10)
    # Progresso
    if progress > 0:
        prog_width = int(width * progress)
        draw_rounded_rect(surface, color, (x, y, prog_width, height), 10)

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
        draw_text(screen, "🕺 SIMON DIZ 🕺", font_title, ACCENT_PINK, 
                  SCREEN_WIDTH//2, title_y)
        
        # Subtítulo
        draw_text(screen, "Jogo de Poses Corporais", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH//2, title_y + 70)
        
        # Card de instruções
        card_x = SCREEN_WIDTH//2 - 500
        card_y = 300
        draw_card(screen, card_x, card_y, 1000, 450)
        
        instructions = [
            "Como Jogar:",
            "",
            "👀 Simon mostrará uma pose",
            "🏃 Você tem 5 segundos para copiar",
            "✅ Complete 10 rodadas para vencer!",
            "",
            "Fique longe o suficiente para aparecer inteiro na câmera",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 40
        for i, text in enumerate(instructions):
            if i == 0 or i == 8:
                color = TEXT_PRIMARY
                font = font_medium
            elif i == 6:
                color = ACCENT_YELLOW
                font = font_small
            else:
                color = TEXT_SECONDARY
                font = font_small
            
            draw_text(screen, text, font, color, SCREEN_WIDTH//2, y_offset, True)
            y_offset += 55 if i == 0 or i == 5 or i == 7 else 48
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    """Loop principal do jogo"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return 0
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)
    
    # Estado do jogo
    score = 0
    round_num = 0
    current_pose = None
    round_start_time = 0
    feedback = ""
    feedback_time = 0
    pose_detected_frames = 0
    
    running = True
    
    while running and round_num < MAX_ROUNDS:
        # Nova rodada
        if current_pose is None:
            round_num += 1
            current_pose = random.choice(list(POSES.keys()))
            round_start_time = time.time()
            pose_detected_frames = 0
            feedback = ""
        
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
        pose_correct = False
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
            )
            
            pose_info = POSES[current_pose]
            pose_correct = pose_info["check"](results.pose_landmarks.landmark)
            
            if pose_correct:
                pose_detected_frames += 1
            else:
                pose_detected_frames = max(0, pose_detected_frames - 1)
        
        # Verifica tempo e acerto
        elapsed = time.time() - round_start_time
        time_left = max(0, POSE_DURATION - elapsed)
        
        if pose_detected_frames >= 15:  # ~0.5 segundo na pose
            score += 100
            feedback = "✅ ACERTOU!"
            feedback_time = time.time()
            current_pose = None
        elif elapsed >= POSE_DURATION:
            feedback = "❌ TEMPO ESGOTADO"
            feedback_time = time.time()
            current_pose = None
        
        # --- Renderização ---
        screen.fill(DARK_BG)
        
        # Webcam (grande, centralizada)
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH * 1.5, WEBCAM_HEIGHT * 1.5))
        webcam_x = (SCREEN_WIDTH - WEBCAM_WIDTH * 1.5) // 2
        webcam_y = 180
        screen.blit(frame_surface, (webcam_x, webcam_y))
        
        # Borda colorida indicando detecção
        border_color = ACCENT_GREEN if pose_correct else ACCENT_RED
        pygame.draw.rect(screen, border_color, 
                         (webcam_x, webcam_y, WEBCAM_WIDTH * 1.5, WEBCAM_HEIGHT * 1.5), 5)
        
        # HUD superior
        hud_height = 100
        draw_card(screen, 20, 20, SCREEN_WIDTH - 40, hud_height, (25, 30, 45))
        
        # Rodada
        draw_text(screen, f"Rodada {round_num}/{MAX_ROUNDS}", font_medium, TEXT_PRIMARY, 150, 70)
        
        # Pontuação
        draw_text(screen, f"Pontos: {score}", font_medium, ACCENT_YELLOW, SCREEN_WIDTH//2, 70)
        
        # Tempo
        time_color = ACCENT_GREEN if time_left > 2 else ACCENT_RED
        draw_text(screen, f"⏱️  {time_left:.1f}s", font_medium, time_color, SCREEN_WIDTH - 150, 70)
        
        # Card da pose atual
        if current_pose:
            pose_info = POSES[current_pose]
            card_y = SCREEN_HEIGHT - 220
            draw_card(screen, 50, card_y, 350, 180, CARD_BG)
            
            draw_text(screen, pose_info["emoji"], font_title, TEXT_PRIMARY, 225, card_y + 50)
            draw_text(screen, pose_info["name"], font_medium, TEXT_PRIMARY, 225, card_y + 120)
            draw_text(screen, pose_info["description"], font_small, TEXT_SECONDARY, 225, card_y + 160)
            
            # Barra de progresso da detecção
            if pose_detected_frames > 0:
                progress = min(1.0, pose_detected_frames / 15)
                draw_progress_bar(screen, 70, card_y + 15, 310, 15, progress, ACCENT_GREEN)
        
        # Feedback
        if feedback and (time.time() - feedback_time < 1.5):
            feedback_color = ACCENT_GREEN if "ACERTOU" in feedback else ACCENT_RED
            draw_text(screen, feedback, font_large, feedback_color, SCREEN_WIDTH//2, webcam_y - 60)
        
        # Dica
        draw_text(screen, "ESC para sair", font_tiny, TEXT_SECONDARY, SCREEN_WIDTH//2, SCREEN_HEIGHT - 30)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    return score

def show_results(score):
    """Mostra resultados finais"""
    max_score = MAX_ROUNDS * 100
    accuracy = (score / max_score) * 100 if max_score > 0 else 0
    
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
        card_x = SCREEN_WIDTH//2 - 500
        card_y = 150
        draw_card(screen, card_x, card_y, 1000, 600)
        
        # Título
        draw_text(screen, "🎉 JOGO FINALIZADO! 🎉", font_title, ACCENT_PINK, 
                  SCREEN_WIDTH//2, card_y + 80)
        
        # Pontuação
        draw_text(screen, "PONTUAÇÃO FINAL", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH//2, card_y + 200)
        draw_text(screen, f"{score} / {max_score}", font_large, ACCENT_YELLOW, 
                  SCREEN_WIDTH//2, card_y + 270)
        
        # Precisão
        draw_text(screen, f"Precisão: {accuracy:.0f}%", font_medium, ACCENT_CYAN, 
                  SCREEN_WIDTH//2, card_y + 360)
        
        # Avaliação
        if accuracy >= 90:
            rating = "🏆 MESTRE DAS POSES! 🏆"
            rating_color = ACCENT_PURPLE
        elif accuracy >= 70:
            rating = "⭐ ÓTIMO DESEMPENHO! ⭐"
            rating_color = ACCENT_GREEN
        elif accuracy >= 50:
            rating = "👍 BOM TRABALHO! 👍"
            rating_color = ACCENT_BLUE
        else:
            rating = "💪 CONTINUE PRATICANDO!"
            rating_color = TEXT_SECONDARY
        
        draw_text(screen, rating, font_large, rating_color, 
                  SCREEN_WIDTH//2, card_y + 460)
        
        # Instruções
        draw_text(screen, "ESPAÇO para jogar novamente  |  ESC para sair", 
                  font_small, TEXT_SECONDARY, SCREEN_WIDTH//2, card_y + 560)
        
        pygame.display.flip()
        clock.tick(FPS)

# --- Main ---
if __name__ == "__main__":
    try:
        while True:
            if main_menu():
                score = game_loop()
                if not show_results(score):
                    break
            else:
                break
    finally:
        pygame.quit()
        sys.exit()

