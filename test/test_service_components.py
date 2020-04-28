"""Test the top level summarizer service functionality."""
import io
import json
import logging
import logging.handlers
import os
import unittest

from test.conftest import TEST_DATA_PATH, TEST_LOG

import mock
from mock import MagicMock
import pytest
from requests import Response

import summarizer.app.main as main
from summarizer.model.slack_summary import SlackRouter
from summarizer.model.ts_config import DEBUG, CHANNEL_IDS

_slack_connect_skip = pytest.mark.skipif('USE_SLACK_TOKEN' not in os.environ,  # pylint: disable=invalid-name
                                         reason='No slack token available')


class Test(unittest.TestCase):
    """Testing object for the summarizer service."""

    # pylint: disable=too-many-instance-attributes
    def setUp(self):
        """Configure the test."""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_level = logging.DEBUG if DEBUG else logging.INFO
        self.logger = logging.getLogger(__name__)
        self.filehandle = logging.handlers.RotatingFileHandler(TEST_LOG, mode='a',
                                                               encoding='utf-8', maxBytes=1000000, backupCount=5, )
        self.filehandle.setLevel(log_level)
        self.filehandle.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(self.filehandle)
        self.expected = {u'has_more': True, u'messages': [{u'text': u'hmmm...',
                                                           u'ts': u'1414028037.000317',
                                                           u'type': u'message',
                                                           u'user': u'U027LSDDA'}], u'ok': True}
        with io.open(f'{TEST_DATA_PATH}/test-events-elastic.json') as json_file:
            self.larger_expected = json.load(json_file)
        self.myresponse = Response()
        self.myresponse.body = self.expected
        self.myresponse.status_code = 200
        attrs = {'history.return_value': self.myresponse, }
        self.channel_mock = MagicMock(**attrs)
        self.large_response = Response()
        self.large_response.body = self.larger_expected
        self.large_response.status_code = 200
        attrs2 = {'history.return_value': self.large_response, }
        self.channel_mock2 = MagicMock(**attrs2)
        main._app.config['TESTING'] = True  # pylint: disable=protected-access
        self._app = main._app.test_client()  # pylint: disable=protected-access

    @_slack_connect_skip
    @mock.patch('slacker.Slacker')
    def test_summary(self, mock_slack):
        """Test summary command."""
        mock_slack.return_value.channels = self.channel_mock
        router = SlackRouter()
        router_response = router.get_response(CHANNEL_IDS['elasticsearch'])
        self.assertTrue(router_response.body['ok'])
        self.assertTrue(len(router_response.body['messages']) >= 1)

    @mock.patch('slacker.Slacker')
    def test_service(self, mock_slack):
        """Test basic request."""
        mock_slack.return_value.channels = self.channel_mock
        response = self._app.post('/slacktest', data=dict(
            channel_id=CHANNEL_IDS['elasticsearch'],
            channel_name='elasticsearch',
            user_id='user123',
            user_name='bob',
            text='-5 days @bob'
        ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.filehandle)
        self.logger.info("Response is %s", response.data)
        self.assertTrue(response.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_no_command(self, mock_slack):
        """Test if the right thing happens when no command is given."""
        mock_slack.return_value.channels = self.channel_mock2
        response = self._app.post('/slacktest', data=dict(
            channel_id=CHANNEL_IDS['elasticsearch'],
            channel_name='elasticsearch',
            user_id='user123456',
            user_name='bob2',
            text=''
        ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.filehandle)
        self.logger.info("Response is %s", response.data)
        self.assertTrue(response.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_no_text(self, mock_slack):
        "Test if no text field provided."
        mock_slack.return_value.channels = self.channel_mock2
        response = self._app.post('/slacktest', data=dict(
            channel_id=CHANNEL_IDS['elasticsearch'],
            channel_name='elasticsearch',
            user_id='user123456',
            user_name='bob2'
        ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.filehandle)
        self.logger.info("Response is %s", response.data)
        self.assertTrue(response.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_bad_text(self, mock_slack):
        "Test is malformed text provided."
        mock_slack.return_value.channels = self.channel_mock2
        response = self._app.post('/slacktest', data=dict(
            channel_id=CHANNEL_IDS['elasticsearch'],
            channel_name='elasticsearch',
            user_id='user123456',
            user_name='bob2',
            text='adjfalkjldkj adfajldkajflkjadh ndnakdjlkjlkjd'
        ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.filehandle)
        self.logger.info("Response is %s", response.data)
        self.assertTrue(response.status_code == 200)

    @mock.patch('slacker.Slacker')
    def test_service_bad_units(self, mock_slack):
        "Test if bad units."
        mock_slack.return_value.channels = self.channel_mock2
        response = self._app.post('/slacktest', data=dict(
            channel_id=CHANNEL_IDS['elasticsearch'],
            channel_name='elasticsearch',
            user_id='user123456',
            user_name='bob2',
            text='2 adjfalkjldkj adfajldkajflkjadh ndnakdjlkjlkjd'
        ), follow_redirects=True)
        self.logger.handlers = []
        self.logger.addHandler(self.filehandle)
        self.logger.info("Response is %s", response.data)
        self.assertTrue(response.status_code == 200)


if __name__ == '__main__':
    unittest.main()
