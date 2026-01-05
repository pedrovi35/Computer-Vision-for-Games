"""
🎮 PEDRA, PAPEL, TESOURA - Com Visão Computacional
Jogue contra o computador usando gestos das mãos!

Gestos:
- ✊ PEDRA: Mão fechada
- ✋ PAPEL: Mão aberta (5 dedos)
- ✌️ TESOURA: 2 dedos levantados
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

# --- Configurações ---
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480
FPS = 30

# Cores modernas
DARK_BG = (20, 20, 30)
CARD_BG = (40, 44, 52)
ACCENT_BLUE = (66, 135, 245)
ACCENT_GREEN = (76, 175, 80)
ACCENT_RED = (244, 67, 54)
ACCENT_YELLOW = (255, 193, 7)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (160, 160, 180)

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("✊✋✌️ Pedra, Papel, Tesoura")
clock = pygame.time.Clock()

# Fontes modernas
font_title = pygame.font.Font(None, 80)
font_large = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)
font_tiny = pygame.font.Font(None, 28)

# MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# --- Funções de UI ---
def draw_rounded_rect(surface, color, rect, radius=20):
    """Desenha retângulo com cantos arredondados"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_text(surface, text, font, color, x, y, center=True):
    """Desenha texto com sombra"""
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

def draw_card(surface, x, y, width, height, color=CARD_BG):
    """Desenha um card moderno"""
    draw_rounded_rect(surface, color, (x, y, width, height), 15)
    # Borda sutil
    pygame.draw.rect(surface, (60, 64, 72), (x, y, width, height), 2, border_radius=15)

def draw_emoji(surface, emoji, x, y, size=100):
    """Desenha emoji grande"""
    emoji_font = pygame.font.Font(None, size)
    draw_text(surface, emoji, emoji_font, TEXT_PRIMARY, x, y, True)

def draw_progress_bar(surface, x, y, width, height, progress, color=ACCENT_BLUE):
    """Desenha barra de progresso moderna"""
    # Fundo
    draw_rounded_rect(surface, (30, 34, 42), (x, y, width, height), 10)
    # Progresso
    if progress > 0:
        prog_width = int(width * progress)
        draw_rounded_rect(surface, color, (x, y, prog_width, height), 10)

# --- Detecção de Gestos ---
def count_fingers(hand_landmarks):
    """Conta dedos levantados"""
    if not hand_landmarks:
        return 0
    
    # IDs dos landmarks
    finger_tips = [8, 12, 16, 20]  # Indicador, médio, anelar, mindinho
    finger_pips = [6, 10, 14, 18]
    
    fingers_up = 0
    
    # Polegar (especial)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers_up += 1
    
    # Outros dedos
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers_up += 1
    
    return fingers_up

def detect_gesture(hand_landmarks):
    """Detecta o gesto: pedra, papel ou tesoura"""
    if not hand_landmarks:
        return None
    
    fingers = count_fingers(hand_landmarks)
    
    if fingers == 0:
        return "pedra"
    elif fingers == 5:
        return "papel"
    elif fingers == 2:
        return "tesoura"
    return None

def get_winner(player, computer):
    """Determina o vencedor"""
    if player == computer:
        return "empate"
    
    wins = {
        "pedra": "tesoura",
        "papel": "pedra",
        "tesoura": "papel"
    }
    
    if wins[player] == computer:
        return "player"
    return "computer"

