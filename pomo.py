import time
import pyttsx3
import tkinter as tk
from tkinter import ttk
import requests
import random
from datetime import datetime, timedelta

# Define the durations in seconds
WORK_TIME = 25 * 60  # 25 minutes
SHORT_BREAK = 5 * 60  # 5 minutes
LONG_BREAK = 30 * 60  # 30 minutes
SESSIONS = 4
LOG_FILE_PATH = "/home/tomc/script/pomolog.txt"  # Log file path

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize Tkinter for visual output
root = tk.Tk()
root.title("Pomodoro Timer")
root.attributes('-fullscreen', True)  # Full screen
root.configure(bg='black')

# Set up the grid layout
root.grid_rowconfigure(0, weight=1, minsize=30)  # Add a line space
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Set labels for displaying the session, timer, and quotes
season_label = tk.Label(root, text="", font=("Terminal", 30), fg="white", bg="black")
season_label.grid(row=1, column=0, columnspan=2, pady=10)

timer_label = tk.Label(root, text="", font=("Terminal", 50, "bold"), fg="white", bg="black")
timer_label.grid(row=2, column=0, columnspan=2, pady=10)

quote_label = tk.Label(root, text="", font=("Terminal", 40, "bold"), fg="white", bg="black", wraplength=1000, justify='center')
quote_label.grid(row=3, column=0, columnspan=2, pady=20)

# Progress bars setup
progress_bars = []
percent_labels = []

# Keep track of the current date for logging purposes
current_log_date = None

# Create progress bars function
def create_progress_bars():
    for i in range(SESSIONS):
        progress = ttk.Progressbar(root, length=400, mode='determinate', maximum=100, style="red.Horizontal.TProgressbar")
        if i < 2:  # First two side by side
            progress.grid(row=4, column=i, padx=20, pady=20)
        else:  # Next two up and down
            progress.grid(row=5, column=i - 2, padx=20, pady=20)
        progress_bars.append(progress)

        percent_label = tk.Label(root, text="0%", font=("Helvetica", 20), fg="white", bg="black")
        if i < 2:
            percent_label.grid(row=4, column=i, padx=20, pady=80)
        else:
            percent_label.grid(row=5, column=i - 2, padx=20, pady=80)
        percent_labels.append(percent_label)

# Update the progress bar and percentage function
def update_progress_bars(progress, session):
    progress_bars[session - 1]['value'] = progress
    percent_labels[session - 1].config(text=f"{int(progress)}%")

# Rotating pipe visual effect
pipe_symbols = ['|', '/', '-', '\\']
pipe_index = 0

# Exit the program on pressing the "Escape" key
root.bind("<Escape>", lambda e: root.destroy())

# Text-to-speech function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initial log entry
def log_start():
    global current_log_date
    current_time = datetime.now()
    current_log_date = current_time.strftime('%Y-%m-%d')
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write("##############################\n")
        log_file.write(f"Date: {current_time.strftime('%A, %B %d, %Y %H:%M:%S')}\n")

# Log the session start and end times
def log_session(work_start_time, work_end_time, session):
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"Session {session} Work Time: {work_start_time.strftime('%H:%M')} - {work_end_time.strftime('%H:%M')}\n")
        log_file.write("Break Time: 5 minutes\n")

# Log total time
def log_total_time(total_work_time, total_break_time):
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"Total Time of 4 Sessions and Breaks: {str(total_work_time + total_break_time)}\n")

# Update timer text and progress bar
def update_timer(text, progress=None, session=None):
    global pipe_index
    pipe_symbol = pipe_symbols[pipe_index % len(pipe_symbols)]  # Rotate pipe symbol
    pipe_index += 1
    timer_label.config(text=text.replace('|', pipe_symbol))
    if session is not None and progress is not None:
        update_progress_bars(progress, session)
    root.update()

# Fetch a random quote
def get_random_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        data = response.json()
        quote = data[0]['q'] + " - " + data[0]['a']
        return quote
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return random.choice([
            "Man needs difficulties; they are necessary for health. - Carl Jung",
            "No tree can grow to heaven unless its roots reach down to hell. - Carl Jung",
            "The creation of something new is not accomplished by the intellect but by the play instinct. - Carl Jung"
        ])

# Update the quote on the screen
def update_quote():
    random_quote = get_random_quote()
    quote_label.config(text=random_quote)

# Handle the countdown for each session
def countdown(duration, session_type, session_number):
    work_start_time = datetime.now()
    total_time = duration
    update_quote()
    while duration:
        mins, secs = divmod(duration, 60)
        current_time = datetime.now()
        day_and_date = current_time.strftime("%A, %B %d")
        season_info = f"{day_and_date} | Session {session_number} of {SESSIONS}"
        season_label.config(text=season_info)  # Update day and session info
        work_time_left = f"{mins:02d}:{secs:02d}"
        timer = f"EST = {current_time.strftime('%H:%M:%S')} | Work = {work_time_left}"  # Display time with seconds
        progress = 100 * (1 - duration / total_time)
        update_timer(timer, progress, session_number)
        if duration % (3 * 60) == 0:  # Update the quote every 3 minutes
            update_quote()
        time.sleep(1)
        duration -= 1
    work_end_time = datetime.now()
    log_session(work_start_time, work_end_time, session=session_number)

# Main Pomodoro function
def pomodoro():
    create_progress_bars()
    total_work_time = timedelta()
    total_break_time = timedelta(minutes=(SESSIONS - 1) * 5)
    log_start()
    for session in range(1, SESSIONS + 1):
        # Work session
        speak(f"Session {session}: Time to work!")
        season_label.config(text=f"Session {session} of {SESSIONS}")
        update_timer(f"Session {session}\nTime to Work!")
        countdown(WORK_TIME, "Work", session)
        total_work_time += timedelta(minutes=25)
        if session < SESSIONS:
            # Short break
            speak("Time for a short break!")
            season_label.config(text=f"Session {session} of {SESSIONS}: Break")
            update_timer("Time for a Short Break!")
            countdown(SHORT_BREAK, "Break", session)
    log_total_time(total_work_time, total_break_time)

if __name__ == "__main__":
    # Style for red progress bar
    style = ttk.Style()
    style.configure("red.Horizontal.TProgressbar", troughcolor='black', background='red')
    root.after(1000, pomodoro)  # Start Pomodoro after a short delay
    root.mainloop()
