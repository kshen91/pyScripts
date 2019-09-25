#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: cylisery@outlook.com

from logging import getLogger
from logging import Formatter
from logging import StreamHandler
from logging import DEBUG

def ConfigureLog(filename):
    log = getLogger(filename)

    formatter = Formatter('[%(asctime)s %(name)s:%(lineno)d][%(levelname)s] %(message)s')
    handler = StreamHandler()
    log.setLevel(DEBUG)
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log
