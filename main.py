import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import simpledialog, Button, Text, Scrollbar, END, Scale
import pyttsx3
import PyPDF2
import threading

# Define color schemes
normal_colors = {
    "background": "SystemButtonFace",
    "text": "black",
    "button": "SystemButtonFace",
    "canvas": "white",
    "subtitle_text": "black"
}

high_contrast_colors = {
    "background": "black",
    "text": "white",
    "button": "yellow",
    "canvas": "black",
    "subtitle_text": "yellow"
}

# Global variables
text_id = None
speech_rate = 150
font_size = 12

def apply_color_scheme(colors):
    root.config(bg=colors["background"])
    pause_button.config(bg=colors["button"], fg=colors["text"])
    resume_button.config(bg=colors["button"], fg=colors["text"])
    high_contrast_button.config(bg=colors["button"], fg=colors["text"])
    speech_rate_label.config(bg=colors["background"], fg=colors["text"])
    subtitle_text.config(bg=colors["canvas"], fg=colors["subtitle_text"])
    canvas.config(bg=colors["canvas"])
    canvas.itemconfig(text_id, fill=colors["text"])

def toggle_high_contrast():
    global high_contrast_mode
    high_contrast_mode = not high_contrast_mode
    colors = high_contrast_colors if high_contrast_mode else normal_colors
    apply_color_scheme(colors)

def update_subtitle(text):
    def _update():
        subtitle_text.config(state=tk.NORMAL)
        subtitle_text.delete(1.0, END)
        subtitle_text.insert(END, text)
        subtitle_text.config(state=tk.DISABLED)

    root.after(0, _update)

def read_pdf(file_path, start_page):
    global pause_reading, currently_speaking, speech_rate

    try:
        with open(file_path, 'rb') as book:
            pdfReader = PyPDF2.PdfReader(book)
            speaker = pyttsx3.init()

            for page_num in range(start_page, len(pdfReader.pages)):
                if pause_reading:
                    while pause_reading:
                        continue
                page = pdfReader.pages[page_num]
                text = page.extract_text()
                for sentence in text.split('.'):
                    if pause_reading:
                        while pause_reading:
                            continue
                    update_subtitle(sentence)

                    # Update and use the current speech rate for each sentence
                    speaker.setProperty('rate', speech_rate)
                    speaker.say(sentence)
                    speaker.runAndWait()

            currently_speaking = False

    except Exception as e:
        print("An error occurred:", e)

def on_drop(event):
    global currently_speaking
    if not currently_speaking:
        file_path = event.data
        start_page = simpledialog.askinteger("Start Page", "Enter start page number:", minvalue=0)

        if start_page is not None:
            currently_speaking = True
            threading.Thread(target=read_pdf, args=(file_path, start_page)).start()

def pause_speech():
    global pause_reading
    pause_reading = True

def resume_speech():
    global pause_reading
    pause_reading = False

def update_speech_rate(value):
    global speech_rate
    speech_rate = int(value)

def change_font_size(delta):
    global font_size
    font_size = max(1, font_size + delta)
    subtitle_text.config(font=("Helvetica", font_size))

# GUI setup
root = TkinterDnD.Tk()
root.title("PDF Reader")

high_contrast_mode = False

canvas = tk.Canvas(root, width=400, height=200)
canvas.pack()

text_id = canvas.create_text(200, 100, text="Drag and drop a PDF here", font=("Helvetica", 16))
canvas.drop_target_register(DND_FILES)
canvas.dnd_bind('<<Drop>>', on_drop)

pause_button = Button(root, text="Pause", command=pause_speech)
pause_button.pack(side=tk.LEFT)

resume_button = Button(root, text="Resume", command=resume_speech)
resume_button.pack(side=tk.RIGHT)

high_contrast_button = Button(root, text="High Contrast Mode", command=toggle_high_contrast)
high_contrast_button.pack()

# Speech rate control
speech_rate_label = tk.Label(root, text="Speech Rate:")
speech_rate_label.pack()

speech_rate_slider = Scale(root, from_=50, to=400, orient=tk.HORIZONTAL, command=update_speech_rate)
speech_rate_slider.set(150)  # Default rate
speech_rate_slider.pack()

# Font size control
font_size_frame = tk.Frame(root)
increase_font_button = Button(font_size_frame, text="+", command=lambda: change_font_size(1))
decrease_font_button = Button(font_size_frame, text="-", command=lambda: change_font_size(-1))
increase_font_button.pack(side=tk.LEFT)
decrease_font_button.pack(side=tk.LEFT)
font_size_frame.pack()

# Subtitle text widget setup
subtitle_frame = tk.Frame(root)
subtitle_scrollbar = Scrollbar(subtitle_frame)
subtitle_text = Text(subtitle_frame, height=4, wrap=tk.WORD, yscrollcommand=subtitle_scrollbar.set)
subtitle_scrollbar.config(command=subtitle_text.yview)
subtitle_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
subtitle_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
subtitle_text.config(state=tk.DISABLED, font=("Helvetica", font_size))
subtitle_frame.pack(fill=tk.BOTH, expand=True)

apply_color_scheme(normal_colors)  # Apply the normal color scheme initially

pause_reading = False
currently_speaking = False

root.mainloop()
