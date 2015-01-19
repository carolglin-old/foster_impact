import pandas as pd
import pylab as pl
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

def gen_hist(df, column_list):
	for column in column_list:
		df[column].hist()
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

def find_best_rsquared(results_list):
	best = 0
	end_result = []
	for results in results_list:
		if results.rsquared_adj > best:
			best = results.rsquared_adj
			end_result.pop()
			end_result.append(results)
	return end_result

def find_best_model_params(param_list):
















