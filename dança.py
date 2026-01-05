import cv2
import mediapipe as mp
import pygame
import sys
import random
import time
import math

# --- Configurações do Jogo ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480
FPS = 30
ROUND_TIME_LIMIT = 5 # Segundos por rodada
MAX_ROUNDS = 7 # 7 poses no total

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# --- Inicialização do Pygame ---
pygame.init()
pygame.display.set_caption("Dance Game com Visão Computacional")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

# --- Inicialização do MediaPipe Pose ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- Definição das Poses Alvo (Landmarks de Referência) ---
# ESTA É A PARTE MAIS CRÍTICA PARA VOCÊ PREENCHER!
# Você precisará capturar essas coordenadas. Uma forma é:
# 1. Faça a pose na frente da câmera.
# 2. Imprima `results.pose_landmarks.landmark` no console para ver os valores.
# 3. Copie os valores dos landmarks chave (ex: ombros, cotovelos, pulsos, quadris, joelhos, tornozelos)
#    para cada pose. Armazene-os em dicionários como abaixo.
# 4. As coordenadas devem ser normalizadas para que a comparação funcione bem.
#    Ex: normalize pela distância entre os ombros (11 e 12) para que o tamanho do corpo não influencie muito.

# Estrutura de exemplo para uma pose:
# "pose_name": {
#     "description": "Texto para exibir",
#     "landmarks": {
#         mp_pose.PoseLandmark.LEFT_SHOULDER: (x, y, z), # Coordenadas normalizadas (0 a 1)
#         mp_pose.PoseLandmark.RIGHT_SHOULDER: (x, y, z),
#         # ... outros landmarks importantes para essa pose
#     }
# }

# Exemplo de landmarks importantes (apenas alguns, adicione mais conforme necessário):
# mp_pose.PoseLandmark.NOSE.value
# mp_pose.PoseLandmark.LEFT_SHOULDER.value # 11
# mp_pose.PoseLandmark.RIGHT_SHOULDER.value # 12
# mp_pose.PoseLandmark.LEFT_ELBOW.value # 13
# mp_pose.PoseLandmark.RIGHT_ELBOW.value # 14
# mp_pose.PoseLandmark.LEFT_WRIST.value # 15
# mp_pose.PoseLandmark.RIGHT_WRIST.value # 16
# mp_pose.PoseLandmark.LEFT_HIP.value # 23
# mp_pose.PoseLandmark.RIGHT_HIP.value # 24
# mp_pose.PoseLandmark.LEFT_KNEE.value # 25
# mp_pose.PoseLandmark.RIGHT_KNEE.value # 26
# mp_pose.PoseLandmark.LEFT_ANKLE.value # 27
# mp_pose.PoseLandmark.RIGHT_ANKLE.value # 28


