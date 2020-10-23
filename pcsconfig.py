#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import yaml

# class of configuration management
class PCSConfig:
    filename = "pcsconfig.yml"
    config = {}
    log = None

    def __init__(self, log):
        self.log = log

    def load(self):
        if os.path.exists(self.filename):
            self.log.msg('loading config file')
            with open(self.filename, mode='r', encoding='utf-8') as yml:
                self.config = yaml.safe_load(yml)
        else:
            self.log.msg('config file not found')

    def get(self, name: string, value = None) -> any:
        if name in self.config:
            return self.config[name]
        if value:
            self.set(name, value)
            return value
        return None

    def set(self, name: string, value):
        if not name in self.config or self.config[name] != value:
            self.config[name] = value
            self.save()

    def save(self):
        with open(self.filename, mode='w', encoding='utf-8') as yml:
            yaml.dump(self.config, yml, encoding='utf-8', allow_unicode=True)
