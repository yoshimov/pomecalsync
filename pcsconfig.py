#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml

# class of configuration management
class PCSConfig:
    filename = "pcsconfig.yml"
    config = {}

    def __init__(self, log):
        self.log = log
    
    def load(self):
        if os.path.exists(self.filename):
            self.log.msg('loading config file')
            with open(self.filename, mode='r', encoding='utf-8') as yml:
                self.config = yaml.safe_load(yml)
        else:
            self.log.msg('config file not found')

    def get(self, name):
        if name in self.config:
            return self.config[name]
        return None

    def set(self, name, value):
        self.config[name] = value

    def save(self):
        with open(self.filename, mode='w', encoding='utf-8') as yml:
            yaml.dump(self.config, yml, encoding='utf-8', allow_unicode=True)
