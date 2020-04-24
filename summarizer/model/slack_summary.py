"""Provide the main summarization functionality."""
import logging
import logging.handlers
import re
import uuid
from datetime import timedelta, datetime

from slacker import Slacker

from summarizer.config import KEYS
from summarizer.model.sp_summarizer import SpacyTsSummarizer
from summarizer.model.ts_config import DEBUG, LOG_FILE, TEST_JSON


class SlackRouter:
    """Summarize a thread."""

    expr = re.compile(r'-?(\d{1,3}?)\s+(\S{1,8})\s*(.*)$')
    plural = re.compile(r'([^s]+)s$')
    temporals = ['minute', 'min', 'hour', 'day', 'week']

    def __init__(self, test=False):
        """Initialize the router."""
        self.test = test
        self.slack = None if self.test else Slacker(KEYS['slack'])
        log_level = logging.DEBUG if DEBUG else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.handlers.RotatingFileHandler('./slack_summary_' + LOG_FILE, mode='a', encoding='utf-8',
                                                            maxBytes=1000000, backupCount=5, )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger = logging.getLogger('slack_summary')
        self.logger.handlers = []
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)

    def get_response(self, channel_id):
        """Return a response."""
        self.logger.debug(u'Generating summary for channel: %s', channel_id)
        return self.slack.conversations.history(channel_id)

    def get_messages(self, channel_id, params):
        """Get messages based upon the interval."""
        tdelt = build_delta(params)
        earliest_time = datetime.now() - tdelt
        self.logger.debug(u'Earliest time %s', earliest_time)
        time_stamp = u'{}.999999'.format(earliest_time.strftime("%s"))
        self.logger.debug(u'Channel id %s, TS string %s', channel_id, time_stamp)
        response = self.slack.conversations.history(channel_id, oldest=time_stamp, limit=999)
        res = (response.body)
        add_more = True
        msgs = []
        msg_ids = set()
        while add_more:
            if 'max_msgs' in params and params['max_msgs'] <= len(msgs):
                return msgs
            if u'messages' in res:
                new_lol = [msg['ts'] for msg in res['messages']]
                new_set = set(new_lol)
                if new_set.intersection(msg_ids):
                    self.logger.debug(u'Overlap in messages')
                    return msgs
                msgs.extend(res['messages'])
                msg_ids.update(new_set)
                self.logger.debug(u'Got %s messages', len(msgs))
            else:
                return msgs
            if 'has_more' in res and res['has_more']:
                self.logger.debug(u'Paging for more messages.')
                response = self.slack.conversations.history(channel_id, oldest=time_stamp,
                                                            latest=res['messages'][-1]['ts'], limit=999)
                res = (response.body)
            else:
                self.logger.debug(u'No more messages.')
                add_more = False
        return msgs

    def get_summary(self, **args):
        """Generate the summary."""
        channel_id = args['channel_id'] if 'channel_id' in args else None
        channel_name = args['channel_name'] if 'channel_name' in args else None
        user_id = args['user_id'] if 'user_id' in args else None
        params = args['params'] if 'params' in args else None
        request_id = uuid.uuid1()
        if self.test:
            msgs = TEST_JSON
        else:
            msgs = self.get_messages(channel_id, params)
        summ_object = args['summ']
        summary = u''
        self.logger.info(u'Using spacy')
        summ_impl = SpacyTsSummarizer()
        summ_impl.set_summarizer(summ_object)
        if summ_impl:
            summ_impl.set_channel(channel_name)
            summary = summ_impl.summarize(msgs)
        else:
            self.logger.warning('No summarizer was set!')
        self.logger.info('Summary request %s user_id: %s', request_id, user_id)
        self.logger.info('Summary request %s channel_name: %s', request_id, channel_name)
        self.logger.info('Summary request %s parameters: %s', request_id, params)
        self.logger.debug('Summary request %s messages: %s', request_id, msgs)
        self.logger.info('Summary request %s summary:\n %s', request_id, summary)
        return f'*Chat Summary:* \n {summary}  \n \n'


def build_interval(commands):
    """Return a single interval for the summarization."""
    unit, units = _parse_args(commands)
    interval = {'size': 3}
    if unit:
        interval[unit + 's'] = units
        interval['txt'] = f'Summary for last {units} {unit}:\n'
    else:
        interval['days'] = 5
        interval['txt'] = f'Summary for last 5 days:\n'
    return [interval]


def build_delta(commands):
    """Return a single interval for the summarization."""
    unit, units = _parse_args(commands)
    interval = {'seconds': 0, 'minutes': 0, 'hours': 0, 'days': 0, 'weeks': 0}
    if unit:
        interval[unit + 's'] = units
    else:
        interval['days'] = 5
    return timedelta(**interval)


def _parse_args(commands):
    units = None
    unit = None
    if commands and len(commands.strip()) > 1:
        match = SlackRouter.expr.match(commands)
        if match:
            units, unit, _ = match.groups()
            unit = unit.lower()
            umatch = SlackRouter.plural.match(unit)
            unit = umatch.groups()[0] if umatch else unit
            unit = unit if unit in SlackRouter.temporals else None
            if unit and unit == 'min':
                unit = 'minute'
            units = int(units) if unit else None
        if not unit:
            units = None
    return unit, units
