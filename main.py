import random
import tkinter as tk
import fnmatch
import os
from pygame import mixer

canvas = tk.Tk()
canvas.title("For Caitlin, ")
canvas.geometry("600x650")
canvas.config(bg='black')

rootpath = r"C:\\Users\aming\Downloads\SongsForCaitlin"
pattern = "*.mp3"

mixer.init()

prev_img = tk.PhotoImage(file="prev_img.png")
next_img = tk.PhotoImage(file="next_img.png")
pause_img = tk.PhotoImage(file="pause_img.png")
stop_img = tk.PhotoImage(file="stop_img.png")
play_img = tk.PhotoImage(file="play_img.png")

def select():
    label.config(text=listBox.get("anchor"))
    mixer.music.load(rootpath + "\\" + listBox.get("anchor"))
    mixer.music.play()


def stop():
    mixer.music.stop()
    listBox.select_clear('active')

def playnext():
    next_song = listBox.curselection()
    next_song = next_song[0] + 1
    next_song_name = listBox.get(next_song)
    label.config(text=next_song_name)

    mixer.music.load(rootpath + "\\" + next_song_name)
    mixer.music.play()

    listBox.select_clear(0,'end')
    listBox.activate(next_song)
    listBox.select_set(next_song)


def playprev():
    prev_song = listBox.curselection()
    prev_song = prev_song[0] - 1
    prev_song_name = listBox.get(prev_song)
    label.config(text=prev_song_name)

    mixer.music.load(rootpath + "\\" + prev_song_name)
    mixer.music.play()

    listBox.select_clear(0,'end')
    listBox.activate(prev_song)
    listBox.select_set(prev_song)


def pausesong():
    if pauseButton["text"] == "Pause":
        mixer.music.pause()
        pauseButton["text"] == "Play"
    else:
        mixer.music.unpause()
        pauseButton["text"] = "Play"

text_widget1 = tk.Text(canvas, width=60, height=1, bg='black', fg='white', font=('calibri', 13))
text_widget1.pack(pady=5, anchor='center')

text_widget1.insert(tk.END, "A playlist of songs for my amazing, sweet girlfriend")

top = tk.Frame(canvas, bg='black')
top.pack(padx=10, anchor='center')

prevButton = tk.Button(canvas, text="Previous", image=prev_img, bg='black', borderwidth=0, command=playprev)
prevButton.pack(padx=5, in_=top, side='left')

playButton = tk.Button(canvas, text="Play", image=play_img, bg='black', borderwidth=0, command=select)
playButton.pack(padx=5, in_=top, side='left')

pauseButton = tk.Button(canvas, text="Pause", image=pause_img, bg='black', borderwidth=0, command=pausesong)
pauseButton.pack(padx=5, in_=top, side='left')

stopButton = tk.Button(canvas, text="Stop", image=stop_img, bg='black', borderwidth=0, command=stop)
stopButton.pack(padx=5, in_=top, side='left')

nextButton = tk.Button(canvas, text="Next", image=next_img, bg='black', borderwidth=0, command=playnext)
nextButton.pack(padx=5, in_=top, side='left')

listBox = tk.Listbox(canvas, fg="yellow", bg="black", width=100, height=19, font=('ds-digital italic', 15))
listBox.pack(padx=10, pady=10)

label = tk.Label(canvas, text='', bg='black', fg='yellow', font=('ds-digital', 15))
label.pack(pady=10)

text_widget2 = tk.Text(canvas, width=60, height=2, bg='black', fg='white', font=('calibri', 13))
text_widget2.pack(pady=5, anchor='center')

text_widget2.insert(tk.END, "I miss you Caitie <3\nHopefully this was worth the wait?")

for root, dirs, files in os.walk(rootpath):
    for filename in fnmatch.filter(files, pattern):
        listBox.insert('end', filename)


canvas.mainloop()
