import tkinter as tk
from tkinter import *
import cv2
import csv
import os
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time

##### Giao diện chính
window = tk.Tk()
window.title("Nhận diện khuôn mặt")
window.geometry('1280x720')
window.configure(bg='white')

### Chụp ảnh
def take_img():
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    ID = txt.get()
    Name = txt2.get()
    sampleNum = 0

    if not os.path.exists("dataset"):
        os.makedirs("dataset")
    if not os.path.exists("data"):
        os.makedirs("data")

    with open('data/StudentDetails.csv', 'a+', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow([ID, Name])
    csvFile.close()

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            sampleNum += 1
            cv2.imwrite("dataset/" + Name + "." + ID + '.' + str(sampleNum) + ".jpg", gray[y:y + h, x:x + w])
            cv2.imshow('Frame', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif sampleNum > 200:
            break

    cam.release()
    cv2.destroyAllWindows()

    res = "Images Saved for ID : " + ID + " Name : " + Name
    Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
    Notification.place(x=250, y=400)

### Huấn luyện
def trainimg():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    global detector
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    try:
        global faces, Id
        faces, Id = getImagesAndLabels("dataset")
    except Exception as e:
        l = 'please make "dataset" folder & put Images'
        Notification.configure(text=l, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
        Notification.place(x=350, y=400)
        return

    recognizer.train(faces, np.array(Id))
    
    if not os.path.exists("model"):
        os.makedirs("model")
    
    recognizer.save("model/trained_model2.yml")

    res = "Model Trained"
    Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
    Notification.place(x=250, y=400)

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    Ids = []

    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(imageNp)

        for (x, y, w, h) in faces:
            faceSamples.append(imageNp[y:y + h, x:x + w])
            Ids.append(Id)

    return faceSamples, Ids

def getNames():
    names = {}
    with open('data/StudentDetails.csv', 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            names[int(row[0])] = row[1]
    return names

def recognize_faces():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("model/trained_model2.yml")
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    names = getNames()

    cam = cv2.VideoCapture(0)
    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
            if conf < 50:
                name = names[Id]
            else:
                name = "Unknown"

            cv2.putText(img, str(name), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow('Face Recognition', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

def on_closing():
    from tkinter import messagebox
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

Notification = tk.Label(window, text="All things good", bg="Green", fg="white", width=15, height=3)

lbl = tk.Label(window, text="Enter ID", width=20, height=2, fg="black", font=('times', 20, 'italic bold '))
lbl.place(x=200, y=200)

def testVal(inStr, acttyp):
    if acttyp == '1': # insert
        if not inStr.isdigit():
            return False
    return True

message = tk.Label(window, text="Face Recognition System", bg="cyan", fg="black", width=50, height=3, font=('times', 30, 'italic bold '))
message.place(x=80, y=20)

txt = tk.Entry(window, validate="key", width=20, fg="red")
txt['validatecommand'] = (txt.register(testVal), '%P', '%d')
txt.place(x=550, y=210)

lbl2 = tk.Label(window, text="Enter Name", width=20, fg="black", height=2, font=('times', 20, 'italic bold '))
lbl2.place(x=200, y=300)

txt2 = tk.Entry(window, width=20, fg="red")
txt2.place(x=550, y=310)

takeImg = tk.Button(window, text="Take Images", command=take_img, fg="black", bg="green", width=20, height=3, activebackground="Red", font=('times', 20, 'italic bold '))
takeImg.place(x=200, y=500)

trainImg = tk.Button(window, text="Train Images", fg="black", command=trainimg, bg="green", width=20, height=3, activebackground="Red", font=('times', 20, 'italic bold '))
trainImg.place(x=590, y=500)

recognizeImg = tk.Button(window, text="Recognize Faces", fg="black", command=recognize_faces, bg="green", width=20, height=3, activebackground="Red", font=('times', 20, 'italic bold '))
recognizeImg.place(x=980, y=500)

window.mainloop()
