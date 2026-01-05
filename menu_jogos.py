import streamlit as st
import subprocess
import sys
import os
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="🎮 Menu de Jogos com Visão Computacional",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .game-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease;
    }
    
    .game-card:hover {
        transform: translateY(-5px);
    }
    
    .game-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        margin-bottom: 1rem;
    }
    
    .game-description {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    .game-features {
        color: rgba(255,255,255,0.8);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    .play-button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .play-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .sidebar-info {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .tech-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Informações dos jogos
GAMES_INFO = {
    "pong.py": {
        "name": "🏓 Pong com Controle de Movimento",
        "description": "O clássico jogo Pong controlado pelos seus movimentos! Use os olhos ou as mãos para mover a raquete e derrotar a IA.",
        "features": [
            "Controle por movimento dos olhos",
            "Controle por movimento das mãos", 
            "IA inteligente como oponente",
            "Sistema de pontuação",
            "Interface moderna"
        ],
        "tech": ["OpenCV", "MediaPipe", "Pygame"],
        "requirements": "Webcam + boa iluminação"
    },
    "pong_pro.py": {
        "name": "🏓 Pong Pro - Edição Premium",
        "description": "Versão PREMIUM do Pong com 5 níveis progressivos! Visual neon cyberpunk, efeitos de partículas e sistema de progressão completo!",
        "features": [
            "Sistema de 5 níveis (Iniciante a Lendário)",
            "Visual neon moderno com efeitos especiais",
            "IA progressiva por nível",
            "Efeitos de partículas em colisões",
            "Sistema de pausa e progressão"
        ],
        "tech": ["MediaPipe Hands", "OpenCV", "Pygame"],
        "requirements": "Webcam + boa iluminação"
    },
    "caçaobjeto.py": {
        "name": "🔍 Caça ao Objeto",
        "description": "Encontre objetos específicos na frente da câmera! O jogo usa inteligência artificial YOLOv5 otimizada para detectar objetos em tempo real.",
        "features": [
            "Detecção aprimorada com YOLOv5",
            "19 tipos de objetos diferentes",
            "Pré-processamento de imagem",
            "Detecção inteligente com validação",
            "UI/UX moderna e profissional"
        ],
        "tech": ["YOLOv5", "OpenCV", "Pygame", "PyTorch"],
        "requirements": "Webcam + objetos físicos + boa iluminação"
    },
    "dança.py": {
        "name": "💃 Dance Game",
        "description": "Imita as poses que aparecem na tela! Um jogo de dança que detecta sua postura corporal e verifica se você está fazendo a pose correta.",
        "features": [
            "7 poses diferentes para imitar",
            "Detecção de pose corporal",
            "Sistema de pontuação",
            "Tempo limite por pose",
            "Feedback visual dos landmarks"
        ],
        "tech": ["MediaPipe Pose", "OpenCV", "Pygame"],
        "requirements": "Webcam + espaço para se mover"
    },
    "pedra_papel_tesoura.py": {
        "name": "✊✋✌️ Pedra, Papel, Tesoura",
        "description": "Jogue pedra, papel, tesoura contra o computador usando gestos das mãos! Detecção precisa de gestos em tempo real.",
        "features": [
            "Detecção de gestos com dedos",
            "Contador de rodadas automático",
            "Sistema de pontuação player vs PC",
            "Animações e transições suaves",
            "Interface moderna e intuitiva"
        ],
        "tech": ["MediaPipe Hands", "OpenCV", "Pygame"],
        "requirements": "Webcam + boa iluminação"
    },
    "acerte_alvo.py": {
        "name": "🎯 Acerte o Alvo",
        "description": "Um Whack-a-Mole moderno! Use suas mãos para acertar alvos que aparecem na tela. Teste seus reflexos e precisão!",
        "features": [
            "Controle com até 2 mãos simultâneas",
            "Sistema de combo para mais pontos",
            "Alvos com valores diferentes",
            "Efeitos visuais de partículas",
            "Dificuldade progressiva - 60 segundos de ação"
        ],
        "tech": ["MediaPipe Hands", "OpenCV", "Pygame"],
        "requirements": "Webcam + espaço para mover os braços"
    },
    "labirinto.py": {
        "name": "🧩 Labirinto - Controle por Cabeça",
        "description": "Navegue por um labirinto usando apenas movimentos da cabeça! Incline para controlar o personagem.",
        "features": [
            "Controle por inclinação da cabeça",
            "Geração procedural de labirintos",
            "Rastro visual do personagem",
            "Cronômetro para desafio",
            "Gráficos modernos e fluidos"
        ],
        "tech": ["MediaPipe Face Mesh", "OpenCV", "Pygame"],
        "requirements": "Webcam + aparecer inteiro na câmera"
    },
    "simon_diz.py": {
        "name": "🕺 Simon Diz - Jogo de Poses",
        "description": "Copie as poses que o Simon mostrar! 8 poses diferentes para testar sua flexibilidade e coordenação corporal.",
        "features": [
            "8 poses corporais diferentes",
            "Detecção precisa de pose completa",
            "10 rodadas progressivas",
            "Sistema de precisão e avaliação",
            "Feedback visual em tempo real"
        ],
        "tech": ["MediaPipe Pose", "OpenCV", "Pygame"],
        "requirements": "Webcam + espaço para se mover + aparecer inteiro"
    },
    "jogocobrinha.py": {
        "name": "🐍 Jogo da Cobrinha",
        "description": "O clássico jogo da cobrinha! Controle a cobra para comer a comida e crescer, mas cuidado para não bater nas paredes ou em si mesma.",
        "features": [
            "Controles tradicionais",
            "Sistema de pontuação",
            "Velocidade progressiva",
            "Interface colorida",
            "Game Over screen"
        ],
        "tech": ["Pygame"],
        "requirements": "Teclado"
    },
    "quebra_blocos.py": {
        "name": "🧱 Quebra Blocos Neon",
        "description": "Breakout moderno com visual neon! Use suas mãos para controlar a plataforma e destruir blocos coloridos com efeitos visuais incríveis.",
        "features": [
            "Visual estilo neon vibrante",
            "Controle com até 2 mãos simultâneas",
            "Blocos com HP variável",
            "Sistema de combo multiplicador",
            "Efeitos de partículas espetaculares"
        ],
        "tech": ["MediaPipe Hands", "OpenCV", "Pygame"],
        "requirements": "Webcam + movimentar mãos horizontalmente"
    },
    "corredor_infinito.py": {
        "name": "🏃 Corredor Infinito",
        "description": "Endless runner emocionante! Pule e agache usando movimentos corporais para desviar de obstáculos e coletar moedas.",
        "features": [
            "Movimento corporal completo",
            "Obstáculos terrestres e aéreos",
            "Moedas para coletar",
            "Velocidade progressiva",
            "Cenário com parallax e nuvens"
        ],
        "tech": ["MediaPipe Pose", "OpenCV", "Pygame"],
        "requirements": "Webcam + aparecer inteiro na câmera"
    },
    "pintura_ar.py": {
        "name": "🎨 Pintura no Ar",
        "description": "Aplicativo criativo de desenho! Use o dedo indicador para desenhar no ar e crie arte digital com 10 cores vibrantes.",
        "features": [
            "Desenho com dedo indicador",
            "10 cores vibrantes disponíveis",
            "4 tamanhos de pincel",
            "Salvar imagens criadas",
            "Sistema de desfazer e limpar"
        ],
        "tech": ["MediaPipe Hands", "OpenCV", "Pygame"],
        "requirements": "Webcam + boa iluminação"
    },
    "desvie_obstaculos.py": {
        "name": "🚗 Desvie dos Obstáculos",
        "description": "Jogo de corrida lateral! Incline a cabeça para desviar de obstáculos coloridos e coletar estrelas douradas em 3 pistas.",
        "features": [
            "Controle por inclinação da cabeça",
            "3 pistas de corrida",
            "Sistema de vidas",
            "Coleta de estrelas",
            "Visual de pista animado"
        ],
        "tech": ["MediaPipe Face Mesh", "OpenCV", "Pygame"],
        "requirements": "Webcam + rosto visível"
    },
    "atirador_espacial.py": {
        "name": "🚀 Atirador Espacial",
        "description": "Space shooter épico! Movimente as mãos para mirar e feche o punho para atirar nos alienígenas invasores!",
        "features": [
            "Controle de mira com as mãos",
            "Atirar fechando o punho",
            "Alienígenas animados",
            "Sistema de vida",
            "Efeitos visuais espaciais"
        ],
        "tech": ["MediaPipe Hands", "OpenCV", "Pygame"],
        "requirements": "Webcam + espaço para mover as mãos"
    },
    "memoria_gestos.py": {
        "name": "🧠 Memória de Gestos",
        "description": "Teste sua memória! Memorize e repita sequências de gestos das mãos. 5 gestos diferentes com dificuldade progressiva!",
        "features": [
            "5 gestos únicos (polegar, paz, ok, rock, mão aberta)",
            "Sequências progressivas",
            "Sistema de pontuação",
            "Feedback visual imediato",
            "Detecção precisa de gestos"
        ],
        "tech": ["MediaPipe Hands", "OpenCV", "Pygame"],
        "requirements": "Webcam + boa iluminação"
    }
}

def run_game(game_file):
    """Executa um jogo específico"""
    try:
        # Muda para o diretório correto
        game_path = Path(__file__).parent / game_file
        
        if not game_path.exists():
            st.error(f"Arquivo do jogo não encontrado: {game_file}")
            return
        
        # Executa o jogo
        st.info(f"🚀 Iniciando {GAMES_INFO[game_file]['name']}...")
        st.info("💡 Dica: O jogo será executado em uma nova janela. Feche a janela do jogo para voltar ao menu.")
        
        # Executa o processo
        process = subprocess.Popen([sys.executable, str(game_path)], 
                                 cwd=Path(__file__).parent)
        
        # Aguarda o processo terminar
        process.wait()
        
        st.success("✅ Jogo finalizado!")
        
    except Exception as e:
        st.error(f"❌ Erro ao executar o jogo: {str(e)}")

def main():
    # Cabeçalho principal
    st.markdown('<h1 class="main-header">🎮 Menu de Jogos com Visão Computacional</h1>', unsafe_allow_html=True)
    
    # Sidebar com informações
    with st.sidebar:
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.markdown("### 📋 Informações")
        st.markdown("""
        **Bem-vindo ao menu de jogos!**
        
        Aqui você encontrará uma coleção de jogos que utilizam tecnologias de visão computacional e inteligência artificial.
        
        **Tecnologias utilizadas:**
        - OpenCV para processamento de imagem
        - MediaPipe para detecção de poses e mãos
        - YOLOv5 para detecção de objetos
        - Pygame para interface dos jogos
        - Streamlit para este menu
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎯 Como usar:")
        st.markdown("""
        1. Escolha um jogo abaixo
        2. Clique em "Jogar"
        3. Siga as instruções na tela
        4. Feche o jogo para voltar ao menu
        """)
        
        st.markdown("### ⚠️ Requisitos:")
        st.markdown("""
        - Webcam (para jogos de visão computacional)
        - Boa iluminação
        - Espaço para se mover (para o Dance Game)
        - Objetos físicos (para Caça ao Objeto)
        """)
    
    # Conteúdo principal
    st.markdown("### 🎮 Escolha seu jogo:")
    
    # Cria cards para cada jogo
    for game_file, info in GAMES_INFO.items():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f'''
            <div class="game-card">
                <div class="game-title">{info["name"]}</div>
                <div class="game-description">{info["description"]}</div>
                <div class="game-features">
                    <strong>Características:</strong><br>
                    {chr(10).join([f"• {feature}" for feature in info["features"]])}
                </div>
                <div class="game-features">
                    <strong>Tecnologias:</strong><br>
                    {chr(10).join([f'<span class="tech-badge">{tech}</span>' for tech in info["tech"]])}
                </div>
                <div class="game-features">
                    <strong>Requisitos:</strong> {info["requirements"]}
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)  # Espaçamento
            if st.button(f"🎮 Jogar", key=f"play_{game_file}", help=f"Executar {info['name']}"):
                run_game(game_file)
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎮 Desenvolvido com Python, Streamlit, OpenCV, MediaPipe e Pygame</p>
        <p>💡 Todos os jogos foram otimizados e testados para funcionar perfeitamente!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
