"""
Script de teste rápido para verificar a detecção YOLO
Mostra todos os objetos detectados em tempo real com estatísticas
"""

import cv2
import time
from ultralytics import YOLO
import torch

# Carrega o modelo
print("Carregando modelo YOLO...")
model = YOLO('yolov5su.pt')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
print(f"Modelo carregado! Usando: {device}")

# Configurações
CONFIDENCE = 0.35
IOU = 0.4
IMGSZ = 640

# Abre a webcam
print("\nAbrindo webcam...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("❌ Erro ao abrir a webcam!")
    exit()

print("✅ Webcam aberta!")
print("\n" + "="*60)
print("TESTE DE DETECÇÃO YOLO")
print("="*60)
print("Pressione 'q' para sair")
print("Pressione 'c' para capturar screenshot")
print("="*60 + "\n")

frame_count = 0
start_time = time.time()
detection_count = {}

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Erro ao ler frame")
            break
        
        # Pré-processamento
        processed_frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=10)
        
        # Detecção
        results = model(
            processed_frame,
            conf=CONFIDENCE,
            iou=IOU,
            imgsz=IMGSZ,
            verbose=False,
            half=True if device == 'cuda' else False
        )
        
        # Processa detecções
        detected_objects = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                conf = float(box.conf[0])
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                box_area = (x2 - x1) * (y2 - y1)
                
                detected_objects.append({
                    'class': class_name,
                    'conf': conf,
                    'area': box_area,
                    'bbox': (x1, y1, x2, y2)
                })
                
                # Atualiza contador
                if class_name not in detection_count:
                    detection_count[class_name] = 0
                detection_count[class_name] += 1
                
                # Desenha no frame
                color = (0, 255, 0) if conf >= 0.5 else (0, 165, 255)  # Verde ou Laranja
                thickness = 3 if conf >= 0.5 else 2
                
                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, thickness)
                
                # Label com fundo
                label = f"{class_name}: {conf:.2f}"
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(processed_frame, (x1, y1 - text_h - 10), (x1 + text_w + 5, y1), color, -1)
                cv2.putText(processed_frame, label, (x1 + 2, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Calcula FPS
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            
            # Mostra estatísticas no console
            print(f"\n{'='*60}")
            print(f"⏱️  FPS: {fps:.1f}")
            print(f"🎯 Detecções neste frame: {len(detected_objects)}")
            if detected_objects:
                print(f"\n📦 Objetos detectados:")
                for obj in detected_objects:
                    print(f"  • {obj['class']:20} Confiança: {obj['conf']:.2%}  Área: {obj['area']:6d}px")
        
        # Adiciona info no frame
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        info_y = 30
        cv2.rectangle(processed_frame, (10, 10), (400, info_y + 80), (0, 0, 0), -1)
        cv2.putText(processed_frame, f"FPS: {fps:.1f}", (20, info_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(processed_frame, f"Detectados: {len(detected_objects)}", (20, info_y + 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(processed_frame, f"Device: {device.upper()}", (20, info_y + 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Legenda de cores
        legend_y = processed_frame.shape[0] - 50
        cv2.rectangle(processed_frame, (10, legend_y), (300, legend_y + 40), (0, 0, 0), -1)
        cv2.rectangle(processed_frame, (20, legend_y + 10), (50, legend_y + 30), (0, 255, 0), -1)
        cv2.putText(processed_frame, "Alta confianca (>0.5)", (60, legend_y + 27), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Mostra o frame
        cv2.imshow('Teste YOLO - Detecção de Objetos', processed_frame)
        
        # Controles
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            filename = f"captura_{int(time.time())}.jpg"
            cv2.imwrite(filename, processed_frame)
            print(f"\n📸 Screenshot salvo: {filename}")

finally:
    # Estatísticas finais
    print("\n" + "="*60)
    print("ESTATÍSTICAS FINAIS")
    print("="*60)
    
    if detection_count:
        print("\n🏆 Objetos mais detectados:")
        sorted_detections = sorted(detection_count.items(), key=lambda x: x[1], reverse=True)
        for obj, count in sorted_detections[:10]:
            print(f"  {count:4d}x  {obj}")
    else:
        print("\n⚠️  Nenhum objeto foi detectado!")
        print("   Dicas:")
        print("   • Verifique a iluminação")
        print("   • Posicione objetos mais próximos da câmera")
        print("   • Use objetos comuns (celular, garrafa, caneca, etc)")
    
    elapsed = time.time() - start_time
    fps_avg = frame_count / elapsed if elapsed > 0 else 0
    print(f"\n⏱️  Tempo total: {elapsed:.1f}s")
    print(f"🎬 Frames processados: {frame_count}")
    print(f"📊 FPS médio: {fps_avg:.1f}")
    print(f"💻 Device: {device.upper()}")
    print("\n" + "="*60)
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Teste finalizado!")

