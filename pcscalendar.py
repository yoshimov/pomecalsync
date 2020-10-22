#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import httplib2
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow as run
import googlecredential

# class of google calendar proxy
class PCSCalendar:
    log = None
    storage = None
    credentials = None
    service = None

    def __init__(self, log):
        self.log = log

    def get_credentials(self):
        self.storage = Storage('google-calendar.dat')
        self.credentials = self.storage.get()
        if not self.credentials or self.credentials.invalid:
            self.log.msg('authorizing credentials')
            flow = OAuth2WebServerFlow(
                client_id=client_id,
                client_secret=client_secret,
                scope=['https://www.googleapis.com/auth/calendar'],
                user_agent='Calendar Sample/1.0')
            # run function blocks main thread of tk
            self.credentials = run(flow, self.storage)
            self.log.msg('finished to get credentials.')
        else:
            self.log.msg('load credentials from file.')
        if self.credentials:
            http = httplib2.Http()
            self.credentials.authorize(http)
            self.service = build('calendar', 'v3', http=http)

    def has_credentials(self):
        return self.credentials

    def get_calendars(self):
        self.log.msg('getting calendar list.')
        calendars = self.service.calendarList().list().execute()
# for debug
#        for calendar in calendars['items']:
#            print(calendar)
        return calendars['items']

    def create_memo(self, id, year, month, day, memo):
        date = "{:02}-{:02}-{:02}".format(year, month, day)
        self.log.msg('creating memo %s' % date)
        event = {'start': {'date': date}, 'end': {'date': date},
            'summary': 'memo', 'description': memo}
        event = self.service.events().insert(calendarId=id, body=event).execute()
# for debug
#        print(event)
