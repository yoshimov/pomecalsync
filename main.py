#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, glob, string, re, sys
import datetime
from pcscalendar import PCSCalendar
from pcsconfig import PCSConfig
from pcsdialog import PCSDialog

class PCSControl:
    tk = None
    dialog = None
    config = None
    cal = None
    calendar_id = None
    memo_files = None
    after_date = None

    def __init__(self, dialog):
        self.dialog = dialog
        self.tk = self.dialog.get_tk()
        self.dialog.set_control(self)

    def set_config(self, config):
        self.config = config
        self.tk.after(100, self.config.load)

    def set_cal(self, cal):
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
            self.config.save()
        else:
            self.msg('please select calendar.')
            return
        # check config
        days = self.config.get('keep_days')
        if not days:
            days = 3
        self.after_date = datetime.date.today() - datetime.timedelta(days=days)
        self.tk.after(100, self.scan_files)

    def scan_files(self):
        available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        # scan pomera memo folder
        pdrive = None
        for d in available_drives:
            if os.path.exists('%s/Pomera_memo' % d):
                self.msg('Pomera found in drive %s' % d)
                pdrive = d
        if pdrive:
            memo_files = glob.glob('%s/Pomera_memo/**/*.txt' % pdrive)
            for file in memo_files:
                self.tk.after(100, self.sync_calendar_memo, file)
        else:
            self.msg('Pomera not found.')

    def sync_calendar_memo(self, file):
        list = re.findall(r"[\\\/]\d{8}\.txt$", file)
        if not list or len(list) < 1:
            self.msg('skip file: %s' % file)
            return
        name = list[0]
        self.msg('found memo file: %s' % file)
        year = int(name[1:5])
        month = int(name[5:7])
        day = int(name[7:9])
        if not year or not month or not day:
            self.msg('fail to parse date format.')
            return
        if datetime.date(year, month, day) > self.after_date:
            self.msg('skip the memo.')
            return
        with open(file, mode='r', encoding='Shift_JIS') as f:
            memo = f.read()
        try:
            if memo:
                self.cal.create_memo(self.calendar_id, year, month, day, memo)
            else:
                self.msg('fail to read memo.')
                return
        except:
            self.msg('fail to create calendar memo.')
            return
        self.tk.after(100, self.delete_memo_file, file)

    def delete_memo_file(self, file):
        self.msg('removing file: %s' % file)
        os.remove(file)

    def finish(self):
        sys.exit(0)

    # logging
    def msg(self, text):
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
