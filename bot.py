# -*- coding: utf-8 -*-
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
import calendar
import psutil
import os
import traceback
from nlg import NLG
from speech0 import Speech
from knowledge import Knowledge
#from vision import Vision
from actions import YouTube_No_Autoplay
from actions import YouTube_Autoplay
from actions import stop
from actions import say
from light import Light
from wit import Wit
from clock import Clock
import subprocess
import math
import _thread
from pydub import AudioSegment
from pydub.playback import play


my_name = "Jacky"
my_name_vn = "sếp"
launch_phrase = {'en': ["okay alex", 'hey alex', 'okay man', 'hey man'],
                 'male': ["đô rê môn", "ê cu", 'ê bắp', 'này bắp', 'bắp ơi', 'tí ơi', 'tèo ơi', 'ê tý', 'ê tèo',
                          'bợm ơi', 'tủn ơi', 'đết pun', 'đết bun', 'deadpool'],
                 'fm': ["bé ơi", "Heo ơi"],
                 'fm2': ["xuca", "xuka"]}
my_address = 'chofu'
use_launch_phrase = True
weather_api_token = "45f4e10502cba6d815e2b8fa3b4c9cc7"

wit_ai_token = "DQCSMAVIZ6ICNULDJNA242I76VS6FC2B"
wit_ai_token_vn = "7Q4BDMDVXZ5GRWVFECTRQEW3EKOC4MCK"
google_cloud_api_key = 'AIzaSyD2-3Jk54Q12YdLT5sZcYOMYO-huaQYopg'
debugger_enabled = True
camera = 0
LEDPIN = 17


