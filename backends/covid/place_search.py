#!/usr/bin/python3

import requests
# foursquare credentials
CLIENT_ID="IQ2JLJHUMBNAHPWX2KWVXUCLXA4PDKRZ4GAQEJJTNRFZDAFR"
CLIENT_SECRET="5EZH20ULM4OWUXE0T0W2YIYMQEBXCA5IX0J5SCVETO33QPOT"


ENDPOINT="https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"


def search_place(search_terms):
	url = ENDPOINT + 'input='
	print(url)
	place = "%20".join(search_terms.split(" "))
	url += place
	url += "&inputtype=textquery&fields=name,formatted_address"
	url += "&key="
	url += API_KEY
	response = requests.get(url)
	return response


if __name__ == "__main__":
	this = search_place("Wuhan")
	print(this.json())
	print(this.ok)
	print(dir(this))