from datamung import *
from regression import *
from datavis import *
import numpy as np
import datetime
import pdb

root = '/Users/carollin/Dev/foster_impact/data' 

# forester specific functions
def remove_same_date(df, var, same_date_list):
	to_remove = df[var].isin(same_date_list)
	return to_remove

def check_dates(name_list, name_type, df):
	same_date_list = []
	for name in name_list:
		column = getattr(df, name_type)
		segment = df[column==name]
		check_value = segment['placed_dt'].iloc[0]
		check_list = segment['placed_dt'].tolist()
		same = 0
		for i in check_list:
			if check_value == i:
				same +=1
		if same == len(check_list):
			same_date_list.append(name)
	return same_date_list

def det_outcome(stat_desc):
	if stat_desc in ('Inital Placement', 'Active - Return to Billing', 'External Transfer', 'Suspended Payment', 'Court Ordered Discharge'):
		return 0
	elif stat_desc in ('Final Discharge', 'Trial Discharge', 'College', 'Adopted'):
		return 1
	elif stat_desc in ('AWOL', 'Hospital', 'Return to Agency', 'Legal Detention'):
		return -1
	else:
		return 'not classified'

def parse_date(column):
	time = 0.0
	column = str(column) 
	time_parts = column.split(',')
	for part in time_parts:
		yr = re.search('(\d+) \yrs\.', part)
		mo = re.search('\s*(\d+) mos?\.', part)
		da = re.search('\s*(\d+) days', part)
		if yr:
			year = yr.group(1)
			year = float(year)
			time += year 
		elif mo:
			month = mo.group(1)
			month = float(month)
			time += (month / 12)		
		elif da:
			day = da.group(1)
			day = float(day)
			time += (day / 365)	
	return time

def check_type(df):
	column_names = list(df.columns.values)
	for column in column_names:
		if column in ('child_id', 'foster_parent', 'outcome'):
			df[column] = df[column].astype(int)
		elif column in ('c_age', 'duration', 'fp_age', 'sw_age', 'term', 'goals_2014', 'competency_2014', 'overall_2014', 'goals_2013', 'competency_2013', 'overall_2013'):
			df[column] = df[column].astype(float)
		elif column in ('placed_dt', 'stat_dt'):
			df[column] = pd.to_datetime(df[column])
		else:
			pass
	return df

# def parse_percent(column):
# 	column = str(column)
# 	pdb.set_trace()
# 	p = re.search('(\d+)', column)
# 	percent = p.group(1)
# 	percent = float(percent)
# 	percent = percent/100
# 	return percent

def create_exp_column(df, column_name, var):
	to_join = pd.DataFrame()
	to_join['child_id'] = df.index
	to_join = to_join.set_index('child_id')
	to_join[column_name] = ''
	for idx in df.index:
		to_join.loc[idx, column_name] = calc_avg_exp(df, idx, var)
	to_join[column_name] = to_join[column_name].astype(float)
	return to_join

# def calculate_exp(df, c_id, var):
# 	exp = []
# 	case_start = df.loc[c_id, 'placed_dt']
# 	case_end = df.loc[c_id, 'stat_dt']
# 	var_id = df.loc[c_id, var]
# 	column = getattr(df, var)
# 	segment = df[column.isin([var_id])]
# 	child_list = segment.index.tolist()
# 	for child in child_list:
# 		end_date = df.loc[child, 'stat_dt']
# 		start_date = df.loc[child, 'placed_dt']
# 		if start_date < case_start:
# 			if (end_date > start_date) & (end_date <= case_end):
# 		elif (start_date < case_start):
# 			if end_date <= case_start:
# 				add_exp = ((end_date - start_date).total_seconds() / (60*60*24))
# 				start_exp += add_exp
# 			elif end_date > case_start:
# 				add_exp = ((case_start - start_date).total_seconds() / (60*60*24))
# 				start_exp += add_exp
# 	exp.append(start_exp)

def calc_avg_exp(df, c_id, var):
	exp = []
	case_start = df.loc[c_id, 'placed_dt']
	duration = df.loc[c_id, 'duration'].astype(int)
	var_id = df.loc[c_id, var]
	column = getattr(df, var)
	segment = df[column.isin([var_id])]
	child_list = segment.index.tolist()
	for day in range(duration): 
		current_date = case_start + datetime.timedelta(days=day)
		current_exp = calc_current_exp(segment, child_list, current_date)
		exp.append(current_exp)
	avg_exp = sum(exp)/duration
	return avg_exp

