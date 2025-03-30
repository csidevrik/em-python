import cv2
import time
import os

# Configuración de la cámara
camera = cv2.VideoCapture(0)  # 0 es la cámara predeterminada
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None
grabando = False

try:
    while True:
        # Verifica si el equipo está bloqueado (esto es un ejemplo básico)
        # En Windows, no hay una forma nativa de detectar el bloqueo desde Python.
        # Puedes usar una combinación de scripts o herramientas externas.

        # Captura un frame
        ret, frame = camera.read()
        if not ret:
            break

        # Si no está grabando, inicia la grabación
        if not grabando:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            video_filename = f"grabacion_{timestamp}.avi"
            out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
            grabando = True
            print(f"Iniciando grabación: {video_filename}")

        # Graba el frame
        out.write(frame)

        # Muestra el video en una ventana (opcional)
        cv2.imshow('Vigilancia', frame)

        # Detiene la grabación si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Libera la cámara y cierra el archivo de video
    camera.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    print("Grabación detenida.")