# Dicionário para armazenar as 7 poses (preencha com seus próprios dados!)
REFERENCE_POSES = {
    "Braços Abertos": {
        "description": "Braços estendidos para os lados (Formando um T)",
        "landmarks": {
            # Exemplo: (x, y, z) obtidos de uma pose de referência
            mp_pose.PoseLandmark.LEFT_SHOULDER.value: (0.3, 0.5, -0.1),
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value: (0.7, 0.5, -0.1),
            mp_pose.PoseLandmark.LEFT_ELBOW.value: (0.2, 0.5, -0.1),
            mp_pose.PoseLandmark.RIGHT_ELBOW.value: (0.8, 0.5, -0.1),
            mp_pose.PoseLandmark.LEFT_WRIST.value: (0.1, 0.5, -0.1),
            mp_pose.PoseLandmark.RIGHT_WRIST.value: (0.9, 0.5, -0.1),
            mp_pose.PoseLandmark.LEFT_HIP.value: (0.4, 0.7, 0.0),
            mp_pose.PoseLandmark.RIGHT_HIP.value: (0.6, 0.7, 0.0),
        }
    },
    "Braços Para Cima": {
        "description": "Ambos braços levantados",
        "landmarks": {
            mp_pose.PoseLandmark.LEFT_SHOULDER.value: (0.4, 0.3, -0.1),
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value: (0.6, 0.3, -0.1),
            mp_pose.PoseLandmark.LEFT_WRIST.value: (0.4, 0.1, -0.1),
            mp_pose.PoseLandmark.RIGHT_WRIST.value: (0.6, 0.1, -0.1),
            mp_pose.PoseLandmark.LEFT_ELBOW.value: (0.4, 0.2, -0.1),
            mp_pose.PoseLandmark.RIGHT_ELBOW.value: (0.6, 0.2, -0.1),
            mp_pose.PoseLandmark.LEFT_HIP.value: (0.4, 0.7, 0.0),
            mp_pose.PoseLandmark.RIGHT_HIP.value: (0.6, 0.7, 0.0),
        }
    },
    "Um Braço Cima, Outro Baixo": {
        "description": "Um braço para cima, outro para baixo (diagonal)",
        "landmarks": {
            mp_pose.PoseLandmark.LEFT_SHOULDER.value: (0.4, 0.5, -0.1),
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value: (0.6, 0.5, -0.1),
            mp_pose.PoseLandmark.LEFT_WRIST.value: (0.4, 0.2, -0.1),
            mp_pose.PoseLandmark.RIGHT_WRIST.value: (0.6, 0.8, -0.1),
            mp_pose.PoseLandmark.LEFT_ELBOW.value: (0.4, 0.35, -0.1),
            mp_pose.PoseLandmark.RIGHT_ELBOW.value: (0.6, 0.65, -0.1),
            mp_pose.PoseLandmark.LEFT_HIP.value: (0.4, 0.7, 0.0),
            mp_pose.PoseLandmark.RIGHT_HIP.value: (0.6, 0.7, 0.0),
        }
    },
    "Pose em X": {
        "description": "Braços e pernas abertos (Formando um X)",
        "landmarks": {
            mp_pose.PoseLandmark.LEFT_SHOULDER.value: (0.3, 0.4, -0.1),
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value: (0.7, 0.4, -0.1),
            mp_pose.PoseLandmark.LEFT_WRIST.value: (0.2, 0.2, -0.1),
            mp_pose.PoseLandmark.RIGHT_WRIST.value: (0.8, 0.2, -0.1),
            mp_pose.PoseLandmark.LEFT_HIP.value: (0.4, 0.6, 0.0),
            mp_pose.PoseLandmark.RIGHT_HIP.value: (0.6, 0.6, 0.0),
            mp_pose.PoseLandmark.LEFT_KNEE.value: (0.3, 0.8, 0.0),
            mp_pose.PoseLandmark.RIGHT_KNEE.value: (0.7, 0.8, 0.0),
            mp_pose.PoseLandmark.LEFT_ANKLE.value: (0.2, 0.9, 0.0),
            mp_pose.PoseLandmark.RIGHT_ANKLE.value: (0.8, 0.9, 0.0),
        }
    },
    "Mão na Cintura": {
        "description": "Uma mão na cintura, outra para cima",
        "landmarks": {
            mp_pose.PoseLandmark.LEFT_SHOULDER.value: (0.4, 0.5, -0.1),
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value: (0.6, 0.5, -0.1),
            mp_pose.PoseLandmark.LEFT_WRIST.value: (0.4, 0.2, -0.1), # Mão esquerda para cima
            mp_pose.PoseLandmark.RIGHT_WRIST.value: (0.7, 0.6, -0.1), # Mão direita na cintura
            mp_pose.PoseLandmark.LEFT_ELBOW.value: (0.4, 0.35, -0.1),
            mp_pose.PoseLandmark.RIGHT_ELBOW.value: (0.65, 0.65, -0.1),
            mp_pose.PoseLandmark.LEFT_HIP.value: (0.4, 0.7, 0.0),
            mp_pose.PoseLandmark.RIGHT_HIP.value: (0.6, 0.7, 0.0),
        }
    },
    "Vitória (V-Pose)": {
        "description": "Braços levantados em V",
        "landmarks": {
            mp_pose.PoseLandmark.LEFT_SHOULDER.value: (0.4, 0.4, -0.1),
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value: (0.6, 0.4, -0.1),
            mp_pose.PoseLandmark.LEFT_WRIST.value: (0.3, 0.2, -0.1),
            mp_pose.PoseLandmark.RIGHT_WRIST.value: (0.7, 0.2, -0.1),
            mp_pose.PoseLandmark.LEFT_ELBOW.value: (0.35, 0.3, -0.1),
            mp_pose.PoseLandmark.RIGHT_ELBOW.value: (0.65, 0.3, -0.1),
            mp_pose.PoseLandmark.LEFT_HIP.value: (0.4, 0.7, 0.0),
            mp_pose.PoseLandmark.RIGHT_HIP.value: (0.6, 0.7, 0.0),
        }
    },
    "Agachado": {
        "description": "Joelhos dobrados (pose de agachar)",
        "landmarks": {
            mp_pose.PoseLandmark.LEFT_SHOULDER.value: (0.4, 0.4, -0.1),
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value: (0.6, 0.4, -0.1),
            mp_pose.PoseLandmark.LEFT_HIP.value: (0.4, 0.6, 0.0),
            mp_pose.PoseLandmark.RIGHT_HIP.value: (0.6, 0.6, 0.0),
            mp_pose.PoseLandmark.LEFT_KNEE.value: (0.4, 0.8, 0.0),
            mp_pose.PoseLandmark.RIGHT_KNEE.value: (0.6, 0.8, 0.0),
            mp_pose.PoseLandmark.LEFT_ANKLE.value: (0.4, 0.9, 0.0), # Tornozelos mais abaixo
            mp_pose.PoseLandmark.RIGHT_ANKLE.value: (0.6, 0.9, 0.0),
        }
    }
}

