#!/usr/bin/python3

from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib import cbook
from datetime import datetime
import numpy as np
import scipy.optimize as opt
from backends.covid.utils import exponential, zerodate
from backends.covid.data_loader import *


class CovidDataPlotter:

	def __init__(self):
		self.day_locator = mdates.DayLocator()

	
	def plot_curve(self, dates, ydat, xlab, ylab, legend):
		xdat = zerodate(dates)
		#print(xdat)
		plt.title(legend)
		#plt.gca().xaxis.set_major_locator(self.day_locator)
		#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
		plt.plot(xdat, ydat, ".", label="Confirmed Cases of COVID-19")
		#plt.gcf().autofmt_xdate()
		
		x, y = np.array(xdat), np.log(ydat)
		a, b = np.polyfit(x, y, 1)
		print("growth rate: {}".format(a))
		f = np.exp(b)*np.exp(a*x)
		plt.plot(x, f)

		#optimized_params, pcov = opt.curve_fit(exponential, xdat, ydat)
		#print(optimized_params)
		#plt.plot(xdat, exponential(xdat, *optimized_params), label=legend)

		plt.legend()
		plt.show()


if __name__ == "__main__":
	COUNTY="San Francisco"
	#test_rawdat = query_by(countries=['UK'])#city_counties=['Istanbul'])#province_states=['FL'])
	test_rawdat = query_by_location(city_counties=['London'])
	test_rawdat = query_by_location(countries=["italy"])

	dates = [datetime.fromisoformat(i[0]) for i in test_rawdat]
	print(dates)
	#xdat = np.array(zerodate(dates))
	# confirmed cases
	ydat = np.array([int(i[4]) for i in test_rawdat])

	test = CovidDataPlotter()
	# print(xdat)
	# print(ydat)
	test.plot_curve(dates, ydat, "day", "confirmed cases", "United States")





