"""Process a slack thread and summarize."""
import logging
from logging import handlers
import os

from flask import Flask, request

# Let's stick to the LSA summarizer for the time being.
from summarizer.model.lsa_summarizer import LsaSummarizer
from summarizer.model.slack_summary import SlackRouter
from summarizer.model.ts_config import LOG_PATH
from summarizer.model.utils import maybe_get

_app = Flask(__name__)  # pylint: disable=invalid-name
_logger = logging.getLogger(__name__)

_summarizer = LsaSummarizer()  # pylint: disable=invalid-name


@_app.route("/slack", methods=['POST'])
def process_slack_request():
    """Process summary request."""
    req_data = request.form
    req = {
        'channel_id': req_data.getlist('channel_id'),
        'channel_name': maybe_get(req_data, 'channel_name', default=''),
        'user_id': maybe_get(req_data, 'user_id', default=''),
        'user_name': maybe_get(req_data, 'user_name', default=''),
        'params': maybe_get(req_data, 'text', default=''),
        'summ': _summarizer
    }
    return SlackRouter().get_summary(**req)


@_app.route("/slacktest", methods=['POST'])
def process_slack_test_request():
    """Process test request."""
    req_data = request.form
    req = {
        'channel_id': req_data.getlist('channel_id'),
        'channel_name': maybe_get(req_data, 'channel_name', default=''),
        'user_id': maybe_get(req_data, 'user_id', default=''),
        'user_name': maybe_get(req_data, 'user_name', default=''),
        'params': maybe_get(req_data, 'text', default=''),
        'summ': _summarizer,
        'test': True
    }
    return SlackRouter(test=True).get_summary(**req)


def _setup_logging(log_level):
    """Set up internal logging."""
    _logger.setLevel(log_level)
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
    file_handler = handlers.RotatingFileHandler(os.path.join(LOG_PATH, 'slack_summarizer.log'),
                                                maxBytes=1e7,
                                                backupCount=10)
    assert file_handler is not None
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter('%(asctime)15s %(name)s %(levelname)s %(message)s'))
    _logger.addHandler(file_handler)
    _app.logger = _logger


def main(host='0.0.0.0', port=8193, log_level=logging.getLevelName(logging.DEBUG)):
    """Initialize and run the Elfbot server.

    Parameters
    ----------
    host : str
        IP address or domain for the host to listen on
    port : int
        Port to listen on
    log_level : str
        Log level (DEBUG, INFO, ERROR, etc.)
    """
    _setup_logging(log_level)
    _app.run(host=host, port=port, debug=False)
