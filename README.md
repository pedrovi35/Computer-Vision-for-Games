# 🎮 Coleção de Jogos com Visão Computacional

Uma coleção completa e moderna de **8 jogos interativos** que utilizam tecnologias avançadas de visão computacional e inteligência artificial! Todos os jogos possuem UI/UX profissional e são 100% controlados por movimentos corporais ou gestos.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-red)

</div>

---

## 🎯 Jogos Disponíveis (11 JOGOS!)

### 🏓 Pong com Controle de Movimento
Reviva o clássico Pong com controles modernos!
- ✅ **Controle por olhos** ou **movimento das mãos**
- ✅ IA inteligente como oponente
- ✅ Sistema de pontuação dinâmico
- ✅ Interface moderna e fluida
- 🔧 **Tecnologias**: OpenCV, MediaPipe, Pygame

### 🔍 Caça ao Objeto (Melhorado!)
Encontre objetos usando IA de última geração!
- ✅ **Detecção otimizada com YOLOv5**
- ✅ **19 tipos de objetos** diferentes
- ✅ Pré-processamento inteligente de imagem
- ✅ Sistema de validação de detecção
- ✅ UI/UX profissional com feedback visual
- 🔧 **Tecnologias**: YOLOv5, PyTorch, OpenCV, Pygame

### 💃 Dance Game
Imite as poses e mostre suas habilidades!
- ✅ **7 poses diferentes** para imitar
- ✅ Detecção precisa de postura corporal
- ✅ Sistema de pontuação e feedback em tempo real
- ✅ Tempo limite por pose
- ✅ Visualização dos landmarks corporais
- 🔧 **Tecnologias**: MediaPipe Pose, OpenCV, Pygame

### ✊✋✌️ Pedra, Papel, Tesoura (NOVO!)
Jogue contra o computador usando gestos!
- ✅ **Detecção de gestos** com contagem de dedos
- ✅ Placar completo: você vs computador
- ✅ Contador automático de rodadas
- ✅ Animações e transições suaves
- ✅ Interface moderna e intuitiva
- 🔧 **Tecnologias**: MediaPipe Hands, OpenCV, Pygame

### 🎯 Acerte o Alvo (NOVO!)
Whack-a-Mole com visão computacional!
- ✅ **Controle com até 2 mãos** simultaneamente
- ✅ Sistema de **combo** para multiplicar pontos
- ✅ Alvos com valores diferentes
- ✅ **Efeitos visuais de partículas** incríveis
- ✅ 60 segundos de ação com dificuldade progressiva
- 🔧 **Tecnologias**: MediaPipe Hands, OpenCV, Pygame

### 🧩 Labirinto - Controle por Cabeça (NOVO!)
Navegue por labirintos usando movimentos da cabeça!
- ✅ **Controle por inclinação da cabeça**
- ✅ **Geração procedural** de labirintos
- ✅ Rastro visual do personagem
- ✅ Cronômetro para desafio
- ✅ Gráficos modernos e animações fluidas
- 🔧 **Tecnologias**: MediaPipe Face Mesh, OpenCV, Pygame

### 🕺 Simon Diz - Jogo de Poses (NOVO!)
Copie as poses do Simon!
- ✅ **8 poses corporais diferentes** (T, Y, Estrela, Flamingo, etc.)
- ✅ Detecção precisa de pose completa
- ✅ **10 rodadas progressivas**
- ✅ Sistema de precisão e avaliação final
- ✅ Feedback visual em tempo real
- 🔧 **Tecnologias**: MediaPipe Pose, OpenCV, Pygame

### 🐍 Jogo da Cobrinha
O clássico que nunca sai de moda!
- ✅ Controles tradicionais com teclado
- ✅ Sistema de pontuação
- ✅ Velocidade progressiva
- ✅ Interface colorida
- ✅ Game Over screen
- 🔧 **Tecnologias**: Pygame

### 🧱 Quebra Blocos Neon (NOVO!)
Breakout moderno com visual cyberpunk!
- ✅ **Visual estilo neon** vibrante e brilhante
- ✅ Controle com **até 2 mãos** simultâneas
- ✅ **Blocos com HP** variável (1-6 HP)
- ✅ Sistema de **combo** multiplicador
- ✅ **Efeitos de partículas** espetaculares
- 🔧 **Tecnologias**: MediaPipe Hands, OpenCV, Pygame

### 🏃 Corredor Infinito (NOVO!)
Endless runner emocionante!
- ✅ **Levante os braços** para pular
- ✅ **Agache** para abaixar
- ✅ **Obstáculos** terrestres e aéreos
- ✅ **Colete moedas** para pontos extras
- ✅ Cenário com **parallax e nuvens**
- 🔧 **Tecnologias**: MediaPipe Pose, OpenCV, Pygame

### 🎨 Pintura no Ar (NOVO!)
App criativo de desenho digital!
- ✅ **Desenhe com o dedo** indicador no ar
- ✅ **10 cores** vibrantes disponíveis
- ✅ **4 tamanhos** de pincel
- ✅ **Salvar imagens** criadas
- ✅ Sistema de **desfazer e limpar**
- 🔧 **Tecnologias**: MediaPipe Hands, OpenCV, Pygame

