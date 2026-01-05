"""
🧠 MEMÓRIA DE GESTOS - Jogo de Sequência
Repita a sequência de gestos que aparece na tela!

Controles: Faça gestos com as mãos (Polegar, Paz, Ok, Rock)
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
WEBCAM_WIDTH = 400
WEBCAM_HEIGHT = 300
FPS = 30

# Cores modernas
DARK_BG = (15, 15, 30)
CARD_BG = (30, 35, 50)
ACCENT_CYAN = (0, 230, 255)
ACCENT_GREEN = (0, 255, 150)
ACCENT_PURPLE = (200, 100, 255)
ACCENT_ORANGE = (255, 150, 50)
ACCENT_PINK = (255, 100, 200)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (180, 180, 200)

# Configurações do jogo
GESTURE_DISPLAY_TIME = 1.5  # Segundos para mostrar cada gesto
PLAYER_TIME_LIMIT = 3.0  # Segundos para fazer cada gesto
STARTING_SEQUENCE = 3

# --- Inicialização ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🧠 Memória de Gestos")
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
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# --- Definição de Gestos ---
GESTOS = {
    "polegar": {
        "nome": "👍 Polegar",
        "cor": ACCENT_GREEN,
        "emoji": "👍",
        "descricao": "Polegar para cima"
    },
    "paz": {
        "nome": "✌️ Paz",
        "cor": ACCENT_CYAN,
        "emoji": "✌️",
        "descricao": "Sinal de paz"
    },
    "ok": {
        "nome": "👌 Ok",
        "cor": ACCENT_PURPLE,
        "emoji": "👌",
        "descricao": "Sinal de OK"
    },
    "rock": {
        "nome": "🤘 Rock",
        "cor": ACCENT_ORANGE,
        "emoji": "🤘",
        "descricao": "Sinal de rock"
    },
    "mao_aberta": {
        "nome": "✋ Mão Aberta",
        "cor": ACCENT_PINK,
        "emoji": "✋",
        "descricao": "Mão aberta (5 dedos)"
    }
}

# --- Detecção de Gestos ---
def count_fingers(hand_landmarks):
    """Conta dedos levantados"""
    if not hand_landmarks:
        return 0
    
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]
    
    fingers_up = 0
    
    # Polegar
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers_up += 1
    
    # Outros dedos
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers_up += 1
    
    return fingers_up

def detect_gesture(hand_landmarks):
    """Detecta qual gesto está sendo feito"""
    if not hand_landmarks:
        return None
    
    fingers = count_fingers(hand_landmarks)
    
    # Polegar: só polegar levantado
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    
    thumb_up = thumb_tip.y < hand_landmarks.landmark[3].y
    index_up = index_tip.y < hand_landmarks.landmark[6].y
    middle_up = middle_tip.y < hand_landmarks.landmark[10].y
    ring_up = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
    pinky_up = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
    
    # Mão aberta (5 dedos)
    if fingers == 5:
        return "mao_aberta"
    
    # Paz (2 dedos - indicador e médio)
    if fingers == 2 and index_up and middle_up and not ring_up:
        return "paz"
    
    # Rock (indicador e mindinho)
    if index_up and pinky_up and not middle_up and not ring_up:
        return "rock"
    
    # OK (polegar e indicador juntos formando círculo)
    thumb_index_dist = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
    if thumb_index_dist < 0.08 and fingers >= 3:
        return "ok"
    
    # Polegar para cima
    if fingers == 1 and thumb_up:
        return "polegar"
    
    return None

# --- UI ---
def draw_text(surface, text, font, color, x, y, center=True, shadow=True):
    if shadow:
        text_obj = font.render(text, True, (0, 0, 0))
        rect = text_obj.get_rect(center=(x+3, y+3)) if center else (x+3, y+3)
        surface.blit(text_obj, rect)
    
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(x, y)) if center else (x, y)
    surface.blit(text_obj, rect)

def draw_card(surface, x, y, width, height, color=CARD_BG, border_color=None):
    pygame.draw.rect(surface, color, (x, y, width, height), border_radius=20)
    if border_color:
        pygame.draw.rect(surface, border_color, (x, y, width, height), 4, border_radius=20)

def draw_gesture_card(surface, x, y, width, height, gesture_key, pulse=False):
    """Desenha um card com o gesto"""
    gesture = GESTOS[gesture_key]
    
    # Pulso de animação
    if pulse:
        pulse_val = abs(math.sin(time.time() * 5)) * 15
        x -= int(pulse_val / 2)
        y -= int(pulse_val / 2)
        width += int(pulse_val)
        height += int(pulse_val)
    
    # Card
    draw_card(surface, x, y, width, height, gesture["cor"], TEXT_PRIMARY)
    
    # Emoji grande
    emoji_font = pygame.font.Font(None, 120)
    draw_text(surface, gesture["emoji"], emoji_font, TEXT_PRIMARY, 
              x + width // 2, y + height // 2 - 20, True, False)
    
    # Nome
    draw_text(surface, gesture["nome"], font_small, TEXT_PRIMARY, 
              x + width // 2, y + height - 40, True, False)

# --- Telas ---
def main_menu():
    particles = []
    
    class Particle:
        def __init__(self):
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.size = random.randint(2, 5)
            self.color = random.choice([ACCENT_CYAN, ACCENT_GREEN, ACCENT_PURPLE, ACCENT_ORANGE])
            self.speed = random.uniform(0.5, 2)
        
        def update(self):
            self.y += self.speed
            if self.y > SCREEN_HEIGHT:
                self.y = 0
                self.x = random.randint(0, SCREEN_WIDTH)
        
        def draw(self, surf):
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)
    
    for _ in range(50):
        particles.append(Particle())
    
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
        
        for p in particles:
            p.update()
            p.draw(screen)
        
        title_y = 100 + int(15 * np.sin(time.time() * 2))
        draw_text(screen, "🧠 MEMÓRIA DE GESTOS 🧠", font_title, ACCENT_CYAN, 
                  SCREEN_WIDTH // 2, title_y)
        
        # Mostra os gestos disponíveis
        gestos_y = 250
        draw_text(screen, "Gestos Disponíveis:", font_medium, TEXT_PRIMARY, 
                  SCREEN_WIDTH // 2, gestos_y)
        
        gestures_list = list(GESTOS.keys())
        card_width = 150
        card_height = 180
        spacing = 20
        total_width = len(gestures_list) * (card_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, gesto_key in enumerate(gestures_list):
            x = start_x + i * (card_width + spacing)
            draw_gesture_card(screen, x, gestos_y + 60, card_width, card_height, gesto_key)
        
        # Instruções
        card_y = 550
        draw_card(screen, SCREEN_WIDTH // 2 - 450, card_y, 900, 280, CARD_BG, ACCENT_CYAN)
        
        instructions = [
            "Como Jogar:",
            "",
            "👀 Memorize a sequência de gestos",
            "✋ Repita a sequência na ordem correta",
            "🧠 A cada acerto, sequência aumenta!",
            "",
            "Pressione ESPAÇO para começar"
        ]
        
        y_offset = card_y + 40
        for i, text in enumerate(instructions):
            if i == 0 or i == 6:
                color = ACCENT_CYAN
                font = font_medium
            else:
                color = TEXT_PRIMARY
                font = font_small
            draw_text(screen, text, font, color, SCREEN_WIDTH // 2, y_offset, True, False)
            y_offset += 48 if i == 0 or i == 5 else 40
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return 0
    
    sequence = []
    player_sequence = []
    current_index = 0
    round_num = 0
    score = 0
    
    game_state = "showing"  # showing, waiting, correct, wrong
    state_start_time = time.time()
    gesture_history = []
    
    # Gera primeira sequência
    gestures_list = list(GESTOS.keys())
    for _ in range(STARTING_SEQUENCE):
        sequence.append(random.choice(gestures_list))
    
    show_index = 0
    
    running = True
    
    while running:
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
        
        # Detecta gesto
        current_gesture = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_gesture = detect_gesture(hand_landmarks)
                
                if current_gesture:
                    cv2.putText(frame, GESTOS[current_gesture]["nome"], (10, 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Suavização de detecção
        if current_gesture:
            gesture_history.append(current_gesture)
            if len(gesture_history) > 10:
                gesture_history.pop(0)
        
        current_time = time.time()
        
        # Lógica do jogo
        if game_state == "showing":
            # Mostrando sequência
            elapsed = current_time - state_start_time
            
            if elapsed >= GESTURE_DISPLAY_TIME:
                show_index += 1
                state_start_time = current_time
                
                if show_index >= len(sequence):
                    game_state = "waiting"
                    player_sequence = []
                    current_index = 0
                    state_start_time = current_time
                    gesture_history = []
        
        elif game_state == "waiting":
            # Esperando jogador repetir
            elapsed = current_time - state_start_time
            
            if gesture_history and len(gesture_history) >= 5:
                detected_gesture = max(set(gesture_history), key=gesture_history.count)
                
                if detected_gesture == sequence[current_index]:
                    player_sequence.append(detected_gesture)
                    current_index += 1
                    gesture_history = []
                    state_start_time = current_time
                    
                    if current_index >= len(sequence):
                        # Completou a sequência!
                        game_state = "correct"
                        state_start_time = current_time
                        score += len(sequence) * 10
                        round_num += 1
                else:
                    # Gesto errado
                    game_state = "wrong"
                    state_start_time = current_time
            
            elif elapsed >= PLAYER_TIME_LIMIT * len(sequence):
                # Tempo esgotado
                game_state = "wrong"
                state_start_time = current_time
        
        elif game_state == "correct":
            if current_time - state_start_time >= 2:
                # Adiciona novo gesto à sequência
                sequence.append(random.choice(gestures_list))
                show_index = 0
                game_state = "showing"
                state_start_time = current_time
        
        elif game_state == "wrong":
            if current_time - state_start_time >= 2:
                # Game over
                break
        
        # --- Renderização ---
        screen.fill(DARK_BG)
        
        # HUD
        draw_text(screen, f"RODADA: {round_num + 1}", font_medium, TEXT_PRIMARY, 150, 50)
        draw_text(screen, f"PONTOS: {score}", font_medium, ACCENT_CYAN, SCREEN_WIDTH // 2, 50)
        draw_text(screen, f"SEQUÊNCIA: {len(sequence)}", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH - 200, 50)
        
        # Área principal
        if game_state == "showing":
            # Mostrando sequência
            draw_text(screen, "👀 MEMORIZE A SEQUÊNCIA", font_large, ACCENT_CYAN, 
                      SCREEN_WIDTH // 2, 150)
            
            # Mostra gestos já exibidos
            card_width = 120
            card_height = 150
            spacing = 20
            total_width = len(sequence) * (card_width + spacing) - spacing
            start_x = (SCREEN_WIDTH - total_width) // 2
            
            for i, gesto in enumerate(sequence):
                x = start_x + i * (card_width + spacing)
                y = 300
                if i < show_index:
                    draw_gesture_card(screen, x, y, card_width, card_height, gesto)
                elif i == show_index:
                    draw_gesture_card(screen, x, y, card_width, card_height, gesto, pulse=True)
                else:
                    draw_card(screen, x, y, card_width, card_height, (50, 50, 70), (100, 100, 120))
                    draw_text(screen, "?", font_large, TEXT_SECONDARY, 
                             x + card_width // 2, y + card_height // 2)
        
        elif game_state == "waiting":
            # Jogador repetindo
            draw_text(screen, "✋ SUA VEZ! REPITA A SEQUÊNCIA", font_large, ACCENT_GREEN, 
                      SCREEN_WIDTH // 2, 150)
            
            # Mostra sequência completa (sem pulso)
            card_width = 120
            card_height = 150
            spacing = 20
            total_width = len(sequence) * (card_width + spacing) - spacing
            start_x = (SCREEN_WIDTH - total_width) // 2
            
            for i, gesto in enumerate(sequence):
                x = start_x + i * (card_width + spacing)
                y = 250
                
                if i < current_index:
                    # Já feito - verde
                    draw_card(screen, x, y, card_width, card_height, ACCENT_GREEN, TEXT_PRIMARY)
                    draw_text(screen, "✓", font_large, TEXT_PRIMARY, 
                             x + card_width // 2, y + card_height // 2)
                elif i == current_index:
                    # Atual - pulsando
                    draw_gesture_card(screen, x, y, card_width, card_height, gesto, pulse=True)
                else:
                    # Futuro - sem mostrar
                    draw_card(screen, x, y, card_width, card_height, (50, 50, 70), (100, 100, 120))
                    draw_text(screen, "?", font_large, TEXT_SECONDARY, 
                             x + card_width // 2, y + card_height // 2)
            
            # Tempo restante
            time_left = PLAYER_TIME_LIMIT * len(sequence) - (current_time - state_start_time)
            bar_width = 400
            bar_height = 30
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = 500
            
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), 
                           border_radius=15)
            progress = max(0, time_left / (PLAYER_TIME_LIMIT * len(sequence)))
            fill_width = int(bar_width * progress)
            color = ACCENT_GREEN if progress > 0.5 else ACCENT_ORANGE if progress > 0.25 else ACCENT_PINK
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height), 
                           border_radius=15)
            
            draw_text(screen, f"TEMPO: {time_left:.1f}s", font_small, TEXT_SECONDARY, 
                      SCREEN_WIDTH // 2, bar_y + 60)
        
        elif game_state == "correct":
            # Acertou!
            draw_text(screen, "🎉 CORRETO! 🎉", font_title, ACCENT_GREEN, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, f"+{len(sequence) * 10} pontos!", font_large, ACCENT_CYAN, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        
        elif game_state == "wrong":
            # Errou
            draw_text(screen, "❌ ERRADO! ❌", font_title, ACCENT_PINK, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, "Game Over!", font_large, TEXT_PRIMARY, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        
        # Webcam
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        webcam_x = SCREEN_WIDTH - WEBCAM_WIDTH - 30
        webcam_y = SCREEN_HEIGHT - WEBCAM_HEIGHT - 30
        screen.blit(frame_surface, (webcam_x, webcam_y))
        
        border_color = ACCENT_GREEN if current_gesture else (100, 100, 100)
        pygame.draw.rect(screen, border_color, (webcam_x, webcam_y, WEBCAM_WIDTH, WEBCAM_HEIGHT), 4)
        
        if current_gesture:
            draw_text(screen, GESTOS[current_gesture]["emoji"], font_large, TEXT_PRIMARY, 
                      webcam_x + WEBCAM_WIDTH // 2, webcam_y - 30, True, False)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    cap.release()
    cv2.destroyAllWindows()
    
    return show_results(score, round_num)

def show_results(score, rounds):
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
        
        card_x = SCREEN_WIDTH // 2 - 450
        card_y = 200
        draw_card(screen, card_x, card_y, 900, 500, CARD_BG, ACCENT_CYAN)
        
        draw_text(screen, "🧠 JOGO FINALIZADO! 🧠", font_title, ACCENT_CYAN, 
                  SCREEN_WIDTH // 2, card_y + 100)
        
        draw_text(screen, f"Pontuação: {score}", font_large, TEXT_PRIMARY, 
                  SCREEN_WIDTH // 2, card_y + 220)
        draw_text(screen, f"Rodadas Completadas: {rounds}", font_medium, TEXT_SECONDARY, 
                  SCREEN_WIDTH // 2, card_y + 310)
        
        if rounds >= 10:
            rating = "🏆 MEMÓRIA EXCEPCIONAL!"
            rating_color = ACCENT_GREEN
        elif rounds >= 7:
            rating = "⭐ MUITO BOM!"
            rating_color = ACCENT_CYAN
        elif rounds >= 5:
            rating = "👍 BOM!"
            rating_color = ACCENT_PURPLE
        else:
            rating = "💪 CONTINUE PRATICANDO!"
            rating_color = TEXT_SECONDARY
        
        draw_text(screen, rating, font_large, rating_color, 
                  SCREEN_WIDTH // 2, card_y + 400)
        
        draw_text(screen, "ESPAÇO para jogar novamente | ESC para sair", 
                  font_small, TEXT_SECONDARY, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        
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

