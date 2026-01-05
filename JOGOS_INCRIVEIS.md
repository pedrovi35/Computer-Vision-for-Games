# 🎮 3 Jogos Incríveis com UI/UX Profissional

## 🌟 Novos Jogos Criados!

Foram desenvolvidos **3 jogos espetaculares** com foco total em **UI/UX moderna**, **interatividade máxima** e **visual impressionante**!

---

## 1. 🧱 Quebra Blocos Neon

### 🎨 Visual Estilo Neon Vibrante
Um Breakout moderno com visual cyberpunk/neon absolutamente deslumbrante!

### 🎮 Como Jogar
1. Movimente suas **mãos horizontalmente** na frente da câmera
2. Controle a plataforma neon brilhante
3. Destrua todos os **blocos coloridos**
4. Blocos superiores têm **mais HP** (mais difíceis!)
5. Faça **combos** para multiplicar pontos!

### ✨ Features Incríveis

#### Visual Neon
- 🌈 **Paleta neon vibrante**: Rosa, Ciano, Verde, Roxo, Laranja, Amarelo
- ✨ **Efeitos de glow** pulsantes em todos elementos
- 💫 **Partículas explosivas** ao destruir blocos
- 🎆 **Trails animados** na bola e plataforma
- 🌟 **Grade decorativa** de fundo estilo matriz

#### Gameplay
- 🎯 **Controle com até 2 mãos** simultaneamente (usa média)
- 🔢 **Sistema de HP** nos blocos (1-6 HP baseado na fileira)
- 🔥 **Sistema de combo** com multiplicador
- 📊 **HUD completo**: Pontos, Vidas, Combo
- 💪 **Feedback visual** de acertos

#### Física
- ⚽ **Física realista** da bola
- 🎯 **Ângulo de rebote** baseado em onde acerta a plataforma
- 🚀 **Velocidade garantida** (não fica lenta)
- 💨 **Movimento suavizado** da plataforma

### 📊 Configurações
```python
PADDLE_WIDTH = 150
BALL_SPEED = 8
BLOCK_ROWS = 6
BLOCK_COLS = 14
FPS = 60  # Super fluido!
```

### 🎨 Código Destacado
```python
# Sistema de HP nos blocos
class Block:
    def __init__(self, x, y, color, row):
        self.hp = row + 1  # Mais HP nas fileiras superiores
        self.max_hp = self.hp
    
    def hit(self):
        self.hp -= 1
        self.hit_animation = 1.0
        return self.hp <= 0  # Retorna True se destruído
```

### 🏆 Sistema de Pontuação
- **Bloco básico**: 10 pontos × HP do bloco
- **Com combo**: Pontos × (1 + combo × 0.1)
- **Exemplo**: Bloco com 5 HP + Combo 10 = 50 × 2.0 = **100 pontos!**

---

## 2. 🏃 Corredor Infinito

### 🌈 Endless Runner com Visual Colorido
Um jogo de corrida infinito com céu gradiente, nuvens paralaxe e ação intensa!

### 🎮 Como Jogar
1. **🙌 LEVANTE OS BRAÇOS** para pular
2. **🙇 AGACHE** para abaixar
3. Desvie de **obstáculos terrestres** (pulando)
4. Desvie de **obstáculos aéreos** (agachando)
5. Colete **moedas douradas** para pontos extras!

### ✨ Features Incríveis

#### Visual Dinâmico
- 🌅 **Gradiente de céu** animado
- ☁️ **Nuvens com parallax** (movimento diferencial)
- 🏔️ **Chão decorativo** com textura
- 👤 **Jogador animado** com olhos e trail
- 💰 **Moedas brilhantes** com efeito glow pulsante

#### Mecânicas
- 🎯 **Física realista** com gravidade
- 🏃 **Agachar reduz altura** pela metade
- ⚡ **Velocidade constante** com dificuldade crescente
- 📏 **Hitbox precisa** para colisões justas
- 🎨 **Animações fluidas** em 60 FPS

#### Obstáculos
- 🚧 **Terrestres**: Blocos no chão (pule!)
- ✈️ **Aéreos**: Blocos altos (agache!)
- 🎲 **Spawn aleatório** com taxa ajustável
- ⚠️ **Visual de perigo**: Listras amarelas

#### Moedas
- 💰 **Valor**: 50 pontos cada
- ✨ **Efeito glow** pulsante
- 🎯 **Spawn aleatório** em alturas variadas
- 📊 **Contador** dedicado

