import time
import cv2
import keyboard  # Para monitorear el teclado
import msvcrt  # Para detectar teclas en Windows

# Configuración de la cámara
camera = cv2.VideoCapture(0)  # 0 es la cámara predeterminada
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Códec de video
out = None
grabando = False
detection_threshold = 500  # Umbral de detección de movimiento

def detect_motion(prev_frame, curr_frame):
    # Convierte los frames a escala de grises
    gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    # Calcula la diferencia absoluta entre los frames
    diff = cv2.absdiff(gray1, gray2)
    _, diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    # Si la diferencia supera el umbral, hay movimiento
    if cv2.countNonZero(diff) > detection_threshold:
        return True
    return False

try:
    print("Iniciando vigilancia...")
    _, frame1 = camera.read()  # Captura el primer frame
    time.sleep(1)  # Espera un segundo para estabilizar la cámara

    while True:
        # Captura un nuevo frame
        _, frame2 = camera.read()

        # Detección de movimiento
        if detect_motion(frame1, frame2):

            if not grabando:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                video_filename = f"grabacion_{timestamp}.avi"
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                print(f"Movimiento detectado. Iniciando grabación: {video_filename}")

        # Si se presiona cualquier tecla, inicia la grabación
        if keyboard.is_pressed('enter'):  # Usamos la tecla 'space' como ejemplo
            if not grabando:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                video_filename = f"grabacion_{timestamp}.avi"
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                print(f"Tecla presionada. Iniciando grabación: {video_filename}")

        # Dentro del bucle principal:
        if msvcrt.kbhit():  # Detecta si se presionó una tecla
            key = msvcrt.getch()  # Obtiene la tecla presionada
            if not grabando:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                video_filename = f"grabacion_{timestamp}.avi"
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                print(f"Tecla presionada. Iniciando grabación: {video_filename}")
        # Si está grabando, guarda el frame
        if grabando:
            out.write(frame2)

        # Actualiza el frame de referencia
        frame1 = frame2

        # Muestra el video en una ventana (opcional)
        cv2.imshow('Vigilancia', frame2)

        # Detiene la grabación si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Libera la cámara y cierra el archivo de video
    camera.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    print("Vigilancia detenida.")