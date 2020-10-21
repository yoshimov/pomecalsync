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
#        root.geometry("600x480")
        root.resizable(0, 0)
        label = tk.Label(root, text="PomeCalSync")
        label.pack()
        text = tkinter.scrolledtext.ScrolledText(root, bg='white', height=20)
        text.place(x=10, y=10)
        self.log = text
        text.pack()
        self.listbox = tk.Listbox(root, selectmode='single', height=4)
        self.listbox.pack()
        start_button = tk.Button(root, text="Sync", command=lambda: self.start())
        start_button.pack()
        cancel_button = tk.Button(root, text="Cancel", command=lambda: self.cancel())
        cancel_button.pack()

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
