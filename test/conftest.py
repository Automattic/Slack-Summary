"""Shared test configuration."""
import json
import os
import io
from pkg_resources import resource_filename
from summarizer.model.ts_config import LOG_PATH

TEST_DATA_PATH = resource_filename(__name__, '../data/test')
TEST_JSON_MSGS = json.load(io.open(f"{TEST_DATA_PATH}/test-events.json"))['messages']
TEST_JSON_MSGS_ELASTIC = json.load(io.open(f"{TEST_DATA_PATH}/test-events-elastic.json"))['messages']
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
TEST_LOG = os.path.join(LOG_PATH, 'test_summary.log')