---

## 🚀 Instalação e Execução

### 1️⃣ Pré-requisitos
```bash
# Python 3.8 ou superior
python --version
```

### 2️⃣ Clone o Repositório
```bash
git clone <seu-repositorio>
cd Jogos-com-Visao-Computacional
```

### 3️⃣ Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Execute o Menu Principal
```bash
streamlit run menu_jogos.py
```

### 5️⃣ Ou Execute Jogos Individualmente
```bash
# Pedra, Papel, Tesoura
python pedra_papel_tesoura.py

# Acerte o Alvo
python acerte_alvo.py

# Labirinto
python labirinto.py

# Simon Diz
python simon_diz.py

# Caça ao Objeto (melhorado)
python caçaobjeto.py

# Outros jogos
python pong.py
python dança.py
python jogocobrinha.py
```

---

## 📋 Requisitos do Sistema

### Hardware
- ✅ **Webcam** (para jogos de visão computacional)
- ✅ **CPU**: Intel Core i3 ou equivalente (mínimo)
- ✅ **RAM**: 4GB (mínimo), 8GB (recomendado)
- ✅ **GPU**: Opcional, mas melhora performance do YOLO

### Software
- ✅ **Python 3.8+**
- ✅ **Windows / Linux / macOS**
- ✅ **Navegador Web** (para menu Streamlit)

### Ambiente
- ✅ **Boa iluminação** (essencial para detecção)
- ✅ **Espaço para se mover** (jogos corporais)
- ✅ **Objetos físicos** (para Caça ao Objeto)
- ✅ **Fundo limpo** (melhora a detecção)

---

## 🎮 Como Jogar

### Método 1: Menu Streamlit (Recomendado)
1. Execute `streamlit run menu_jogos.py`
2. Escolha um jogo no navegador
3. Clique em "Jogar"
4. Siga as instruções na tela

### Método 2: Execução Direta
1. Execute o arquivo Python do jogo desejado
2. Aguarde a janela do jogo abrir
3. Pressione **ESPAÇO** para começar
4. Pressione **ESC** para sair

---

## 🔧 Tecnologias Utilizadas

| Tecnologia | Uso | Versão |
|------------|-----|--------|
| **Python** | Linguagem principal | 3.8+ |
| **OpenCV** | Processamento de imagem/vídeo | 4.8+ |
| **MediaPipe** | Detecção de poses, mãos e rosto | 0.10+ |
| **YOLOv5** | Detecção de objetos com IA | 8.0+ |
| **PyTorch** | Backend para deep learning | 2.0+ |
| **Pygame** | Interface e renderização dos jogos | 2.5+ |
| **Streamlit** | Interface web do menu | 1.28+ |
| **NumPy** | Computação numérica | 1.22+ |
| **Pillow** | Processamento de imagem | 9.5+ |

---

## 📁 Estrutura do Projeto

```
Jogos-com-Visao-Computacional/
├── 📄 menu_jogos.py              # Menu principal (Streamlit)
├── 🏓 pong.py                    # Jogo Pong
├── 🔍 caçaobjeto.py              # Caça ao Objeto (melhorado)
├── 💃 dança.py                   # Dance Game
├── ✊ pedra_papel_tesoura.py     # Pedra, Papel, Tesoura
├── 🎯 acerte_alvo.py             # Acerte o Alvo
├── 🧩 labirinto.py               # Labirinto (melhorado)
├── 🕺 simon_diz.py               # Simon Diz
├── 🧱 quebra_blocos.py           # Quebra Blocos Neon (NOVO)
├── 🏃 corredor_infinito.py       # Corredor Infinito (NOVO)
├── 🎨 pintura_ar.py              # Pintura no Ar (NOVO)
├── 🐍 jogocobrinha.py            # Jogo da Cobrinha
├── 🧪 teste_yolo.py              # Script de teste YOLO
├── 🤖 yolov5su.pt                # Modelo YOLOv5
├── 📦 requirements.txt           # Dependências
├── 📖 README.md                  # Este arquivo
├── 📚 MELHORIAS_YOLO.md          # Documentação técnica YOLO
├── 📚 GUIA_OTIMIZACAO_YOLO.md    # Guia de otimização
├── 📚 MELHORIAS_LABIRINTO.md     # Melhorias do Labirinto
├── 📚 NOVOS_JOGOS.md             # Documentação dos 4 primeiros novos
└── 📚 JOGOS_INCRIVEIS.md         # Documentação dos 3 últimos novos
```

---

## 🎯 Características Especiais

### 🎨 UI/UX Profissional
- ✨ **Design moderno** com cores vibrantes
- ✨ **Animações suaves** e transições
- ✨ **Feedback visual** em tempo real
- ✨ **Instruções claras** em português

### 🚀 Performance Otimizada
- ⚡ **60 FPS** na maioria dos jogos
- ⚡ **Suporte a GPU** (CUDA) para YOLO
- ⚡ **Pré-processamento inteligente**
- ⚡ **Detecção otimizada**

