# 🎮 Novos Jogos com Visão Computacional

## 🎉 4 Jogos Novos Criados!

Esta documentação apresenta os **4 novos jogos** criados com foco em **UI/UX profissional** e **interatividade total** usando visão computacional.

---

## 1. ✊✋✌️ Pedra, Papel, Tesoura

### 📝 Descrição
Jogue o clássico pedra, papel, tesoura contra o computador usando apenas gestos das suas mãos! O jogo detecta automaticamente quantos dedos você está mostrando e determina seu gesto.

### 🎮 Como Jogar
1. Pressione **ESPAÇO** para iniciar uma rodada
2. Prepare seu gesto durante a contagem regressiva (3 segundos)
3. Mostre seu gesto:
   - **✊ PEDRA**: Feche a mão (0 dedos)
   - **✋ PAPEL**: Abra a mão (5 dedos)
   - **✌️ TESOURA**: Mostre 2 dedos
4. O computador faz seu gesto automaticamente
5. Veja quem venceu!

### 🎨 Features UI/UX
- ✨ **Contagem regressiva animada** com cores dinâmicas
- ✨ **Barra de progresso** visual do tempo
- ✨ **Placar detalhado**: Você, Computador, Empates
- ✨ **Emojis grandes** para gestos
- ✨ **Feedback visual** do gesto detectado
- ✨ **Transições suaves** entre estados
- ✨ **Cores modernas**: Azul, Verde, Vermelho, Amarelo

### 🔧 Tecnologias
- **MediaPipe Hands**: Detecção de mãos e dedos
- **OpenCV**: Captura e processamento de vídeo
- **Pygame**: Interface gráfica e renderização
- **NumPy**: Cálculos matemáticos

### 📊 Configurações
- **Resolução**: 1400x900
- **FPS**: 30
- **Detecção**: 1 mão, confiança 0.7
- **Tempo de contagem**: 3 segundos
- **Suavização**: Histórico de 5 frames

---

## 2. 🎯 Acerte o Alvo

### 📝 Descrição
Um moderno Whack-a-Mole com visão computacional! Use suas mãos como cursores para acertar alvos que aparecem aleatoriamente na tela. Teste seus reflexos e precisão!

### 🎮 Como Jogar
1. Movimente suas mãos na frente da câmera
2. Seus dedos indicadores controlam os cursores na tela
3. Acerte os alvos coloridos que aparecem
4. Alvos maiores valem mais pontos!
5. Faça **combos** acertando seguidos para multiplicar pontos
6. Você tem **60 segundos** de jogo

### 🎨 Features UI/UX
- ✨ **Controle com até 2 mãos** simultâneas
- ✨ **Cursores pulsantes** coloridos (Ciano e Rosa)
- ✨ **Alvos com pontuação variável** (10-50 pontos)
- ✨ **Sistema de combo** com multiplicador
- ✨ **Efeitos de partículas** na explosão dos alvos
- ✨ **Dificuldade progressiva** (spawn mais rápido)
- ✨ **HUD completo**: Pontos, Combo, Tempo
- ✨ **Grade decorativa** no fundo
- ✨ **Webcam pequena** no canto
- ✨ **Borda colorida** indicando acerto (Verde/Vermelho)

### 🔧 Tecnologias
- **MediaPipe Hands**: Detecção de até 2 mãos
- **OpenCV**: Processamento de vídeo em tempo real
- **Pygame**: Renderização de gráficos e animações
- **Sistema de partículas** customizado

### 📊 Configurações
- **Resolução**: 1400x900
- **FPS**: 60 (alta fluidez)
- **Duração**: 60 segundos
- **Tamanho dos alvos**: 80px
- **Tempo de vida**: 2 segundos
- **Distância de acerto**: 60px

### 🏆 Sistema de Pontuação
- **Acerto**: 10-50 pontos (valor do alvo)
- **Combo**: +10% por combo acumulado
- **Avaliação final**:
  - 1000+ pontos: 🏆 INCRÍVEL!
  - 500+ pontos: ⭐ EXCELENTE!
  - 250+ pontos: 👍 BOM!
  - <250 pontos: 💪 CONTINUE PRATICANDO!

---

## 3. 🧩 Labirinto - Controle por Cabeça

### 📝 Descrição
Navegue por labirintos gerados proceduralmente usando apenas movimentos da sua cabeça! Incline a cabeça para controlar o personagem e chegue até o troféu.