ALL_POSE_NAMES = list(REFERENCE_POSES.keys())

# --- Funções de Ajuda ---
def draw_text(surface, text, font, color, x, y, center_x=False):
    text_surface = font.render(text, True, color)
    if center_x:
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    else:
        surface.blit(text_surface, (x, y))

def normalize_landmarks_for_comparison(landmarks_dict):
    """
    Normaliza os landmarks em relação a um ponto central do corpo (ex: meio do quadril)
    e a uma escala (ex: distância entre ombros ou altura do tronco).
    Isso é crucial para comparar poses de pessoas de tamanhos diferentes ou a distâncias variadas da câmera.
    
    Para este exemplo, faremos uma normalização simples baseada no centro do tronco e distância entre os ombros.
    """
    if not landmarks_dict:
        return {}

    # Obter landmarks chave para normalização
    left_shoulder = landmarks_dict.get(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
    right_shoulder = landmarks_dict.get(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
    left_hip = landmarks_dict.get(mp_pose.PoseLandmark.LEFT_HIP.value)
    right_hip = landmarks_dict.get(mp_pose.PoseLandmark.RIGHT_HIP.value)

    if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
        # Se os landmarks centrais não forem detectados, retornamos os originais ou vazios
        return landmarks_dict

    # Calcula o centro do tronco como ponto de referência (para translação)
    center_x = (left_shoulder[0] + right_shoulder[0] + left_hip[0] + right_hip[0]) / 4
    center_y = (left_shoulder[1] + right_shoulder[1] + left_hip[1] + right_hip[1]) / 4

    # Calcula a distância entre os ombros como escala (para scaling)
    shoulder_distance = math.sqrt((right_shoulder[0] - left_shoulder[0])**2 + (right_shoulder[1] - left_shoulder[1])**2)
    if shoulder_distance == 0: # Evita divisão por zero
        shoulder_distance = 0.1 # Um valor pequeno

    # Normaliza todos os landmarks
    normalized_landmarks = {}
    for landmark_id, (x, y, z) in landmarks_dict.items():
        # Translação: subtrai o centro
        norm_x = (x - center_x) / shoulder_distance
        norm_y = (y - center_y) / shoulder_distance
        # Mantém z como está (ou pode normalizar também se necessário)
        normalized_landmarks[landmark_id] = (norm_x, norm_y, z)

    return normalized_landmarks

def calculate_pose_similarity(pose1_landmarks, pose2_landmarks, threshold=0.3):
    """
    Calcula a similaridade entre duas poses baseada na distância euclidiana dos landmarks.
    Retorna True se a similaridade for maior que o threshold.
    """
    if not pose1_landmarks or not pose2_landmarks:
        return False

    total_distance = 0
    valid_landmarks = 0

    for landmark_id in pose1_landmarks:
        if landmark_id in pose2_landmarks:
            x1, y1, z1 = pose1_landmarks[landmark_id]
            x2, y2, z2 = pose2_landmarks[landmark_id]
            
            # Calcula distância euclidiana (apenas x e y para simplificar)
            distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            total_distance += distance
            valid_landmarks += 1

    if valid_landmarks == 0:
        return False

    average_distance = total_distance / valid_landmarks
    return average_distance < threshold

def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        screen.fill(BLACK)
        draw_text(screen, "Dance Game!", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, True)
        draw_text(screen, "Faça as poses na frente da câmera!", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, True)
        draw_text(screen, "Pressione ESPAÇO para começar", font_medium, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, True)
        pygame.display.flip()

def game_over_screen(score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        screen.fill(BLACK)
        draw_text(screen, "FIM DO JOGO!", font_large, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, True)
        draw_text(screen, f"Você acertou {score} de {MAX_ROUNDS} poses!", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, True)
        draw_text(screen, "Pressione ESPAÇO para jogar novamente", font_medium, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, True)
        pygame.display.flip()

def game_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao abrir a câmera.")
        sys.exit()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)

    score = 0
    round_num = 0

    while round_num < MAX_ROUNDS:
        round_num += 1
        target_pose_name = random.choice(ALL_POSE_NAMES)
        target_pose = REFERENCE_POSES[target_pose_name]

        pose_found_in_round = False
        round_start_time = time.time()

        while not pose_found_in_round and (time.time() - round_start_time < ROUND_TIME_LIMIT):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    sys.exit()

            ret, frame = cap.read()
            if not ret:
                print("Não foi possível ler o frame da câmera.")
                break

            # Processa o frame com MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose_detector.process(frame_rgb)

            current_time = time.time()
            time_elapsed = current_time - round_start_time
            time_remaining = max(0, ROUND_TIME_LIMIT - time_elapsed)

            screen.fill(BLACK)
            draw_text(screen, f"Rodada {round_num} de {MAX_ROUNDS}", font_small, WHITE, 20, 20)
            draw_text(screen, f"Pontuação: {score}", font_small, WHITE, 20, 60)
            draw_text(screen, f"Tempo: {int(time_remaining)}s", font_small, WHITE, 20, 100)
            draw_text(screen, f"Faça a pose: {target_pose_name}", font_medium, YELLOW, SCREEN_WIDTH // 2, 20, True)
            draw_text(screen, target_pose["description"], font_small, WHITE, SCREEN_WIDTH // 2, 60, True)

            # Desenha os landmarks detectados
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )

                # Extrai landmarks atuais
                current_landmarks = {}
                for landmark_id, landmark in enumerate(results.pose_landmarks.landmark):
                    current_landmarks[landmark_id] = (landmark.x, landmark.y, landmark.z)

                # Normaliza os landmarks atuais
                normalized_current = normalize_landmarks_for_comparison(current_landmarks)
                
                # Compara com a pose alvo
                if calculate_pose_similarity(normalized_current, target_pose["landmarks"]):
                    print(f"Pose '{target_pose_name}' detectada!")
                    pose_found_in_round = True
                    score += 1
                    time.sleep(1)  # Pausa para mostrar o acerto

            # Exibe o frame da webcam
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
            screen.blit(frame_surface, (SCREEN_WIDTH // 2 - WEBCAM_WIDTH // 2, SCREEN_HEIGHT - WEBCAM_HEIGHT - 20))
            
            pygame.display.flip()
            clock.tick(FPS)

        if not pose_found_in_round:
            print(f"Tempo esgotado para a pose '{target_pose_name}'.")
            time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()
    game_over_screen(score)

# --- Início do Jogo ---
if __name__ == "__main__":
    while True:
        main_menu()
        game_loop()