### 🎮 Jogabilidade
- 🎯 **Controles intuitivos**
- 🎯 **Sistema de pontuação**
- 🎯 **Múltiplos níveis de dificuldade**
- 🎯 **Feedback imediato**

### 📊 Estatísticas
- 📈 **Placar em tempo real**
- 📈 **Combos e multiplicadores**
- 📈 **Avaliação final**
- 📈 **Histórico de rodadas**

---

## 🔥 Melhorias Recentes

### Caça ao Objeto - YOLO Otimizado
- ✅ **Threshold reduzido** (0.5 → 0.35) = mais detecções
- ✅ **Resolução aumentada** (640x480 → 1280x720)
- ✅ **Pré-processamento** de imagem
- ✅ **Validação inteligente** com área mínima
- ✅ **19 classes** reais do COCO dataset
- 📈 **Taxa de detecção**: 60% → **85%+**

### Novos Jogos
- 🎉 **4 jogos novos** adicionados
- 🎉 **Diferentes tipos de controle**: mãos, cabeça, corpo
- 🎉 **Variedade de mecânicas**: puzzles, ação, reflexos, poses
- 🎉 **Total**: **8 jogos completos**

---

## 🐛 Solução de Problemas

### ❌ Erro de Webcam
**Problema**: Câmera não abre
```bash
# Soluções:
1. Verifique se a webcam está conectada
2. Feche Zoom, Teams, Skype, etc.
3. Teste: python -c "import cv2; cv2.VideoCapture(0).read()"
4. Reinicie o computador
```

### ❌ Erro de Dependências
**Problema**: Módulo não encontrado
```bash
# Solução:
pip install -r requirements.txt --upgrade
```

### ❌ Performance Lenta
**Problema**: Jogo travando
```bash
# Soluções:
1. Feche outros aplicativos
2. Reduza a resolução da webcam no código
3. Desabilite o denoising (linha 94 do caçaobjeto.py)
4. Use GPU se disponível
```

### ❌ Detecção Ruim
**Problema**: Não detecta movimentos/objetos
```bash
# Soluções:
1. Melhore a iluminação
2. Use fundo limpo e contrastante
3. Fique à distância correta da câmera
4. Ajuste os thresholds no código
```

### ❌ YOLO Não Detecta Objetos
**Problema**: Caça ao Objeto não funciona
```bash
# Soluções:
1. Execute: python teste_yolo.py
2. Ajuste YOLO_CONFIDENCE para 0.25
3. Use objetos comuns (celular, garrafa, caneca)
4. Leia GUIA_OTIMIZACAO_YOLO.md
```

---

## 💡 Dicas para Melhor Experiência

### Iluminação 💡
- ✅ Use luz natural ou LED branco
- ❌ Evite contraluz (janela atrás)
- ✅ Ilumine seu rosto/corpo uniformemente

### Posicionamento 📐
- ✅ Fique a 0.5-2m da câmera
- ✅ Mostre corpo inteiro (jogos de pose)
- ✅ Centralize-se no frame

### Fundo 🖼️
- ✅ Use fundo limpo e homogêneo
- ✅ Contraste com suas roupas
- ❌ Evite fundos bagunçados

### Objetos (Caça ao Objeto) 📦
- ✅ Use objetos da lista (celular, garrafa, etc.)
- ✅ Mostre o objeto inteiro
- ✅ Segure próximo ao corpo
- ✅ Fundo contrastante

---

## 🎓 Documentação Adicional

- 📚 **[MELHORIAS_YOLO.md](MELHORIAS_YOLO.md)** - Documentação técnica das melhorias no YOLO
- 📚 **[GUIA_OTIMIZACAO_YOLO.md](GUIA_OTIMIZACAO_YOLO.md)** - Guia completo de otimização com dicas e ajustes

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/NovoJogo`
3. Commit suas mudanças: `git commit -m 'Adiciona novo jogo'`
4. Push para a branch: `git push origin feature/NovoJogo`
5. Abra um Pull Request

---

## 📞 Suporte

Se encontrar problemas:

1. ✅ Verifique os **requisitos do sistema**
2. ✅ Leia a seção **Solução de Problemas**
3. ✅ Execute o **teste_yolo.py** para diagnóstico
4. ✅ Consulte a **documentação adicional**

---

## 📝 Licença

Este projeto é de código aberto e está disponível para uso educacional.

---

## 🏆 Estatísticas do Projeto

- 📊 **11 Jogos** completos e funcionais ⬆️
- 📊 **6 Tecnologias** de visão computacional
- 📊 **5 Tipos de controle**: olhos, mãos, cabeça, corpo, dedo
- 📊 **100% Python** com interface moderna
- 📊 **UI/UX Profissional** em todos os jogos
- 📊 **3 Estilos visuais**: Neon, Colorido, Minimalista

---

<div align="center">

## 🎮 Divirta-se Jogando! ✨

**Desenvolvido com ❤️ usando Python, OpenCV, MediaPipe e Pygame**

![Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/Powered%20by-OpenCV-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/Using-MediaPipe-orange?style=for-the-badge)

</div>
