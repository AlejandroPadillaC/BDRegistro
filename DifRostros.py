from collections import deque
import cv2
import os
import threading
import tkinter as tk
from tkinter import PhotoImage
import json
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': '3306',
    'database': 'bdusuarios1'
}

dataPath = 'C:\\Users\\Alejandro Padilla\\Documents\\Programacion\\POO\\Sistema-de-Reconocimiento-Facial\\Data'
pathxml = "C:\\Users\\Alejandro Padilla\\Documents\\Programacion\\POO\\Sistema-de-Reconocimiento-Facial\\haarcascade_frontalface_default.xml"

imagePaths = os.listdir(dataPath)
face_recognizer = cv2.face.FisherFaceRecognizer_create()
face_recognizer.read('C:/Users/Alejandro Padilla/Documents/Programacion/POO/Sistema-de-Reconocimiento-Facial/3.xml')

faceClassif = cv2.CascadeClassifier(pathxml)

# Inicialización del contador de asistencia
attendance_counter = {name: 0 for name in imagePaths}
recognized_people = set()
running = False
cap = None  # Inicializar cap como None

def save_attendance():
    with open('attendance.json', 'w') as f:
        json.dump(attendance_counter, f)

def get_user_id_by_name(name):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "SELECT id FROM usuarios WHERE nombres = %s"
        cursor.execute(sql, (name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def register_attendance_in_db(user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        now = datetime.now()
        sql = "INSERT INTO asistencia (user_id, fecha) VALUES (%s, %s)"
        values = (user_id, now.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        message = f"Asistencia registrada para user_id {user_id} a las {now.strftime('%Y-%m-%d %H:%M:%S')}"
        print(message)
        attendance_message_label.config(text=message)
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def update_frame():
    global recognized_people, running, cap
    if running:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceClassif.detectMultiScale(gray, 1.1, 8)

            for (x, y, w, h) in faces:
                rostro = cv2.resize(gray[y:y + h, x:x + w], (150, 150), interpolation=cv2.INTER_CUBIC)
                result = face_recognizer.predict(rostro)

                recent_results.append(result[0])
                
                # Promediar las últimas predicciones
                if len(recent_results) > 5:  # Suavizado con los últimos 5 fotogramas
                    recent_results.popleft()

                most_common_result = max(set(recent_results), key=recent_results.count)

                if result[1] < 120:
                    # Verificar que result[0] esté dentro de los límites de imagePaths
                    if 0 <= result[0] < len(imagePaths):
                        person_name = imagePaths[result[0]]
                        user_id = get_user_id_by_name(person_name)

                        if user_id and person_name not in recognized_people:
                            try:
                                attendance_counter[person_name] += 1
                                save_attendance()  # Guardar asistencia después de actualizar el contador
                            except KeyError:
                                print(f"Error: {person_name} no está en attendance_counter.")
                            recognized_people.add(person_name)
                            register_attendance_in_db(user_id)

                        cv2.putText(frame, person_name, (x, y - 25), 2, 1.1, (0, 255, 0), 1, cv2.LINE_AA)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                else:
                    cv2.putText(frame, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Convertir el marco a imagen y mostrarlo en Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

        video_label.after(10, update_frame)

recent_results = deque(maxlen=5)


def start_video_capture():
    global running, cap
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Mover la inicialización aquí
    running = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
 
    video_label.pack()  # Mostrar el video
    update_frame()

def stop_video_capture():
    global running, cap
    running = False
    if cap is not None:
        cap.release()  # Liberar la captura de video
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
   
    video_label.pack_forget()  # Ocultar el video

def close_app():
    stop_video_capture()
    root.quit()

# Función para configurar la interfaz gráfica
def configurar_interfaz():
    global root, attendance_message_label, start_button, stop_button, attendance_label, video_label, bg_photo

    # Inicialización de la interfaz gráfica
    root = tk.Tk()
    root.title("Puntualify")
    root.iconphoto(False, PhotoImage(file="C:/Users/Alejandro Padilla/Documents/Programacion/POO/Sistema-de-Reconocimiento-Facial/Temas/LogoPOO.png"))

    # Cargar la imagen de fondo
    bg_image = Image.open("C:/Users/Alejandro Padilla/Documents/Programacion/POO/Sistema-de-Reconocimiento-Facial/Temas/ReconocimientoOS.png")  # Cambia esto a tu imagen
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Crear un label para mostrar la imagen de fondo
    background_label = tk.Label(root, image=bg_photo)
    background_label.place(relwidth=1, relheight=1)

    # Tamaño de la ventana
    window_width = 800
    window_height = 500

    # Obtener las dimensiones de la pantalla
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcular la posición centrada
    x = (screen_width // 2) - (window_width // 2) - 8
    y = (screen_height // 2) - (window_height // 2) - 43

    # Establecer la geometría de la ventana
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Crear un marco con bordes para el video
    frame = tk.Frame(root, bd=2, relief=tk.GROOVE, bg='black')
    frame.place(relx=0.3, rely=0.5, relwidth=0.5, relheight=0.8, anchor=tk.CENTER)

    # Cargar la imagen
    image_path = "C:/Users/Alejandro Padilla/Documents/Programacion/POO/Sistema-de-Reconocimiento-Facial/Temas/ReconocimientoOS.png"
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    # Etiqueta para mostrar la imagen como fondo
    video_label = tk.Label(frame, image=photo)
    video_label.pack(fill="both", expand=True)
    # Crear etiquetas y botones
    attendance_message_label = tk.Label(root, text="", bg='white',font=("Roboto Black", 12, "bold"), justify=tk.LEFT)
    attendance_message_label.pack(pady=10)

    start_button = tk.Button(root, text="Iniciar Captura",font=("Roboto Black", 12, "bold"), command=start_video_capture, bg="#ff6600")
    start_button.place(x=600,y=150,width=150, height=40)

    stop_button = tk.Button(root, text="Detener Captura", command=stop_video_capture,fg="black",font=("Roboto Black", 12, "bold"), state=tk.DISABLED, bg="#ff6600")
    stop_button.place(x=600,y=225,width=150, height=40)

    close_button = tk.Button(root, text="Regresar",font=("Roboto Black", 12, "bold"), command=close_app, bg="#ff6600")
    close_button.place(x=600,y=300,width=150, height=40)

# Punto de entrada principa
configurar_interfaz()
root.mainloop()
