#!/usr/bin/python3


from os import path
from os import getcwd as pwd
from os import listdir as ls
from os import chdir as cd
from rasa.nlu import load_data
from rasa.nlu.model import Interpreter
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English
import requests
import sys

print("loading english")
en = English()
print("complete")

RASA_MODEL=path.join(pwd(), 'models', 'nlu.tar.gz')

RASA_SERVER_ENDPOINT = "http://localhost:5005/model/parse"
MIN_CONFIDENCE_THRESHOLD = .6


class IntentHandler:

	def __init__(self):
		self.endpoint = RASA_SERVER_ENDPOINT
		self.min_confidence_threshold = MIN_CONFIDENCE_THRESHOLD
		self.tokenize = Tokenizer(en.vocab)


	def parse(self, text):
		r = requests.post(self.endpoint, json={"text": text})
		# TODO add error code handling
		dat = r.json()
		#print(dat)
		if dat['intent']['confidence'] < self.min_confidence_threshold:
			return {'intent': 'PUNT', 'entities': []}
		entity_dat = {ent["entity"]: ent["value"] for ent in dat['entities']}
		odat = {
			'intent': dat['intent']['name']
		}
		odat.update(entity_dat)
		return odat


	def respondToFindSomething(self, idat):
		role = idat.get('role')
		target = idat.get('target')
		location = idat.get('location')
		# check role determiner
		# TODO: make this better
		if role:
			role = list(map(str, self.tokenize(role)))
			if role[0].lower() == "my":
				role[0] = " your"
			role = " ".join(role) + " "
		else:
			role = " "
		if location: # handle prep phrase for location
			pp = " in {}".format(location)
		else:
			pp = ""
		target = " " if target is None else target
		full_text = "I'm not sure how to find {}{}{}".format(role, target, pp)

		return {"response_text": full_text}

if __name__ == "__main__":
	imp = sys.argv[1]
	#print("constructing intent handler")
	parser = IntentHandler()
	#print("complete")
	#print("parsing...")
	while True:
		imp = input("whatsup?: ")
		test = parser.parse(imp)
	#print("complete")
	#print("responding to parse...")
		response = parser.respondToFindSomething(test)['response_text']
	#print("\n")
		print(response)








