# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import (timedelta, datetime)
import re
import logging
import logging.handlers
import sys
import json
import io
from ts_config import TS_DEBUG, TS_LOG
import glob
from utils import get_msg_text
from slacker import Slacker
from config import keys

logging.basicConfig(level=logging.INFO)

class IntervalSpec(object):
    slk_ts = re.compile(r'(?P<epoch>[1-9][^\.]+).*')
    
class TsSummarizer(object):
    """Constructs summaries over a set of ranges"""
    flrg = re.compile(r'[\n\r\.]|\&[a-z]+;|<http:[^>]+>|\:[^: ]+\:|`{3}[^`]*`{3}')
    archive_link = u'https://a8c.slack.com/archives/{}/p{}'
    def __init__(self, ):
        self.logger = logging.getLogger(__name__)
        self.channel = None
        self.slack = None
        log_level = logging.DEBUG if TS_DEBUG else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.handlers.RotatingFileHandler('./interval_'+TS_LOG, mode='a', encoding='utf-8', maxBytes=1000000, backupCount=5)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger = logging.getLogger('interval_summarizer')
        self.logger.handlers = []
        self.logger.addHandler(fh)

    def summarize(self, messages, range_spec=None):
        """ Produce the input """
        return messages

    def report_summary(self, messages, range_spec=None):
        """The interval summaries are joined."""
        return '\n'.join(self.summarize(messages, range_spec=range_spec))

    def set_channel(self, channel):
        self.channel = channel

    def set_slack(self, conn):
        self.slack = conn

    def tagged_sum(self, msg):
        user = "USER UNKNOWN"
        if 'user' in msg:
            user = msg['user']
        elif 'bot_id' in msg:
            user = msg['bot_id']
        elif 'username' in msg and msg['username'] == u'bot':
            user = 'bot'
        split_text = get_msg_text(msg).split()
        text = u' '.join(split_text[:30])+u'...' if len(split_text) > 30 else u' '.join(split_text)
        if self.channel:
            link = TsSummarizer.archive_link.format(self.channel, re.sub(r'\.',u'',msg['ts']))
            text = u'<'+link+'|'+text+'>'
        return u'@{} <@{}>: {}'.format(ts_to_time(msg['ts']).strftime("%a-%b-%-m-%Y %H:%M:%S"), user,  text)
    

def ts_to_time(slack_ts):
    """
    Parameters
    slack_ts : string EPOCH.ID
    Return
    datetime
    """
    return datetime.utcfromtimestamp(long(IntervalSpec.slk_ts.search(slack_ts).group('epoch')))

def tspec_to_delta(seconds=0, minutes= 0, hours= 0, days= 0, weeks=0, **args):
    return timedelta(seconds= seconds, minutes= minutes, hours= hours, days= days, weeks=weeks)

def canonicalize(txt):
    """Filter and change text to sentece form"""
    ntxt = TsSummarizer.flrg.sub(u'', txt)
    return ntxt.strip() if re.match(r'.*[\.\?\!]\s*$', ntxt) else u'{}.'.format(ntxt.strip())
    #return ntxt if re.match(r'.*[\.\?]$', ntxt) else u'{}.'.format(ntxt)

