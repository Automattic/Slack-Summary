import unittest
import json
import io
import config
from ts_config import SUMMS
from interval_summarizer import (IntervalSpec, TsSummarizer, tagged_sum,
                                 ts_to_time)
from datetime import datetime
import logging
import sys
from ts_config import DEBUG
if "spacy" in SUMMS:
    from sp_summarizer import (SpacyTsSummarizer)
    import lsa
if "gensim" in SUMMS:
    from ts_summarizer import (TextRankTsSummarizer)

logger = logging.getLogger()
logger.level = logging.DEBUG if DEBUG else logging.INFO

class TestSummarize(unittest.TestCase):

    test_msgs = json.load(io.open("./test-events.json", encoding='utf-8'))['messages']

    def test_interval_conversion(self):
        self.assertTrue(ts_to_time("1441925382.000186") == datetime.fromtimestamp(1441925382))

    def test_create_intervals(self):
        asd = [{'minutes': 10}, {'hours':12}]
        self.assertTrue(len(TestSummarize.test_msgs) == 8)
        summ = TsSummarizer(asd)
        msgs = summ.segment_messages(TestSummarize.test_msgs)
        logger.debug("Messages received %s", msgs)
        self.assertTrue(len(msgs) == 2)
        logger.debug("First entry should be %s is %s", TestSummarize.test_msgs[0:4], msgs[1][1][::-1])
        self.assertTrue(msgs[0][1][::-1] == TestSummarize.test_msgs[4:])
        self.assertTrue(msgs[1][1][::-1] == TestSummarize.test_msgs[0:4])
        asd2 = [{'minutes': 5}, ]
        summ = TsSummarizer(asd2)
        msgs = summ.segment_messages(TestSummarize.test_msgs)
        logger.debug("Messages received %s", msgs)
        self.assertTrue(len(msgs) == 1)
        logger.debug("First entry should be %s is %s", TestSummarize.test_msgs[4:], msgs[0][1][::-1])
        self.assertTrue(msgs[0][1][::-1] == TestSummarize.test_msgs[4:])

    def test_gensim_summarization(self):
        """Pass the intervals to summarizer"""
        if "gensim" in SUMMS:
            asd = [{'minutes': 60, 'size' : 2, 'txt' : u'Summary for first 60 minutes:\n'}, {'hours':12, 'size' : 1, 'txt' : u'Summary for last 12 hours:\n'}]
            summ = None
            summ = TextRankTsSummarizer(asd)
            logger.debug("Testing gensim summarizer")
            sumry = summ.summarize(TestSummarize.test_msgs)
            logger.debug("Summary is %s", sumry)
            self.assertTrue(len(sumry) == 2)
        else:
            pass

    def test_spacy_summarization(self):
        """Pass the intervals to summarizer"""
        if "spacy" in SUMMS:
            asd = [{'minutes': 60, 'size' : 2, 'txt' : u'Summary for first 60 minutes:\n'}, {'hours':12, 'size' : 1, 'txt' : u'Summary for last 12 hours:\n'}]
            summ = None
            lsa_summ = lsa.LsaSummarizer()
            summ = SpacyTsSummarizer(asd)
            summ.set_summarizer(lsa_summ)
            logger.debug("Testing spacy summarizer")
            sumry = summ.summarize(TestSummarize.test_msgs)
            logger.debug("Summary is %s", sumry)
            self.assertTrue(len(sumry) == 2)
        else:
            pass

if __name__ == '__main__':
    unittest.main()

