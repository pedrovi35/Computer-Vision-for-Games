"""
Configuração para suprimir warnings desnecessários do TensorFlow e MediaPipe
Importe este módulo no início de cada jogo para ter uma execução limpa
"""

import os
import warnings
import logging

# Suprime warnings do TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0=ALL, 1=INFO, 2=WARNING, 3=ERROR
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suprime warnings do absl (usado pelo TensorFlow)
logging.getLogger('absl').setLevel(logging.ERROR)

# Suprime warnings gerais do Python
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Suprime warnings específicos do MediaPipe
logging.getLogger('mediapipe').setLevel(logging.ERROR)

# Suprime warnings do PyTorch
warnings.filterwarnings('ignore', message='.*torch.*')

print("✅ Configurações de warnings aplicadas - execução limpa!")



