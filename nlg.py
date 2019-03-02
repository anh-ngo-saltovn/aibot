# -*- coding: utf-8 -*-
# nlg.py
import random
import datetime
from py4j_server import launch_py4j_server
from py4j.java_gateway import java_import

gateway = launch_py4j_server()

# Import the SimpleNLG classes
java_import(gateway.jvm, "simplenlg.features.*")
java_import(gateway.jvm, "simplenlg.realiser.*")

# Define aliases so that we don't have to use the gateway.jvm prefix.
NPPhraseSpec = gateway.jvm.NPPhraseSpec
PPPhraseSpec = gateway.jvm.PPPhraseSpec
SPhraseSpec = gateway.jvm.SPhraseSpec
InterrogativeType = gateway.jvm.InterrogativeType
Realiser = gateway.jvm.Realiser
TextSpec = gateway.jvm.TextSpec
Tense = gateway.jvm.Tense
Form = gateway.jvm.Form


class NLG(object):
    """
    Used to generate natural language. Most of these sections are hard coded. However, some use simpleNLG which is
    used to string together verbs and nouns.
    """
    def __init__(self, user_name=None, language = None):
        self.user_name = user_name
        self.language = language
        # make random more random by seeding with time
        random.seed(datetime.datetime.now())

    def acknowledge(self):
        user_name = self.user_name
        if user_name is None:
            user_name = ""

        if self.language == 'vi':
            simple_acknoledgement = [
                "dạ, có em?",
                "anh muốn em làm gì?",
                "vâng thưa sếp?",
                "anh gọi em?",
                "vâng anh?"
            ]

            personal_acknowledgement = [
                "Hôm nay anh muốn em làm gì?, %s" % user_name,
                "có em thưa, %s" % user_name,
                "em làm gì được cho, %s đây ạ" % user_name,
                "chào %s, em sẵn sàng chờ lệnh?" % user_name,
                "ê %s, mày muốn gì?" % user_name
            ]
        else:
            simple_acknoledgement = [
                "Yes?",
                "What can I do for you?",
                "How can I help?"
            ]


            personal_acknowledgement = [
                "How can I help you today, %s" % user_name,
                "How can I help you, %s" % user_name,
                "What can I do for you, %s" % user_name,
                "Hi %s, what can I do for you?" % user_name,
                "Hey %s, what can I do for you?" % user_name
            ]



        choice = 0
        if self.user_name is not None:
            choice = random.randint(0, 2)
        else:
            choice = random.randint(0,1)

        ret_phrase = ""

        if choice == 0:
            ret_phrase = random.choice(simple_acknoledgement)
        elif choice == 1:
            date = datetime.datetime.now()
            if self.language == 'vi':
                ret_phrase = "Buối %s. thế nào sếp?" % self.time_of_day(date)
            else:
                ret_phrase = "Good %s. What can I do for you?" % self.time_of_day(date)
        else:
            ret_phrase = random.choice(personal_acknowledgement)

        return ret_phrase

    def searching(self):
        searching_phrases = [
            "I'll see what I can find"
        ]

        return random.choice(searching_phrases)

    def snow_white(self):

        phrases = [
            "You are",
            "You",
            "You are, of course"
        ]

        return random.choice(phrases)

    def user_status(self, type='positive', attribute=None):

        ret_phrase = ""

        positive_complements = [
            "good",
            "nice",
            "great",
            "perfect",
            "Beautiful"
        ]

        negative_complements = [
            "bad",
            "terrible"
        ]

        moderate_complements = [
            "alright",
            "okay"
        ]

        complement_choice = positive_complements
        if type == 'negative':
            complement_choice = negative_complements
        elif type == 'moderate':
            complement_choice = moderate_complements

        if attribute is None:
            ret_phrase = "You look %s" % random.choice(complement_choice)
        else:
            ret_phrase = self.generate('none', {'subject': "Your %s" % attribute, 'verb': 'look %s' % random.choice(complement_choice)}, "present")

        return ret_phrase

    def personal_status(self, status_type=None):
        positive_status=[
            "I'm doing well",
            "Great, thanks for asking",
            "I'm doing great"
        ]

        negative_status = [
            "I'm not doing well",
            "I'm feeling terrible",
            "I'm not doing well today",
            "I could be much better"
        ]

        moderate_status = [
            "I'm doing alright",
            "I'm okay",
            "I could be better",
            "I'm alright"
        ]

        if status_type == 'negative':
            return random.choice(negative_status)
        elif status_type == 'moderate':
            return random.choice(moderate_status)

        return random.choice(positive_status)

    def joke(self):
        jokes = [
            "Artificial intelligence is no match for natural stupidity.",
            "This morning I made a mistake and poured milk over my breakfast instead of oil, and it rusted before I could eat it.",
            "An Englishman, an Irishman and a Scotsman walk into a bar. The bartender turns to them, takes one look, and says, \"What is this - some kind of joke?\"",
            "What's an onomatopoeia? Just what it sounds like!",
            "Why did the elephant cross the road? Because the chicken retired.",
            "Today a man knocked on my door and asked for a small donation towards the local swimming pool. I gave him a glass of water.",
            "A recent study has found that women who carry a little extra weight live longer than the men who mention it.",
            "I can totally keep secrets. It's the people I tell them to that can't.",
            "My therapist says I have a preoccupation with vengeance. We'll see about that.",
            "Money talks ...but all mine ever says is good-bye.",
            "I started out with nothing, and I still have most of it.",
            "I used to think I was indecisive, but now I'm not too sure.",
            "I named my hard drive dat ass so once a month my computer asks if I want to 'back dat ass up'.",
            "A clean house is the sign of a broken computer.",
            "My favorite mythical creature? The honest politician.",
            "Regular naps prevent old age, especially if you take them while driving.",
            "For maximum attention, nothing beats a good mistake.",
            "Take my advice. I'm not using it."
        ]

        return random.choice(jokes)

    def news_question(self):
        #Anh muốn nghe tin gì, nước nào hả %s ?
        headlines_nouns = [
            "tin tức",
            "tin",
        ]

        headlines_prepmodifiers = [
            "Nhật",
            "Viêt nam"
        ]
        # nlg = NaturalLanguageGenerator(logging.getLogger())
        words = {'subject': 'Anh',
                 'verb': 'nghe',
                 'object': random.choice(headlines_nouns),
                 'preposition': 'của',
                 # 'objmodifiers': ['Thai'],
                 'prepmodifiers': headlines_prepmodifiers,
                 'adverbs': ['muốn'],
        }
        # words = {'subject': 'You',
        #          'verb': 'prefer',
        #          'object': 'recipes',
        #          'preposition': 'that contains',
        #          'objmodifiers': ['Thai'],
        #          'prepmodifiers': ['potatoes', 'celery', 'carrots'],
        #          'adverbs': ['confidently'],
        # }

        return self.generate('what', words,'past')
        # u'Do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        # nlg.generate('how', words)
        # u'How do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'



    def news(self, tense):

        headlines_nouns = [
            "stories",
            "articles",
            "headlines",
        ]

        headlines_adjectives = [
            ["these"],
            ["some"],
            ["a", "few"],
            ["a", "couple"]
        ]

        headlines_prepmodifiers = [
            "you"
        ]

        choice = random.randint(0, 1)

        if choice == 1:
            ret_phrase = self.generate('none', {'subject': "I", 'object': random.choice(headlines_nouns), 'verb': 'find', 'objmodifiers': random.choice(headlines_adjectives), 'preposition': 'for', 'prepmodifiers': [random.choice(headlines_prepmodifiers)]}, tense)
        else:
            ret_phrase = self.generate('none', {'subject': "I", 'object': random.choice(headlines_nouns), 'verb': 'find', 'objmodifiers': random.choice(headlines_adjectives)}, tense)

        return ret_phrase

    def article_interest(self, news, index = 0):
        ret_phrase = None
        if news is not None:
            new = random.choice(news)
            ret_phrase = new['summary']
        return ret_phrase

    def insult(self):
        return "That's not very nice. Talk to me again when you have fixed your attitude"

    def greet(self):
        """
        Creates a greeting phrase.
        :return:
        """
        if self.language == 'vi':
            greeting_words = [
                "dạ anh khoẻ không ",
                "Hi ",
                "Hế lô!"
            ]

            goofy_greetings = [
                "gì cu?",
                "quát thờ heo?",
                "chào chào quần què ",
                "biến đê "
            ]
        else:
            greeting_words = [
                "Hi",
                "Hey",
                "Hello"
            ]

            goofy_greetings = [
                "what's up?",
                "howdy",
                "what's crackin'?",
                "top of the morning to ya"
            ]

        choice = random.randint(0,4)
        ret_phrase = ""

        if (choice == 0) or (choice == 3): # time related
            if self.language == 'vi':
                ret_phrase = "chào buổi %s sếp " % self.time_of_day(datetime.datetime.now())
            else:
                ret_phrase = "Good %s" % self.time_of_day(datetime.datetime.now())
            if self.user_name is not None:
                if random.randint(0, 1) == 0:
                    ret_phrase = "%s %s" % (ret_phrase, self.user_name)
        elif (choice == 1) or (choice == 4): # standard greeting
            ret_phrase = random.choice(greeting_words)
            if self.user_name is not None:
                if random.randint(0, 1) == 0:
                    ret_phrase = "%s %s" % (ret_phrase, self.user_name)
        elif choice == 2: # goofy greeting
            ret_phrase = random.choice(goofy_greetings)

        return ret_phrase

    def weather(self, temperature, date, tense):
        """
        Generates a statement about the current weather.
        :param temperature:
        :param date:
        :param tense:
        :return:
        """
        # if self.language == 'vi':
        #     ret_phrase = 'Thời tiết hiện tại  '
        # else:

        ret_phrase = self.generate('none', {'subject':"the temperature", 'object': "%d degrees" % temperature, 'verb': 'is', 'adverbs': ["%s" % self.time_of_day(date, with_adjective=True)]}, tense)
        return ret_phrase

    def forecast(self, forecast_obj):

        ret_phrase = ""
        forecast = ""
        location = ""
        if forecast_obj.get("forecast") is None:
            return ret_phrase
        else:
            forecast = forecast_obj.get("forecast")
            location = forecast_obj.get("location")

        forecast_current = [
            "Currently, it's",
            "Right now, it's",
            "At the moment, it's",
            "It's",
            "It is"
        ]

        forecast_hourly = [
            "It's",
            "It will be",
            "Looks like it will be"
        ]

        forecast_daily = [
            ""
        ]

        if forecast_obj.get('forecast_type') == "current":
            ret_phrase = "Weather at %s %s %s" % (location,random.choice(forecast_current), forecast)
        elif forecast_obj.get('forecast_type') == "hourly":
            ret_phrase = "Weather at %s %s %s" % (location,random.choice(forecast_hourly), forecast)
        elif forecast_obj.get('forecast_type') == "daily":
            ret_phrase = "Weather at %s %s %s" % (location,random.choice(forecast_daily), forecast)

        return ret_phrase

    def appreciation(self):
        phrases = [
            "No problem!",
            "Any time",
            "You are welcome",
            "You're welcome",
            "Sure, no problem",
            "Of course",
            "Don't mention it",
            "Don't worry about it"
        ]

        phrases_vn = [
            "cảm ơn cái quần quề!",
            "luôn luôn lắng nghe, luôn luôn thấu hiểu, tè reee",
            "Rất vui được phục vụ",
            "hỏi tiếp đi anh",
            "không có chi!",
            "bổn phận của em mà",
            "em pro vãi",
            "chuyện?",
            "em cân hết",
            "hãy để cả thế giới em lo",
            "Don't worry about it"
        ]
        if self.language == 'vi':
            return random.choice(phrases_vn)
        else:
            return random.choice(phrases)

    def holiday(self, holiday_name):
        phrases = [
            "",
            "Looks like the next holiday is ",
            "The next important day is "
        ]

        return "%s%s" % (random.choice(phrases), holiday_name)

    def meaning_of_life(self):
        phrases = [
            "42",
            "The meaning of life, the universe, and everything else is 42"
        ]

        return random.choice(phrases)

    def name(self):
        return self.user_name

    def time_of_day(self, date, with_adjective=False):
        ret_phrase = ""
        if date.hour < 10:
            if self.language == 'vi':
                ret_phrase = "sáng"
            else:
                ret_phrase = "morning"
            if with_adjective:
                ret_phrase = "%s %s" % ("this", ret_phrase)
        elif (date.hour >= 10) and (date.hour < 18):
            if self.language == 'vi':
                ret_phrase = "trưa "
            else:
                ret_phrase = "afternoon"
            if with_adjective:
                ret_phrase = "%s %s" % ("this", ret_phrase)
        elif date.hour >= 18:
            if self.language == 'vi':
                ret_phrase = "tối"
            else:
                ret_phrase = "evening"
            if with_adjective:
                ret_phrase = "%s %s" % ("this", ret_phrase)

        return ret_phrase

    def unknown(self):
        phrases = [
            "Cái này em chưa học, cho em đổi câu hỏi",
            "Cái này em chưa học, hỏi cái câu khác đi?",
            "Câu này khó quá không trả lời",
            "Câu này khó quá không làm được",
            "Bỏ qua, câu tiếp",
            "Hãy dạy em thêm nhé"
        ]

        return random.choice(phrases)

    def generate(self, utter_type, keywords, tense=None):
        """
        Input: a type of inquiry to create and a dictionary of keywords.
        Types of inquiries include 'what', 'who', 'where', 'why', 'how',
        and 'yes/no' questions. Alternatively, 'none' can be specified to
        generate a declarative statement.

        The dictionary is essentially divided into three core parts: the
        subject, the verb, and the object. Modifiers can be specified to these
        parts (adverbs, adjectives, etc). Additionally, an optional
        prepositional phrase can be specified.

        Example:

        nlg = NaturalLanguageGenerator(logging.getLogger())
        words = {'subject': 'you',
                 'verb': 'prefer',
                 'object': 'recipes',
                 'preposition': 'that contains',
                 'objmodifiers': ['Thai'],
                 'prepmodifiers': ['potatoes', 'celery', 'carrots'],
                 'adverbs': ['confidently'],
        }

        nlg.generate('yes_no', words)
        u'Do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        nlg.generate('how', words)
        u'How do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        """
        utterance = SPhraseSpec()
        subject = NPPhraseSpec(keywords['subject'])
        target = None
        if 'object' in keywords:
            target = NPPhraseSpec(keywords['object'])
        preposition = PPPhraseSpec()

        if 'preposition' in keywords:
            preposition.setPreposition(keywords['preposition'])

        if 'prepmodifiers' in keywords:
            for modifier in keywords['prepmodifiers']:
                preposition.addComplement(modifier)

        if 'submodifiers' in keywords:
            for modifier in keywords['submodifiers']:
                subject.addModifier(modifier)

        if 'objmodifiers' in keywords:
            for modifier in keywords['objmodifiers']:
                target.addModifier(modifier)

        if utter_type.lower() == 'yes_no':
            utterance.setInterrogative(InterrogativeType.YES_NO)
        elif utter_type.lower() == 'how':
            utterance.setInterrogative(InterrogativeType.HOW)
        elif utter_type.lower() == 'what':
            utterance.setInterrogative(InterrogativeType.WHAT)
        elif utter_type.lower() == 'where':
            utterance.setInterrogative(InterrogativeType.WHERE)
        elif utter_type.lower() == 'who':
            utterance.setInterrogative(InterrogativeType.WHO)
        elif utter_type.lower() == 'why':
            utterance.setInterrogative(InterrogativeType.WHY)

        if target is not None:
            target.addModifier(preposition)
        utterance.setSubject(subject)
        utterance.setVerb(keywords['verb'])
        if 'adverbs' in keywords:
            for modifier in keywords['adverbs']:
                utterance.addModifier(modifier)
        if target is not None:
            utterance.addComplement(target)

        if tense.lower() == 'future':
            utterance.setTense(Tense.FUTURE)
        elif tense.lower() == 'past':
            utterance.setTense(Tense.PAST)

        realiser = Realiser()
        output = realiser.realiseDocument(utterance).strip()
        return output
