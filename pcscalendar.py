#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import importlib.util
import os
import string
import sys
import time
from argparse import Namespace
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow as run

def get_app_dir():
    """
    設定ファイルや認証トークンを置くアプリケーションのフォルダを返す。
    PyInstaller 実行時は exe と同じフォルダを使う。
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_googlecredential():
    """
    Google API の client_id/client_secret を持つ googlecredential.py を読み込む。
    PyInstaller 実行時は exe と同じフォルダの外部ファイルも探す。
    """
    try:
        return importlib.import_module('googlecredential')
    except ModuleNotFoundError:
        pass

    candidates = [
        os.path.join(get_app_dir(), 'googlecredential.py'),
        os.path.join(os.getcwd(), 'googlecredential.py'),
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        spec = importlib.util.spec_from_file_location('googlecredential', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None

def create_oauth_flags():
    """
    GUI アプリでもブラウザ認証を使うための oauth2client 用フラグを作成する。
    """
    return Namespace(
        auth_host_name='localhost',
        auth_host_port=[8080, 8090],
        logging_level='ERROR',
        noauth_local_webserver=False,
    )

# class of google calendar proxy
class PCSCalendar:
    log = None
    storage = None
    credentials = None
    service = None

    def __init__(self, log):
        self.log = log

    def get_credentials(self):
        credential_file = os.path.join(get_app_dir(), 'google-calendar.dat')
        self.storage = Storage(credential_file)
        self.credentials = self.storage.get()
        if not self.credentials or self.credentials.invalid:
            self.log.msg('credential not found. opening browser for authorization.')
            googlecredential = load_googlecredential()
            if not googlecredential:
                self.log.msg('googlecredential.py not found. please put it next to the exe.')
                return
            flow = OAuth2WebServerFlow(
                client_id=googlecredential.client_id,
                client_secret=googlecredential.client_secret,
                scope=['https://www.googleapis.com/auth/calendar'],
                user_agent='Calendar Sample/1.0')
            # run function blocks main thread of tk
            self.credentials = run(flow, self.storage, flags=create_oauth_flags())
            self.log.msg('finished to get credentials.')
        else:
            self.log.msg('load credentials from file.')
        if self.credentials:
            http = httplib2.Http()
            self.credentials.authorize(http)
            self.service = build('calendar', 'v3', http=http)

    def has_credentials(self) -> bool:
        return self.credentials

    def get_calendars(self) -> list:
        self.log.msg('getting calendar list.')
        calendars = self.service.calendarList().list().execute()
# for debug
#        for calendar in calendars['items']:
#            print(calendar)
        if calendars:
            return calendars['items']
        else:
            return None

    def create_memo(self, id: string, year: int, month: int, day: int, memo: string):
        date = f'{year:04}-{month:02}-{day:02}'
        self.log.msg(f'creating memo {date}')
        event = {'start': {'date': date}, 'end': {'date': date},
            'summary': 'memo', 'description': memo}
        event = self.service.events().insert(calendarId=id, body=event).execute()
# for debug
#        print(event)
