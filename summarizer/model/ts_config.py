"""Provide constants."""
import os
import json
import io
from pkg_resources import resource_filename


SUMMARY_INTERVALS = [{'days': 5, 'size': 2}, ]
TEST_DATA_PATH = resource_filename(__name__, '../../data/test')
TEST_JSON = json.load(io.open(f"{TEST_DATA_PATH}/test-events.json"))['messages']
CHANNELS = ['api-test', 'calypso', 'games', 'happiness', 'hg', 'jetpack',
            'jetpackfuel', 'livechat', 'tickets', 'vip']
CHANNEL_IDS = {'vip': 'C029H6R8C', 'data-science': 'C5RPL6XBP', 'calypso': 'C02DQP0FP', 'elasticsearch': 'C02JQ08G0'}
ROOT_PATH = os.getcwd()
CONFIG_PATH = os.path.join(ROOT_PATH, 'configs')
LOG_PATH = resource_filename(__name__, '../logs')
TS_DEBUG = True
TS_LOG = os.path.join(LOG_PATH, 'ts_summ.log')
INTERVAL_LOG = os.path.join(LOG_PATH, 'ts_summ_interval.log')
SLACK_ROUTER_LOG = os.path.join(LOG_PATH, 'slack_summary.log')
SPACY_SUMMARIZER_LOG = os.path.join(LOG_PATH, 'spacy_summ.log')
DEBUG = True
LOG_FILE = os.path.join(LOG_PATH, 'summary.log')
TEMPORAL_VALUES = {'seconds', 'minutes', 'hours', 'days', 'weeks'}
