# speech.py
# speechrecognition, pyaudio, brew install portaudio
import speech_recognition as sr
import os
import requests
import time
import io


from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


class Speech(object):

    def __init__(self, launch_phrase,launch_phrase_vn=None, debugger_enabled=False):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/baapcenter-6f642c9f1e33.json"
        self.alex = launch_phrase['en']
        self.ty = launch_phrase['male']
        self.xuka = launch_phrase['fm']
        self.be = launch_phrase['fm2']
        self.debugger_enabled = debugger_enabled
        # self.__debugger_microphone(enable=False)
        # Instantiates a client

    def google_speech_recognition(self, recognizer, audio,language='en-US'):
        speech = None
        try:
            speech = recognizer.recognize_google(audio, language = language)

            print("Google Speech Recognition thinks you said " + speech)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        return speech


    def listen_for_audio(self):
        # obtain audio from the microphone
        r = sr.Recognizer()
        m = sr.Microphone()
        with m as source:
            r.energy_threshold = 4500
            r.adjust_for_ambient_noise(source)
            r.dynamic_energy_threshold = False
            # self.__debugger_microphone(enable=True)
            print("I'm listening")
            audio = r.listen(source, phrase_time_limit=10)
        # self.__debugger_microphone(enable=False)
        # with open("microphone-results.wav", "wb") as f:
        #     f.write(audio.get_wav_data())
        print("Found audio")
        return r, audio

    def is_call_to_action(self, recognizer, audio, language=None):
        if audio is not None:
            if language is not None:
                speech = self.google_speech_recognition(recognizer, audio, language)
            else:
                speech = self.google_speech_recognition(recognizer, audio)
            if speech is not None:
                if speech.lower() in self.alex:
                    return 'alex'
                elif speech.lower() in self.be:
                    return 'be'
                elif speech.lower() in self.xuka:
                    return 'xuka'
                elif speech.lower() in self.ty:
                    return 'ty'
                else:
                    return None
        return None


    def synthesize_text(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("tmp.mp3")
        song = AudioSegment.from_mp3("tmp.mp3")
        play(song)
        os.remove("tmp.mp3")

    def __debugger_microphone(self, enable=True):
        if self.debugger_enabled:
            try:
                r = requests.get("http://localhost:8080/microphone?enabled=%s" % str(enable))
                if r.status_code != 200:
                    print("Used wrong endpoint for microphone debugging")
            except Exception as e:
                print(e)
