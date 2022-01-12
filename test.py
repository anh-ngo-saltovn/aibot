from clock import Clock
from pydub import AudioSegment
from pydub.playback import play
import time

with Clock(seconds = 30):
    alarm_file = "/home/pi/AI-Smart-Mirror/sample-audio-files/martian-gun.mp3"
    song = AudioSegment.from_mp3(alarm_file)
    while True:
        play(song)
        time.sleep(2)

print("Hello Test")
