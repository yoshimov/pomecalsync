#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.scrolledtext
import sys

# class of user interface
class PCSDialog:
    dialog = None
    control = None
    log = None
    listbox = None
    calendar_list = None

    def __init__(self):
        root = tk.Tk()
        self.dialog = root
#        root.attributes("-topmost", True)
        root.title("PomeCalSync")
        root.resizable(0, 0)
        # log area
        text = tkinter.scrolledtext.ScrolledText(root, bg='white', height=20)
        text.pack(anchor=tk.CENTER, padx = 10)
        self.log = text
        frame = tk.Frame(root)
        frame.pack(anchor=tk.CENTER, pady = 10)
        # calendar list
        label = tk.Label(frame, text='Google Calendars:')
        label.pack(side=tk.LEFT)
        self.listbox = tk.Listbox(frame, selectmode='single', height=4)
        self.listbox.pack(side=tk.LEFT)
        bar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        bar.pack(side=tk.LEFT, fill=tk.Y)
        frame = tk.Frame(root)
        frame.pack(anchor=tk.CENTER, pady=10)
        # buttons
        start_button = tk.Button(frame, text="Start Sync", command=lambda: self.start())
        start_button.pack(side=tk.LEFT, padx = 10)
        cancel_button = tk.Button(frame, text="Cancel/Finish", command=lambda: self.cancel())
        cancel_button.pack(side=tk.LEFT, padx = 10)

    def set_control(self, control):
        self.control = control

    def start(self):
        self.control.sync()

    def cancel(self):
        self.control.finish()

    def get_tk(self):
        return self.dialog

    def show(self):
        """
        call tk.mainloop()
        """
        self.dialog.mainloop()

    def append(self, text):
        # append log
        self.log.insert(tk.END, text + '\n')
        # scroll to end
        self.log.see("end")
#        self.log.pack()
        print('append ' + text)

    def set_calendar_list(self, list):
        self.calendar_list = list
#        self.listbox.delete()
        for item in list:
            self.listbox.insert(tk.END, item['summary'])

    def select_calendar(self, id):
        index = 0
        for item in self.calendar_list:
            if item['id'] == id:
                break
            index += 1
        self.listbox.select_set(index)
        self.listbox.see(index)

    def get_selected_calendar(self):
        index = 0
        for item in self.calendar_list:
            if self.listbox.selection_includes(index):
                break
            index += 1
        if index < len(self.calendar_list):
            return self.calendar_list[index]['id']
        return None