### 🎮 Como Jogar
1. Posicione-se para que seu rosto apareça na webcam
2. **Incline a cabeça para ESQUERDA/DIREITA** para mover horizontalmente
3. **Incline para FRENTE/TRÁS** para mover verticalmente
4. Comece no **ponto azul** 🏁
5. Chegue até o **troféu dourado** 🏆
6. Pressione **R** para gerar novo labirinto

### 🎨 Features UI/UX
- ✨ **Geração procedural** de labirintos únicos
- ✨ **Algoritmo de backtracking** para labirintos perfeitos
- ✨ **Personagem com rastro** visual colorido
- ✨ **Efeito de brilho** no personagem
- ✨ **Saída pulsante** com animação
- ✨ **Cronômetro** em tempo real
- ✨ **Webcam com indicador** de movimento
- ✨ **Gradiente nas paredes** do labirinto
- ✨ **Tela de vitória** com tempo final
- ✨ **Controles visuais**: setas na webcam

### 🔧 Tecnologias
- **MediaPipe Face Mesh**: Detecção precisa do rosto
- **OpenCV**: Captura de vídeo
- **Pygame**: Renderização do labirinto
- **Algoritmo de geração**: Recursive Backtracking

### 📊 Configurações
- **Resolução**: 1400x900
- **FPS**: 60
- **Tamanho do labirinto**: 19x13 células
- **Tamanho da célula**: 60px
- **Velocidade do jogador**: 4px/frame
- **Sensibilidade da cabeça**: 1.5x

### 🎯 Características Técnicas
- Labirinto sempre tem solução (grafo conexo)
- Entrada na esquerda, saída na direita
- Colisão precisa com paredes
- Suavização de movimento
- 30 frames de rastro visual

---

## 4. 🕺 Simon Diz - Jogo de Poses

### 📝 Descrição
Copie as poses que o Simon mostrar! Um jogo de imitação de poses corporais que testa sua flexibilidade, coordenação e tempo de reação. 8 poses diferentes em 10 rodadas desafiadoras!

### 🎮 Como Jogar
1. Fique **longe o suficiente** para aparecer inteiro na câmera
2. Simon mostrará uma **pose** para você copiar
3. Você tem **5 segundos** para fazer a pose
4. Mantenha a pose por **0.5 segundos** para confirmar
5. Complete **10 rodadas** para terminar o jogo
6. Receba sua **avaliação final** baseada em precisão

### 🕺 Poses Disponíveis

| Pose | Emoji | Descrição | Detecção |
|------|-------|-----------|----------|
| **Letra T** | 🙆 | Braços na horizontal | Ângulo dos cotovelos |
| **Letra Y** | 🙌 | Braços para cima em V | Mãos acima da cabeça |
| **Agachamento** | 🧘 | Agache com braços para frente | Ângulo dos joelhos |
| **Guerreiro** | 🧘‍♂️ | Perna atrás, braços abertos | Diferença de altura pés |
| **Estrela** | ⭐ | Pernas e braços abertos | Distância entre membros |
| **Flamingo** | 🦩 | Uma perna levantada | Diferença altura pés |
| **Avião** | ✈️ | Inclinado com braços abertos | Inclinação do corpo |
| **Dab** | 💪 | Dab clássico | Mão próxima ao rosto |

### 🎨 Features UI/UX
- ✨ **Card informativo** da pose atual
- ✨ **Emoji grande** representando a pose
- ✨ **Descrição clara** de como fazer
- ✨ **Barra de progresso** da detecção
- ✨ **Feedback visual imediato**: borda Verde/Vermelha
- ✨ **Cronômetro decrescente** colorido
- ✨ **Contador de rodadas**: X/10
- ✨ **Placar em tempo real**
- ✨ **Tela de resultados** com avaliação
- ✨ **Skeleton visual** do corpo detectado

### 🔧 Tecnologias
- **MediaPipe Pose**: Detecção de 33 pontos corporais
- **OpenCV**: Processamento de vídeo
- **Pygame**: Interface e animações
- **Cálculo de ângulos**: Geometria vetorial

### 📊 Configurações
- **Resolução**: 1400x900
- **FPS**: 30
- **Tempo por pose**: 5 segundos
- **Frames para confirmar**: 15 (~0.5s)
- **Total de rodadas**: 10
- **Pontos por acerto**: 100