def calc_current_exp(seg, child_list, current_date):
	current_exp = 0
	to_days = 60*60*24
	for child in child_list:
		start_date = seg.loc[child, 'placed_dt']
		end_date = seg.loc[child, 'stat_dt']
		if start_date > current_date:
			pass
		elif start_date < current_date:
			if end_date <= current_date:
				add_exp = ((end_date - start_date).total_seconds() / to_days)
				current_exp += add_exp
			elif end_date > current_date:
				add_exp = ((current_date - start_date).total_seconds() / to_days)
				current_exp += add_exp
	return current_exp

def fix_zeros(row):
	if row['case_order'] == 0.0:
		row['diff'] = np.nan
	return row

def segment_results(var_id, segment, endog, exog):
	regress = Analysis(segment, endog, [exog])
	# regress.show_all_fit()
	# segment = segment.sort('placed_dt')
	# dot_plot(segment, var_id, 'child_id', 'placed_dt', 'stat_dt')
	# pdb.set_trace()
	if exog == 'case_order':
		return regress, (var_id, regress.result(exog).params.case_order, regress.result(exog).rsquared_adj)
	elif exog == 'exp':
		return regress, (var_id, regress.result(exog).params.exp, regress.result(exog).rsquared_adj)

def coef_data_prep(df, iv, endog, exog):
	names = uniques_to_list(df, iv)
	column = getattr(df, iv)
	coef_list = []
	for n in names:
		segment = df[column.isin([n])]
		r, c = segment_results(n, segment, endog, exog)
		coef_list.append(c)
	indiv_coef = pd.DataFrame(coef_list, columns=[iv, 'coef', 'rsqu'])
	new_df = pd.merge(df, indiv_coef, how='left', on=iv)
	return new_df, indiv_coef

def show_attributes(regress_list, restrictions=None):
	for r in regress_list:
		r.show_all_fit()
		r.show_all_results()

# analysis-specific data prep functions
def order_data_prep(df, iv):
	names = uniques_to_list(df, iv)
	same_dates_list = check_dates(names, iv, df)
	to_del = remove_same_date(df, iv, same_dates_list)
	new_df = df[~to_del]
	new_df['case_order'] = add_order(new_df, iv, 'placed_dt')
	new_df['case_order'] = change_type(new_df['case_order'], 'float')
	new_df = add_count(new_df, iv, 'case_count')
	final_df = new_df[['child_id', 'foster_parent', 'social_worker', 'duration', 'case_order', 'case_count', 'placed_dt', 'stat_dt', 'term', 'sw_age', 'overall_2014', 'overall_2013']]
	return final_df

def exp_data_prep(df, iv):
	df.set_index('child_id')
	df = add_count(df, iv, 'case_count')
	exp = create_exp_column(df, 'avg_exp', iv)
	new_df = pd.merge(df, exp, left_index=True, right_index=True)
	final_df = new_df[['child_id', 'foster_parent', 'social_worker', 'duration', 'avg_exp', 'case_count', 'placed_dt', 'stat_dt']]
	return final_df

def change_data_prep(df, iv):
	new_df = order_data_prep(df, iv)
	new_df = new_df.sort([iv, 'case_order'])
	new_df['diff'] = new_df['duration'].diff()
	new_df = new_df.apply(fix_zeros, axis=1)
	# final_df = drop_na(new_df, ['diff'])
	return new_df

# create columns/combine csv files
# intakes = load_csv(root, '/csv/intakes.csv')
# res = load_csv(root, '/csv/resources.csv')
# sw = load_csv(root, '/csv/sw_info.csv')
# edu = load_csv(root, '/csv/education.csv')
# perf = load_csv(root, '/csv/perf_data.csv')

# intakes['c_age'] = change_type(intakes['c_age'], 'float')
# intakes['placed_dt'] = change_type(intakes['placed_dt'], 'date')
# intakes['stat_dt'] = change_type(intakes['stat_dt'], 'date')

# intakes['social_worker'] = intakes['wlast']+intakes['wfirst']
# intakes['outcome'] = intakes['stat_desc'].map(det_outcome)
# intakes['duration'] = subt_day(intakes['stat_dt'], intakes['placed_dt'])

# res['foster_parent'] = change_type(res['foster_parent'], 'int')
# res['fp_age'] = change_type(res['fp_age'], 'float')

