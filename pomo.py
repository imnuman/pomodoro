import time
import requests
import random
from datetime import datetime, timedelta

# Define the durations in seconds
WORK_TIME = 25 * 60  # 25 minutes
SHORT_BREAK = 5 * 60  # 5 minutes
SESSIONS = 4

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

# Countdown for a session
def countdown(duration, session_type, session_number):
    quote = get_random_quote()
    print("\n" + "=" * 60)
    print(f"Session {session_number} - {session_type}")
    print(f"Quote: {quote}")
    print("=" * 60)
    while duration:
        mins, secs = divmod(duration, 60)
        print(f"{mins:02d}:{secs:02d}", end='\r')
        time.sleep(1)
        duration -= 1
    print("\nSession complete!\n")

# Main Pomodoro function
def pomodoro():
    for session in range(1, SESSIONS + 1):
        # Work session
        countdown(WORK_TIME, "Work", session)
        if session < SESSIONS:
            # Short break
            countdown(SHORT_BREAK, "Break", session)

if __name__ == "__main__":
    pomodoro()
