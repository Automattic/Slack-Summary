"""Summarize using spacy."""

import glob
import io
import json
import logging
import logging.handlers
from datetime import time
from typing import List, Dict, Any

from summarizer.model.interval_summarizer import (TsSummarizer, canonicalize, ts_to_time, tspec_to_delta)
from summarizer.model.ts_config import TS_DEBUG, SPACY_SUMMARIZER_LOG, TEMPORAL_VALUES
from summarizer.model.utils import get_msg_text

logging.basicConfig(level=logging.INFO)


class SpacyTsSummarizer(TsSummarizer):
    """Summarize using a parse of the thread."""

    def __init__(self, ):
        """Initialize the summarizer."""
        TsSummarizer.__init__(self, )
        log_level = logging.DEBUG if TS_DEBUG else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.handlers.RotatingFileHandler(SPACY_SUMMARIZER_LOG, mode='a',
                                                            encoding='utf-8', maxBytes=1000000, backupCount=5)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger = logging.getLogger('sp_summarizer')
        self.logger.handlers = []
        self.logger.addHandler(file_handler)
        self.sumr = None

    def set_summarizer(self, spacy_summ):
        """Set the particular summarizer."""
        self.sumr = spacy_summ

    def summarize(self, msgs, range_spec=None):  # pylint: disable=invalid-name,too-many-locals,invalid-sequence-index
        """Return a summary of the text."""
        size = 3
        txt = u'Summary is'
        if not msgs:
            self.logger.warning('No messages to form summary')
            return u'\n Unable to form summary here.\n'
        if range_spec:
            size = range_spec['size'] if 'size' in range_spec else size
            txt = range_spec['txt'] if 'txt' in range_spec else txt
            time_specs = {spec: int(val) for (spec, val) in range_spec.items() if spec in TEMPORAL_VALUES}
            self.logger.info('First 10 messages  %s of %s', msgs[:10], len(msgs))
            self.logger.info('Using time range spec %s', range_spec)
            start_time = time.strptime(range_spec['start'], "%B %d %Y") if 'start' in range_spec else ts_to_time(
                min(msgs, key=lambda m: m['ts'])['ts'])
            self.logger.info('Start time is  %s', start_time)
            end_time = start_time + tspec_to_delta(**time_specs)
            self.logger.info('End time is  %s', end_time)
            msgs = [msg for msg in msgs if ts_to_time(msg['ts']) >= start_time and ts_to_time(msg['ts']) <= end_time]
            self.logger.info('First 10 messages  %s of %s', msgs[:10], len(msgs))
        summ = txt + u' '
        can_dict = {canonicalize(get_msg_text(msg)): msg for msg in msgs}
        top_keys = sorted(can_dict.keys(), key=lambda x: len(x.split()), reverse=True)
        can_dict = {key: can_dict[key] for key in top_keys}
        self.logger.info('Length of can_dict is %s', len(can_dict))
        simple_sum_list: List[Dict[str, Any]] = [can_dict[ss] for ss in
                                                 sorted(can_dict.keys(),
                                                        key=lambda x: len(x.split()), reverse=True)[:size]]
        assert len(simple_sum_list) <= size
        if len(msgs) < 10:
            # return the longest
            sents_sorted = sorted(simple_sum_list, key=lambda x: x['ts'])  # pylint: disable=invalid-sequence-index
            summ += u'\n'.join([self.tagged_sum(ss) for ss in sents_sorted])
        else:
            summ = self._summarize_large_seq(can_dict, size, summ, simple_sum_list)
        self.logger.info("Summary for segment %s is %s", msgs, summ)
        return summ

    def parify_text(self, msg_segment):
        """Create a paragraph formatted summarization."""
        ptext = u'. '.join([SpacyTsSummarizer.f_regexp.sub(u'', msg['text']) for msg in msg_segment if 'text' in msg])
        self.logger.debug("Parified text is %s", ptext)
        return ptext

    def _summarize_large_seq(self, can_dict, size, summ, simple_sum_list):
        max_sents = {}
        user_sents = {}
        for (txt, msg) in can_dict.items():
            if len(txt.split()) > 3:
                sents = list(self.sumr.nlp(txt).sents)
                max_sents[max(sents, key=len).text] = msg
                user_sents[max(sents, key=len).text] = msg['user'] if 'user' in msg else u''
        txt_sum = [v for v in self.sumr(u' '.join(max_sents.keys()), size, user_sents)]
        self.logger.info('Canonical keys are \n%s', u' '.join(can_dict.keys()))
        self.logger.info('Spacy summ %s', txt_sum)
        nlp_summ = u'\n'.join([self.tagged_sum(max_sents[ss]) for ss in txt_sum if len(ss) > 1 and ss in max_sents])
        nlp_list = [max_sents[ss] for ss in txt_sum if len(ss) > 1 and ss in max_sents]
        for summary_sentence in txt_sum:
            if summary_sentence not in max_sents and len(summary_sentence.split()) > 5:
                self.logger.info('Searching for: %s', summary_sentence)
                for (kval, msg) in max_sents.items():
                    if summary_sentence in kval or (len(kval.split()) > 10 and kval in summary_sentence) \
                            and len(nlp_list) <= size:
                        nlp_summ += u'\n' + self.tagged_sum(msg)
                        nlp_list.append(msg)
        if len(nlp_list) < 2:
            self.logger.info("Failed to find nlp summary using heuristic")
            sorted_list = sorted(simple_sum_list, key=lambda x: x['ts'])  # pylint: disable=invalid-sequence-index
            summ += u'\n'.join([self.tagged_sum(ss) for ss in sorted_list])
        else:
            self.logger.info('First msg is %s, %s', nlp_list[0], nlp_list[0]['ts'])
            self.logger.info('Sorted is %s', sorted(nlp_list, key=lambda x: x['ts']))
            summ += u'\n'.join([self.tagged_sum(ss) for ss in sorted(nlp_list, key=lambda x: x['ts'])])
        return summ


def main():
    """Start the summarizer."""
    asd = [{'minutes': 30, 'txt': u'Summary for first 30 minutes:\n', 'size': 2},
           {'hours': 36, 'txt': u'Summary for next 36 hours:\n', 'size': 3}]
    logger = logging.getLogger(__name__)
    tr_summ = SpacyTsSummarizer()
    all_msgs = []
    for msg_file in glob.glob('./data/*.json'):
        with io.open(msg_file, encoding='utf-8', ) as mfile:
            all_msgs += json.load(mfile)
    for filt in asd:
        logger.info(tr_summ.summarize(all_msgs, range_spec=filt))


if __name__ == '__main__':
    main()
