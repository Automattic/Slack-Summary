"""Test the spacy based summarizer using hypothesis to generate test cases."""
import glob
import io
import json
import logging
import os
import random
import unittest
from test.conftest import TEST_DATA_PATH, TEST_JSON_MSGS, TEST_JSON_MSGS_ELASTIC
import pytest
from hypothesis import given, settings
from hypothesis.strategies import sampled_from, lists, integers

from summarizer.model.lsa_summarizer import LsaSummarizer
from summarizer.model.sp_summarizer import SpacyTsSummarizer
from summarizer.model.ts_config import DEBUG, CHANNELS

_logger = logging.getLogger()  # pylint: disable=invalid-name
_logger.level = logging.DEBUG if DEBUG else logging.INFO

_slack_logs_skip = pytest.mark.skipif('USE_SLACK_LOGS' not in os.environ,  # pylint: disable=invalid-name
                                      reason='No slack log files present')


def _read_log_dir(fdir):
    coll = []
    for jfile in glob.glob(f'{TEST_DATA_PATH}/slack-logs-2/{fdir}/*.json'):
        coll += json.load(io.open(jfile, ))
    return coll


class TestSummarize(unittest.TestCase):
    """Summarizer testing object."""
    summ = SpacyTsSummarizer()
    summ.set_summarizer(LsaSummarizer())

    @given(
        lists(elements=sampled_from(TEST_JSON_MSGS), min_size=3),
        integers(min_value=1, max_value=20)
    )
    @settings(deadline=1000, max_examples=20)
    def test_spacy_small_days(self, smp_msgs, days):
        """Generate something for N day interval"""
        _logger.info("Input is %s", smp_msgs)
        asd = {'days': days, 'size': 3, 'txt': u'Summary for first {} days:\n'.format(days)}
        # TestSummarize.summ.set_interval()
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        _logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry.split('\n')) >= 1)

    @given(
        lists(elements=sampled_from(TEST_JSON_MSGS_ELASTIC), min_size=12),
        integers(min_value=1, max_value=20)
    )
    @settings(deadline=1000, max_examples=20)
    def test_spacy_med_days(self, smp_msgs, days):
        """Generate something for N day interval"""
        _logger.info("Input is %s", smp_msgs)
        asd = {'days': days, 'size': 3, 'txt': f'Summary for first {days} days:\n'}
        # TestSummarize.summ.set_interval(asd)
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        _logger.debug("Summary is %s", sumry)
        print(f"Summary is {sumry}")
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry.split('\n')) >= 1)

    @_slack_logs_skip
    @given(
        integers(min_value=2, max_value=20)
    )
    @settings(deadline=1000, max_examples=20)
    def test_spacy_large_days(self, days):
        """Generate something for N day interval"""
        channel, ssamp = random.choice([[fdir, _read_log_dir(fdir)] for fdir in CHANNELS])
        samp = ssamp[random.randint(1, len(ssamp) - 2):]
        _logger.info("Input is segment is %s", samp)
        asd = {'days': days, 'size': 3, 'txt': f'Summary for first {days} days:\n'}
        TestSummarize.summ.set_channel(channel)
        sumry = TestSummarize.summ.summarize(samp, range_spec=asd)
        _logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry.split('\n')) >= 1)

    @given(lists(elements=sampled_from(TEST_JSON_MSGS), min_size=1),
           integers(min_value=2, max_value=24)
           )
    @settings(deadline=1000, max_examples=20)
    def test_spacy_small_hours(self, smp_msgs, hours):
        """Generate something for N hour intervals"""
        _logger.info("Input is %s", smp_msgs)
        asd = {'hours': hours, 'size': 3, 'txt': u'Summary for first {} hours:\n'.format(hours)}
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        _logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry.split('\n')) >= 1)

    @given(lists(elements=sampled_from(TEST_JSON_MSGS_ELASTIC), min_size=1),
           integers(min_value=1, max_value=24)
           )
    @settings(deadline=1000, max_examples=20)
    def test_spacy_med_hours(self, smp_msgs, hours):
        """Generate something for N hour intervals"""
        _logger.info("Input is %s", smp_msgs)
        asd = {'hours': hours, 'size': 3, 'txt': u'Summary for first {} hours:\n'.format(hours)}
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        _logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry.split('\n')) >= 1)

    @_slack_logs_skip
    @given(
        integers(min_value=2, max_value=24)
    )
    @settings(deadline=1000, max_examples=20)
    def test_spacy_large_hours(self, hours):
        """Generate something for N hour intervals"""
        channel, ssamp = random.choice([[fdir, _read_log_dir(fdir)] for fdir in CHANNELS])
        _logger.info("Length of input is segment is %s", len(ssamp))
        samp = ssamp[random.randint(1, len(ssamp) - 2):]
        TestSummarize.summ.set_channel(channel)
        _logger.info("Input is segment is %s", samp)
        asd = {'hours': hours, 'size': 3, 'txt': u'Summary for first {} hours:\n'.format(hours)}
        sumry = TestSummarize.summ.summarize(samp, range_spec=asd)
        _logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry.split('\n')) >= 1)


if __name__ == '__main__':
    unittest.main()
