import unittest
import json
import io
import config
from ts_config import SUMMS
from interval_summarizer import (IntervalSpec, TsSummarizer,
                                 ts_to_time)
from datetime import datetime
import logging
import logging.handlers
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
        self.assertTrue(ts_to_time("1441925382.000186") == datetime.utcfromtimestamp(1441925382))


    def test_summarizer_tag_display(self):
        """Make sure that the display of the tag is correct"""
        logger.info("Running the taggger test")
        asd = {'minutes': 60, 'size' : 2, 'txt' : u'Summary for first 60 minutes:\n'}
        summ = TsSummarizer()
        summ.set_channel("elasticsearch")
        summ_msg = summ.tagged_sum(TestSummarize.test_msgs[1])
        logger.debug("Test summ msg is %s", summ_msg)
        self.assertTrue(summ_msg == "@Thu-Sep-9-2015 18:32:08 <@U0EBEC5T5>: <https://a8c.slack.com/archives/elasticsearch/p1441909928000131|because i imagine the places we link people will vary quite a bit with tests>")


    def test_gensim_summarization(self):
        """Pass the intervals to summarizer"""
        if "gensim" in SUMMS:
            asd = [{'minutes': 60, 'size' : 2, 'txt' : u'Summary for first 60 minutes:\n'}, {'hours':12, 'size' : 1, 'txt' : u'Summary for last 12 hours:\n'}]
            summ = None
            summ = TextRankTsSummarizer()
            summ.set_channel('elasticsearch')
            logger.debug("Testing gensim summarizer")
            sumry = summ.summarize(TestSummarize.test_msgs, range_spec=asd)
            logger.debug("Summary is %s", sumry)
            self.assertTrue(len(sumry) > 1)
        else:
            pass

    def test_spacy_summarization(self):
        """Pass the intervals to summarizer"""
        if "spacy" in SUMMS:
            asd = [{'minutes': 60, 'size' : 2, 'txt' : u'Summary for first 60 minutes:\n'}, {'hours':12, 'size' : 1, 'txt' : u'Summary for last 12 hours:\n'}]
            summ = None
            lsa_summ = lsa.LsaSummarizer()
            summ = SpacyTsSummarizer()
            for rs in asd:
                summ.set_summarizer(lsa_summ)
                summ.set_channel('elasticsearch')
                logger.debug("Testing spacy summarizer")
                sumry = summ.summarize(TestSummarize.test_msgs, range_spec=rs)
                logger.debug("Summary is %s, length %s", sumry, len(sumry))
                self.assertTrue(len(sumry) > 1)
        else:
            pass


if __name__ == '__main__':
    unittest.main()