class Bot(object):
    def __init__(self):
        self.nlg = NLG(user_name=my_name)
        self.nlg_vn = NLG(user_name=my_name_vn, language='vi')
        self.speech = Speech(launch_phrase=launch_phrase, debugger_enabled=debugger_enabled)
        self.wit_client_vn = Wit(wit_ai_token_vn)
        self.wit_client_en = Wit(wit_ai_token)
        self.knowledge = Knowledge(weather_api_token, google_cloud_api_key=google_cloud_api_key)
        #self.vision = Vision(camera=camera)
        self.bot_vn = 'ty';

        subprocess.Popen(["aplay", "/home/pi/AI-Smart-Mirror/sample-audio-files/Startup.wav"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(4)

    def __setup(self):
        GPIO.setwarnings(False)
        # set the gpio modes to BCM numbering
        GPIO.setmode(GPIO.BCM)
        # set LEDPIN's mode to output,and initial level to LOW(0V)
        GPIO.setup(LEDPIN, GPIO.OUT, initial=GPIO.LOW)

    def start(self):
        """
        Main loop. Waits for the launch phrase, then decides an action.
        :return:
        """

        self.__setup()
        while True:
            # requests.get("http://localhost:8080/clear")
            if True:
                # if True:
                print('Found face')

                if use_launch_phrase:
                    recognizer, audio = self.speech.listen_for_audio()  # save file audio
                    vn_bot = self.speech.is_call_to_action(recognizer, audio, language='vi')
                    self.bot_vn = vn_bot
                    en_bot = None
                    if not (vn_bot in ['ty', 'be', 'xuka']):
                        # vn_bot = self.speech_vn.is_call_to_action(recognizer, audio, language='vi')
                        en_bot = self.speech.is_call_to_action(recognizer, audio)  # check vn or en bot

                    if en_bot is not None or vn_bot is not None:
                        GPIO.output(LEDPIN, GPIO.HIGH)  # light on

                        # set volumn_down 10
                        if self.__ismpvplaying():  # check mpv have play or not
                            if os.path.isfile("/home/pi/.mediavolume.json"):
                                mpvsetvol = os.system("echo '" + json.dumps(
                                    {"command": ["set_property", "volume", "10"]}) + "' | socat - /tmp/mpvsocket")
                            else:
                                mpvgetvol = subprocess.Popen([("echo '" + json.dumps(
                                    {"command": ["get_property", "volume"]}) + "' | socat - /tmp/mpvsocket")],
                                                             shell=True, stdout=subprocess.PIPE)
                                output = mpvgetvol.communicate()[0]
                                for currntvol in re.findall(r"[-+]?\d*\.\d+|\d+", str(output)):
                                    with open('/home/pi/.mediavolume.json', 'w') as vol:
                                        json.dump(currntvol, vol)
                                mpvsetvol = os.system("echo '" + json.dumps(
                                    {"command": ["set_property", "volume", "10"]}) + "' | socat - /tmp/mpvsocket")

                        if vn_bot in ['ty', 'be', 'xuka']:
                            self.__acknowledge_action(langague='vi')  #
                            self.decide_action(langague='vi')
                        else:
                            self.__acknowledge_action()  #
                            self.decide_action()

                        GPIO.output(LEDPIN, GPIO.LOW)

                        # set back volume
                        if self.__ismpvplaying():  # check mpv have play or not
                            if os.path.isfile("/home/pi/.mediavolume.json"):
                                with open('/home/pi/.mediavolume.json', 'r') as vol:
                                    oldvollevel = json.load(vol)
                                print(oldvollevel)
                                mpvsetvol = os.system("echo '" + json.dumps({"command": ["set_property", "volume", str(
                                    oldvollevel)]}) + "' | socat - /tmp/mpvsocket")

                else:
                    self.decide_action(langague='vi')
        # Wait for all threads to complete

    def decide_action(self, langague=None, oldintent=None, pre_message=None):
        """
        Recursively decides an action based on the intent.
        :return:
        """
        speech_en = None
        speech_vn = None

        # received audio data, now we'll recognize it using Google Speech Recognition
        if langague is not None:
            while speech_vn is None:
                recognizer, audio = self.speech.listen_for_audio()
                speech_vn = self.speech.google_speech_recognition(recognizer, audio, langague)
                if oldintent is not None:
                    speech_vn = '%s %s' % (oldintent, speech_vn)
        else:
            while speech_en is None:
                recognizer, audio = self.speech.listen_for_audio()
                speech_en = self.speech.google_speech_recognition(recognizer, audio)

        # Run EN Bot
        if speech_en is not None:
            try:
                # r = requests.get('https://api.wit.ai/message?v=20180428&q=%s' % speech_en,
                #                  headers={"Authorization": wit_ai_token})
                response = self.wit_client_en.message(speech_en)
                entities = None
                intent = None

                if response is not None:
                    entities = response['entities']
                    intent = entities['intent'][0]["value"]

                if intent == 'greeting':
                    self.__text_action(self.nlg.greet())
                elif intent == 'snow white':
                    self.__text_action(self.nlg.snow_white())
                elif intent == 'weather':
                    self.__weather_action(entities)
                elif intent == 'news':
                    self.__text_action('News function is not yet implemted')
                elif intent == 'maps':
                    self.__maps_action(entities)
                elif intent == 'holidays':
                    self.__holidays_action()
                # elif intent == 'appearance':
                #     self.__appearance_action()
                elif intent == 'user status':
                    self.__user_status_action(entities)
                elif intent == 'user name':
                    self.__user_name_action()
                elif intent == 'personal status':
                    self.__personal_status_action()
                elif intent == 'joke':
                    self.__joke_action()
                elif intent == 'appreciation':
                    self.__appreciation_action()
                    return
                elif intent == 'music':
                    self.__playmusic(entities)
                    return
                elif intent == 'light':
                    self.__light_action(entities);
                    return
                else:  # No recognized intent
                    self.__text_action("I'm sorry, I don't know about that yet.")
                    return

            except Exception as e:
                print("Failed wit!")
                print(e)
                traceback.print_exc()
                self.__text_action("I'm sorry, I couldn't understand what you meant by that")
                return
            self.decide_action()
        else:
            # Run VN Bot
            if speech_vn is not None:

                try:
                    # r = requests.get('https://api.wit.ai/message?v=20180428&q=%s' % speech_vn,
                    #                  headers={"Authorization": wit_ai_token_vn})
                    # resp = json.loads(r.text)
                    response = self.wit_client_vn.message(speech_vn)
                    entities = None
                    intent = None
                    print(response)
                    if response is not None:
                        entities = response['entities']
                        if 'intent' in entities:
                            intent = entities['intent'][0]["value"]

                    print(intent)

                    if intent == 'lời chào':
                        self.__text_action(self.nlg_vn.greet())
                    elif intent == 'thời tiết':
                        self.__weather_action_vn(entities)
                    elif intent == 'tin tức':
                        self.__news_action(entities, langague, oldintent)
                        if pre_message is not None:
                            if speech_vn is not None and 'dịch' in speech_vn:
                                self.__text_action(pre_message)
                                return
                        if oldintent is not None:
                            self.__text_action('Kết thúc đọc tin tức')
                            return
                    elif intent == 'bản đồ':
                        self.__maps_action(entities)
                    elif intent == 'ngày nghỉ':
                        self.__holidays_action(entities)
                    elif intent == 'điều khiển':
                        self.__device_action(entities)
                    # elif intent == 'self':
                    #     self.__appearance_action()
                    elif intent == 'alarm':
                        self.__alarm(entities)
                        return
                    elif intent == 'user status':
                        self.__user_status_action(entities)
                    elif intent == 'user name':
                        self.__user_name_action()
                    elif intent == 'personal status':
                        self.__personal_status_action()
                    elif intent == 'joke':
                        self.__joke_action()
                    elif intent == 'đánh giá':
                        self.__appreciation_action()
                        return
                    elif intent == 'nhạc':
                        self.__playmusic(entities)
                        return
                    elif intent == 'light':
                        self.__light_action(entities);
                        return
                    elif intent == 'current time':
                        ti = datetime.datetime.now().time()
                        self.__text_action(ti)
                    else:  # No recognized intent
                        self.__text_action(self.nlg_vn.unknown())
                        # return

                except Exception as e:
                    print("Failed wit!")
                    print(e)
                    traceback.print_exc()
                    self.__text_action("Code thối lỗi banh xác rồi, fix đêêêêê")
                    return

                self.decide_action(langague='vi')

    def __device_action(self, nlu_entities=None):
        action = None
        position = None
        device = None
        mode = None

        if nlu_entities is not None:
            if 'action' in nlu_entities:
                action = nlu_entities['action'][0]['value'].lower().encode()
            if 'position' in nlu_entities:
                position = nlu_entities['position'][0]['value'].lower().encode()
            if 'device' in nlu_entities:
                device = nlu_entities['device'][0]['value'].lower().encode()
            if 'mode' in nlu_entities:
                mode = nlu_entities['mode'][0]['value'].lower().encode()

            if device is not None and action is not None:
                if device == 'loa'.encode():
                    if action == 'bật'.encode() or action == 'tắt'.encode():
                        os.system('irsend SEND_ONCE speaker KEY_POWER')
                    elif action == 'tăng'.encode() or action == 'lớn'.encode():
                        os.system('irsend SEND_ONCE speaker KEY_VOLUMEUP')
                    elif action == 'giảm'.encode() or action == 'nhỏ'.encode():
                        os.system('irsend SEND_ONCE speaker KEY_VOLUMEDOWN')
                    elif action == 'ánh sáng'.encode():
                        os.system('irsend SEND_ONCE speaker KEY_LIGHTS_TOGGLE')

                elif device == 'điều hòa'.encode():
                    print('%s, %s, %s' % (device, mode, action))
                    if action == 'bật'.encode() or action == 'chuyển'.encode():
                        if mode is not None and mode == 'lạnh'.encode():
                            os.system('irsend SEND_ONCE air COLD')  # lanh
                            self.__text_action('đã bật điều hoà, chế độ lạnh')
                        elif mode is not None and mode == 'nóng'.encode():
                            os.system('irsend SEND_ONCE air HOT')  # nong
                            self.__text_action('đã bật điều hoà, chế độ nóng')
                    elif action == 'tắt'.encode():
                        os.system('irsend SEND_ONCE air OFF')  # tắt
                        self.__text_action('đã tắt điều hoà')
                    elif action == 'giảm'.encode():
                        os.system('irsend SEND_ONCE air DOWN')  # DOWN
                        self.__text_action('đã giảm điều hoà')
                    elif action == 'tăng'.encode():
                        os.system('irsend SEND_ONCE air UP')  # UP
                        self.__text_action('đã tăng điều hoà')

                elif device == 'quạt'.encode():
                    if action == 'bật'.encode() or action == 'chuyển'.encode():
                        if mode is not None and mode == 'lạnh'.encode():
                            os.system('irsend SEND_ONCE fan KEY_POWER  KEY_BLUE KEY_BLUE')  # lanh
                            self.__text_action('đã bật quạt chế độ lạnh')
                        elif mode is not None and mode == 'nóng':
                            os.system('irsend SEND_ONCE fan KEY_POWER  KEY_0 KEY_0')  # nong
                            self.__text_action('đã bật quạt chế độ nóng')
                        else:
                            os.system('irsend SEND_ONCE fan KEY_POWER  KEY_BLUE KEY_BLUE')  # lanh
                            self.__text_action('đã bật quạt chế độ nóng')
                    elif action == 'tắt'.encode():
                        os.system('irsend SEND_ONCE fan KEY_POWER KEY_POWER')  # tắt
                        self.__text_action('đã tắt quạt')
                    elif action == 'giảm'.encode():
                        if mode is not None and mode == 'lạnh'.encode():
                            os.system('irsend SEND_ONCE fan KEY_DOWN KEY_DOWN')  # giam
                            self.__text_action('đã giảm quạt chế độ lạnh')
                        elif mode is not None and mode == 'nóng'.encode():
                            os.system('irsend SEND_ONCE fan KEY_1 KEY_1')  # giam
                            self.__text_action('đã giảm quạt chế độ nóng')
                    elif action == 'tăng'.encode():
                        if mode is not None and mode == 'lạnh'.encode():
                            os.system('irsend SEND_ONCE fan KEY_UP KEY_UP')  # tăng
                            self.__text_action('đã tăng quạt chế độ lạnh')
                        elif mode is not None and mode == 'nóng'.encode():
                            os.system('irsend SEND_ONCE fan KEY_0 KEY_0')  # giam
                            self.__text_action('đã tăng quạt chế độ nóng')
                    elif action == 'xoay'.encode():
                        os.system('irsend SEND_ONCE fan KEY_RO KEY_RO')  # xoay
                        self.__text_action('đã xoay quạt')

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

    # def __appearance_action(self):
    #     requests.get("http://localhost:8080/face")

    def __appreciation_action(self):
        if self.bot_vn in ['ty', 'be', 'xuka']:
            self.__text_action(self.nlg_vn.appreciation())
        else:
            self.__text_action(self.nlg.appreciation())

    def __acknowledge_action(self, langague=None):
        if self.bot_vn in ['ty', 'be', 'xuka']:
            self.__text_action(self.nlg_vn.acknowledge())
        else:
            self.__text_action(self.nlg.acknowledge())

    def __insult_action(self):
        self.__text_action(self.nlg.insult())

    def __personal_status_action(self):
        self.__text_action(self.nlg.personal_status())

    def __text_action(self, text=None):
        if text is not None:
            # requests.get("http://localhost:8080/statement?text=%s" % text)
            # self.speech.synthesize_text(text)
            if self.bot_vn in ['ty', 'be', 'xuka']:
                say(text, 'vi', self.bot_vn)
            else:
                say(text)

    # Voi viet nam thoi
    def __news_action(self, nlu_entities=None, language='vi', oldintent=None):
        country = None
        intent = None
        action = None
        if nlu_entities is not None:
            # get entites from API
            if 'country' in nlu_entities:
                country = nlu_entities['country'][0]['value']
            if 'intent' in nlu_entities:
                intent = nlu_entities['intent'][0]['value']

            # doc tin tuc cua nc nao
            if country is not None and 'việt' in country.lower():
                self.__text_action('tin việt nam ạ, chờ em tý!')
                # todo:get_vnex_news
                news_vn = self.knowledge.get_news('vi')
                if news_vn:
                    # requests.post("http://localhost:8080/news", data=json.dumps({"articles":headlines}))
                    interest = self.nlg.article_interest(news_vn)
                    if interest is not None:
                        self.__text_action(interest)
            elif country is not None and 'nhật bản' in country.lower():
                self.__text_action('tin nhật bản ạ, chờ tý em bảo chị gu gồ đọc cho %s nghe' % my_name_vn)
                news_jp = self.knowledge.get_news('jp')
                if news_jp:
                    # requests.post("http://localhost:8080/news", data=json.dumps({"articles":headlines}))
                    interest = self.nlg.article_interest(news_jp)
                    if interest is not None:
                        say(interest, 'ja')
                        self.decide_action(langague=language, oldintent=intent, pre_message=interest)
                else:
                    self.__text_action('không tìm thấy tin nào hết, %s ạ' % my_name_vn)
            elif oldintent is None:
                self.__text_action('Anh muốn nghe tin gì, nước nào nhật bản hay việt nam hả  %s ?' % my_name_vn)
                self.decide_action(langague=language, oldintent=intent)

    def __weather_action(self, nlu_entities=None):

        current_dtime = datetime.datetime.now()
        skip_weather = False  # used if we decide that current weather is not important

        weather_obj = self.knowledge.find_weather(my_address)
        temperature = weather_obj['temperature']
        icon = weather_obj['icon']
        wind_speed = weather_obj['windSpeed']

        weather_speech = self.nlg.weather(temperature, current_dtime, "present")
        forecast_speech = None

        if nlu_entities is not None:
            if 'datetime' in nlu_entities:
                if 'grain' in nlu_entities['datetime'][0] and nlu_entities['datetime'][0]['grain'] == 'day':
                    dtime_str = nlu_entities['datetime'][0]['value']  # 2016-09-26T00:00:00.000-07:00
                    dtime = dateutil.parser.parse(dtime_str)
                    if current_dtime.date() == dtime.date():  # hourly weather
                        forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['hourly_forecast'],
                                        'location': my_address}
                        forecast_speech = self.nlg.forecast(forecast_obj)
                    elif current_dtime.date() < dtime.date():  # sometime in the future ... get the weekly forecast/ handle specific days
                        forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['weekly_forecast'],
                                        'location': my_address}
                        forecast_speech = self.nlg.forecast(forecast_obj)
                        skip_weather = True
            if 'Weather_Type' in nlu_entities:
                weather_type = nlu_entities['Weather_Type'][0]['value']
                print(weather_type)
                if weather_type == "current":
                    forecast_obj = {'forecast_type': 'current', 'forecast': weather_obj['current_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                elif weather_type == 'today':
                    forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['hourly_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                elif weather_type == 'tomorrow':
                    forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['tomorrow_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                    skip_weather = True
                elif weather_type == '3 day' or weather_type == '7 day':
                    forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['weekly_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg.forecast(forecast_obj)
                    skip_weather = True
                else:
                    forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['hourly_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg.forecast(forecast_obj)

        weather_data = {"temperature": temperature, "icon": icon, 'windSpeed': wind_speed,
                        "hour": datetime.datetime.now().hour}
        # requests.post("http://localhost:8080/weather", data=json.dumps(weather_data))

        if not skip_weather:
            # self.speech.synthesize_text(weather_speech)
            say(weather_speech)

        if forecast_speech is not None:
            # self.speech.synthesize_text(forecast_speech)
            say(forecast_speech)

    def __weather_action_vn(self, nlu_entities=None):

        current_dtime = datetime.datetime.now()
        skip_weather = False  # used if we decide that current weather is not important

        weather_obj = self.knowledge.find_weather(my_address)
        temperature = weather_obj['temperature']
        icon = weather_obj['icon']
        wind_speed = weather_obj['windSpeed']

        weather_speech = self.nlg_vn.weather(temperature, current_dtime, "present")
        forecast_speech = None

        if nlu_entities is not None:
            if 'timely' in nlu_entities:
                timely = nlu_entities['timely'][0]['value']
                print(timely)
                if timely == 'hôm nay':
                    forecast_obj = {'forecast_type': 'hourly', 'forecast': weather_obj['hourly_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg_vn.forecast(forecast_obj)
                elif timely == 'bây giờ':
                    forecast_obj = {'forecast_type': 'current', 'forecast': weather_obj['current_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg_vn.forecast(forecast_obj)
                elif timely == 'ngày mai':
                    forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['tomorrow_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg_vn.forecast(forecast_obj)
                    skip_weather = True
                elif 'tuần' in timely or timely == 'cuối tuần':
                    forecast_obj = {'forecast_type': 'daily', 'forecast': weather_obj['weekly_forecast'],
                                    'location': my_address}
                    forecast_speech = self.nlg_vn.forecast(forecast_obj)
                    skip_weather = True

        weather_data = {"temperature": temperature, "icon": icon, 'windSpeed': wind_speed,
                        "hour": datetime.datetime.now().hour}
        # requests.post("http://localhost:8080/weather", data=json.dumps(weather_data))

        if not skip_weather:
            # self.speech.synthesize_text(weather_speech)
            say(weather_speech, 'vi', self.bot_vn)

        if forecast_speech is not None:
            # self.speech.synthesize_text(forecast_speech)
            say(forecast_speech, 'vi', self.bot_vn)

    def __maps_action(self, nlu_entities=None):

        location = None
        map_type = None
        origin = None
        destination = None
        maps_url = None
        if self.bot_vn in ['ty', 'be', 'xuka']:
            if nlu_entities is not None:
                if 'city' in nlu_entities:
                    location = nlu_entities['city'][0]["value"]
                if 'country' in nlu_entities:
                    country = nlu_entities['country'][0]["value"]
                if 'from' in nlu_entities:
                    origin = nlu_entities['from'][0]["value"]
                if 'to' in nlu_entities:
                    destination = nlu_entities['to'][0]["value"]

            if origin is not None and destination is not None:
                maps_url = self.knowledge.get_direction_map(origin, destination)
                location = 'đường đi'
            else:
                if location is not None:
                    maps_url = self.knowledge.get_map_url(location, map_type)
                else:
                    self.__text_action("Em xin lỗi, em không biết nơi anh muốn tìm")
            if maps_url is not None:
                maps_action = "chắc chắn rồi, đây là bản đồ %s." % location
                body = {'url': maps_url}
                # requests.post("http://localhost:8080/image", data=json.dumps(body))
                say(maps_action, 'vi', self.bot_vn)
        else:
            if nlu_entities is not None:
                if 'location' in nlu_entities:
                    location = nlu_entities['location'][0]["value"]
                if "Map_Type" in nlu_entities:
                    map_type = nlu_entities['Map_Type'][0]["value"]

            if location is not None:
                maps_url = self.knowledge.get_map_url(location, map_type)
                maps_action = "Sure. Here's a map of %s." % location
                body = {'url': maps_url}
                # requests.post("http://localhost:8080/image", data=json.dumps(body))
                self.speech.synthesize_text(maps_action)
            else:
                self.__text_action("I'm sorry, I couldn't understand what location you wanted.")

    def __playmusic(self, nlu_entities=None):
        chanel = 'youtube'
        action = None
        region_code = 'VN'
        location = None
        search_query = None

        if self.bot_vn in ['ty', 'be', 'xuka']:  # vn bot
            if nlu_entities is not None:
                if 'chanel' in nlu_entities:
                    chanel = nlu_entities['chanel'][0]['value']
                if 'action' in nlu_entities:
                    action = nlu_entities['action'][0]['value']
                if 'search_query' in nlu_entities:
                    search_query = nlu_entities['search_query'][0]['value']
                # Play music
                if chanel is not None:
                    if 'youtube' == chanel:
                        if 'mở' == action:
                            stop()
                            if search_query is not None and search_query != 'nghe':
                                YouTube_Autoplay(search_query, region_code)
                            else:
                                YouTube_Autoplay('Le quyen', region_code)
                        elif 'tắt' == action:
                            stop()
                            self.__text_action("ok, em tắt rồi")
                        else:
                            self.__text_action("em chưa hiểu, thưa %s" % my_name)
        else:  # en bot
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

    def __holidays_action(self, nlu_entities=None):
        country = None
        if nlu_entities is not None:
            if 'country' in nlu_entities:
                country = nlu_entities['country'][0]["value"]
                print(nlu_entities['country'][0]["value"])
        if country is not None:
            holidays = self.knowledge.get_holidays(country)
        else:
            holidays = self.knowledge.get_holidays(country='vi')
        if not holidays:
            self.__text_action("No upcoming events found.")
        else:
            i = 0
            words = ''
            while i < 3:
                dayho = dateutil.parser.parse(holidays[i]['start'])
                print(dayho.weekday())
                dayofweek = self.__dayofweek(dayho.weekday())
                words = "%s . %s Ngày %s, tháng %s, năm %s, %s" % (
                    words, dayofweek, dayho.day, dayho.month, dayho.year, holidays[i]['summary'])
                i = i + 1
            self.__text_action(words)

    def __dayofweek(self, i):
        days = ['Thứ hai', 'Thứ ba', 'Thứ tư', 'Thứ năm', 'Thứ sáu', 'Thứ bảy', 'Chủ nhật']
        return days[i]


    def __alarm(self, nlu_entities=None):
        __datetime = None
        __action = None
        current_ts = time.time()
        if nlu_entities is not None:
            if 'datetime' in nlu_entities:
                __datetime = nlu_entities['datetime'][0]['value']

        if  __datetime is not None:
            dtime = dateutil.parser.parse(__datetime)
            str = '%s giờ, %s, Ngày %s, Tháng %s' %(dtime.hour, dtime.minute, dtime.day , dtime.month)
            timestamp2 = time.mktime(dtime.timetuple())
            delay = timestamp2 - current_ts
            if delay > 0:
                _thread.start_new_thread(self.__start_alarm, ("alarm", delay, ) )
                say('đã cài báo thức %s', str)

    # Function to check if mpv is playing
    def __ismpvplaying(self):
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if 'mpv' in p.name():
                mpvactive = True
                break
            else:
                mpvactive = False
        return mpvactive

    # registe alarm
    def __start_alarm( self, threadName, delay):
        time.sleep(delay)
        alarm_file = "/home/pi/AI-Smart-Mirror/sample-audio-files/martian-gun.mp3"
        song = AudioSegment.from_mp3(alarm_file)
        i = 0
        while i <= 30:
            play(song)
            time.sleep(2)
            i +=1




if __name__ == "__main__":
    bot = Bot()
    try:
        bot.start()
    except KeyboardInterrupt:
        # turn off led
        GPIO.output(LEDPIN, GPIO.LOW)
        # release resource
        GPIO.cleanup()
