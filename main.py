#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, glob, string, re, sys
import datetime
from pcscalendar import PCSCalendar
from pcsconfig import PCSConfig
from pcsdialog import PCSDialog

FUSEN_STR = '★付箋文★'

class PCSControl:
    tk = None
    dialog = None
    config = None
    cal = None
    calendar_id = None
    memo_files = None
    after_date = None

    def __init__(self, dialog: PCSDialog):
        self.dialog = dialog
        self.tk = self.dialog.get_tk()
        self.dialog.set_control(self)

    def set_config(self, config: PCSConfig):
        self.config = config
        self.tk.after(100, self.config.load)

    def set_cal(self, cal: PCSCalendar):
        self.cal = cal
        self.tk.after(200, self.get_credentials)

    def get_credentials(self):
        self.cal.get_credentials()
        if self.cal.has_credentials:
            self.tk.after(100, self.get_calendars)
        else:
            self.log.msg('fail to get credentials.')

    def get_calendars(self):
        if self.cal.has_credentials():
            calendars = self.cal.get_calendars()
            self.dialog.set_calendar_list(calendars)
            sid = self.config.get('selected_calendar')
            if sid:
                self.msg('selected calendar id: %s' % sid)
                self.tk.after(100, self.dialog.select_calendar, sid)
        else:
            self.msg('fail to get calendar list.')

    def config(self):
        pass    

    # start sync with google calendar
    def sync(self):
        self.msg('starting sync with google calendar.')
        self.calendar_id = self.dialog.get_selected_calendar()
        if self.calendar_id:
            self.config.set('selected_calendar', self.calendar_id)
        else:
            self.msg('please select calendar.')
            return
        # check config
        days = self.config.get('keep_days', 3)
        self.after_date = datetime.date.today() - datetime.timedelta(days=days)
        self.tk.after(100, self.scan_files)

    def scan_files(self):
        available_drives = [f'{d}:' for d in string.ascii_uppercase if os.path.exists(f'{d}:')]
        # scan pomera memo folder
        pdrive = None
        for d in available_drives:
            if os.path.exists(f'{d}/Pomera_memo'):
                self.msg(f'Pomera found in drive {d}')
                pdrive = d
        if pdrive:
            memo_files = glob.glob(f'{pdrive}/Pomera_memo/**/*.txt')
            for file in memo_files:
                self.tk.after(100, self.sync_calendar_memo, file)
        else:
            self.msg('Pomera not found.')

    def sync_calendar_memo(self, file: string):
        match = re.search(r'[\\\/](\d{4})(\d{2})(\d{2})\.txt$', file)
        if not match:
            self.msg(f'skip file: {file}')
            return
        self.msg(f'found memo file: {file}')
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        if not year or not month or not day:
            self.msg('fail to parse date format.')
            return
        if datetime.date(year, month, day) > self.after_date:
            self.msg('skip the recent memo.')
            return
        with open(file, mode='r', encoding='Shift_JIS') as f:
            memo = f.read()
        if not memo:
            self.msg('fail to read memo.')
            return
        # skip the memo start with fusen string
        if memo.startswith(FUSEN_STR):
            self.msg('skip the memo starts with fusen.')
            return
        try:
            self.cal.create_memo(self.calendar_id, year, month, day, memo)
        except:
            self.msg('fail to create calendar memo.')
            return
        self.tk.after(100, self.delete_memo_file, file)

    def delete_memo_file(self, file: string):
        if self.config.get('delete_memo', True):
            self.msg(f'removing file: {file}')
            os.remove(file)
        else:
            self.msg(f'adding fusen to file: {file}')
            with open(file, mode='r', encoding='Shift_JIS') as f:
                content = f.read()
            with open(file, mode='w', encoding='Shift_JIS') as f:
                f.write(f'{FUSEN_STR}\n{content}')

    def finish(self):
        sys.exit(0)

    # logging
    def msg(self, text: string):
        self.dialog.append(text)

def main():
    dialog = PCSDialog()
    control = PCSControl(dialog)
    config = PCSConfig(control)
    control.set_config(config)
    cal = PCSCalendar(control)
    control.set_cal(cal)
    dialog.show()

if __name__ == "__main__":
    # execute only if run as a script
    main()