### 📊 Sistema de Pontuação
- **Obstáculo passado**: 10 pontos + 1m distância
- **Moeda coletada**: 50 pontos
- **Métricas**: Pontos, Distância (m), Moedas

### 🎨 Controles Visuais
```
┌─────────┬─────────┐
│ 🙌 PULAR│🙇 AGACHAR│
└─────────┴─────────┘
  Verde     Laranja
 (quando    (quando
  ativo)     ativo)
```

### 🎯 Detecção de Pose
```python
def detect_jump_and_duck(landmarks):
    # Pulo: mãos acima dos ombros
    jump = (left_wrist < left_shoulder - 0.1) and 
           (right_wrist < right_shoulder - 0.1)
    
    # Agachar: cabeça próxima do quadril
    duck = nose > left_hip - 0.2
    
    return jump, duck
```

### 🏆 Avaliação
Baseada na distância percorrida e moedas coletadas!

---

## 3. 🎨 Pintura no Ar

### 🖌️ App Criativo de Desenho Digital
Transforme o ar em sua tela! Desenhe com o dedo indicador e crie arte digital incrível.

### 🎮 Como Usar
1. **☝️ LEVANTE o dedo indicador** para desenhar
2. **✌️ Faça PINÇA** (polegar + indicador) para apagar
3. Escolha entre **10 cores vibrantes**
4. Ajuste o **tamanho do pincel** (4 opções)
5. **Salve** suas obras de arte!

### ✨ Features Incríveis

#### Paleta de Cores
```
🔴 Vermelho   🟠 Laranja   🟡 Amarelo
🟢 Verde      🔵 Ciano     🔵 Azul
🟣 Roxo       🩷 Rosa      ⚪ Branco
⚫ Preto
```

#### Tamanhos de Pincel
- **Pequeno**: 3px - Detalhes finos
- **Médio**: 8px - Uso geral
- **Grande**: 15px - Preenchimento
- **Enorme**: 25px - Efeitos dramáticos

#### UI/UX Profissional
- 🎨 **Paleta lateral** com botões circulares
- ✨ **Efeito glow** no botão selecionado
- 👁️ **Preview em tempo real** do pincel
- 🖱️ **Cursor virtual** colorido
- 📹 **Webcam integrada** com feedback

#### Funcionalidades
- ✏️ **Desenho suave** com interpolação entre pontos
- 🧹 **Borracha** (desenha com cor de fundo)
- ↩️ **Desfazer** (U) - Remove último traço
- 🗑️ **Limpar** (C) - Limpa tudo
- 💾 **Salvar** (S) - Exporta PNG
- ⬆️⬇️ **Setas** - Muda tamanho do pincel

### 🎨 Técnicas de Desenho

#### Suavização
```python
# Interpolação para linha suave
steps = 5
for step in range(steps):
    t = step / steps
    x = last_x + (current_x - last_x) * t
    y = last_y + (current_y - last_y) * t
    canvas.add_point(x, y, color, size)
```

#### Trail do Cursor
- 🌈 **10 frames** de histórico
- 💫 **Fade out** gradual com alpha
- 📏 **Tamanho progressivo** do pequeno ao grande

### 🎯 Detecção de Gestos
```python
def detect_drawing_gesture(hand_landmarks):
    # Indicador levantado, outros baixos = DESENHAR
    index_up = index_tip.y < index_pip.y
    middle_down = middle_tip.y > index_pip.y
    is_drawing = index_up and middle_down and not pinching
    
    # Polegar + Indicador juntos = APAGAR
    pinch_distance = sqrt((thumb.x - index.x)² + (thumb.y - index.y)²)
    is_erasing = pinch_distance < 0.05
    
    return is_drawing, is_erasing, (x, y)
```

### 💾 Sistema de Salvamento
```python
# Salva com timestamp
filename = f"pintura_{int(time.time())}.png"
pygame.image.save(canvas.surface, filename)
# Exemplo: pintura_1698765432.png
```

### 🎨 Canvas Features
- 📐 **Tamanho**: 1150 × 880 pixels
- 🎨 **Fundo**: Branco suave (240, 240, 250)
- 📝 **Histórico**: Sistema de traços individuais
- ↩️ **Undo inteligente**: Remove traços completos

---

## 📊 Comparação dos 3 Jogos

