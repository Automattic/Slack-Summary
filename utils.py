# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

class ItemsCount(object):
    def __init__(self, value):
        self._value = value
        self.string_types = (str, unicode)

    def __call__(self, sequence):
        if isinstance(self._value, self.string_types):
            if self._value.endswith("%"):
                total_count = len(sequence)
                percentage = int(self._value[:-1])
                # at least one sentence should be chosen
                count = max(1, total_count*percentage // 100)
                return sequence[:count]
            else:
                return sequence[:int(self._value)]
        elif isinstance(self._value, (int, float)):
            return sequence[:int(self._value)]
        else:
            ValueError("Unsuported value of items count '%s'." % self._value)

    def __repr__(self):
        return to_string("<ItemsCount: %r>" % self._value)

def maybe_get(cont, key, default=None):
    return cont[key] if key in cont else default

def get_msg_text(msg):
    """Pull the appropriate text from the message"""
    if 'text' in msg and len(msg['text']) > 0:
        return msg['text']
    if 'attachments' in msg:
        ats = msg['attachments']
        if len(ats) > 0:
            at = ats[0]
            att_text = []
            if 'title' in at:
                att_text.append(at['title'])
            if 'text' in at:
                att_text.append(at['text'])
            max_text = max(att_text, key=lambda txt: len(txt))
            if len(max_text) > 0:
                return max_text
    return u""
            
