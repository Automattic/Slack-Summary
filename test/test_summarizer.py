"""Test the core spacy summarizer."""
import unittest
from datetime import datetime
import logging.handlers
from test.conftest import TEST_JSON_MSGS
from summarizer.model.interval_summarizer import (TsSummarizer, ts_to_time)
from summarizer.model.ts_config import DEBUG
from summarizer.model.sp_summarizer import SpacyTsSummarizer
from summarizer.model.lsa_summarizer import LsaSummarizer

_logger = logging.getLogger()  # pylint: disable=invalid-name
_logger.level = logging.DEBUG if DEBUG else logging.INFO


class TestSummarize(unittest.TestCase):
    """Object for testing the core spacy summarizer."""

    def test_interval_conversion(self):
        """Test the interval conversion."""
        self.assertTrue(ts_to_time("1441925382.000186") == datetime.utcfromtimestamp(1441925382))

    def test_summarizer_tag_display(self):
        """Make sure that the display of the tag is correct"""
        _logger.info("Running the taggger test")
        summarizer = TsSummarizer()
        summarizer.set_channel("elasticsearch")
        summary = summarizer.tagged_sum(TEST_JSON_MSGS[1])
        _logger.debug('Test summ msg is %s', summary)
        msg = '@Thu-Sep-9-2015 18:32:08 <@U0EBEC5T5>: '
        msg += '<https://a8c.slack.com/archives/elasticsearch/p1441909928000131|'
        msg += 'because i imagine the places we link people will'
        msg += ' vary quite a bit with tests'
        self.assertTrue(summary == msg)

    def test_spacy_summarization(self):
        """Pass the intervals to summarizer"""
        asd = [{'minutes': 60, 'size': 2, 'txt': 'Summary for first 60 minutes:\n'},
               {'hours': 12, 'size': 1, 'txt': 'Summary for last 12 hours:\n'}]
        lsa_summarizer = LsaSummarizer()
        spacy_summarizer = SpacyTsSummarizer()
        for range_spec in asd:
            spacy_summarizer.set_summarizer(lsa_summarizer)
            spacy_summarizer.set_channel('elasticsearch')
            _logger.debug('Testing spacy summarizer')
            summary = spacy_summarizer.summarize(TEST_JSON_MSGS, range_spec=range_spec)
            _logger.debug('Summary is %s, length %s', summary, len(summary))
            self.assertTrue(len(summary) > 1)


if __name__ == '__main__':
    unittest.main()
