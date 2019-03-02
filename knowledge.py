# -*- coding: utf-8 -*-
import requests
import json
import feedparser
import datetime
from gcal import GCal

class Knowledge(object):
    def __init__(self, weather_api_token,google_cloud_api_key=None):
        self.weather_api_token = weather_api_token
        self.google_cloud_api_key = google_cloud_api_key
        self.calendar = GCal()

    def find_weather(self, address=None):
        loc_obj = self.get_location(address)
        lat = loc_obj['lat']
        lon = loc_obj['lon']

        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?%s" % (self.weather_api_token, lat, lon,"units=si")
        r = requests.get(weather_req_url)
        weather_json = json.loads(r.text)

        if 'currently' in weather_json :
            temperature = int(weather_json['currently']['temperature'])
            current_forecast = weather_json['currently']['summary']
            icon = weather_json['currently']['icon']
            wind_speed = int(weather_json['currently']['windSpeed'])
        else:
            current_forecast = ''

        if 'minutely' in weather_json :
            minutely_forecast = weather_json['minutely']['summary'] # gio trong ngay
        else:
            minutely_forecast = ''

        if 'hourly' in weather_json :
            hourly_forecast = weather_json['hourly']['summary'] ## hom nay
        else:
            hourly_forecast = ''

        if 'daily' in weather_json :
            tomorrow_forecast = weather_json['daily']['data'][0]['summary'] # get weather tomorrow

            weekly_forecast = weather_json['daily']['summary'] # on week
        else:
            weekly_forecast = ''
            tomorrow_forecast = ''
        return {'temperature': temperature,
            'icon': icon,
            'windSpeed': wind_speed,
            'current_forecast': current_forecast,
            'hourly_forecast': hourly_forecast,
            #'weeken_forecast': weeken_forecast,
            'tomorrow_forecast': tomorrow_forecast,
            'weekly_forecast': weekly_forecast,
            'location': address}


    def get_location(self,location = 'shibuya'):
        # get location
        # location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
        # r = requests.get(location_req_url)
        # location_obj = json.loads(r.text)
        #
        # lat = location_obj['latitude']
        # lon = location_obj['longitude']
        location_req_url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % location
        r = requests.get(location_req_url)
        location_obj = json.loads(r.text)
        if location_obj['status'] ==  'OK':
            lat = location_obj['results'][0]['geometry']['location']['lat']
            lon = location_obj['results'][0]['geometry']['location']['lng']
        else:
            lat = 35
            lon = 139
        return {'lat': lat, 'lon': lon}

    def get_ip(self):
        ip_url = "http://jsonip.com/"
        req = requests.get(ip_url)
        ip_json = json.loads(req.text)
        return ip_json['ip']

    def get_map_url(self, location, map_type=None):
        if map_type == "satellite":
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=satellite&format=png" % location
        elif map_type == "terrain":
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=terrain&format=png" % location
        elif map_type == "hybrid":
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=hybrid&format=png" % location
        else:
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=roadmap&format=png" % location

    def get_direction_map(self, origin, destination):
        url = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=roadmap&key=%s" % (origin,destination,self.google_cloud_api_key)
        res = requests.get(url)
        pos = []
        makers = []
        if res.status_code == 200:
            res_json = json.loads(res.text)
            star = '%s, %s' % (res_json['routes'][0]['legs'][0]['start_location']['lat'],res_json['routes'][0]['legs'][0]['start_location']['lng'])
            end = '%s, %s' % (res_json['routes'][0]['legs'][0]['end_location']['lat'],res_json['routes'][0]['legs'][0]['end_location']['lng'])
            start_makers = 'markers=color:red|label:S|%s' % star
            end_makers = 'markers=color:red|label:S|%s' % star
            pos.append(star)
            locations = res_json['routes'][0]['legs'][0]['steps']
            for loc in locations:
                p = "%s,%s" % (loc['end_location']['lat'],loc['end_location']['lng'])
                pos.append(p)

            pos_str = "|".join(pos)
            print(pos_str)
            return "https://maps.googleapis.com/maps/api/staticmap?size=1200x600&maptype=roadmap&path=color:red|weight:3|%s&%s&%s" % (pos_str, start_makers, end_makers)


    def get_news(self,country='vi'):
        ret_headlines = []
        if country == 'jp':
            url = "https://www3.nhk.or.jp/rss/news/cat0.xml"
        else:
            url = "http://feeds.bbci.co.uk/vietnamese/vietnam/rss.xml"
        d = feedparser.parse(url)
        for post in d.entries:
            new = {
                'title':post.title,
                'summary':post.summary,
                'link':post.link
            }
            ret_headlines.append(new)
        return ret_headlines


    def get_holidays(self,country='vn'):
        if country.lower() == 'nhật bản':
            holidays = self.calendar.get_cal("vi.japanese#holiday@group.v.calendar.google.com")
        else:
            holidays = self.calendar.get_cal("vi.vietnamese#holiday@group.v.calendar.google.com")
        if holidays:
            return holidays

    def get_country_code(country_name):
        r = requests.get("https://restcountries.eu/rest/v2/name/%s" % country_name)
        json_data = json.loads(r.text)
        country_code = json_data[0]['alpha2Code']

        return country_code
