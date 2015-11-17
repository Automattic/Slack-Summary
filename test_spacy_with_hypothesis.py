import unittest
import json
import io
from sp_summarizer import (SpacyTsSummarizer)
import hypothesis.settings as hs
from interval_summarizer import (IntervalSpec, TsSummarizer,
                                 ts_to_time)
import lsa
from datetime import datetime
import logging
import sys
import config
from ts_config import DEBUG
from hypothesis import given
from hypothesis.strategies import (sampled_from, lists, just, integers)
import glob
import random
logger = logging.getLogger()
logger.level = logging.DEBUG if DEBUG else logging.INFO
test_json_msgs = json.load(io.open("./test-events.json", encoding='utf-8'))['messages']
test_json_msgs_c2 = json.load(io.open("./data/test-events-elastic.json", encoding='utf-8'))['messages']
test_json_msgs_c3 = []

def read_dir(fdir):
    coll = []
    for jfile in glob.glob('./data/slack-logs-2/{}/*.json'.format(fdir)):
        coll += json.load(io.open(jfile, encoding='utf-8'))
    return coll

test_json_msgs_c3 = [(fdir, read_dir(fdir)) for fdir in ['api-test',  'calypso',  'games',  'happiness',  'hg',  'jetpack',  'jetpackfuel',  'livechat',  'tickets',  'vip']]

class TestSummarize(unittest.TestCase):

    test_msgs = test_json_msgs
    summ = SpacyTsSummarizer()
    summ.set_summarizer(lsa.LsaSummarizer())


    @given(
        lists(elements=sampled_from(test_json_msgs), min_size=3),
        integers(min_value=1, max_value=20), settings=hs.Settings(timeout=1000)
    )
    def test_text_rank_summarization_ds1_days(self, smp_msgs, days):
        """Generate something for N day interval"""
        logger.info("Input is %s", smp_msgs)
        asd = {'days': days, 'size' : 3, 'txt' : u'Summary for first {} days:\n'.format(days)}
        #TestSummarize.summ.set_interval()
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry) >= 1)
        #self.assertTrue(len(sumry) <= 3)
        # Length of summary is less than or equal to the original length
        #self.assertTrue(len(sumry) <= len(smp_msgs))
        # Each message in the summary must correspond to a message


    @given(
        lists(elements=sampled_from(test_json_msgs_c2), min_size=12),
        integers(min_value=1, max_value=20), settings=hs.Settings(timeout=1000)
    )
    def test_text_rank_summarization_ds2_days(self, smp_msgs, days):
        """Generate something for N day interval"""
        logger.info("Input is %s", smp_msgs)
        asd = {'days': days, 'size' : 3, 'txt' : u'Summary for first {} days:\n'.format(days)}
        #TestSummarize.summ.set_interval(asd)
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry) >= 1)
        #self.assertTrue(len(sumry) <= 3)
        # Length of summary is less than or equal to the original length
        #self.assertTrue(len(sumry) <= len(smp_msgs))
        # Each message in the summary must correspond to a message


    @given(
        integers(min_value=1, max_value=1000),
        integers(min_value=1, max_value=20), settings=hs.Settings(timeout=1000)
    )
    def test_text_rank_summarization_ds3_days(self, sampsize, days):
        """Generate something for N day interval"""
        channel, ssamp = random.choice(test_json_msgs_c3)
        samp = ssamp[random.randint(1,len(ssamp)-2):]
        logger.info("Input is segment is %s", samp)
        asd = {'days': days, 'size' : 3, 'txt' : u'Summary for first {} days:\n'.format(days)}
        #TestSummarize.summ.set_interval()
        TestSummarize.summ.set_channel(channel)
        sumry = TestSummarize.summ.summarize(samp, range_spec=asd)
        logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry) >= 1)
        #self.assertTrue(len(sumry) <= 3)
        # Length of summary is less than or equal to the original length
        #self.assertTrue(len(sumry) <= len(samp))
        # Each message in the summary must correspond to a message


    @given(lists(elements=sampled_from(test_json_msgs), min_size=1),
           integers(min_value=1, max_value=24), settings=hs.Settings(timeout=1000)
    )
    def test_text_rank_summarization_ds1_hours(self, smp_msgs, hours):
        """Generate something for N hour intervals"""
        logger.info("Input is %s", smp_msgs)
        asd = {'hours': hours, 'size' : 3, 'txt' : u'Summary for first {} hours:\n'.format(hours)}
        #TestSummarize.summ.set_interval()
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry) >= 1)
        #self.assertTrue(len(sumry) <= 3)
        # Length of summary is less than or equal to the original length
        #self.assertTrue(len(sumry) <= len(smp_msgs))
        # Each message in the summary must correspond to a message
        

    @given(lists(elements=sampled_from(test_json_msgs_c2), min_size=1),
           integers(min_value=1, max_value=24), settings=hs.Settings(timeout=1000)
    )
    def test_text_rank_summarization_ds2_hours(self, smp_msgs, hours):
        """Generate something for N hour intervals"""
        logger.info("Input is %s", smp_msgs)
        asd = {'hours': hours, 'size' : 3, 'txt' : u'Summary for first {} hours:\n'.format(hours)}
        #TestSummarize.summ.set_interval()
        TestSummarize.summ.set_channel('elasticsearch')
        sumry = TestSummarize.summ.summarize(smp_msgs, range_spec=asd)
        logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry) >= 1)
        #self.assertTrue(len(sumry) <= 3)
        # Length of summary is less than or equal to the original length
        #self.assertTrue(len(sumry) <= len(smp_msgs))
        # Each message in the summary must correspond to a message
        

    @given(
        integers(min_value=2, max_value=1000),
        integers(min_value=1, max_value=24), settings=hs.Settings(timeout=1000)
    )
    def test_text_rank_summarization_ds3_hours(self, sampsize, hours):
        """Generate something for N hour intervals"""
        channel, ssamp = random.choice(test_json_msgs_c3)
        samp = ssamp[random.randint(1,len(ssamp)-2):]
        TestSummarize.summ.set_channel(channel)
        logger.info("Input is segment is %s", samp)
        asd = {'hours': hours, 'size' : 3, 'txt' : u'Summary for first {} hours:\n'.format(hours)}
        sumry = TestSummarize.summ.summarize(samp, range_spec=asd)
        logger.debug("Summary is %s", sumry)
        # Length of summary is at least 1 and no greater than 3
        self.assertTrue(len(sumry) >= 1)
        #self.assertTrue(len(sumry) <= 3)
        # Length of summary is less than or equal to the original length
        #self.assertTrue(len(sumry) <= len(samp))
        # Each message in the summary must correspond to a message
        

if __name__ == '__main__':
    unittest.main()

