from twilio.rest import Client
from datetime import datetime
from collections import deque
from tkinter import messagebox, simpledialog
import cv2
import os
import threading
import tkinter as tk
from tkinter import PhotoImage
import json
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk
import time

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': '3306',
    'database': 'bdusuarios1'
}

account_sid = 'ACe1f6b0a990171a46bf585894f66fee3d'
auth_token = 'f534a880a149fbe6a0ac9ebd68023769'
FROM_NUMBER = 'whatsapp:+14155238886'
TO_NUMBER = ['whatsapp:+573196476264', 'whatsapp:+573186135778'] 

current_recognition = {'name': None,'start_time': None}

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

def send_notification(strname):
    client = Client(account_sid, auth_token)
    now = datetime.now()
    fecha = now.strftime("%d-%m-%Y %H:%M")
    message_body = f"{fecha} | Se registró la asistencia de: " + strname
    for to_number in TO_NUMBER:
        message = client.messages.create(
            body=message_body,
            from_=FROM_NUMBER,
            to=to_number
        )
    print(f"Mensaje enviado a {to_number}: {message.sid}")

def get_user_id_by_name(name):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)  # Cursor con buffering activado
        sql = "SELECT id FROM usuarios WHERE Documento = %s"
        cursor.execute(sql, (name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def get_user_fullname_by_document(document):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)  # Cursor con buffering activado
        sql = "SELECT nombres, apellidos FROM usuarios WHERE Documento = %s"
        cursor.execute(sql, (document,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"{result[0]} {result[1]}" if result else None
    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
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
            faces = faceClassif.detectMultiScale(gray, 1.1, 10)

            person_name = None

            for (x, y, w, h) in faces:
                rostro = cv2.resize(gray[y:y + h, x:x + w], (150, 150), interpolation=cv2.INTER_CUBIC)
                result = face_recognizer.predict(rostro)

                recent_results.append(result[0])
                
                # Promediar las últimas predicciones
                if len(recent_results) > 8:  # Suavizado con los últimos 5 fotogramas
                    recent_results.popleft()

                most_common_result = max(set(recent_results), key=recent_results.count)

                if result[1] < 80:
                    # Verificar que result[0] esté dentro de los límites de imagePaths
                    if 0 <= result[0] < len(imagePaths):
                        person_name = imagePaths[result[0]]
                        person_name_str = person_name
                        person_name_int = int(person_name)
                        user_id = get_user_id_by_name(person_name)
                        current_time = time.time()

                        if person_name_int == current_recognition['name']:
                            # Acumular el tiempo que el rostro ha sido reconocido
                            if ( current_time - current_recognition['start_time']) >= 3:
                                if user_id and person_name_int not in recognized_people:
                                    try:
                                        verificacion = verify_Assist()
                                        if (user_id == verificacion):

                                            attendance_counter[person_name_str] += 1
                                            recognized_people.add(person_name)
                                            save_attendance() 
                                            register_attendance_in_db(user_id) # Guardar asistencia después de actualizar el contador
                                            send_notification(get_user_fullname_by_document(person_name_int))
                                            current_recognition["name"] = None
                                            current_recognition['start_time'] = time.time()
                                            
                                        else:
                                            messagebox.showwarning("Advertencia"," El ID ingresado no es correcto")
                                    except KeyError:
                                        print(f"Error: {person_name_str} no está en attendance_counter.")
                        else:
                            # Actualizar el reconocimiento actual
                            current_recognition['name'] = person_name_int
                            current_recognition['start_time'] = current_time

                        cv2.putText(frame, str(person_name), (x, y - 25), 2, 1.1, (0, 255, 0), 1, cv2.LINE_AA)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                else:
                    cv2.putText(frame, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            if person_name is None:
                current_recognition['name'] = None
                current_recognition['start_time'] = time.time()

            # Convertir el marco a imagen y mostrarlo en Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

        video_label.after(10, update_frame)

recent_results = deque(maxlen=10)

def verify_Assist():

    user_input = simpledialog.askstring("Entrada", "Por favor ingresa tu ID:")
    if user_input is not None:
        messagebox.showinfo("Informacion", "La id ingresada es: "+ user_input)
        userintinput = int(user_input)
        return userintinput
    else:
        messagebox.showwarning("Advertencia", "Usted no ingreso ningun valor")


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
