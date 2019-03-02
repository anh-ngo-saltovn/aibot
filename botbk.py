# bot.py

# speechrecognition, pyaudio, brew install portaudio
import sys
sys.path.append("./")

import requests
import datetime
import dateutil.parser
import json
import RPi.GPIO as GPIO
import time
import psutil
import os
import traceback
from nlg import NLG
from speech import Speech
from knowledge import Knowledge
from vision import Vision
from actions import YouTube_No_Autoplay
from actions import YouTube_Autoplay
from actions import stop
from actions import say
from light import Light
import subprocess

my_name = "Jacky"
launch_phrase = ["okay alex",'hey alex', 'okay son', 'hey son']
use_launch_phrase = True
weather_api_token = "45f4e10502cba6d815e2b8fa3b4c9cc7"
wit_ai_token = "Bearer DQCSMAVIZ6ICNULDJNA242I76VS6FC2B"
debugger_enabled = True
camera = 0
language = 'en'
LEDPIN = 17

class Bot(object):
    def __init__(self):
        self.nlg = NLG(user_name=my_name)
        self.speech = Speech(launch_phrase=launch_phrase, debugger_enabled=debugger_enabled)
        self.knowledge = Knowledge(weather_api_token)
        self.vision = Vision(camera=camera)

    def start(self):
        """
        Main loop. Waits for the launch phrase, then decides an action.
        :return:
        """
        # subprocess.Popen(["aplay", "/home/pi/AI-Smart-Mirror/sample-audio-files/Startup.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # time.sleep(1)
        self.__setup()
        while True:
            requests.get("http://localhost:8080/clear")
            if self.vision.recognize_face():
            # if True:
                print('Found face')
                if use_launch_phrase:
                    recognizer, audio = self.speech.listen_for_audio()
                    if self.speech.is_call_to_action(recognizer, audio):
                        GPIO.output(LEDPIN,GPIO.HIGH)

                        # set volumn_down 10
                        if self.__ismpvplaying(): #check mpv have play or not
                            if os.path.isfile("/home/pi/.mediavolume.json"):
                                mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume","10"]})+"' | socat - /tmp/mpvsocket")
                            else:
                                mpvgetvol=subprocess.Popen([("echo '"+json.dumps({ "command": ["get_property", "volume"]})+"' | socat - /tmp/mpvsocket")],shell=True, stdout=subprocess.PIPE)
                                output=mpvgetvol.communicate()[0]
                                for currntvol in re.findall(r"[-+]?\d*\.\d+|\d+", str(output)):
                                    with open('/home/pi/.mediavolume.json', 'w') as vol:
                                        json.dump(currntvol, vol)
                                mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume","10"]})+"' | socat - /tmp/mpvsocket")


                        self.__acknowledge_action()
                        self.decide_action()
                        GPIO.output(LEDPIN,GPIO.LOW)

                        #set back volume
                        if self.__ismpvplaying(): #check mpv have play or not
                            if os.path.isfile("/home/pi/.mediavolume.json"):
                                with open('/home/pi/.mediavolume.json', 'r') as vol:
                                    oldvollevel = json.load(vol)
                                print(oldvollevel)
                                mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(oldvollevel)]})+"' | socat - /tmp/mpvsocket")

                else:
                    self.decide_action()

    def __setup(self):
        GPIO.setwarnings(False)
        #set the gpio modes to BCM numbering
        GPIO.setmode(GPIO.BCM)
        #set LEDPIN's mode to output,and initial level to LOW(0V)
        GPIO.setup(LEDPIN,GPIO.OUT,initial=GPIO.LOW)

    def decide_action(self):
        """
        Recursively decides an action based on the intent.
        :return:
        """
        recognizer, audio = self.speech.listen_for_audio()

        # received audio data, now we'll recognize it using Google Speech Recognition
        speech = self.speech.google_speech_recognition(recognizer, audio)

        if speech is not None:
            try:
                r = requests.get('https://api.wit.ai/message?v=20180428&q=%s' % speech,
                                 headers={"Authorization": wit_ai_token})
                print(r.text)
                json_resp = json.loads(r.text)
                entities = None
                intent = None
                if 'entities' in json_resp and 'Intent' in json_resp['entities']:
                    entities = json_resp['entities']
                    intent = json_resp['entities']['Intent'][0]["value"]
                if intent == 'greeting':
                    self.__text_action(self.nlg.greet())
                elif intent == 'snow white':
                    self.__text_action(self.nlg.snow_white())
                elif intent == 'weather':
                    self.__weather_action(entities)
                elif intent == 'news':
                    self.__news_action()
                elif intent == 'maps':
                    self.__maps_action(entities)
                elif intent == 'holidays':
                    self.__holidays_action()
                elif intent == 'appearance':
                    self.__appearance_action()
                elif intent == 'user status':
                    self.__user_status_action(entities)
                elif intent == 'user name':
                    self.__user_name_action()
                elif intent == 'personal status':
                    self.__personal_status_action()
                elif intent == 'joke':
                    self.__joke_action()
                elif intent == 'insult':
                    self.__insult_action()
                    return
                elif intent == 'appreciation':
                    self.__appreciation_action()
                    return
                elif intent == 'music':
                    self.__playmusic(entities)
                    return
                elif intent == 'light':
                    self.__light_action(entities);
                    return
                else: # No recognized intent
                    self.__text_action("I'm sorry, I don't know about that yet.")
                    return

            except Exception as e:
                print("Failed wit!")
                print(e)
                traceback.print_exc()
                self.__text_action("I'm sorry, I couldn't understand what you meant by that")
                return

            self.decide_action()

    def __light_action(self, nlu_entities=None):
        action = None
        position = None
        light = Light(23)
        if nlu_entities is not None:
            if 'action' in nlu_entities:
                action = nlu_entities['action'][0]['value']
            if 'position' in nlu_entities:
                position = nlu_entities['position'][0]['value']
            if action == 'on':
                light.turn_on()
            elif action == 'off':
                light.turn_off()
                self.__text_action("Ok")
            else:
                self.__text_action("I'm sorry, I couldn't understand what you meant by that")

    def __joke_action(self):
        joke = self.nlg.joke()

        if joke is not None:
            self.__text_action(joke)
        else:
            self.__text_action("I couldn't find any jokes")

    def __user_status_action(self, nlu_entities=None):
        attribute = None

        if (nlu_entities is not None) and ("Status_Type" in nlu_entities):
            attribute = nlu_entities['Status_Type'][0]['value']

        self.__text_action(self.nlg.user_status(attribute=attribute))

    def __user_name_action(self):
        if self.nlg.user_name is None:
            self.__text_action("I don't know your name. You can configure it in bot.py")

        self.__text_action(self.nlg.user_name)

    def __appearance_action(self):
        requests.get("http://localhost:8080/face")

    def __appreciation_action(self):
        self.__text_action(self.nlg.appreciation())

    def __acknowledge_action(self):
        self.__text_action(self.nlg.acknowledge())

    def __insult_action(self):
        self.__text_action(self.nlg.insult())

    def __personal_status_action(self):
        self.__text_action(self.nlg.personal_status())

    def __text_action(self, text=None):
        if text is not None:
            requests.get("http://localhost:8080/statement?text=%s" % text)
            # self.speech.synthesize_text(text)
            say(text,language)

    def __news_action(self):
        headlines = self.knowledge.get_news()

        if headlines:
            requests.post("http://localhost:8080/news", data=json.dumps({"articles":headlines}))
            self.speech.synthesize_text(self.nlg.news("past"))
            interest = self.nlg.article_interest(headlines)
            if interest is not None:
                self.speech.synthesize_text(interest)
        else:
            self.__text_action("I had some trouble finding news for you")

    def __weather_action(self, nlu_entities=None):

        current_dtime = datetime.datetime.now()
        skip_weather = False # used if we decide that current weather is not important

        weather_obj = self.knowledge.find_weather()
        temperature = weather_obj['temperature']
        icon = weather_obj['icon']
        wind_speed = weather_obj['windSpeed']

        weather_speech = self.nlg.weather(temperature, current_dtime, "present")
        forecast_speech = None

        if nlu_entities is not None:
            if 'datetime' in nlu_entities:
                if 'grain' in nlu_entities['datetime'][0] and nlu_entities['datetime'][0]['grain'] == 'day':
                    dtime_str = nlu_entities['datetime'][0]['value'] # 2016-09-26T00:00:00.000-07:00
                    dtime = dateutil.parser.parse(dtime_str)
                    if current_dtime.date() == dtime.date(): # hourly weather
                        forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['daily_forecast']}
                        forecast_speech = self.nlg.forecast(forecast_obj)
                    elif current_dtime.date() < dtime.date(): # sometime in the future ... get the weekly forecast/ handle specific days
                        forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['weekly_forecast']}
                        forecast_speech = self.nlg.forecast(forecast_obj)
                        skip_weather = True
            if 'Weather_Type' in nlu_entities:
                weather_type = nlu_entities['Weather_Type'][0]['value']
                print(weather_type)
                if weather_type == "current":
                    forecast_obj = {'forecast_type': 'current', 'forecast': weather_obj['current_forecast']}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                elif weather_type == 'today':
                    forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['daily_forecast']}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                elif weather_type == 'tomorrow' or weather_type == '3 day' or weather_type == '7 day':
                    forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['weekly_forecast']}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                    skip_weather = True


        weather_data = {"temperature": temperature, "icon": icon, 'windSpeed': wind_speed, "hour": datetime.datetime.now().hour}
        requests.post("http://localhost:8080/weather", data=json.dumps(weather_data))

        if not skip_weather:
            # self.speech.synthesize_text(weather_speech)
            say(weather_speech)

        if forecast_speech is not None:
            # self.speech.synthesize_text(forecast_speech)
            say(forecast_speech)

    def __maps_action(self, nlu_entities=None):

        location = None
        map_type = None
        origin = None
        destination = None
        if nlu_entities is not None:
            if 'location' in nlu_entities:
                location = nlu_entities['location'][0]["value"]
            if "Map_Type" in nlu_entities:
                map_type = nlu_entities['Map_Type'][0]["value"]
            if 'origin' in nlu_entities:
                origin = nlu_entities['origin'][0]["value"]
            if 'destination' in nlu_entities:
                destination = nlu_entities['destination'][0]["value"]

        if origin is not None:
            if destination is not None:
                print(origin, destination)

        if location is not None:
            maps_url = self.knowledge.get_map_url(location, map_type)
            maps_action = "Sure. Here's a map of %s." % location
            body = {'url': maps_url}
            requests.post("http://localhost:8080/image", data=json.dumps(body))
            self.speech.synthesize_text(maps_action)
        else:
            self.__text_action("I'm sorry, I couldn't understand what location you wanted.")

    def __playmusic(self, nlu_entities=None):
        chanel = None
        action = None
        region_code = 'VN'
        location = None
        local_search_query = None

        if nlu_entities is not None:
            if 'chanel' in nlu_entities:
                chanel = nlu_entities['chanel'][0]['value']
            if 'action' in nlu_entities:
                action = nlu_entities['action'][0]['value']
            if 'local_search_query' in nlu_entities:
                local_search_query = nlu_entities['local_search_query'][0]['value']
            if 'location' in nlu_entities:
                location = nlu_entities['location'][0]['value']
                region_code = self.knowledge.get_country_code(location)
            if chanel is not None:
                if 'youtube' == chanel:
                    if 'play' == action:
                        stop()
                        if local_search_query is not None:
                            YouTube_Autoplay(local_search_query, region_code)
                        else:
                            YouTube_Autoplay('Le quyen', region_code)
                    elif 'stop' == action:
                        stop()
                        self.__text_action("OK, stoped it")
                    else:
                        self.__text_action("what are you want to do %s" % my_name)

    def __holidays_action(self):
        holidays = self.knowledge.get_holidays()
        next_holiday = self.__find_next_holiday(holidays)
        requests.post("http://localhost:8080/holidays", json.dumps({"holiday": next_holiday}))
        self.speech.synthesize_text(self.nlg.holiday(next_holiday['localName']))

    def __find_next_holiday(self, holidays):
        today = datetime.datetime.now()
        for holiday in holidays:
            date = holiday['date']
            if (date['day'] > today.day) and (date['month'] > today.month):
                return holiday

        # next year
        return holidays[0]

    #Function to check if mpv is playing
    def __ismpvplaying(self):
        for pid in psutil.pids():
            p=psutil.Process(pid)
            if 'mpv'in p.name():
                mpvactive=True
                break
            else:
                mpvactive=False
        return mpvactive
if __name__ == "__main__":
    bot = Bot()
    bot.start()
