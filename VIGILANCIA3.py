import time
import cv2
import keyboard  # Para monitorear el teclado
import msvcrt  # Para detectar teclas en Windows
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, messagebox

# Función para obtener el horario y fecha de activación usando una ventana de Tkinter
def obtener_horario_fecha():
    def guardar_fecha_hora():
        nonlocal fecha_hora  # Usamos nonlocal para modificar la variable en el ámbito superior
        fecha_hora = entry_fecha_hora.get()
        try:
            # Verifica que la fecha y hora tengan el formato correcto
            datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
            ventana.destroy()  # Cierra la ventana
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha y hora incorrecto. Usa YYYY-MM-DD HH:MM.")

    # Variable para almacenar la fecha y hora
    fecha_hora = None

    # Crear la ventana de Tkinter
    ventana = Tk()
    ventana.title("Configurar fecha y hora de activación")
    ventana.geometry("300x150")

    # Etiqueta y campo de entrada
    Label(ventana, text="Fecha y hora (YYYY-MM-DD HH:MM):").pack(pady=10)
    entry_fecha_hora = Entry(ventana)
    entry_fecha_hora.pack(pady=10)

    # Botón para guardar la fecha y hora
    Button(ventana, text="Guardar", command=guardar_fecha_hora).pack(pady=10)

    # Iniciar el bucle de la ventana
    ventana.mainloop()

    return fecha_hora

# Función para verificar si la hora actual es igual a la hora de activación
def es_hora_de_activar(fecha_hora_activacion):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    return ahora >= fecha_hora_activacion

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

# Obtener la fecha y hora de activación desde la ventana de Tkinter
fecha_hora_activacion = obtener_horario_fecha()

try:
    print("Esperando la hora de activación...")
    while not es_hora_de_activar(fecha_hora_activacion):
        time.sleep(30)  # Verifica cada 30 segundos si es hora de activar

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
                inicio_grabacion = time.time()  # Registra el momento en que comenzó la grabación
                print(f"Movimiento detectado. Iniciando grabación: {video_filename}")

        # Si se presiona cualquier tecla, inicia la grabación
        if keyboard.is_pressed('enter'):  # Usamos la tecla 'enter' como ejemplo
            if not grabando:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                video_filename = f"grabacion_{timestamp}.avi"
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                inicio_grabacion = time.time()
                print(f"Tecla presionada. Iniciando grabación: {video_filename}")

        # Dentro del bucle principal:
        if msvcrt.kbhit():  # Detecta si se presionó una tecla
            key = msvcrt.getch()  # Obtiene la tecla presionada
            if not grabando:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                video_filename = f"grabacion_{timestamp}.avi"
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                inicio_grabacion = time.time()
                print(f"Tecla presionada. Iniciando grabación: {video_filename}")

        # Si está grabando, guarda el frame
        if grabando:
            out.write(frame2)

            # Detiene la grabación después de 5 minutos
            if time.time() - inicio_grabacion >= 300:  # 300 segundos = 5 minutos
                print("Grabación detenida después de 5 minutos.")
                grabando = False
                out.release()

        # Actualiza el frame de referencia
        frame1 = frame2

        # Muestra el video en una ventana (opcional)
        cv2.imshow('Vigilancia', frame2)

        # Detiene el programa si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Libera la cámara y cierra el archivo de video
    camera.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    print("Vigilancia detenida.")