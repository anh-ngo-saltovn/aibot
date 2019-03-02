"""
Shows basic usage of the Google Calendar API. Creates a Google Calendar API
service object and outputs a list of the next 10 events on the user's calendar.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

class GCal(object):
    def __init__(self):
        # Setup the Calendar API
        SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('../client_secret_351325976697-o2e7ksq7t8ojigfag56293655qne9g2v.apps.googleusercontent.com.json', SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('calendar', 'v3', http=creds.authorize(Http()))

    def get_cal(self,calendarId='primary'):
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(calendarId=calendarId, timeMin=now,
                                              maxResults=7, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        results = []
        if not events:
            return results
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            results.append({'start':start, 'summary': event['summary']})
            # print(start, event['summary'])
        return results
