import unittest
import mock
from mock import MagicMock, patch
from slacker import Slacker
import slacker
import main
from slack_summary import SlackRouter
from requests import Response
import config
from ts_config import DEBUG, LOG_FILE
import sys
import logging
import json
import io

class Test(unittest.TestCase):
    def setUp(self):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_level = logging.DEBUG if DEBUG else logging.INFO
        self.logger = logging.getLogger(__name__)
        self.fh = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        self.fh.setLevel(log_level)
        self.fh.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.expected = {u'has_more': True, u'messages': [{u'text': u'hmmm...',
                       u'ts': u'1414028037.000317',
                       u'type': u'message',
                       u'user': u'U027LSDDA'}], u'ok': True}
        with io.open('./data/test-events-elastic.json', encoding='utf-8') as jf:
            self.larger_expected = json.load(jf)
        self.myresponse = Response()
        self.myresponse.body = self.expected
        self.myresponse.status_code = 200
        attrs = {'history.return_value': self.myresponse,}
        self.channel_mock = MagicMock(**attrs)
        self.large_response = Response()
        self.large_response.body = self.larger_expected
        self.large_response.status_code = 200
        attrs2 = {'history.return_value': self.large_response,}
        self.channel_mock2 = MagicMock(**attrs2)
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()

    def tearDown(self):
        pass
    
    @mock.patch('slacker.Slacker')
    def test_summary(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock
        sr = SlackRouter()
        self.assertTrue(sr.get_response('achannell') == self.myresponse)

    @mock.patch('slacker.Slacker')
    def test_service(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123',
                    user_name='bob',
                    text='-5 days @bob'
                ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_lr(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock2
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123456',
                    user_name='bob2',
                    text='-2 days @bob'
                ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_no_command(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock2
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123456',
                    user_name='bob2',
                    text=''
                ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_no_text(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock2
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123456',
                    user_name='bob2'
                ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_bad_text(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock2
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123456',
                    user_name='bob2',
                    text='adjfalkjldkj adfajldkajflkjadh ndnakdjlkjlkjd'
                ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_bad_units(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock2
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123456',
                    user_name='bob2',
                    text='2 adjfalkjldkj adfajldkajflkjadh ndnakdjlkjlkjd'
                ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_gensim(self, mock_slack):
        mock_slack.return_value.channels = self.channel_mock2
        rv = self.app.post('/slack', data=dict(
                    channel_id='achannel',
                    channel_name='achannel',
                    user_id='user123456',
                    user_name='bob2',
                    text='2 days gensim'
                ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.fh)
        self.logger.info("Response is %s", rv.data)
        self.assertTrue(rv.status_code == 200)
        

if __name__ == '__main__':
    unittest.main()
