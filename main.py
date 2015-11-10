from flask import Flask, jsonify, request
import requests
import json
import os
from config import *
from ts_config import SUMMS
from slack_summary import SlackRouter
app = Flask(__name__)
from utils import maybe_get
global lsa_summ
lsa_summ = None
if "spacy" in SUMMS:
        import lsa
        import spacy.en
        import spacy
        lsa_summ = lsa.LsaSummarizer()


@app.route("/slack", methods=['POST'])
def slackReq():
        global lsa_summ
        if "spacy" in SUMMS:
                if not lsa_summ:
                        lsa_summ = lsa.LsaSummarizer()
	req_data = request.form
        req = {
	        'channel_id' : req_data.getlist('channel_id'),
                'channel_name' : maybe_get(req_data, 'channel_name', default=''),
                'user_id' : maybe_get(req_data, 'user_id', default=''),
                'user_name' : maybe_get(req_data, 'user_name', default=''),
                'params' : maybe_get(req_data, 'text', default=''),
                'summ' : lsa_summ
                }
        if "gensim" in SUMMS and "gensim" in req['params'].split():
                req['summ'] = None
	return (SlackRouter().get_summary(**req))


@app.route("/slacktest", methods=['POST'])
def slackTestReq():
        global lsa_summ
        if "spacy" in SUMMS:
                if not lsa_summ:
                        lsa_summ = lsa.LsaSummarizer()
	req_data = request.form
        req = {
	        'channel_id' : req_data.getlist('channel_id'),
                'channel_name' : maybe_get(req_data, 'channel_name', default=''),
                'user_id' : maybe_get(req_data, 'user_id', default=''),
                'user_name' : maybe_get(req_data, 'user_name', default=''),
                'params' : maybe_get(req_data, 'text', default=''),
                'summ' : lsa_summ,
                'test' : True
                }
        if "gensim" in SUMMS and "gensim" in req['params'].split():
                req['summ'] = None
	return (SlackRouter(test=True).get_summary(**req))

def main():
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
        
if __name__ == "__main__":
        main()
