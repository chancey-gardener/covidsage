#!/usr/bin/python3

import numpy as np
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English

print("loading english tokenizer")
en = English()
tokenizer = Tokenizer(en.vocab)
print("complete")


def capitalize(string):
	return " ".join(i.text.capitalize() for i in tokenizer(string))


def exponential(a, b, x, c=0):
	#print(a)
	return a * np.exp(b * x) + c

def zerodate(datelist):
	'''takes a list of datetime.datetime objects
	returns a list of integers representing the days
	with day 0 being the date of the 1st day
	'''
	day_zero = datelist[0].day
	daylist = [i.day - day_zero for i in sorted(datelist, key=lambda d: d.day)]
	return daylist

def safedivForRatio(n, d, round_to=3):
	if n == 0 and d == 0:
		return 0
	else:
		try:
			out = n / d
		except ZeroDivisionError:
			return np.nan
		return round(out, round_to)