# sw['sw_age'] = change_type(sw['sw_age'], 'float')

# sw['term'] = sw['years_service'].map(parse_date)
# sw['social_worker'] = sw['wlast']+sw['wfirst']

# # edu['attend'] = parse_percent(edu['total'])

# perf['goals_2014'] = change_type(perf['goals_2014'], 'float')
# perf['competency_2014'] = change_type(perf['competency_2014'], 'float')
# perf['overall_2014'] = change_type(perf['overall_2014'], 'float')
# perf['goals_2013'] = change_type(perf['goals_2013'], 'float')
# perf['competency_2013'] = change_type(perf['competency_2013'], 'float')
# perf['overall_2013'] = change_type(perf['overall_2013'], 'float')

# perf['social_worker'] = perf['wlast']+perf['wfirst']

# intakes_tojoin = intakes[['child_id', 'c_age', 'c_sex', 'program', 'foster_parent', 'social_worker', 'placed_dt', 'stat_dt', 'duration', 'outcome']]
# res_tojoin = res[['foster_parent', 'fp_age', 'fp_sex']]
# sw_tojoin = sw[['social_worker', 'sw_age', 'sw_sex', 'term']]
# perf_tojoin = perf[['social_worker', 'goals_2014', 'competency_2014', 'overall_2014', 'goals_2013', 'competency_2013', 'overall_2013']]

# clean = pd.merge(intakes_tojoin, res_tojoin, how='left', on='foster_parent')
# clean = pd.merge(clean, sw_tojoin, how='left', on='social_worker')
# clean = pd.merge(clean, perf_tojoin, how='left', on='social_worker')

# clean.to_csv(root+'/working/clean.csv')
# pos = clean[clean.outcome==1]
# pos.to_csv(root+'/working/clean_pos.csv')

pos = load_csv(root, '/working/clean_pos.csv')
pos = check_type(pos)

# trimming and segmenting data
clean_fp = drop_na(pos, ['foster_parent'])
trim_fp = segment_data(clean_fp, 30, clean_fp['duration'].max(), 'duration')
clean_sw = drop_na(pos, ['social_worker'])
trim_sw = segment_data(clean_sw, 30, clean_sw['duration'].max(), 'duration')

# order analysis
order_fp = order_data_prep(clean_fp, 'foster_parent') 
order_analysis_fp = Analysis(order_fp, 'duration', ['case_order'])

order_sw = order_data_prep(clean_sw, 'social_worker')
order_analysis_sw = Analysis(order_sw, 'duration', ['case_order'])

torder_fp = order_data_prep(trim_fp, 'foster_parent') 
torder_analysis_fp = Analysis(order_fp, 'duration', ['case_order'])

torder_sw = order_data_prep(trim_sw, 'social_worker')
torder_analysis_sw = Analysis(order_sw, 'duration', ['case_order'])

# individual improvement
slim_sw = torder_sw[torder_sw['case_count']>3]
coef_sw, imp_sw = coef_data_prep(slim_sw, 'social_worker', 'duration', 'case_order')

# removing years before 2005 and after 2012
test1 = order_sw.groupby(order_sw['placed_dt'].map(lambda x: x.year))['duration'].mean()
test2 = order_sw.groupby(order_sw['placed_dt'].map(lambda x: x.year))['duration'].std()
test3 = order_sw.groupby(order_sw['placed_dt'].map(lambda x: x.year)).size()

test_df = slim_sw[(slim_sw['placed_dt']>datetime.date(2005,01,01)) & (slim_sw['placed_dt']<datetime.date(2012,12,31))]
coef_test, imp_test = coef_data_prep(test_df, 'social_worker', 'duration', 'case_order')

# # time experience analysis
# exp_fp = exp_data_prep(clean_fp, 'foster_parent')
# exp_sw = exp_data_prep(clean_sw, 'social_worker')

# exp_analysis_fp = Analysis(exp_fp, 'duration', ['exp'])
# exp_analysis_sw = Analysis(exp_sw, 'duration', ['exp'])

# unclip = drop_na(pos, ['social_worker'])
# exp_unclip = exp_data_prep(unclip)
# exp_u_analysis = Analysis(exp_unclip, 'duration', ['fp_exp', 'sw_exp'])

# # subsequent change analysis
# change_fp = change_data_prep(trim_fp, 'foster_parent')

# social worker attributes

# foster parent attributes
















