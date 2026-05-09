#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, glob, string, re, sys
import datetime
from pcscalendar import PCSCalendar
from pcsconfig import PCSConfig
from pcsdialog import PCSDialog

FUSEN_STR = '★付箋文★'

class PCSFlow:
    """
    PCSControl の各処理ステップを外側から順番に実行する。
    各ステップの実行後、PCSControl の状態を見て次の処理を判断する。
    """
    def __init__(self, tk, control, delay=10):
        self.tk = tk
        self.control = control
        self.delay = delay

    def schedule(self, step, *args):
        self.tk.after(self.delay, step, *args)

    def initialize(self):
        self.schedule(self._load_config)

    def _load_config(self):
        self.control.load_config()
        self.schedule(self._get_credentials)

    def _get_credentials(self):
        self.control.get_credentials()
        if self.control.has_credentials():
            self.schedule(self._get_calendars)

    def _get_calendars(self):
        self.control.get_calendars()

    def start_sync(self):
        self.schedule(self._prepare_sync)

    def _prepare_sync(self):
        self.control.prepare_sync()
        if self.control.is_sync_ready():
            self.schedule(self._scan_files)

    def _scan_files(self):
        self.control.scan_files()
        if self.control.has_scanned_files():
            self.schedule(self._sync_next_memo)

    def _sync_next_memo(self):
        self.control.prepare_next_memo()
        if self.control.has_current_memo():
            self.schedule(self._sync_calendar_memo)
        else:
            self.control.msg('finished sync.')

    def _sync_calendar_memo(self):
        self.control.sync_calendar_memo()
        if self.control.should_delete_current_memo():
            self.schedule(self._delete_memo_file)
        else:
            self.schedule(self._sync_next_memo)

    def _delete_memo_file(self):
        self.control.delete_current_memo_file()
        self.schedule(self._sync_next_memo)

class PCSControl:
    tk = None
    dialog = None
    config = None
    cal = None
    flow = None
    calendar_id = None
    memo_files = None
    current_memo_file = None
    calendar_memo_created = False
    after_date = None

    def __init__(self, dialog: PCSDialog):
        """
        UI ダイアログを受け取り、操作を制御するための参照を初期化する。
        """
        self.dialog = dialog
        self.tk = self.dialog.get_tk()
        self.dialog.set_control(self)

    def set_flow(self, flow: PCSFlow):
        """
        処理の進行を担当する外側のフロー実行器を登録する。
        """
        self.flow = flow

    def set_config(self, config: PCSConfig):
        """
        設定管理オブジェクトを登録する。
        """
        self.config = config

    def load_config(self):
        """
        保存済み設定を読み込み、画面上の設定項目へ反映する。
        """
        self.config.load()
        self.dialog.set_delete_memo(self.config.get('delete_memo', True))
        self.dialog.set_days(self.config.get('keep_days', 3))

    def set_cal(self, cal: PCSCalendar):
        """
        Google Calendar 操作用オブジェクトを登録する。
        """
        self.cal = cal

    def get_credentials(self):
        """
        Google Calendar API の認証情報を取得する。
        """
        self.cal.get_credentials()
        if not self.has_credentials():
            self.msg('fail to get credentials.')

    def has_credentials(self):
        """
        Google Calendar API の認証情報を取得済みかを返す。
        """
        return self.cal.has_credentials()

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
                self.dialog.select_calendar(sid)
        else:
            self.msg('fail to get calendar list.')

    def open_config(self):
        """
        将来の設定画面用に残されているプレースホルダー。
        """
        pass    

    # start sync with google calendar
    def sync(self):
        """
        UI から同期を開始する。
        """
        self.flow.start_sync()

    def prepare_sync(self):
        """
        画面の選択内容と設定値を保存する。
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

    def is_sync_ready(self):
        """
        同期開始に必要な情報が揃っているかを返す。
        """
        return bool(self.calendar_id)

    def scan_files(self):
        """
        接続されているドライブから Pomera_memo フォルダを探し、同期対象ファイルを集める。
        """
        self.memo_files = None
        available_drives = [f'{d}:' for d in string.ascii_uppercase if os.path.exists(f'{d}:')]
        # scan pomera memo folder
        pdrive = None
        for d in available_drives:
            if os.path.exists(f'{d}/Pomera_memo'):
                self.msg(f'Pomera found in drive {d}')
                pdrive = d
        if pdrive:
            self.memo_files = glob.glob(f'{pdrive}/Pomera_memo/**/*.txt', recursive=True)
        else:
            self.msg('Pomera not found.')

    def has_scanned_files(self):
        """
        Pomera_memo フォルダのスキャンが終わっているかを返す。
        """
        return self.memo_files is not None

    def prepare_next_memo(self):
        """
        同期対象のメモを1件取り出し、現在処理中のメモとして保持する。
        """
        self.current_memo_file = None
        self.calendar_memo_created = False
        if not self.memo_files:
            return
        self.current_memo_file = self.memo_files.pop(0)

    def has_current_memo(self):
        """
        現在処理中のメモがあるかを返す。
        """
        return bool(self.current_memo_file)

    def sync_calendar_memo(self):
        """
        メモファイル名から日付を読み取り、条件に合うメモを Google Calendar に登録する。
        """
        self.calendar_memo_created = False
        file = self.current_memo_file
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
        self.calendar_memo_created = True

    def should_delete_current_memo(self):
        """
        現在のメモがカレンダーへ登録済みで、同期済み処理へ進めるかを返す。
        """
        return self.calendar_memo_created

    def delete_current_memo_file(self):
        """
        同期済みメモを設定に応じて削除するか、付箋マークを追加して同期済みにする。
        """
        file = self.current_memo_file
        if self.config.get('delete_memo'):
            self.msg(f'removing file: {file}')
            os.remove(file)
        else:
            self.msg(f'adding fusen to file: {file}')
            with open(file, mode='r', encoding='Shift_JIS') as f:
                content = f.read()
            with open(file, mode='w', encoding='Shift_JIS') as f:
                f.write(f'{FUSEN_STR}\n{content}')
        self.current_memo_file = None
        self.calendar_memo_created = False

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
    flow = PCSFlow(dialog.get_tk(), control)
    control.set_flow(flow)
    flow.initialize()
    dialog.show()

if __name__ == "__main__":
    # execute only if run as a script
    main()
