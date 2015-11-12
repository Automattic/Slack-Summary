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
    
    def __init__(self, seconds=0, minutes=0, hours=0, days=0, weeks=0, size=10, txt=u"Summary for interval: \n"):
        self.intv = timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)
        self.size = size
        self.txt = txt

    def contains(self, ts_start, msg_ts):
        """
        Parameters
        start_ts : string in form EPOCH.ID start of interval
        msg_ts : string in form EPOCH.ID message
        Return
        boolean
        """
        return self.in_interval(ts_to_time(ts_start), ts_to_time(msg_ts))

    def in_interval(self, d0, d1):
        return d1 <= d0 and d1 >= d0 - self.intv 
    
class TsSummarizer(object):
    """Constructs summaries over a set of ranges"""
    flrg = re.compile(r'[\n\r\.]|\&[a-z]+;|<http:[^>]+>|\:[^: ]+\:|`{3}[^`]*`{3}')
    archive_link = u'https://a8c.slack.com/archives/{}/p{}'
    def __init__(self, ispecs):
        self.intervals = map(lambda ispec: IntervalSpec(**ispec), ispecs)
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

    def summarize(self, messages):
        """ Produce the input """
        return [self.summarize_segment(msg_seg) for msg_seg in self.segment_messages(messages)]

    def report_summary(self, messages):
        """The interval summaries are joined."""
        return '\n'.join(self.summarize(messages))

    def set_interval(self, ispecs):
        self.intervals = map(lambda ispec: IntervalSpec(**ispec), ispecs)

    def set_channel(self, channel):
        self.channel = channel

    def set_slack(self, conn):
        self.slack = conn

    def summarize_segment(self, msg_seg):
        """Call the summarizer that is used."""
        return msg_seg

    def tagged_sum(self, msg):
        user = "USER UNKNOWN"
        if 'user' in msg:
            user = msg['user']
        elif 'bot_id' in msg:
            user = msg['bot_id']
        split_text = get_msg_text(msg).split()
        text = u' '.join(split_text[:30])+u'...' if len(split_text) > 30 else u' '.join(split_text)
        if self.channel:
            link = TsSummarizer.archive_link.format(self.channel, re.sub(r'\.',u'',msg['ts']))
            text = u'<'+link+'|'+text+'>'
        return u'@{} <@{}>: {}'.format(ts_to_time(msg['ts']).strftime("%a-%b-%-m-%Y %H:%M:%S"), user,  text)
    
    def segment_messages(self, messages):
        """Create message bins.
        Parameters
        messages : [ dict ] a list of messages
        Return
        [ [ dict ] ] a list of messages segmented
        """
        self.logger.debug("Running the segmenter")
        ts = None
        interval_idx = 0
        msg_intervals = []
        idx_start = 0
        idx_end = 0
        interval_start = None
        msgs = [msg for msg in messages if u'attachments' in msg or u'text' in msg ]
        if len(msgs) == 0:
            return [(self.intervals[0].size, None, self.intervals[0].txt)]
        if len(msgs) == 1:
            return [(self.intervals[0].size, msgs, self.intervals[0].txt)]
        smessages = sorted(msgs, reverse=True, key=lambda msg: ts_to_time(msg['ts']))
        for (idx, msg) in enumerate(smessages):
            idx_end = idx
            self.logger.debug("Checking index %s message %s", idx, msg)
            if not interval_start:
                interval_start = msg['ts']
                self.logger.debug("Setting the initial interval to %s", interval_start)
            if interval_idx == len(self.intervals):
                self.logger.debug("Reached final interval now")
                self.logger.debug("Events at index %s message %s", idx, msg)
                break
            if not self.in_interval(interval_start, msg['ts'], interval_idx):
                self.logger.debug("Starting new interval at %s", msg['ts'])
                msg_intervals.append((self.intervals[interval_idx].size, smessages[idx_start:idx_end], self.intervals[interval_idx].txt))
                idx_start = idx
                interval_idx += 1
                interval_start = msg['ts']
            elif idx == len(messages) - 1:
                msg_intervals.append((self.intervals[interval_idx].size, smessages[idx_start:idx_end+1], self.intervals[interval_idx].txt))
        self.logger.debug("Computed intervals %s", msg_intervals)
        return msg_intervals

    def in_interval(self, istart, msg_ts, idx):
        """Check if the msg is inside the given interval
        Parmeters
        start_ts : string a Slack timestamp EPOCH.ID
        msg_ts : string a Slack timestamp EPOCH.ID
        Returns
        boolean
        """
        self.logger.debug("Checking to see if %s is between %s and end", msg_ts, istart)
        return self.intervals[idx].contains(istart, msg_ts)

def ts_to_time(slack_ts):
    """
    Parameters
    slack_ts : string EPOCH.ID
    Return
    datetime
    """
    return datetime.utcfromtimestamp(long(IntervalSpec.slk_ts.search(slack_ts).group('epoch')))

def canonicalize(txt):
    """Filter and change text to sentece form"""
    ntxt = TsSummarizer.flrg.sub(u'', txt)
    return ntxt.strip() if re.match(r'.*[\.\?\!]\s*$', ntxt) else u'{}.'.format(ntxt.strip())
    #return ntxt if re.match(r'.*[\.\?]$', ntxt) else u'{}.'.format(ntxt)

