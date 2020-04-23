"""Summarize by picking most informative sentences."""
import logging
from collections import namedtuple
from operator import attrgetter

from summarizer.model.utils import ItemsCount

logging.basicConfig(level=logging.INFO)

SentenceInfo = namedtuple("SentenceInfo", ("sentence", "order", "rating",))


def normalize_word(word):
    """Convert word toke to lower case."""
    return word.lower()


class BaseSummarizer:
    """Base class for the summarizers."""

    def __init__(self, ):
        """Initialize the summarizer."""
        self.logger = logging.getLogger(__name__)

    def __call__(self, document, sentences_count):
        """Produce the summarization."""
        raise NotImplementedError("This method should be overriden in subclass")

    def get_best_sentences(self, sentences, count, rating, *args, **kwargs):
        """Return the best sentences from the ones presented."""
        rate = rating
        self.logger.info("Sentences are %s", sentences)

        infos = (SentenceInfo(s, o, rate(s, *args, **kwargs))
                 for o, s in enumerate(sentences))
        # sort sentences by rating in descending order
        infos = sorted(infos, key=attrgetter("rating"), reverse=True)
        # get `count` first best rated sentences
        count = ItemsCount(count)
        # if not isinstance(count, ItemsCount):
        #     count = ItemsCount(count)
        infos = count(infos)
        # sort sentences by their order in document
        infos = sorted(infos, key=attrgetter("order"))
        return tuple(i.sentence for i in infos)
