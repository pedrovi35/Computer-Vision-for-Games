import cv2
import pygame
import sys
import random
import time
from ultralytics import YOLO # Usaremos YOLOv5 da biblioteca ultralytics
import torch # Necessário para verificar a disponibilidade de GPU

# --- Configurações do Jogo ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WEBCAM_WIDTH = 1280  # Aumentado para melhor qualidade
WEBCAM_HEIGHT = 720  # Aumentado para melhor qualidade
FPS = 30
ROUND_TIME_LIMIT = 20 # Segundos por rodada
MAX_ROUNDS = 10

# --- Configurações YOLO ---
YOLO_CONFIDENCE = 0.35  # Threshold de confiança reduzido para detectar mais objetos
YOLO_IOU = 0.4  # Threshold de IOU para NMS
YOLO_IMGSZ = 640  # Tamanho da imagem para inferência
DETECTION_CONFIDENCE = 0.45  # Confiança mínima para considerar objeto encontrado

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# --- Lista de Objetos para Caçar (mapear para classes YOLOv5) ---
# Classes reais do COCO dataset (treinado pelo YOLOv5) e seus nomes no jogo
OBJECT_MAP = {
    "Celular": ["cell phone"],
    "Caneca": ["cup"],
    "Garrafa": ["bottle"],
    "Mochila": ["backpack"],
    "Notebook": ["laptop"],
    "Teclado": ["keyboard"],
    "Mouse": ["mouse"],
    "Livro": ["book"],
    "Relógio": ["clock"],
    "Controle Remoto": ["remote"],
    "Tesoura": ["scissors"],
    "Pessoa": ["person"],  # Adicionado para melhor taxa de sucesso
    "Cadeira": ["chair"],
    "TV": ["tv"],
    "Vaso": ["vase"],
    "Tigela": ["bowl"],
    "Banana": ["banana"],
    "Maçã": ["apple"],
    "Laranja": ["orange"]
}

# Filtrar para apenas os que queremos realmente ter como alvos no jogo (keys do dict acima)
GAME_OBJECTS = list(OBJECT_MAP.keys())

# --- Inicialização do Pygame ---
pygame.init()
pygame.display.set_caption("Caça ao Objeto com Visão Computacional")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

# --- Carregar Modelo YOLOv5 ---
try:
    model = YOLO('yolov5su.pt') # Carrega o modelo YOLOv5
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    
    # Configurações do modelo para melhor desempenho
    model.overrides['conf'] = YOLO_CONFIDENCE
    model.overrides['iou'] = YOLO_IOU
    model.overrides['agnostic_nms'] = False
    model.overrides['max_det'] = 50  # Máximo de detecções por imagem
    
    print(f"Modelo YOLOv5 carregado e rodando em: {device}")
    print(f"Confiança: {YOLO_CONFIDENCE}, IOU: {YOLO_IOU}")
except Exception as e:
    print(f"Erro ao carregar o modelo YOLOv5: {e}")
    print("Certifique-se de ter PyTorch e Ultralytics instalados e que o arquivo do modelo (.pt) pode ser baixado/acessado.")
    sys.exit()

# --- Função de Pré-processamento de Imagem ---
def preprocess_frame(frame):
    """Melhora a qualidade da imagem para melhor detecção"""
    # Aumenta o contraste e brilho
    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=10)
    
    # Aplica denoising leve para reduzir ruído
    frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
    
    return frame

# --- Funções de Ajuda ---
def draw_text(surface, text, font, color, x, y, center_x=False):
    text_surface = font.render(text, True, color)
    if center_x:
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    else:
        surface.blit(text_surface, (x, y))

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
        draw_text(screen, "Caça ao Objeto!", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, True)
        draw_text(screen, "Mostre o objeto para a câmera!", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, True)
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
                    return # Volta para o menu principal

        screen.fill(BLACK)
        draw_text(screen, "FIM DO JOGO!", font_large, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, True)
        draw_text(screen, f"Você encontrou {score} de {MAX_ROUNDS} objetos!", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, True)
        draw_text(screen, "Pressione ESPAÇO para jogar novamente", font_medium, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, True)
        pygame.display.flip()

