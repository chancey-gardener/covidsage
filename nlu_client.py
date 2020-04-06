#!.usr/bin/python3


import requests
from rasa.nlu.model import Interpreter
from os import path
from os import getcwd as pwd
from discourse import ConversationStateHandler

RASA_MODEL=path.join(pwd(), 'models', 'nlu')

RASA_SERVER_ENDPOINT = "http://localhost:5005/model/parse"
MIN_CONFIDENCE_THRESHOLD = .6


class RasaNluClient:

	def __init__(self, use_http=False):
		self.endpoint = RASA_SERVER_ENDPOINT
		self.min_confidence_threshold = MIN_CONFIDENCE_THRESHOLD
		self.discourse_state = ConversationStateHandler()
		self._rasa_intepreter = Interpreter.load(RASA_MODEL)

	def detectIntent(self, text):
		return self._rasa_intepreter.parse(text)


	def detectIntentFromHttp(self, text):
		r = requests.post(self.endpoint, json={"text": text})
		# TODO add error code handling
		if not r.ok:
			return {'ERROR': r.reason, 'status_code': r.status_code}
		dat = r.json()
		return dat

	def constructFulfillmentRequest(self, dat):
		if dat['intent']['confidence'] < self.min_confidence_threshold:
			return {'intent': 'PUNT', 'entities': []}
		entity_dat = {ent["entity"]: ent["value"] for ent in dat['entities']}
		odat = {
			'intent': dat['intent']['name']
		}
		odat.update(entity_dat)
		odat['output_contexts'] = list(self.discourse_state.contexts.keys())
		self.discourse_state.step(odat)
		return odat

	def parse(self, text):
		nlu_dat = self.detectIntent(text)
		fr = self.constructFulfillmentRequest(nlu_dat)
		return fr
