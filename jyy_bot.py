# export FLASK_APP=chatbot
# python3 -m flask run --debugger 
from flask import Flask, request
import logging
import logging.handlers
import requests
import sys
import json

app = Flask(__name__)

# init logger
msg_logger = logging.getLogger('msg_logger')
handler = logging.handlers.RotatingFileHandler(
  './msg_logger', maxBytes=(1048576*5), backupCount=70
)
msg_logger.addHandler(handler)
msg_logger.setLevel(logging.INFO)

nlu_logger = logging.getLogger('nlu_logger')
handler = logging.handlers.RotatingFileHandler(
  './nlu_logger', maxBytes=(1048576*5), backupCount=70
)
nlu_logger.addHandler(handler)
nlu_logger.setLevel(logging.INFO)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def log(msg):
    print(msg, file=sys.stderr)


def get_nlu(query):
  appkey = "TODO"
  url = f'http://m.mobvoi.com/search/qa/?query={query}&appkey={appkey}&output=lite'
  r = requests.get(url)
  nlu_json = r.json()
  nlu_logger.info(nlu_json)
  return nlu_json


@app.route("/msg", methods=['POST'])
def receive_mesg():
    data = str(request.data)
    msg_logger.info("[raw_request] " + data)
    data_json = json.loads(request.data)

    reply = get_reply(data_json)
    return json.dumps(reply)


def mk_response(response_text, to):
    if response_text:
        msg_logger.info(f"[response] {response_text}")

    return {
      'response': response_text,
      'to': to,
    }


BOT_SENDER_LIST = ['X. J', '追寻萝土']


def get_slot_value(nlu_json, slot):
    semantic_slots = nlu_json['states']['semantic']['slots']
    if slot not in semantic_slots:
        return None, None
    else:
        raw_value = semantic_slots[slot][0]['raw_data']
        norm_value = semantic_slots[slot][0]['norm_value']
        return raw_value, norm_value
    

def get_reply(request_json):
    from_name = request_json['from_name']
    from_id = request_json['from_id']
    input_text = request_json['text']

    msg_logger.info(f"[msg] {from_name}: {input_text}")

    if from_name not in BOT_SENDER_LIST:
        return mk_response(None, None)

    nlu_json = get_nlu(input_text)
    faq_response, _ = get_slot_value(nlu_json, 'faq_answer')
    if faq_response:
        return mk_response(faq_response, from_id)

    # normal slot
    _, event_type = get_slot_value(nlu_json, 'event_type')
    if event_type:
        response = f"好的！添加蒋一一的【{event_type}】记录"
        return mk_response(response, from_id)
    
    return mk_response(None, None)


if __name__ == '__main__':
    # query = "蒋一一是谁"
    query = "蒋一一睡觉了"
    request_json = {
      'from_name': 'X. J',
      'from_id': '@a1231lk23j1l2k3j',
      'text': query,
    }
    print(get_reply(request_json))
