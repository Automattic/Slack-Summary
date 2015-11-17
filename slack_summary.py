# -*- coding: utf-8 -*-
import requests
import json
from config import *
from ts_config import DEBUG, LOG_FILE, SUMMARY_INTERVALS, TEST_JSON, SUMMS
from slacker import Slacker
import slacker
import logging
import logging.handlers
import uuid
import re
import io
from datetime import timedelta, datetime
if "gensim" in SUMMS:
    from ts_summarizer import TextRankTsSummarizer
if "spacy" in SUMMS:
    from sp_summarizer import SpacyTsSummarizer

class SlackRouter(object):
    expr = re.compile(r'-?(\d{1,3}?)\s+(\S{1,8})\s*(.*)$')
    plural = re.compile(r'([^s]+)s$')
    temporals = ['minute', 'min', 'hour', 'day', 'week']


    def __init__(self, test=False):
        self.test = test
        self.slack = None if self.test else slacker.Slacker(keys["slack"])
        log_level = logging.DEBUG if DEBUG else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.handlers.RotatingFileHandler('./slack_summary_'+LOG_FILE, mode='a', encoding='utf-8', maxBytes=1000000, backupCount=5,)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger = logging.getLogger('slack_summary')
        self.logger.handlers = []
        self.logger.setLevel(log_level)
        self.logger.addHandler(fh)

    def get_response(self, channel_id):
        self.logger.debug(u'Generating summary for channel: %s', channel_id)
        return self.slack.channels.history(channel_id)

    def get_messages(self, channel_id, params):
        """Get messages based upon the interval"""
        tdelt = self.build_delta(params)
        earliest_time = datetime.now()-tdelt
        self.logger.debug(u'Earliest time %s', earliest_time)
        ts = u'{}.999999'.format(earliest_time.strftime("%s"))
        self.logger.debug(u'Channel id %s, TS string %s', channel_id, ts)
        response =  self.slack.channels.history(channel_id, oldest=ts, count=999)
	res = (response.body)
        add_more = True
        msgs = []
        msg_ids = set()
        while add_more:
            if 'max_msgs' in params and params['max_msgs'] <= len(msgs):
                return msgs
            if u'messages' in res:
                new_set = set([msg['ts'] for msg in res['messages']])
                if len(new_set.intersection(msg_ids)) > 0:
                    self.logger.debug(u'Overlap in messages')
                    return msgs
                msgs.extend(res['messages'])
                msg_ids.update(new_set)
                self.logger.debug(u'Got %s messages', len(msgs))
            else:
                return msgs    
            if 'has_more' in res and res['has_more']:
                self.logger.debug(u'Paging for more messages.')
                response =  self.slack.channels.history(channel_id, oldest=ts, latest=res['messages'][-1]['ts'], count=999)
                res = (response.body)
            else:
                self.logger.debug(u'No more messages.')
                add_more = False
        return msgs

    def get_summary(self, **args):
        channel_id = args['channel_id'] if 'channel_id' in args else None
        channel_name = args['channel_name'] if 'channel_name' in args else None
        user_id = args['user_id'] if 'user_id' in args else None
        user_name = args['user_name'] if 'user_name' in args else None
        params = args['params'] if 'params' in args else None
        request_id = uuid.uuid1()
        response = None
        msgs = None
        if self.test:
            with io.open(TEST_JSON, encoding='utf-8') as iot:
                msgs = json.load(iot)[u'messages']
        else:
            msgs = self.get_messages(channel_id, params)
        summ_object = args['summ']
        summ_impl = None
        summary = u''
        if summ_object and "spacy" in SUMMS:
            self.logger.info(u'Using spacy')
            summ_impl = SpacyTsSummarizer()
            summ_impl.set_summarizer(summ_object)
        elif "gensim" in SUMMS:
            self.logger.info(u'Using gensim')
            summ_impl = TextRankTsSummarizer()
        if summ_impl:
            summ_impl.set_channel(channel_name)
            summary = summ_impl.summarize(msgs)
        else:
            self.logger.warn(u'No summarizer was set!')
        self.logger.info(u'Summary request %s user_id: %s', request_id, user_id)
        self.logger.info(u'Summary request %s channel_name: %s', request_id, channel_name)
        self.logger.info(u'Summary request %s parameters: %s', request_id, params)
        self.logger.debug(u'Summary request %s messages: %s', request_id, msgs)
        self.logger.info(u'Summary request %s summary:\n %s', request_id, summary)
	res = u"*Chat Summary:* \n " + summary + "\n \n"
        return res

    def _parse_args(self, commands):   
        units = None
        unit = None
        keywords = None
        if commands and len(commands.strip()) > 1:
            match = SlackRouter.expr.match(commands)
            if match:
                units, unit, keywords = match.groups()
                unit = unit.lower()
                umatch = SlackRouter.plural.match(unit)
                unit = umatch.groups()[0] if umatch else unit
                unit = unit if unit in SlackRouter.temporals else None
                if unit and unit == 'min':
                    unit = 'minute'
                units = int(units) if unit else None
            else:
                keywords = commands
            if not unit:
                units = None
                keywords = commands    
        return unit, units, keywords

    def build_interval(self, commands):
        """Return a single interval for the summarization"""
        unit, units, keywords = self._parse_args(commands)
        interval = {'size': 3}
        if unit:
            interval[unit+'s'] = units
            interval['txt'] = u"Summary for last {} {}:\n".format(units, unit)
        else:
            interval['days'] = 5
            interval['txt'] = u"Summary for last 5 days:\n"
        return [interval]

    def build_delta(self, commands):
        """Return a single interval for the summarization"""
        unit, units, keywords = self._parse_args(commands)
        interval = {'seconds':0, 'minutes': 0, 'hours': 0, 'days': 0, 'weeks': 0}
        if unit:
            interval[unit+'s'] = units
        else:
            interval['days'] = 5
        return timedelta(**interval)
    
