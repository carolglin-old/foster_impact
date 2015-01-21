import pandas as pd
import pylab as pl
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

from transform import *

def gen_hist(df, column_list):
	for column in column_list:
		df[column].hist(bins=100)
		plt.title(column+' n='+str(len(df)))
		plt.show()

def gen_qq(results):
	res = results.resid 
	fig = sm.qqplot(res)
	plt.show()

def gen_residuals(results):
	res = results.resid
	res.plot()
	plt.show()

def sols_result(endog, exog):
	exog = sm.add_constant(exog)
	results = sm.OLS(endog, exog).fit()
	return results

def plot_sols_result(results):
	for i in results.model.exog_names:
		if i != 'const':
			exog = i
	x_data = pd.DataFrame(results.model.exog, columns=results.model.exog_names)[exog]
	y_data = results.model.endog
	x_line = np.linspace(x_data.min(), x_data.max(), 100)
	y_predict = results.predict(sm.add_constant(x_line))
	pl.scatter(x_data, y_data, alpha=0.1)
	pl.ylabel(results.model.endog_names)
	pl.xlabel(exog)
	plt.plot(x_line, y_predict, 'r', alpha=0.9)
	plt.show()

def find_best_rsquared(results_list):
	best = 0
	end_result = []
	for results in results_list:
		if results.rsquared_adj > best:
			best = results.rsquared_adj
			end_result.pop()
			end_result.append(results)
	return end_result

# def find_best_model_params(param_list):

class Analysis:
	def __init__(self, data, endog, exog_list):
		self.endog = endog
		self.exog_list = exog_list
		self.std_list = self.create_std_list()
		self.data = standardize(data, self.std_list)	
		
	def create_std_list(self):
		std_list = []
		std_list.append(self.endog)
		for exog in self.exog_list:
			std_list.append(exog)
		return std_list

	def transform(self, var):
		t_var, lambda_, c = box_cox(var)
		return t_var

	def reverse_transform(self, var):
		tvar, lambda_, c = self.get_lambda(var)
		orig = reverse_boxcox(tvar, lambda_, c)
		return orig

	def get_lambda(self, var):
		t_var, lambda_, c = boxcox(var)
		return lambda_, c

	def result(self, exog, transform=False):
		if transform:
			r = sols_result(self.transform(self.data[self.endog]), self.data[exog])
		else:
			r = sols_result(self.data[self.endog], self.data[exog])
		return r

	def all_results(self, transform=False):
		results_list = []
		for exog in self.exog_list:
			r = self.result(exog, transform)
			results_list.append(r)
		return results_list

	def show_result(self, exog, transform=False):
		r = self.result(exog, transform)
		print r.summary()

	def show_all_results(self, transform=False):
		results_list = []
		for exog in self.exog_list:
			r = self.result(exog, transform)
			results_list.append(r.summary())
		for result in results_list:
			print result

	def show_all_hist(self, transform=False):
		if transform:
			data = pd.DataFrame()
			for var in self.std_list:
				data[var] = self.transform(self.data[var])
		else:
			data = self.data
		gen_hist(data, self.std_list)

	def show_all_fit(self, transform=False):
		results_list = self.all_results(transform)
		for result in results_list:
			plot_sols_result(result)






