| Aspecto | 🧱 Quebra Blocos | 🏃 Corredor Infinito | 🎨 Pintura no Ar |
|---------|------------------|---------------------|------------------|
| **Controle** | Mãos (horizontal) | Corpo (pular/agachar) | Dedo indicador |
| **Tipo** | Arcade | Ação/Reflexos | Criativo |
| **Dificuldade** | ⭐⭐ Médio | ⭐⭐⭐ Difícil | ⭐ Fácil |
| **Estilo Visual** | Neon Cyberpunk | Colorido Alegre | Minimalista Moderno |
| **FPS** | 60 | 60 | 60 |
| **Espaço** | Pequeno | Grande | Pequeno |
| **Objetivo** | Destruir blocos | Sobreviver | Criar arte |
| **Multiplayer** | Não | Não | Não |
| **Salvamento** | Não | Não | Sim (PNG) |

---

## 🎯 Qual Jogo Escolher?

### Para Diversão Arcade
- 🧱 **Quebra Blocos** - Visual neon incrível, ação intensa!

### Para Desafio Físico
- 🏃 **Corredor Infinito** - Teste seus reflexos e resistência!

### Para Relaxar e Criar
- 🎨 **Pintura no Ar** - Libere sua criatividade!

---

## 🚀 Como Executar

### Execução Direta
```bash
# Quebra Blocos Neon
python quebra_blocos.py

# Corredor Infinito
python corredor_infinito.py

# Pintura no Ar
python pintura_ar.py
```

### Pelo Menu Streamlit
```bash
streamlit run menu_jogos.py
# Escolha o jogo no navegador
```

---

## 💡 Dicas para Melhor Experiência

### Quebra Blocos 🧱
- ✅ Movimente as mãos **horizontalmente** apenas
- ✅ Fique a **1m** da câmera
- ✅ Use **movimentos amplos**
- ✅ Aproveite o **efeito neon** em ambiente escuro!

### Corredor Infinito 🏃
- ✅ Apareça **inteiro** na câmera (cabeça aos pés)
- ✅ **Levante bem os braços** para pular alto
- ✅ **Agache completamente** para passar sob obstáculos
- ✅ Observe os **indicadores visuais** de controle

### Pintura no Ar 🎨
- ✅ Use **boa iluminação**
- ✅ Mantenha apenas o **indicador levantado**
- ✅ Movimentos **lentos e deliberados**
- ✅ Experimente **diferentes cores e tamanhos**!
- ✅ Salve suas **obras-primas** (tecla S)

---

## 🎨 Destaques Técnicos

### Performance
- ⚡ **60 FPS** constantes
- ⚡ **Suavização** de movimento
- ⚡ **Interpolação** para fluidez
- ⚡ **Otimizações** de renderização

### Visual
- 🎨 **Paletas harmoniosas**
- ✨ **Efeitos de partículas**
- 💫 **Animações suaves**
- 🌈 **Gradientes dinâmicos**

### UX
- 🎯 **Feedback imediato**
- 📊 **HUD informativo**
- 🎮 **Controles intuitivos**
- 🔄 **Transições suaves**

---

## 🏆 Estatísticas do Projeto

Com estes 3 novos jogos:
- 📊 **11 Jogos** totais no projeto!
- 📊 **3 Estilos visuais** diferentes
- 📊 **5 Tipos de controle**: mãos, corpo, cabeça, dedo, teclado
- 📊 **100% Python** com Pygame moderno
- 📊 **UI/UX de nível profissional**

---

## 🎉 Conclusão

Foram criados **3 jogos espetaculares** com:

✅ **UI/UX Profissional** - Design moderno e atraente
✅ **Alta Interatividade** - Controles naturais e responsivos
✅ **Visuais Incríveis** - Efeitos especiais e animações
✅ **Código Limpo** - Bem organizado e documentado
✅ **Performance** - 60 FPS constantes

**Total no projeto**: **11 jogos completos e jogáveis!** 🎮✨

---

<div align="center">

## 🎮 Divirta-se Criando e Jogando! ✨

**Desenvolvido com ❤️ usando Python, OpenCV, MediaPipe e Pygame**

![Python](https://img.shields.io/badge/11%20Jogos-Completos-success)
![UI/UX](https://img.shields.io/badge/UI%2FUX-Profissional-blue)
![FPS](https://img.shields.io/badge/Performance-60%20FPS-orange)

</div>



