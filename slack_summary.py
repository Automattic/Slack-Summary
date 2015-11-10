# -*- coding: utf-8 -*-
import requests
import json
from config import *
from ts_config import DEBUG, LOG_FILE, SUMMARY_INTERVALS, TEST_JSON, SUMMS
from slacker import Slacker
import slacker
import logging
import uuid
import re
import io
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
        fh = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        self.logger = logging.getLogger('slack_summary')
        self.logger.handlers = []
        self.logger.setLevel(log_level)
        self.logger.addHandler(fh)

    def get_response(self, channel_id):
        self.logger.debug(u'Generating summary for channel: %s', channel_id)
        return self.slack.channels.history(channel_id)

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
            response =  self.get_response(channel_id)
	    msgs = (response.body)
            msgs = msgs[u'messages'] if u'messages' in msgs else msgs
        summ_object = args['summ']
        summ_impl = None
        summary = u''
        if summ_object and "spacy" in SUMMS:
            self.logger.info(u'Using spacy')
            summ_impl = SpacyTsSummarizer(self.build_interval(params))
            summ_impl.set_summarizer(summ_object)
        elif "gensim" in SUMMS:
            self.logger.info(u'Using gensim')
            summ_impl = TextRankTsSummarizer(self.build_interval(params))
        if summ_impl:
            summary = summ_impl.report_summary(msgs)
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

