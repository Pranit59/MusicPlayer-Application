from tkinter import *
from tkinter import filedialog
from tkinter import ttk  # Import for Progressbar
from pygame import mixer
import sqlite3
import time
from pygame.examples.moveit import HEIGHT

# Initialize pygame mixer
mixer.init()

# Create a connection to SQLite
conn = sqlite3.connect('songs.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    favorite INTEGER DEFAULT 0  -- 0: Not Favorite, 1: Favorite
)
''')
conn.commit()

# Variable to store current loop mode
loop_mode = 0  # 0: Continue Playlist, 1: Single Loop, 2: Random Loop
song_playing = False  # Variable to track if a song is playing

# Placeholder for song paths
song_paths = {}


# Function to load songs from the database when the app starts
def load_songs_from_db():
    cursor.execute('SELECT name, path FROM songs')
    songs = cursor.fetchall()
    for song_name, song_path in songs:
        song_listbox.insert(END, song_name)
        song_paths[song_name] = song_path

# Function to open and add a song
def add_song():
    song_path = filedialog.askopenfilename(title="Choose a song", filetypes=[("Audio Files", "*.mp3 *.wav")])
    if song_path:
        song_name = song_path.split("/")[-1]  # Extract the song name
        song_listbox.insert(END, song_name)  # Display only the song name
        song_paths[song_name] = song_path  # Store the full path for playback

        # Insert the song into the database
        cursor.execute("INSERT INTO songs (name, path) VALUES (?, ?)", (song_name, song_path))
        conn.commit()

# Function to delete the selected song
def delete_song():
    selected_song = song_listbox.get(ACTIVE)  # Get the selected song name
    if selected_song:
        song_listbox.delete(ACTIVE)  # Remove from the Listbox
        song_path = song_paths.pop(selected_song)  # Remove from song_paths dictionary

        # Delete from the database
        cursor.execute("DELETE FROM songs WHERE path = ?", (song_path,))
        conn.commit()

# Function to update the progress bar according to the song's position
def update_progress_bar():
    while song_playing:
        current_time = mixer.music.get_pos() / 1000  # Get the current time in seconds
        song_length = mixer.Sound(song_paths[song_listbox.get(ACTIVE)]).get_length()  # Get the length of the song
        progress_bar['value'] = (current_time / song_length) * 100  # Calculate the percentage for the progress bar
        current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(current_time))}")
        song_length_label.config(text=f"{time.strftime('%M:%S', time.gmtime(song_length))}")
        root.update()  # Update the GUI to reflect changes
        time.sleep(1)
        if not mixer.music.get_busy():  # Stop updating if the song ends
            stop_song()

# Function to play the selected song
def play_pause_song():
    global song_playing
    if play_pause_btn['text'] == "Pause":
        selected_song = song_listbox.get(ACTIVE)  # Get the selected song name
        if selected_song:
            song_path = song_paths[selected_song]  # Retrieve the full path
            mixer.music.load(song_path)
            mixer.music.play()
            song_playing = True  # Mark the song as playing
            play_pause_btn.config(text="Play", image=photo2, bg='white')  # Switch button to "Pause"
            current_song_label.config(text=f"Playing: {selected_song}")  # Update the label with the current song name
            update_progress_bar()  # Start updating the progress bar
    else:
        mixer.music.pause()
        song_playing = False  # Song is paused
        play_pause_btn.config(text="Pause", image=photo1, bg='white')  # Switch button back to "Play"

# Function to play the next song
def next_song():
    current_index = song_listbox.curselection()  # Get the current selected index
    if current_index:
        next_index = (current_index[0] + 1) % song_listbox.size()  # Calculate the next index
        song_listbox.selection_clear(0, END)  # Clear the selection
        song_listbox.selection_set(next_index)  # Set the selection to the next song
        song_listbox.activate(next_index)  # Activate the next song in the listbox
        play_pause_btn.config(text="Pause")  # Switch button to "Pause"
        play_pause_song()  # Play the next song

# Function to play the previous song
def prev_song():
    current_index = song_listbox.curselection()  # Get the current selected index
    if current_index:
        prev_index = (current_index[0] - 1) % song_listbox.size()  # Calculate the previous index
        song_listbox.selection_clear(0, END)  # Clear the selection
        song_listbox.selection_set(prev_index)  # Set the selection to the previous song
        song_listbox.activate(prev_index)  # Activate the previous song in the listbox
        play_pause_btn.config(text="Pause")  # Switch button to "Pause"
        play_pause_song()  # Play the previous song

# Function to switch between loop modes
def switch_loop_mode():
    global loop_mode
    loop_mode = (loop_mode + 1) % 3  # Cycle through the 3 modes
    if loop_mode == 0:
        loop_mode_btn.config(text="Continue Playlist Mode", image=photo5, bg='white')
    elif loop_mode == 1:
        loop_mode_btn.config(text="Single Loop Mode", image=photo6, bg='white')
    else:
        loop_mode_btn.config(text="Random Loop Mode", image=photo7, bg='white')

# Function to mark a song as favorite
def mark_favorite():
    selected_song = song_listbox.get(ACTIVE)
    if selected_song:
        # Check if the song is already favorited
        cursor.execute("SELECT favorite FROM songs WHERE name = ?", (selected_song,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            # If already favorited, do nothing or notify the user
            current_song_label.config(text=f"{selected_song} is already a favorite.")
        else:
            # Mark as favorite in the database
            cursor.execute("UPDATE songs SET favorite = 1 WHERE name = ?", (selected_song,))
            conn.commit()

            # Update the UI
            favorite_button.config(image= photo9, bg='white')  # Change the button image
            current_song_label.config(text=f"Favorited: {selected_song}")

# Main application window
root = Tk()
root.title("MY-Music Player")
root.geometry("920x550")
root.resizable(False, False)
root.configure(bg="white")

# Top Label (Music)
title_label = Label(root, text="My Music", font=("Times New Roman bold", 32), bg="white", fg='Black')
title_label.place(x=380, y=12)

f1 = LabelFrame(root, bd=7, relief=GROOVE, bg='white')
f1.place(x=500, y=80, height=400, width=400)

sl = Label(f1, text='Song list', font=("Times New Roman bold", 24), bg='White')
sl.place(x=130, y=10)

# Listbox for displaying the songs
song_listbox = Listbox(f1, font=("Times New Roman bold", 16), width=30, height=9, bg="White")
song_listbox.place(x=30, y=60)

# Add Song Button
add_button = Button(f1, text="Add Song", bg='DeepSkyBlue', font=("Times New Roman bold", 18), width=10, command=add_song)
add_button.place(x=33, y=310)

# Delete Song Button
delete_button = Button(f1, text="Delete Song", bg='firebrick1', font=("Times New Roman bold", 18), width=10, command=delete_song)
delete_button.place(x=210, y=310)

f2 = LabelFrame(root, bd=7, relief=GROOVE, bg='white')
f2.place(x=10, y=80, height=400, width=490)

photo10 = PhotoImage(file="listen1.png")
I1=Label(f2, image=photo10, bg='white')
I1.place(x=40, y=10)

photo11 = PhotoImage(file="musicalnotes.png")
I2=Label(f2, image=photo11, bg='white')
I2.place(x=250, y=50)


# Style for the progress bar
style = ttk.Style()
style.configure('TProgressbar', thickness=0)
# Progress bar to show song progress
progress_bar = ttk.Progressbar(f2, style='TProgressbar', orient=HORIZONTAL, length=350, mode='determinate')
progress_bar.place(x=60, y=230)

# Labels for the current time and song length
current_time_label = Label(f2, text="00:00", font=("Times New Roman bold", 13), bg="white", fg="black")
current_time_label.place(x=10, y=228)

song_length_label = Label(f2, text="00:00", font=("Times New Roman bold", 13), bg="white", fg="black")
song_length_label.place(x=415, y=228)

# Current song label
current_song_label = Label(f2, text="No Song Playing", font=("Times New Roman bold", 13), bg="white", fg='black')
current_song_label.place(x=20, y=180)

# Play/Pause Button
photo1 = PhotoImage(file="pause1.png")
photo2 = PhotoImage(file="play1.png")
play_pause_btn = Button(f2, text="Pause", font=("Times New Roman bold", 16), image=photo1, bg='white', width=50, height=50, bd=3, command=play_pause_song)
play_pause_btn.place(x=210, y=275)

# Previous Button
photo3 = PhotoImage(file="previous.png")
prev_button = Button(f2, font=("Times New Roman bold", 16), image=photo3, bg='white', width=50, height=50, bd=3, command=prev_song)
prev_button.place(x=125, y=275)

# Next Button
photo4 = PhotoImage(file="next.png")
next_button = Button(f2, font=("Times New Roman bold", 16), image=photo4, bg='white', width=50, height=50, bd=3, command=next_song)
next_button.place(x=295, y=275)

# Loop Mode Button
photo5 = PhotoImage(file="repeat1.png")
photo6 = PhotoImage(file="single.png")
photo7 = PhotoImage(file="random.png")
loop_mode_btn = Button(f2, font=("Times New Roman bold", 16), image=photo5, bg='white', width=50, height=50, bd=3, command=switch_loop_mode)
loop_mode_btn.place(x=45, y=275)

# Favorite Button
photo8 = PhotoImage(file="heart.png")
photo9 = PhotoImage(file="save.png")
favorite_button = Button(f2, font=("Times New Roman bold", 16), image=photo8, bg='white', width=50, height=50, bd=3, command=mark_favorite)
favorite_button.place(x=375, y=275)

# Load the songs from the database
load_songs_from_db()

v=Label(root,text="Develop by :- Vinay Meshram",font=("Times New Roman bold", 24),bg='white',fg='black')
v.place(x=250,y=490)

root.mainloop()

