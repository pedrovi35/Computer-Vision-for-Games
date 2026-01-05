import cv2
import mediapipe as mp
import pygame
import sys
import math
import random

# --- Configurações do Jogo ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
BALL_SIZE = 20
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# --- Inicialização do Pygame ---
pygame.init()
pygame.display.set_caption("Pong com Controle de Movimento")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74) # Fonte maior para scores e Game Over
small_font = pygame.font.Font(None, 48)

# Carregar sons (se possível, descomente e ajuste os caminhos)
# try:
#     paddle_hit_sound = pygame.mixer.Sound("paddle_hit.wav")
#     wall_hit_sound = pygame.mixer.Sound("wall_hit.wav")
#     score_sound = pygame.mixer.Sound("score.wav")
# except pygame.error as e:
#     print(f"Erro ao carregar sons: {e}. O jogo continuará sem sons.")
#     paddle_hit_sound = None
#     wall_hit_sound = None
#     score_sound = None

# --- Inicialização do MediaPipe ---
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands

# Variáveis globais para os modelos MediaPipe
hands_model = None
face_mesh_model = None

# --- Classes do Jogo Pong ---
class Paddle:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.base_speed = 7 # Velocidade base da IA
        self.speed = self.base_speed
        self.error_margin = 0  # Margem de erro na IA (quanto maior, mais fraca a IA)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def adjust_difficulty(self, score_difference):
        """
        Ajusta a dificuldade da IA baseado na diferença de pontuação
        score_difference = player_score - opponent_score
        Positivo = jogador está ganhando (IA fica mais forte)
        Negativo = jogador está perdendo (IA fica mais fraca)
        """
        if score_difference >= 2:
            # Jogador está ganhando por 2+ pontos: IA fica mais forte
            self.speed = self.base_speed + 2
            self.error_margin = 5
        elif score_difference == 1:
            # Jogador está ganhando por 1 ponto: IA fica um pouco mais forte
            self.speed = self.base_speed + 1
            self.error_margin = 10
        elif score_difference == 0:
            # Empate: IA em dificuldade normal
            self.speed = self.base_speed
            self.error_margin = 15
        elif score_difference == -1:
            # Jogador está perdendo por 1 ponto: IA fica um pouco mais fraca
            self.speed = self.base_speed - 1
            self.error_margin = 25
        else:
            # Jogador está perdendo por 2+ pontos: IA fica mais fraca
            self.speed = max(self.base_speed - 2, 3)  # Mínimo de 3 de velocidade
            self.error_margin = 40

    def move_ai(self, ball_y):
        # IA adaptativa: tenta seguir a bola com margem de erro
        target_y = ball_y + random.randint(-self.error_margin, self.error_margin)
        
        if self.rect.centery < target_y - 10:
            self.rect.y += self.speed
        elif self.rect.centery > target_y + 10:
            self.rect.y -= self.speed
        
        # Garante que a raquete não saia da tela
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Ball:
    def __init__(self, x, y, size, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.base_speed = 7
        self.speed_x = self.base_speed * random.choice((1, -1)) # Começa em direção aleatória
        self.speed_y = self.base_speed * random.choice((1, -1))
        self.speed_multiplier = 1.0  # Multiplicador de velocidade que aumenta com o tempo
        self.max_speed_multiplier = 2.0  # Velocidade máxima (2x a velocidade inicial)

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def move(self):
        self.rect.x += self.speed_x * self.speed_multiplier
        self.rect.y += self.speed_y * self.speed_multiplier

        # Colisão com as paredes superior/inferior
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1
            # if wall_hit_sound: wall_hit_sound.play()

    def increase_speed(self):
        """Aumenta a velocidade da bola gradualmente"""
        if self.speed_multiplier < self.max_speed_multiplier:
            self.speed_multiplier += 0.05
            
    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = self.base_speed * random.choice((1, -1))
        self.speed_y = self.base_speed * random.choice((1, -1))
        # Mantém o multiplicador de velocidade ao resetar (não volta ao início)

# --- Funções de Ajuda ---
def draw_score(surface, player_score, opponent_score):
    player_text = font.render(str(player_score), True, WHITE)
    opponent_text = font.render(str(opponent_score), True, WHITE)
    surface.blit(player_text, (SCREEN_WIDTH // 4, 20))
    surface.blit(opponent_text, (SCREEN_WIDTH * 3 // 4 - opponent_text.get_width(), 20))

def game_over_screen(winner, final_score_player, final_score_opponent):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return # Volta para o menu principal ou reinicia

        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        winner_text = small_font.render(f"Vencedor: {winner}", True, WHITE)
        score_text = small_font.render(f"Pontuação Final: Jogador {final_score_player} - {final_score_opponent} IA", True, WHITE)
        restart_text = small_font.render("Pressione ESPAÇO para jogar novamente", True, WHITE)

        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 4))
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        pygame.display.flip()

# --- Menu Inicial ---
def main_menu():
    global hands_model, face_mesh_model
    control_mode = None
    
    while control_mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    control_mode = "eyes"
                    face_mesh_model = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
                elif event.key == pygame.K_2:
                    control_mode = "hand"
                    hands_model = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

        screen.fill(BLACK)
        title_text = font.render("Jogo Pong", True, WHITE)
        choice_text = small_font.render("Escolha o modo de controle:", True, WHITE)
        eyes_option = small_font.render("Pressione 1 para controlar com os olhos", True, WHITE)
        hand_option = small_font.render("Pressione 2 para controlar com a mão", True, WHITE)

        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))
        screen.blit(choice_text, (SCREEN_WIDTH // 2 - choice_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(eyes_option, (SCREEN_WIDTH // 2 - eyes_option.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(hand_option, (SCREEN_WIDTH // 2 - hand_option.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
        pygame.display.flip()
        
    return control_mode

# --- Loop Principal do Jogo ---
def game_loop(control_mode):
    global hands_model, face_mesh_model
    
    player_paddle = Paddle(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, WHITE)
    opponent_paddle = Paddle(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, WHITE)
    ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, WHITE)

    player_score = 0
    opponent_score = 0
    max_score = 5
    
    # Contador para aumentar a velocidade com o tempo
    speed_increase_counter = 0
    speed_increase_interval = 180  # Aumenta a cada 3 segundos (60 FPS * 3)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao abrir a câmera.")
        sys.exit()
    
    # Configuração da janela da webcam no canto superior esquerdo
    window_name = f"Webcam - Controle por {control_mode.upper()}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 320, 240)  # Tamanho da janela
    cv2.moveWindow(window_name, 0, 0)  # Posiciona no canto superior esquerdo (x=0, y=0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Adiciona ESC para voltar ao menu
                    cap.release()
                    cv2.destroyAllWindows()
                    return # Retorna para o menu principal

        # --- Captura e Processamento da Webcam ---
        ret, frame = cap.read()
        if not ret:
            print("Não foi possível ler o frame da câmera.")
            break

        frame = cv2.flip(frame, 1) # Espelha a imagem
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Variável para armazenar a posição vertical de controle (mapeada para a altura da tela do Pygame)
        control_y = SCREEN_HEIGHT // 2 

        if control_mode == "eyes" and face_mesh_model:
            results_face = face_mesh_model.process(frame_rgb)
            if results_face.multi_face_landmarks:
                for face_landmarks in results_face.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION, # Apenas para visualização
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing.DrawingSpec(color=BLUE, thickness=1, circle_radius=1)
                    )
                    
                    # Para o olho direito (aproximadamente, você pode refinar com índices específicos)
                    # Exemplo: Landmark 159 é um bom ponto no canto inferior direito do olho direito
                    # Veja a documentação do MediaPipe Face Mesh para índices exatos.
                    right_eye_landmark = face_landmarks.landmark[159] 
                    h, w, _ = frame.shape
                    eye_y = int(right_eye_landmark.y * h)

                    # Desenha um círculo no olho para feedback visual
                    cv2.circle(frame, (int(right_eye_landmark.x * w), eye_y), 5, (0, 255, 0), -1)

                    # Mapeia a posição Y do olho para a posição da raquete
                    # Normalize eye_y (0 a h) para a altura da tela do Pygame (0 a SCREEN_HEIGHT)
                    control_y = int(eye_y / h * SCREEN_HEIGHT)

        elif control_mode == "hand" and hands_model:
            results_hands = hands_model.process(frame_rgb)
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Landmark 0 é a base da palma da mão
                    palm_landmark = hand_landmarks.landmark[0]
                    h, w, _ = frame.shape
                    palm_y = int(palm_landmark.y * h)

                    # Desenha um círculo na palma da mão para feedback visual
                    cv2.circle(frame, (int(palm_landmark.x * w), palm_y), 10, (255, 0, 255), cv2.FILLED)

                    # Mapeia a posição Y da palma para a posição da raquete
                    control_y = int(palm_y / h * SCREEN_HEIGHT)

        # Atualiza a posição da raquete do jogador
        player_paddle.rect.centery = control_y
        # Garante que a raquete do jogador não saia da tela
        if player_paddle.rect.top < 0:
            player_paddle.rect.top = 0
        if player_paddle.rect.bottom > SCREEN_HEIGHT:
            player_paddle.rect.bottom = SCREEN_HEIGHT

        # --- Lógica do Jogo Pong ---
        ball.move()
        
        # Ajusta a dificuldade da IA baseada na diferença de pontuação
        score_difference = player_score - opponent_score
        opponent_paddle.adjust_difficulty(score_difference)
        opponent_paddle.move_ai(ball.rect.centery)
        
        # Aumenta a velocidade da bola gradualmente com o tempo
        speed_increase_counter += 1
        if speed_increase_counter >= speed_increase_interval:
            ball.increase_speed()
            speed_increase_counter = 0

        # Colisão da bola com as raquetes
        if ball.rect.colliderect(player_paddle.rect) or ball.rect.colliderect(opponent_paddle.rect):
            ball.speed_x *= -1
            # Aumenta a velocidade também a cada rebate nas raquetes
            ball.increase_speed()
            # Adiciona um pouco de aleatoriedade no rebote vertical
            ball.speed_y = random.uniform(ball.speed_y - 2, ball.speed_y + 2)
            # if paddle_hit_sound: paddle_hit_sound.play()

        # Ponto para o adversário
        if ball.rect.left <= 0:
            opponent_score += 1
            # if score_sound: score_sound.play()
            ball.reset()
        # Ponto para o jogador
        if ball.rect.right >= SCREEN_WIDTH:
            player_score += 1
            # if score_sound: score_sound.play()
            ball.reset()

        # Verifica Game Over
        if player_score >= max_score:
            game_over_screen("Jogador", player_score, opponent_score)
            player_score = 0
            opponent_score = 0
            player_paddle.rect.centery = SCREEN_HEIGHT // 2 # Reseta posição
            ball.reset()
        elif opponent_score >= max_score:
            game_over_screen("IA", player_score, opponent_score)
            player_score = 0
            opponent_score = 0
            player_paddle.rect.centery = SCREEN_HEIGHT // 2 # Reseta posição
            ball.reset()

        # --- Desenho no Pygame ---
        screen.fill(BLACK)
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT)) # Linha central
        player_paddle.draw(screen)
        opponent_paddle.draw(screen)
        ball.draw(screen)
        draw_score(screen, player_score, opponent_score)
        
        # --- Informações adicionais na tela ---
        info_font = pygame.font.Font(None, 24)
        
        # Mostra a velocidade atual da bola
        speed_text = info_font.render(f"Velocidade: {ball.speed_multiplier:.1f}x", True, WHITE)
        screen.blit(speed_text, (SCREEN_WIDTH - 150, 10))
        
        # Mostra a dificuldade da IA
        difficulty_text = info_font.render(f"IA: Vel {opponent_paddle.speed}", True, WHITE)
        screen.blit(difficulty_text, (SCREEN_WIDTH - 150, 35))
        
        # Mostra o modo de controle
        control_text = info_font.render(f"Controle: {control_mode.upper()}", True, WHITE)
        screen.blit(control_text, (10, 10))
        
        pygame.display.flip()
        
        # --- Exibir Webcam em janela separada ---
        cv2.imshow(window_name, frame)

        clock.tick(FPS)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): # Pressione 'q' para sair
            break

    # --- Limpeza ---
    cap.release()
    cv2.destroyAllWindows()
    # Os modelos MediaPipe são descartados no final do game_loop para liberar recursos
    try:
        if hands_model:
            hands_model.close()
            hands_model = None
    except:
        pass
    try:
        if face_mesh_model:
            face_mesh_model.close()
            face_mesh_model = None
    except:
        pass


# --- Início do Jogo ---
if __name__ == "__main__":
    while True:
        mode = main_menu()
        game_loop(mode)