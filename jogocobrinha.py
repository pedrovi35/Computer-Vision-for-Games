import cv2
import mediapipe as mp
import pygame
import random
import sys

# --- Configurações do Jogo ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SNAKE_SPEED = 10

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Direções
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# --- Inicialização do Pygame ---
pygame.init()
pygame.display.set_caption("Jogo da Cobrinha com Controle de Mão")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Inicialização do MediaPipe ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# --- Inicialização da Webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro ao abrir a câmera.")
    sys.exit()

# --- Classe da Cobra ---
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.score = 0
        self.grow = False

    def move(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction: # Evita virar 180 graus
            self.direction = new_direction

    def grow_snake(self):
        self.grow = True
        self.score += 1

    def check_collision(self):
        head_x, head_y = self.body[0]
        # Colisão com as bordas
        if not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT):
            return True
        # Colisão com o próprio corpo
        if self.body[0] in self.body[1:]:
            return True
        return False

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# --- Classe da Comida ---
class Food:
    def __init__(self):
        self.position = self.randomize_position()

    def randomize_position(self):
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# --- Função de Desenho da Pontuação ---
def draw_score(surface, score):
    score_text = font.render(f"Pontuação: {score}", True, BLACK)
    surface.blit(score_text, (10, 10))

# --- Tela de Início ---
def start_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        screen.fill(BLUE)
        title_text = font.render("Jogo da Cobrinha por Mão", True, WHITE)
        start_text = font.render("Pressione ESPAÇO para começar", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

# --- Tela de Game Over ---
def game_over_screen(final_score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Pontuação Final: {final_score}", True, WHITE)
        restart_text = font.render("Pressione ESPAÇO para reiniciar", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()

# --- Loop Principal do Jogo ---
def game_loop():
    snake = Snake()
    food = Food()
    game_running = True

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

        # --- Captura e Processamento da Webcam ---
        ret, frame = cap.read()
        if not ret:
            print("Não foi possível ler o frame da câmera.")
            break

        frame = cv2.flip(frame, 1)  # Espelha a imagem para uma visualização mais intuitiva
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Desenha os landmarks na janela da webcam
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Obtém a posição do Landmark 0 (base da palma)
                palm_landmark = hand_landmarks.landmark[0]
                h, w, _ = frame.shape
                cx, cy = int(palm_landmark.x * w), int(palm_landmark.y * h)

                # Desenha um círculo na palma da mão
                cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

                # --- Controle da Cobra com Base na Posição da Mão ---
                # Normaliza as coordenadas da mão para a tela do jogo (0 a 1)
                normalized_x = palm_landmark.x
                normalized_y = palm_landmark.y

                # Divide a tela em zonas para determinar a direção
                if normalized_x < 0.3:  # Mais à esquerda
                    snake.change_direction(LEFT)
                elif normalized_x > 0.7:  # Mais à direita
                    snake.change_direction(RIGHT)
                elif normalized_y < 0.3:  # Mais para cima
                    snake.change_direction(UP)
                elif normalized_y > 0.7:  # Mais para baixo
                    snake.change_direction(DOWN)

        # --- Lógica do Jogo ---
        snake.move()

        if snake.check_collision():
            game_running = False
            game_over_screen(snake.score)
            return # Sai do game_loop para reiniciar

        if snake.body[0] == food.position:
            snake.grow_snake()
            food.position = food.randomize_position()
            # Garante que a comida não apareça dentro da cobra
            while food.position in snake.body:
                food.position = food.randomize_position()

        # --- Desenho no Pygame ---
        screen.fill(WHITE)
        snake.draw(screen)
        food.draw(screen)
        draw_score(screen, snake.score)
        pygame.display.flip()

        # --- Exibir Webcam ---
        cv2.imshow("Webcam - Controle de Mão", frame)

        clock.tick(SNAKE_SPEED)

        if cv2.waitKey(1) & 0xFF == ord('q'): # Pressione 'q' para sair da webcam
            break

    # --- Limpeza ---
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

# --- Início do Jogo ---
while True:
    start_screen()
    game_loop()