# --- Loop Principal do Jogo ---
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
        target_object_game_name = random.choice(GAME_OBJECTS)
        target_yolo_classes = OBJECT_MAP[target_object_game_name]

        object_found_in_round = False
        round_start_time = time.time()

        while not object_found_in_round and (time.time() - round_start_time < ROUND_TIME_LIMIT):
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

            # Pré-processa o frame para melhorar a detecção
            processed_frame = preprocess_frame(frame)
            
            # Executa a detecção YOLO com configurações otimizadas
            results = model(
                processed_frame,
                conf=YOLO_CONFIDENCE,
                iou=YOLO_IOU,
                imgsz=YOLO_IMGSZ,
                verbose=False,
                half=True if device == 'cuda' else False  # Usa FP16 se GPU disponível
            )

            current_time = time.time()
            time_elapsed = current_time - round_start_time
            time_remaining = max(0, ROUND_TIME_LIMIT - time_elapsed)

            screen.fill(BLACK)
            draw_text(screen, f"Rodada {round_num} de {MAX_ROUNDS}", font_small, WHITE, 20, 20)
            draw_text(screen, f"Pontuação: {score}", font_small, WHITE, 20, 60)
            draw_text(screen, f"Tempo: {int(time_remaining)}s", font_small, WHITE, 20, 100)
            draw_text(screen, f"Encontre: {target_object_game_name}", font_medium, YELLOW, SCREEN_WIDTH // 2, 20, True)

            detected_frame = processed_frame.copy()
            
            # Lista para armazenar detecções válidas
            valid_detections = []
            
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]
                    conf = float(box.conf[0])
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Calcula o tamanho da bounding box (área)
                    box_area = (x2 - x1) * (y2 - y1)
                    
                    # Desenha todas as detecções
                    is_target = class_name in target_yolo_classes
                    color = GREEN if is_target else BLUE
                    thickness = 3 if is_target else 2
                    
                    cv2.rectangle(detected_frame, (x1, y1), (x2, y2), color, thickness)
                    label = f"{class_name} {conf:.2f}"
                    
                    # Fundo para o texto para melhor visibilidade
                    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(detected_frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
                    cv2.putText(detected_frame, label, (x1, y1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Verifica se o objeto alvo foi encontrado com confiança suficiente
                    if is_target and conf >= DETECTION_CONFIDENCE and box_area > 5000:  # Área mínima para evitar falsos positivos
                        valid_detections.append((class_name, conf, box_area))
            
            # Se houver detecções válidas, escolhe a com maior confiança
            if valid_detections and not object_found_in_round:
                best_detection = max(valid_detections, key=lambda x: x[1])
                class_name, conf, area = best_detection
                print(f"Objeto '{target_object_game_name}' detectado ({class_name}) com confiança {conf:.2f}!")
                object_found_in_round = True
                score += 1
                time.sleep(1.5)  # Pausa para o jogador ver o acerto 

            frame_rgb = cv2.cvtColor(detected_frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            frame_surface = pygame.transform.scale(frame_surface, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
            screen.blit(frame_surface, (SCREEN_WIDTH // 2 - WEBCAM_WIDTH // 2, SCREEN_HEIGHT - WEBCAM_HEIGHT - 20))
            
            pygame.display.flip()
            clock.tick(FPS)

        if not object_found_in_round:
            print(f"Tempo esgotado para encontrar '{target_object_game_name}'.")
            time.sleep(1) 

    cap.release()
    cv2.destroyAllWindows()
    game_over_screen(score)

# --- Início do Jogo ---
if __name__ == "__main__":
    while True:
        main_menu()
        game_loop()