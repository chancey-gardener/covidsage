#!/usr/bin/python3


from os import path
from os import getcwd as pwd
from os import listdir as ls
from os import chdir as cd
import requests
import sys
from nlu_client import RasaNluClient
from discourse import *
from backends.covid.data_loader import disambiguate, death_rate, STATES_TO_ABBREVIATIONS
from backends.covid.utils import *
from backends.covid.plotter import CovidDataPlotter


RASA_MODEL = path.join(pwd(), 'models', 'nlu.tar.gz')

RASA_SERVER_ENDPOINT = "http://localhost:5005/model/parse"
MIN_CONFIDENCE_THRESHOLD = .6

response_bank = {
    'covid_deathrate': "CovidDeathRateResponse",
    'help_findsomething': "FindSomethingResponse",
    'covid_casecount': "CovidCaseCountResponse",
    'covid_growthcurve': "CovidGrowthCurveResponse"
}


class FulfillmentEngine:

    def __init__(self):
        self.min_confidence_threshold = MIN_CONFIDENCE_THRESHOLD
        self.nlu = RasaNluClient()
        self.discourse = ConversationStateHandler()
        self.plotter = CovidDataPlotter()

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
        if location:  # handle prep phrase for location
            pp = " in {}".format(location)
        else:
            pp = ""
        target = " " if target is None else target
        full_text = "I'm not sure how to find {}{}{}".format(role, target, pp)

        return {"response_text": full_text}

    def CovidDeathRateResponse(self, idat):
        area = idat.get('area')
        if not area:
            return {"response_text": "Sorry, I didn't catch the place you're talking about"}
        else:
            selection = disambiguate(area)
            if not selection:
                return {"response_text": "I don't have any data on {}, sorry.".format(area)}
            else:
                selection = selection[0]
                dr = death_rate(*selection)
                return {"response_text": "The death rate in {} is {}%".format(area, dr*100)}

    def CovidGrowthCurveResponse(self, idat):
        area = idat.get('area')
        if not area:
            return {"response_text": "Sorry, I didn't catch the place you're talking about"}
        else:
            no_data_response = "I don't have any data on {}, sorry.".format(
                area)
            selection = disambiguate(area)
            if not selection:
                return {"response_text": no_data_response}
            else:
                selection = selection[0]
                dat = query_by_location(city_counties=[selection[0]],
                                        province_states=[selection[1]],
                                        countries=[selection[2]])
                if not dat:
                    return {"response_text": no_data_response}
                else:
                    self.plotter.plot_curve(list(
                        map(lambda x: datetime.fromisoformat(x[0]),
                            dat)))



if __name__ == "__main__":
    imp = sys.argv[1]
    #print("constructing intent handler")
    fl = FulfillmentEngine()
    # print("complete")
    # print("parsing...")

    while True:
        imp = input("whatsup?: ")
        test = fl.nlu.parse(imp)
        intent_name = test['intent']
        print(intent_name)
        ffname = response_bank[intent_name]
        fulfunc = getattr(fl, ffname)

        response_dat = fulfunc(test)
        print(test)
        resp = response_dat['response_text']
        print(resp)

    # print("complete")
    #print("responding to parse...")
        #response = parser.respondToFindSomething(test)['response_text']
    # print("\n")
        # print(response)
