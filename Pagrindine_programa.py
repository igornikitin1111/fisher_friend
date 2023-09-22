import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import subprocess

def simulate_loading():
    progress_bar['maximum'] = 100
    for i in range(101):
        time.sleep(0.03)
        progress_bar['value'] = i
        root.update_idletasks()
    
    root.destroy()

root = tk.Tk()
root.title("Fisher Friend")

root.geometry("1000x666")

image_filename = 'bg.png'
bg_image = Image.open(image_filename)
bg_photo = ImageTk.PhotoImage(bg_image)
background_label = tk.Label(root, image=bg_photo)
background_label.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg='white')
frame.place(relx=0.5, rely=0.5, anchor='center')

progress_bar = ttk.Progressbar(frame, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=20)

start_button = tk.Button(frame, text="Paleisti Fisher Friend programą", command=simulate_loading)
start_button.pack()

root.mainloop()

subprocess.Popen(['python', 'main.py'])