### 🏆 Sistema de Avaliação
- **90%+ precisão**: 🏆 MESTRE DAS POSES!
- **70-89% precisão**: ⭐ ÓTIMO DESEMPENHO!
- **50-69% precisão**: 👍 BOM TRABALHO!
- **<50% precisão**: 💪 CONTINUE PRATICANDO!

### 🎯 Detecção de Poses
Cada pose usa algoritmos específicos:
- **Cálculo de ângulos** entre 3 pontos (cotovelos, joelhos)
- **Distância relativa** entre landmarks
- **Posição vertical/horizontal** de pontos-chave
- **Comparação de alturas** (pés, mãos, cabeça)

---

## 🎨 Características Comuns

### Design Profissional
Todos os jogos compartilham elementos de design moderno:

- ✨ **Paleta de cores vibrante** e consistente
- ✨ **Cards com cantos arredondados** e sombras
- ✨ **Texto com sombra** para melhor legibilidade
- ✨ **Animações suaves** e transições
- ✨ **Feedback visual imediato**
- ✨ **Instruções claras** em português
- ✨ **Menu principal atraente**
- ✨ **Tela de resultados** profissional

### Performance Otimizada
- ⚡ **60 FPS** (ou 30 FPS para poses complexas)
- ⚡ **Baixa latência** na detecção
- ⚡ **Suavização** de detecção para evitar flickering
- ⚡ **Webcam otimizada** com resolução adequada

### Acessibilidade
- 🎯 **Instruções completas** antes do jogo
- 🎯 **Feedback constante** durante o jogo
- 🎯 **Controles intuitivos**
- 🎯 **ESC para sair** em qualquer momento
- 🎯 **ESPAÇO para iniciar/continuar**

---

## 📊 Comparação dos Jogos

| Jogo | Tipo de Controle | Dificuldade | Tempo Médio | Espaço Necessário |
|------|------------------|-------------|-------------|-------------------|
| **Pedra, Papel, Tesoura** | Mão (gestos) | ⭐ Fácil | 2-5 min | Pequeno |
| **Acerte o Alvo** | Mãos (ponteiro) | ⭐⭐ Médio | 1 min | Médio |
| **Labirinto** | Cabeça (inclinação) | ⭐⭐⭐ Difícil | 1-5 min | Pequeno |
| **Simon Diz** | Corpo (poses) | ⭐⭐⭐ Difícil | 3-5 min | Grande |

---

## 🎯 Qual Jogo Escolher?

### Para Iniciantes
- ✊✋✌️ **Pedra, Papel, Tesoura** - Fácil e divertido!

### Para Testar Reflexos
- 🎯 **Acerte o Alvo** - Ação rápida e combos!

### Para Desafio Mental
- 🧩 **Labirinto** - Controle preciso e estratégia!

### Para Exercício
- 🕺 **Simon Diz** - Movimento corporal completo!

---

## 🚀 Como Executar

### Execução Individual
```bash
# Pedra, Papel, Tesoura
python pedra_papel_tesoura.py

# Acerte o Alvo
python acerte_alvo.py

# Labirinto
python labirinto.py

# Simon Diz
python simon_diz.py
```

### Pelo Menu Principal
```bash
streamlit run menu_jogos.py
```

---

## 💡 Dicas Gerais

### Para Melhor Detecção
1. ✅ **Boa iluminação** é essencial
2. ✅ **Fundo limpo** melhora a detecção
3. ✅ **Distância adequada** da câmera
4. ✅ **Centralize-se** no frame da webcam

### Para Melhor Experiência
1. 🎮 Leia as instruções antes de jogar
2. 🎮 Pratique os controles no início
3. 🎮 Ajuste sua posição se necessário
4. 🎮 Divirta-se!

---

## 🏆 Conclusão

Foram criados **4 jogos completos** com:
- ✅ **UI/UX profissional** e moderna
- ✅ **Diferentes tipos de controle** (mãos, cabeça, corpo)
- ✅ **Mecânicas variadas** (ação, puzzle, imitação)
- ✅ **Alta interatividade** 100% sem teclado/mouse
- ✅ **Código limpo** e bem documentado
- ✅ **Performance otimizada** 30-60 FPS

Total de jogos no projeto: **8 jogos completos!** 🎉

---

**Desenvolvido com ❤️ usando Python, OpenCV, MediaPipe e Pygame**



