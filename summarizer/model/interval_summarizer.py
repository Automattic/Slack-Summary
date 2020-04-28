"""Summarize on a given interval."""
import logging
import logging.handlers
import os
import re
from datetime import timedelta, datetime

from summarizer.model.ts_config import TS_DEBUG, LOG_PATH, INTERVAL_LOG
from summarizer.model.utils import get_msg_text

logging.basicConfig(level=logging.INFO)


_slack_ts_regex = re.compile(r'(?P<epoch>[1-9][^\.]+).*')  # pylint: disable=invalid-name


class TsSummarizer:
    """Constructs summaries over a set of ranges."""

    f_regexp = re.compile(r'[\n\r\.]|\&[a-z]+;|<http:[^>]+>|\:[^: ]+\:|`{3}[^`]*`{3}')
    archive_link = u'https://a8c.slack.com/archives/{}/p{}'

    def __init__(self, ):
        """Initialize the interval summarizer."""
        self.logger = logging.getLogger(__name__)
        self.channel = None
        self.slack = None
        log_level = logging.DEBUG if TS_DEBUG else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)
        file_handler = logging.handlers.RotatingFileHandler(INTERVAL_LOG, mode='a',
                                                            encoding='utf-8', maxBytes=1000000, backupCount=5)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger = logging.getLogger('interval_summarizer')
        self.logger.handlers = []
        self.logger.addHandler(file_handler)

    def set_channel(self, channel):
        """Set the channel."""
        self.channel = channel

    def set_slack(self, conn):
        """Set the connection."""
        self.slack = conn

    def tagged_sum(self, msg):
        """Tag the summary."""
        user = "USER UNKNOWN"
        if 'user' in msg:
            user = msg['user']
        elif 'bot_id' in msg:
            user = msg['bot_id']
        elif 'username' in msg and msg['username'] == u'bot':
            user = 'bot'
        split_text = get_msg_text(msg).split()
        text = u' '.join(split_text[:30]) + u'...' if len(split_text) > 30 else u' '.join(split_text)
        if self.channel:
            link = TsSummarizer.archive_link.format(self.channel, re.sub(r'\.', u'', msg['ts']))
            text = f'<{link}|{text}'
        return u'@{} <@{}>: {}'.format(ts_to_time(msg['ts']).strftime("%a-%b-%-m-%Y %H:%M:%S"), user, text)


def ts_to_time(slack_ts):
    """Convert a time spec to a datetime.

    Parameters
    ----------
    slack_ts : string EPOCH.ID
    Returns
    -------
    datetime
    """
    return datetime.utcfromtimestamp(int(_slack_ts_regex.search(slack_ts).group('epoch')))


def tspec_to_delta(seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0, weeks: int = 0) -> object:
    """Convert a time spec to time delta."""
    return timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)


def canonicalize(txt):
    """Filter and change text to sentence form."""
    ntxt = TsSummarizer.f_regexp.sub(u'', txt)
    return ntxt.strip() if re.match(r'.*[\.\?\!]\s*$', ntxt) else u'{}.'.format(ntxt.strip())
    # return ntxt if re.match(r'.*[\.\?]$', ntxt) else u'{}.'.format(ntxt)
