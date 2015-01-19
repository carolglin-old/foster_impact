from scipy import stats
from sklearn import preprocessing

def standardize(df, columns):
	standardized_df = df.copy()
	for i in columns:
		standardized_df[i] = preprocessing.scale(standardized_df[i])
	return standardized_df

def box_cox(var):
	num = 0
	if var.min() <= 0:
		num = ((0 - var.min()) + 1)
		vart, lambda_ = stats.boxcox(var + num)
	elif var.min() > 0:
		vart, lambda_ = stats.boxcox(var)
	stats.probplot(vart, dist=stats.norm)
	return vart, (lambda_, num)

# not sure if reciprocal implementation is correct

# def reciprocal(var):
# 	reflected_var = ((var*-1) + var.max()+1)
# 	inverse_var = (1/reflected_var)
# 	return inverse_var

# square root transformation
# log transformation 
# exponential transformation
# create a transformation generator and return one with highest r squared