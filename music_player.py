import sys
import tkinter as tk
import random
from tkinter import filedialog, ttk
import pygame
import os
from PIL import Image, ImageTk, ImageDraw
import time

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("For Caitie ❤️")
        self.root.geometry("395x700")
        self.root.configure(bg='#2A2828')

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.init()
        self.check_events()

        # Current song and playlist
        self.current_song = None
        self.playlist = []
        self.paused = False
        self.stopped = True
        self.ignore_end_event = False
        self.shuffle_mode = False  # Shuffle mode flag
        self.shuffled_indices = []  # Store shuffled order
        self.current_shuffle_index = -1  # Track position in shuffled playlist

        self.progress_update_id = None
        self.song_length = 0

        # Photo display variables
        self.photos_folder = resource_path("PhotosForCaitlin")
        self.photo_files = []
        self.current_photo_index = 0
        self.photo_display = None

        # Love messages
        self.love_messages = [
            "Thinking of my super amazing hot gf 💖",
            "I miss you so so so much",
            "Hope this was worth the wait 💖",
            "Extremely happy to be with you :)",
            "Wish you were here!",
            "Hope my 10/10 gf has an amazing day today"
        ]

        # Custom fonts
        self.title_font = ("Helvetica", 18, "bold")
        self.normal_font = ("Helvetica", 12)

        # Load images
        self.default_cover = self.create_default_cover()

        # Create UI first
        self.create_ui()

        # Then load songs
        self.load_initial_songs()

    def load_initial_songs(self):
        music_folder = resource_path("SongsForCaitlin")
        if os.path.exists(music_folder):
            for file in os.listdir(music_folder):
                if file.lower().endswith('.mp3'):
                    song_path = os.path.join(music_folder, file)
                    self.playlist.append(song_path)
                    self.playlist_box.insert(tk.END, file)

    def create_default_cover(self):
        img = Image.new('RGB', (250, 250), color='#2A2828')
        draw = ImageDraw.Draw(img)
        draw.ellipse([(25, 25), (225, 225)], fill='#DEE188')
        draw.text((125, 125), "❤️", font_size=120, anchor="mm")

        try:
            if hasattr(self, 'photos_folder') and os.path.exists(self.photos_folder):
                self.load_photos()
                if self.photo_files:
                    return self.load_next_photo()
        except Exception as e:
            print(f"Error loading photos: {e}")

        return ImageTk.PhotoImage(img)

    def create_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2A2828')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.message_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 10, "italic"),
            bg='#2A2828',
            fg='#E3655B'
        )
        self.message_label.pack(pady=5)
        self.rotate_message()

        # Album art
        self.cover_label = tk.Label(main_frame, image=self.default_cover, bg='#2A2828')
        self.cover_label.pack()

        photo_btn = tk.Button(main_frame, text="Next Photo", command=self.rotate_photo,
                              bg='#2A2828', fg='#E3655B', relief=tk.FLAT)
        photo_btn.pack(pady=5)

        # Song info
        self.song_label = tk.Label(main_frame, text="None selected", font=("Helvetica", 9, "italic"),
                                   bg='#2A2828', fg='#E3655B')
        self.song_label.pack(pady=5)

        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Yellow.Horizontal.TProgressbar",
                        troughcolor='#3A3838',
                        background='#DEE188',
                        bordercolor='#3A3838',
                        lightcolor='#DEE188',
                        darkcolor='#DEE188')

        self.progress = ttk.Progressbar(main_frame,
                                        orient=tk.HORIZONTAL,
                                        length=300,
                                        mode='determinate',
                                        style="Yellow.Horizontal.TProgressbar")
        self.progress.pack(pady=10)

        # Time labels
        time_frame = tk.Frame(main_frame, bg='#2A2828')
        time_frame.pack()
        self.current_time = tk.Label(time_frame, text="00:00", bg='#D0D0D0')
        self.current_time.pack(side=tk.LEFT)
        self.total_time = tk.Label(time_frame, text="00:00", bg='#D0D0D0')
        self.total_time.pack(side=tk.RIGHT)

        # Controls frame
        controls_frame = tk.Frame(main_frame, bg='#2A2828')
        controls_frame.pack(pady=20)

        # Control buttons
        self.prev_btn = tk.Button(controls_frame, text="⏮", command=self.prev_song,
                                  font=("Helvetica", 14), bg='#2A2828', fg='#D0D0D0', relief=tk.FLAT)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(controls_frame, text="⏹", command=self.full_stop,
                                  font=("Helvetica", 14), bg='#2A2828', fg='#D0D0D0', relief=tk.FLAT)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.play_btn = tk.Button(controls_frame, text="⏵", command=self.play_song,
                                  font=("Helvetica", 14), bg='#2A2828', fg='#D0D0D0', relief=tk.FLAT)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = tk.Button(controls_frame, text="⏸", command=self.pause_song,
                                   font=("Helvetica", 14), bg='#2A2828', fg='#D0D0D0', relief=tk.FLAT)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(controls_frame, text="⏭", command=self.next_song,
                                  font=("Helvetica", 14), bg='#2A2828', fg='#D0D0D0', relief=tk.FLAT)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Shuffle button
        self.shuffle_btn = tk.Button(controls_frame, text="🔀", command=self.toggle_shuffle,
                                     font=("Segoe UI Emoji", 14), bg='#2A2828', fg='#D0D0D0', relief=tk.FLAT)
        self.shuffle_btn.pack(side=tk.LEFT, padx=5)

        # Playlist
        playlist_frame = tk.Frame(main_frame, bg='#2A2828')
        playlist_frame.pack(fill=tk.BOTH, expand=True)

        self.playlist_box = tk.Listbox(playlist_frame, selectbackground='#DEE188',
                                       selectforeground='#880e4f', bg='#D0D0D0',
                                       fg='#E3655B', font=("ds-digital", 11))
        self.playlist_box.pack(fill=tk.BOTH, expand=True)
        self.playlist_box.bind('<<ListboxSelect>>', self.select_song)

        # Personal message
        message = tk.Label(main_frame, text="❤️ ManMan",
                           font=("Helvetica", 10, "italic"), bg='#2A2828', fg='#E3655B')
        message.pack(side=tk.BOTTOM, pady=5)

    def toggle_shuffle(self):
        """Toggle shuffle mode on/off"""
        self.shuffle_mode = not self.shuffle_mode

        if self.shuffle_mode:
            # Create a new shuffled playlist
            self.shuffle_btn.config(fg='#E3655B')  # Highlight when active
            self.generate_shuffled_indices()

            # If we have a current song, play the next shuffled song
            if self.current_song and self.shuffled_indices:
                current_index = self.playlist.index(self.current_song)
                if current_index in self.shuffled_indices:
                    self.current_shuffle_index = self.shuffled_indices.index(current_index)
        else:
            self.shuffle_btn.config(fg='#D0D0D0')  # Return to normal color

    def generate_shuffled_indices(self):
        """Generate a new shuffled order of indices"""
        if not self.playlist:
            return

        # Create a list of all indices except current song
        all_indices = list(range(len(self.playlist)))
        if self.current_song in self.playlist:
            current_index = self.playlist.index(self.current_song)
            all_indices.remove(current_index)

        # Shuffle the remaining indices
        random.shuffle(all_indices)

        # Insert current song at the beginning (so it plays next if we hit next)
        if self.current_song in self.playlist:
            all_indices.insert(0, current_index)

        self.shuffled_indices = all_indices
        self.current_shuffle_index = 0  # Reset position in shuffled list

    def add_songs(self):
        songs = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3"), ("WAV Files", "*.wav")])
        for song in songs:
            self.playlist.append(song)
            self.playlist_box.insert(tk.END, os.path.basename(song))

    def select_song(self, event):
        selected = self.playlist_box.curselection()
        if selected:
            index = selected[0]
            self.current_song = self.playlist[index]
            self.song_label.config(text=os.path.basename(self.current_song))

    def play_song(self):
        if not self.current_song and self.playlist:
            # Always start with first song
            self.playlist_box.selection_set(0)
            self.current_song = self.playlist[0]
            self.song_label.config(text=os.path.basename(self.current_song))

        if self.current_song:
            if self.stopped:
                try:
                    self.ignore_end_event = False
                    pygame.mixer.music.load(self.current_song)
                    pygame.mixer.music.play()
                    self.stopped = False
                    self.paused = False
                    self.play_btn.config(text="⏵")

                    # Get song length
                    sound = pygame.mixer.Sound(self.current_song)
                    self.song_length = sound.get_length()
                    self.total_time.config(text=self.format_time(self.song_length))

                    # Set up song end detection
                    pygame.mixer.music.set_endevent(pygame.USEREVENT)

                    # Update photo display when starting playback
                    if self.photo_files:
                        photo = self.load_next_photo()
                        self.cover_label.config(image=photo)
                        self.cover_label.image = photo

                    # Start progress updates
                    self.update_progress()

                except Exception as e:
                    print(f"Error playing song: {e}")
                    self.stopped = True

            elif self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.play_btn.config(text="⏵")
                self.update_progress()

    def pause_song(self):
        if not self.paused and not self.stopped:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_btn.config(text="▶")

    def stop_song(self):
        pygame.mixer.music.stop()
        self.stopped = True
        if self.progress_update_id:
            self.root.after_cancel(self.progress_update_id)
            self.progress_update_id = None
        self.progress['value'] = 0
        self.current_time.config(text="00:00")
        if hasattr(self, 'song_length'):
            self.total_time.config(text=self.format_time(self.song_length))

    def prev_song(self):
        if not self.playlist or not self.current_song:
            return

        if self.shuffle_mode and self.shuffled_indices:
            # Handle shuffle mode navigation
            if self.current_shuffle_index > 0:
                self.current_shuffle_index -= 1
                prev_index = self.shuffled_indices[self.current_shuffle_index]
                self._play_selected_song(prev_index)
        else:
            # Normal mode navigation
            try:
                current_index = self.playlist.index(self.current_song)
                prev_index = max(0, current_index - 1)
                if prev_index != current_index:
                    self._play_selected_song(prev_index)
            except ValueError:
                pass

    def next_song(self):
        if not self.playlist or not self.current_song:
            return

        if self.shuffle_mode and self.shuffled_indices:
            # Handle shuffle mode navigation
            if self.current_shuffle_index < len(self.shuffled_indices) - 1:
                self.current_shuffle_index += 1
                next_index = self.shuffled_indices[self.current_shuffle_index]
                self._play_selected_song(next_index)
            else:
                # Reached end of shuffle playlist - generate new one
                self.generate_shuffled_indices()
                if self.shuffled_indices:
                    self.current_shuffle_index = 0
                    self._play_selected_song(self.shuffled_indices[0])
        else:
            # Normal mode navigation
            try:
                current_index = self.playlist.index(self.current_song)
                next_index = min(len(self.playlist) - 1, current_index + 1)
                if next_index != current_index:
                    self._play_selected_song(next_index)
            except ValueError:
                pass

    def full_stop(self):
        """Completely stop playback and reset player"""
        self.ignore_end_event = True
        self.stop_song()

        # Clear current selection
        self.current_song = None
        self.playlist_box.selection_clear(0, tk.END)

        # Reset display
        self.song_label.config(text="None selected")
        self.progress['value'] = 0
        self.current_time.config(text="00:00")
        self.total_time.config(text="00:00")

        # Update button states
        self.play_btn.config(text="⏵")
        self.paused = False
        self.stopped = True

    def update_progress(self):
        if self.stopped:
            return

        if not self.paused:
            try:
                current_pos = pygame.mixer.music.get_pos() / 1000

                if current_pos < 0:
                    current_pos = self.progress['value'] * self.song_length / 100

                if current_pos >= 0 and self.song_length > 0:
                    progress_percent = (current_pos / self.song_length) * 100
                    self.progress['value'] = progress_percent

                    self.current_time.config(text=self.format_time(current_pos))
                    self.total_time.config(text=self.format_time(self.song_length))

            except Exception as e:
                print(f"Progress update error: {e}")

        self.progress_update_id = self.root.after(50, self.update_progress)

    def format_time(self, seconds):
        if seconds < 0:
            return "00:00"
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def load_photos(self):
        try:
            if os.path.exists(self.photos_folder):
                self.photo_files = [
                    os.path.join(self.photos_folder, f)
                    for f in os.listdir(self.photos_folder)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]
                self.current_photo_index = 0
        except Exception as e:
            print(f"Error loading photos: {e}")
            self.photo_files = []

    def load_next_photo(self):
        if not self.photo_files:
            return self.create_default_cover()

        try:
            img = Image.open(self.photo_files[self.current_photo_index])

            if img.width != img.height:
                size = min(img.width, img.height)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                right = (img.width + size) // 2
                bottom = (img.height + size) // 2
                img = img.crop((left, top, right, bottom))

            img = img.resize((250, 250), Image.LANCZOS)

            mask = Image.new('L', (250, 250), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (250, 250)], fill=255)

            result = Image.new('RGB', (250, 250), '#2A2828')
            result.paste(img, (0, 0), mask)

            self.photo_display = ImageTk.PhotoImage(result)

            self.current_photo_index = (self.current_photo_index + 1) % len(self.photo_files)

            return self.photo_display

        except Exception as e:
            print(f"Error loading photo: {e}")
            return self.create_default_cover()

    def rotate_photo(self):
        if self.photo_files:
            photo = self.load_next_photo()
            self.cover_label.config(image=photo)
            self.cover_label.image = photo

    def rotate_message(self):
        msg = random.choice(self.love_messages)
        self.message_label.config(text=msg)
        self.root.after(10000, self.rotate_message)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT and not self.ignore_end_event:
                if not self.stopped and self.current_song:
                    if self.shuffle_mode and self.shuffled_indices:
                        # Shuffle mode handling
                        if self.current_shuffle_index < len(self.shuffled_indices) - 1:
                            self.current_shuffle_index += 1
                            next_index = self.shuffled_indices[self.current_shuffle_index]
                            self._play_selected_song(next_index)
                        else:
                            # Generate new shuffle order when reaching end
                            self.generate_shuffled_indices()
                            if self.shuffled_indices:
                                self.current_shuffle_index = 0
                                self._play_selected_song(self.shuffled_indices[0])
                    else:
                        # Normal mode handling
                        try:
                            current_index = self.playlist.index(self.current_song)
                            if current_index < len(self.playlist) - 1:
                                self._play_selected_song(current_index + 1)
                            else:
                                self.stop_song()
                        except ValueError:
                            pass

        self.root.after(100, self.check_events)

    def _play_selected_song(self, index):
        """Core method to play a specific song index"""
        if index < 0 or index >= len(self.playlist):
            return

        # Set flag to ignore the upcoming end event
        self.ignore_end_event = True

        try:
            # Update current song reference
            self.current_song = self.playlist[index]

            # Update UI selection
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(index)
            self.playlist_box.see(index)
            self.song_label.config(text=os.path.basename(self.current_song))

            # Stop any current playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            # Load and play new song
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()
            self.stopped = False
            self.paused = False

            # Update song info
            sound = pygame.mixer.Sound(self.current_song)
            self.song_length = sound.get_length()
            self.total_time.config(text=self.format_time(self.song_length))

            # Update photo display when song changes
            if self.photo_files:
                photo = self.load_next_photo()
                self.cover_label.config(image=photo)
                self.cover_label.image = photo

            # Start progress updates
            self.update_progress()

        except Exception as e:
            print(f"Error playing song: {e}")
        finally:
            # Reset the ignore flag after a short delay
            self.root.after(100, lambda: setattr(self, 'ignore_end_event', False))

    def generate_shuffled_indices(self):
        """Generate a new shuffled order of indices"""
        if not self.playlist:
            return

        # Create a list of all indices
        all_indices = list(range(len(self.playlist)))

        # If we have a current song, make sure it's first in the new shuffle order
        if self.current_song in self.playlist:
            current_index = self.playlist.index(self.current_song)
            all_indices.remove(current_index)
            random.shuffle(all_indices)
            all_indices.insert(0, current_index)
        else:
            random.shuffle(all_indices)

        self.shuffled_indices = all_indices
        self.current_shuffle_index = 0



if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    try:
        root.mainloop()
    finally:
        pygame.quit()