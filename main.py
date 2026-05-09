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
        """
        UI ダイアログを受け取り、操作を制御するための参照を初期化する。
        """
        self.dialog = dialog
        self.tk = self.dialog.get_tk()
        self.dialog.set_control(self)

    def set_config(self, config: PCSConfig):
        """
        設定管理オブジェクトを登録し、Tk のイベントループ開始後に設定を読み込む。
        """
        self.config = config
        self.tk.after(10, self.load_config)

    def load_config(self):
        """
        保存済み設定を読み込み、画面上の設定項目へ反映する。
        """
        self.config.load()
        self.dialog.set_delete_memo(self.config.get('delete_memo', True))
        self.dialog.set_days(self.config.get('keep_days', 3))

    def set_cal(self, cal: PCSCalendar):
        """
        Google Calendar 操作用オブジェクトを登録し、認証処理を開始する。
        """
        self.cal = cal
        self.tk.after(10, self.get_credentials)

    def get_credentials(self):
        """
        Google Calendar API の認証情報を取得し、成功したらカレンダー一覧取得へ進む。
        """
        self.cal.get_credentials()
        if self.cal.has_credentials:
            self.tk.after(10, self.get_calendars)
        else:
            self.log.msg('fail to get credentials.')

    def get_calendars(self):
        """
        Google Calendar のカレンダー一覧を取得し、画面のリストへ反映する。
        """
        if self.cal.has_credentials():
            calendars = self.cal.get_calendars()
            self.dialog.set_calendar_list(calendars)
            sid = self.config.get('selected_calendar')
            if sid:
                self.msg('selected calendar id: %s' % sid)
                self.tk.after(10, self.dialog.select_calendar, sid)
        else:
            self.msg('fail to get calendar list.')

    def config(self):
        """
        将来の設定画面用に残されているプレースホルダー。
        """
        pass    

    # start sync with google calendar
    def sync(self):
        """
        画面の選択内容と設定値を保存し、Pomera メモの同期処理を開始する。
        """
        self.msg('starting sync with google calendar.')
        self.calendar_id = self.dialog.get_selected_calendar()
        if self.calendar_id:
            self.config.set('selected_calendar', self.calendar_id)
        else:
            self.msg('please select calendar.')
            return
        # check config
        self.config.set('keep_days', days := self.dialog.get_days())
        self.config.set('delete_memo', self.dialog.get_delete_memo())
        self.after_date = datetime.date.today() - datetime.timedelta(days=days)
        self.tk.after(10, self.scan_files)

    def scan_files(self):
        """
        接続されているドライブから Pomera_memo フォルダを探し、同期対象ファイルを集める。
        """
        available_drives = [f'{d}:' for d in string.ascii_uppercase if os.path.exists(f'{d}:')]
        # scan pomera memo folder
        pdrive = None
        for d in available_drives:
            if os.path.exists(f'{d}/Pomera_memo'):
                self.msg(f'Pomera found in drive {d}')
                pdrive = d
        if pdrive:
            self.memo_files = glob.glob(f'{pdrive}/Pomera_memo/**/*.txt', recursive=True)
            self.tk.after(10, self.sync_next_memo)
        else:
            self.msg('Pomera not found.')

    def sync_next_memo(self):
        """
        同期対象のメモを1件取り出して処理する。残りがなければ同期完了を通知する。
        """
        if not self.memo_files:
            self.msg('finished sync.')
            return
        self.sync_calendar_memo(self.memo_files.pop(0))

    def finish_current_memo(self):
        """
        現在のメモ処理を終え、Tk の再描画を挟んで次のメモ処理を予約する。
        """
        self.tk.after(10, self.sync_next_memo)

    def sync_calendar_memo(self, file: string):
        """
        メモファイル名から日付を読み取り、条件に合うメモを Google Calendar に登録する。
        """
        match = re.search(r'[\\\/](\d{4})(\d{2})(\d{2})\.txt$', file)
        if not match:
            self.msg(f'skip file: {file}')
            self.finish_current_memo()
            return
        self.msg(f'found memo file: {file}')
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        if not year or not month or not day:
            self.msg('fail to parse date format.')
            self.finish_current_memo()
            return
        if datetime.date(year, month, day) > self.after_date:
            self.msg('skip the recent memo.')
            self.finish_current_memo()
            return
        with open(file, mode='r', encoding='Shift_JIS') as f:
            memo = f.read()
        if not memo:
            self.msg('fail to read memo.')
            self.finish_current_memo()
            return
        # skip the memo start with fusen string
        if memo.startswith(FUSEN_STR):
            self.msg('skip the memo starts with fusen.')
            self.finish_current_memo()
            return
        try:
            self.cal.create_memo(self.calendar_id, year, month, day, memo)
        except:
            self.msg('fail to create calendar memo.')
            self.finish_current_memo()
            return
        self.tk.after(10, self.delete_memo_file, file)

    def delete_memo_file(self, file: string):
        """
        同期済みメモを設定に応じて削除するか、付箋マークを追加して同期済みにする。
        """
        if self.config.get('delete_memo'):
            self.msg(f'removing file: {file}')
            os.remove(file)
        else:
            self.msg(f'adding fusen to file: {file}')
            with open(file, mode='r', encoding='Shift_JIS') as f:
                content = f.read()
            with open(file, mode='w', encoding='Shift_JIS') as f:
                f.write(f'{FUSEN_STR}\n{content}')
        self.finish_current_memo()

    def finish(self):
        """
        アプリケーションを終了する。
        """
        sys.exit(0)

    # logging
    def msg(self, text: string):
        """
        画面のログ欄へメッセージを追加する。
        """
        self.dialog.append(text)

def main():
    """
    UI、設定、Google Calendar 操作オブジェクトを作成し、アプリケーションを起動する。
    """
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
