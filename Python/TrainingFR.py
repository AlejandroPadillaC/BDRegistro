import cv2
import os
import numpy as np
from tkinter import PhotoImage, Tk, Label, Button, filedialog, messagebox
from PIL import Image, ImageTk

def select_folder():
    global dataPath, peopleList, labels, facesData, label
    dataPath = filedialog.askdirectory(title='Selecciona la carpeta de imágenes')
    if not dataPath:
        messagebox.showwarning("Advertencia", "No se seleccionó ninguna carpeta.")
        return
    peopleList = os.listdir(dataPath)
    print('Lista de personas: ', peopleList)
    labels = []
    facesData = []
    label = 0
    messagebox.showinfo("Informacion","Se estan leyendo las imagenes")
    for nameDir in peopleList:
        personPath = os.path.join(dataPath, nameDir)
        
        for fileName in os.listdir(personPath):
            if fileName.endswith(('.png', '.jpg', '.jpeg')):
                #print('Rostros: ', os.path.join(nameDir, fileName))
                labels.append(label)
                image = cv2.imread(os.path.join(personPath, fileName), 0)
                if image is not None:
                    facesData.append(image)
                    #cv2.imshow('image', image)
                    cv2.waitKey(10)
                else:
                    print(f'Error al cargar la imagen: {fileName}')
        label += 1
    messagebox.showinfo("Información", "Imágenes cargadas correctamente.")

def train_model():
    global face_recognizer
    if not facesData or not labels:
        messagebox.showwarning("Advertencia", "No hay datos para entrenar el modelo.")
        return
    face_recognizer = cv2.face.FisherFaceRecognizer_create()
    messagebox.showinfo("Informacion","Entrenando modelo")
    face_recognizer.train(facesData, np.array(labels))
    messagebox.showinfo("Información", "Modelo entrenado correctamente.")

def save_model():
    global face_recognizer
    if 'face_recognizer' not in globals():
        messagebox.showwarning("Advertencia", "No hay modelo entrenado para guardar.")
        return
    model_save_path = filedialog.asksaveasfilename(defaultextension=".xml",
                                                   filetypes=[("XML files", "*.xml")],
                                                   title="Guardar modelo como")
    if model_save_path:
        face_recognizer.write(model_save_path)
        print("Modelo almacenado en:", model_save_path)
        messagebox.showinfo("Información", f"Modelo almacenado en: {model_save_path}")
    else:
        messagebox.showwarning("Advertencia", "No se guardó el modelo.")

def exit_application():
    pantalla.destroy()

def main():
    global pantalla, dataPath, peopleList, labels, facesData, label, face_recognizer
    pantalla = Tk()
    pantalla.title("Puntualify")
    pantalla.iconphoto(False, PhotoImage(file="C:/Users/Alejandro Padilla/Documents/Programacion/POO/Sistema-de-Reconocimiento-Facial/Temas/LogoPOO.png"))

    screen_width = pantalla.winfo_screenwidth()
    screen_height = pantalla.winfo_screenheight()
    width = 800
    height = 500
    pantalla.geometry("{}x{}".format(width, height))
    pantalla .geometry("+{}+{}".format(int((screen_width/2) - (width/2)), int((screen_height/2) - (height/2))))

    # Cargar la imagen de fondo
    background_image = Image.open("C:\\Users\\Alejandro Padilla\\Documents\\Programacion\\POO\\Sistema-de-Reconocimiento-Facial\\Temas\\Informacion.png")
    background_image = background_image.resize((800, 500), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)

    # Crear un Label para la imagen de fondo
    background_label = Label(pantalla, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Botón para seleccionar la carpeta de imágenes
    btn_select_folder = Button(pantalla, text="Seleccionar carpeta de imágenes", command=select_folder, font=("Sans Serif", 12, "bold"))
    btn_select_folder.place(x=200, y=100, width=300, height=40)

    # Botón para entrenar el modelo
    btn_train_model = Button(pantalla, text="Entrenar modelo", command=train_model, font=("Roboto Black", 12, "bold"))
    btn_train_model.place(x=200, y=200, width=300, height=40)

    btn_exit_model = Button(pantalla, text="Regresar", command=exit_application,  font=("Roboto Black", 12, "bold"), bg="#ff6600")
    btn_exit_model.place(x=75, y=450, width=100, height=30)

    # Botón para guardar el modelo
    btn_save_model = Button(pantalla, text="Guardar modelo", command=save_model, font=("Roboto Black", 12, "bold"),fg="black", bg="#ff6600")
    btn_save_model.place(x=200, y=300, width=300, height=40)
    pantalla.mainloop()

if __name__ == "__main__":
    main()