# --- Telas ---
def main_menu():
    """Tela inicial moderna"""
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
        
        # Título com animação
        title_y = 150 + int(10 * np.sin(time.time() * 2))
        draw_text(screen, "✊ ✋ ✌️", font_title, ACCENT_YELLOW, SCREEN_WIDTH//2, title_y)
        draw_text(screen, "PEDRA, PAPEL, TESOURA", font_large, TEXT_PRIMARY, 
                  SCREEN_WIDTH//2, title_y + 80)
        
        # Card de instruções
        card_x = SCREEN_WIDTH//2 - 400
        card_y = 350
        draw_card(screen, card_x, card_y, 800, 350)
        
        instructions = [
            "Como Jogar:",
            "",
            "✊  PEDRA: Feche a mão",
            "✋  PAPEL: Abra a mão (5 dedos)",
            "✌️  TESOURA: Mostre 2 dedos",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 40
        for i, text in enumerate(instructions):
            color = TEXT_PRIMARY if i == 0 or i == 6 else TEXT_SECONDARY
            font = font_medium if i == 0 or i == 6 else font_small
            draw_text(screen, text, font, color, SCREEN_WIDTH//2, y_offset, True)
            y_offset += 50 if i == 0 or i == 5 else 45
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    """Loop principal do jogo"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)
    
    # Estatísticas
    player_score = 0
    computer_score = 0
    ties = 0
    rounds_played = 0
    
    # Estado do jogo
    game_state = "waiting"  # waiting, countdown, showing, result
    countdown_start = 0
    result_start = 0
    player_gesture = None
    computer_gesture = None
    last_result = None
    
    gesture_history = []  # Para suavizar detecção
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and game_state == "waiting":
                    game_state = "countdown"
                    countdown_start = time.time()
                    gesture_history = []
        
        # Captura e processa frame
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Detecta gesto
        current_gesture = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_gesture = detect_gesture(hand_landmarks)
        
        # Suavização de detecção
        if current_gesture:
            gesture_history.append(current_gesture)
            if len(gesture_history) > 5:
                gesture_history.pop(0)
        
        # Lógica do jogo
        current_time = time.time()
        
        if game_state == "countdown":
            elapsed = current_time - countdown_start
            if elapsed >= 3:
                # Captura gesto do jogador
                if gesture_history:
                    player_gesture = max(set(gesture_history), key=gesture_history.count)
                else:
                    player_gesture = None
                
                computer_gesture = random.choice(["pedra", "papel", "tesoura"])
                game_state = "showing"
                result_start = current_time
                
                # Calcula resultado
                if player_gesture:
                    last_result = get_winner(player_gesture, computer_gesture)
                    rounds_played += 1
                    if last_result == "player":
                        player_score += 1
                    elif last_result == "computer":
                        computer_score += 1
                    else:
                        ties += 1
                else:
                    last_result = "no_gesture"
        
        elif game_state == "showing":
            if current_time - result_start >= 3:
                game_state = "waiting"
                player_gesture = None
                computer_gesture = None
        
        # --- Renderização ---
        screen.fill(DARK_BG)
        
        # Webcam
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        pygame.draw.rect(screen, ACCENT_BLUE, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 3)
        
        # Placar
        score_y = 50
        draw_text(screen, "VOCÊ", font_medium, ACCENT_GREEN, 200, score_y)
        draw_text(screen, str(player_score), font_title, TEXT_PRIMARY, 200, score_y + 60)
        
        draw_text(screen, "COMPUTADOR", font_medium, ACCENT_RED, 520, score_y)
        draw_text(screen, str(computer_score), font_title, TEXT_PRIMARY, 520, score_y + 60)
        
        # Estatísticas
        stats_y = score_y + 140
        draw_text(screen, f"Empates: {ties}  |  Rodadas: {rounds_played}", 
                  font_small, TEXT_SECONDARY, 360, stats_y)
        
        # Área de jogo
        game_area_y = 250
        
        if game_state == "waiting":
            draw_card(screen, 50, game_area_y, 700, 400)
            draw_text(screen, "Pronto para jogar?", font_large, TEXT_PRIMARY, 400, game_area_y + 80)
            draw_emoji(screen, "👋", 400, game_area_y + 180, 120)
            draw_text(screen, "Pressione ESPAÇO", font_medium, ACCENT_YELLOW, 400, game_area_y + 300)
            
            # Mostrar gesto detectado
            if current_gesture:
                gesture_emojis = {"pedra": "✊", "papel": "✋", "tesoura": "✌️"}
                draw_text(screen, f"Detectado: {gesture_emojis.get(current_gesture, '❓')}", 
                          font_small, ACCENT_GREEN, 400, game_area_y + 360)
        
        elif game_state == "countdown":
            elapsed = current_time - countdown_start
            remaining = 3 - int(elapsed)
            
            draw_card(screen, 50, game_area_y, 700, 400)
            draw_text(screen, "Prepare seu gesto!", font_large, TEXT_PRIMARY, 400, game_area_y + 60)
            
            # Countdown grande
            countdown_color = ACCENT_YELLOW if remaining > 1 else ACCENT_RED
            draw_text(screen, str(remaining), font_title, countdown_color, 400, game_area_y + 180, True)
            
            # Barra de progresso
            progress = elapsed / 3
            draw_progress_bar(screen, 100, game_area_y + 320, 600, 30, progress, countdown_color)
            
            # Mostrar gesto atual
            if current_gesture:
                gesture_emojis = {"pedra": "✊", "papel": "✋", "tesoura": "✌️"}
                draw_emoji(screen, gesture_emojis.get(current_gesture, "❓"), 400, game_area_y + 240, 80)
        
        elif game_state == "showing":
            draw_card(screen, 50, game_area_y, 700, 400)
            
            gesture_emojis = {"pedra": "✊", "papel": "✋", "tesoura": "✌️"}
            
            # Gestos
            draw_text(screen, "VOCÊ", font_medium, TEXT_SECONDARY, 200, game_area_y + 50)
            if player_gesture:
                draw_emoji(screen, gesture_emojis[player_gesture], 200, game_area_y + 150, 120)
            else:
                draw_emoji(screen, "❓", 200, game_area_y + 150, 120)
            
            draw_text(screen, "VS", font_large, TEXT_SECONDARY, 400, game_area_y + 150)
            
            draw_text(screen, "PC", font_medium, TEXT_SECONDARY, 600, game_area_y + 50)
            draw_emoji(screen, gesture_emojis[computer_gesture], 600, game_area_y + 150, 120)
            
            # Resultado
            result_y = game_area_y + 300
            if last_result == "player":
                draw_text(screen, "🎉 VOCÊ VENCEU! 🎉", font_large, ACCENT_GREEN, 400, result_y)
            elif last_result == "computer":
                draw_text(screen, "😅 COMPUTADOR VENCEU", font_large, ACCENT_RED, 400, result_y)
            elif last_result == "empate":
                draw_text(screen, "🤝 EMPATE!", font_large, ACCENT_YELLOW, 400, result_y)
            else:
                draw_text(screen, "❌ Nenhum gesto detectado", font_large, ACCENT_RED, 400, result_y)
        
        # Instruções no rodapé
        footer_y = SCREEN_HEIGHT - 50
        draw_text(screen, "ESC para sair  |  ESPAÇO para jogar", 
                  font_tiny, TEXT_SECONDARY, SCREEN_WIDTH//2, footer_y)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()

# --- Main ---
if __name__ == "__main__":
    try:
        if main_menu():
            game_loop()
    finally:
        pygame.quit()
        sys.exit()

