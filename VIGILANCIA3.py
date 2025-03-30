import time
import cv2
import keyboard  # Para monitorear el teclado
import msvcrt  # Para detectar teclas en Windows
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, messagebox, filedialog
import os  # Para manejar rutas
import pyaudio  # Para capturar audio
import wave  # Para guardar el audio
from moviepy.editor import VideoFileClip, AudioFileClip  # Para combinar video y audio

# Función para obtener el horario, fecha y carpeta de guardado usando una ventana de Tkinter
def obtener_configuracion():
    def guardar_configuracion():
        nonlocal fecha_hora, carpeta_guardado  # Usamos nonlocal para modificar las variables en el ámbito superior
        fecha_hora = entry_fecha_hora.get()
        try:
            # Verifica que la fecha y hora tengan el formato correcto
            datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
            ventana.destroy()  # Cierra la ventana
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha y hora incorrecto. Usa YYYY-MM-DD HH:MM.")

    def seleccionar_carpeta():
        nonlocal carpeta_guardado
        carpeta_guardado = filedialog.askdirectory()  # Abre un diálogo para seleccionar una carpeta
        if carpeta_guardado:
            label_carpeta.config(text=f"Carpeta seleccionada: {carpeta_guardado}")

    # Variables para almacenar la fecha, hora y carpeta de guardado
    fecha_hora = None
    carpeta_guardado = None

    # Crear la ventana de Tkinter
    ventana = Tk()
    ventana.title("Configurar vigilancia")
    ventana.geometry("400x250")
    ventana.configure(bg="#87CEEB")  # Fondo celeste suave

    # Etiqueta y campo de entrada para la fecha y hora
    label_fecha_hora = Label(ventana, text="Fecha y hora (YYYY-MM-DD HH:MM):", fg="white", bg="#87CEEB", font=("Arial", 12))
    label_fecha_hora.pack(pady=10)
    entry_fecha_hora = Entry(ventana, font=("Arial", 12))
    entry_fecha_hora.pack(pady=10)

    # Botón para seleccionar la carpeta de guardado
    boton_carpeta = Button(ventana, text="Seleccionar carpeta", command=seleccionar_carpeta, fg="black", bg="#D3D3D3", font=("Arial", 12))
    boton_carpeta.pack(pady=10)
    label_carpeta = Label(ventana, text="Carpeta seleccionada: Ninguna", fg="white", bg="#87CEEB", font=("Arial", 12))
    label_carpeta.pack(pady=10)

    # Botón para guardar la configuración
    boton_guardar = Button(ventana, text="Guardar", command=guardar_configuracion, fg="black", bg="#D3D3D3", font=("Arial", 12))
    boton_guardar.pack(pady=20)

    # Iniciar el bucle de la ventana
    ventana.mainloop()

    return fecha_hora, carpeta_guardado

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

# Configuración de audio
audio = pyaudio.PyAudio()
audio_stream = None
audio_frames = []

def iniciar_audio():
    global audio_stream
    audio_stream = audio.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=44100,
                             input=True,
                             frames_per_buffer=1024)

def detener_audio():
    global audio_stream
    if audio_stream:
        audio_stream.stop_stream()
        audio_stream.close()

def grabar_audio():
    global audio_frames
    audio_frames = []
    if audio_stream:
        for _ in range(0, int(44100 / 1024 * 300)):  # Grabar 5 minutos de audio
            data = audio_stream.read(1024)
            audio_frames.append(data)

def guardar_audio(nombre_archivo):
    with wave.open(nombre_archivo, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(audio_frames))

def combinar_video_audio(video_file, audio_file, output_file):
    video_clip = VideoFileClip(video_file)
    audio_clip = AudioFileClip(audio_file)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_file, codec='libx264')

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

# Obtener la fecha, hora y carpeta de guardado desde la ventana de Tkinter
fecha_hora_activacion, carpeta_guardado = obtener_configuracion()

try:
    print("Esperando la hora de activación...")
    while not es_hora_de_activar(fecha_hora_activacion):
        time.sleep(30)  # Verifica cada 30 segundos si es hora de activar

    print("Iniciando vigilancia...")
    _, frame1 = camera.read()  # Captura el primer frame
    time.sleep(1)  # Espera un segundo para estabilizar la cámara

    # Iniciar la captura de audio
    iniciar_audio()

    while True:
        # Captura un nuevo frame
        _, frame2 = camera.read()

        # Detección de movimiento
        if detect_motion(frame1, frame2):
            if not grabando:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                video_filename = os.path.join(carpeta_guardado, f"grabacion_{timestamp}.avi")
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                inicio_grabacion = time.time()  # Registra el momento en que comenzó la grabación
                print(f"Movimiento detectado. Iniciando grabación: {video_filename}")
                grabar_audio()  # Iniciar la grabación de audio

        # Si se presiona cualquier tecla, inicia la grabación
        if keyboard.is_pressed('enter'):  # Usamos la tecla 'enter' como ejemplo
            if not grabando:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                video_filename = os.path.join(carpeta_guardado, f"grabacion_{timestamp}.avi")
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                inicio_grabacion = time.time()
                print(f"Tecla presionada. Iniciando grabación: {video_filename}")
                grabar_audio()  # Iniciar la grabación de audio

        # Dentro del bucle principal:
        if msvcrt.kbhit():  # Detecta si se presionó una tecla
            key = msvcrt.getch()  # Obtiene la tecla presionada
            if not grabando:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                video_filename = os.path.join(carpeta_guardado, f"grabacion_{timestamp}.avi")
                out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
                grabando = True
                inicio_grabacion = time.time()
                print(f"Tecla presionada. Iniciando grabación: {video_filename}")
                grabar_audio()  # Iniciar la grabación de audio

        # Si está grabando, guarda el frame
        if grabando:
            # Agrega la fecha y hora al frame
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame2, fecha_hora, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)  # Letras pequeñas y rojas
            out.write(frame2)

            # Detiene la grabación después de 5 minutos
            if time.time() - inicio_grabacion >= 300:  # 300 segundos = 5 minutos
                print("Grabación detenida después de 5 minutos.")
                grabando = False
                out.release()
                detener_audio()

                # Guardar el audio
                audio_filename = os.path.join(carpeta_guardado, f"audio_{timestamp}.wav")
                guardar_audio(audio_filename)

                # Combinar video y audio
                output_filename = os.path.join(carpeta_guardado, f"grabacion_con_audio_{timestamp}.avi")
                combinar_video_audio(video_filename, audio_filename, output_filename)

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
    detener_audio()
    print("Vigilancia detenida.")