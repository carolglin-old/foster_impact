from datamung import *
from regression import *

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

# analysis-specific data prep

def add_order(df, column_to_order, date_column):
	new_df = df.sort([column_to_order, date_column])
	ordered = new_df.groupby(column_to_order).cumcount()
	return ordered

def order_data_prep(df):
	df['fp_case_order'] = add_order(df, 'foster_parent', 'placed_dt')
	df['sw_case_order'] = add_order(df, 'social_worker', 'placed_dt')
	df['fp_case_order'] = change_type(df['fp_case_order'], 'float')
	df['sw_case_order'] = change_type(df['sw_case_order'], 'float')
	df['fp_case_count'] = add_count(df, 'foster_parent')
	df['sw_case_count'] = add_count(df, 'social_worker')
	fp_names = uniques_to_list(df, 'foster_parent')
	sw_names = uniques_to_list(df, 'social_worker')
	fp_same_dates_list = check_dates(fp_names, 'foster_parent', df)
	sw_same_dates_list = check_dates(sw_names, 'social_worker', df)
	del_fp = remove_same_date(df, 'foster_parent', fp_same_dates_list)
	new_df = df[~del_fp]
	del_sw = remove_same_date(df, 'social_worker', sw_same_dates_list)
	new_df = new_df[~del_sw]
	final_df = new_df[['duration', 'fp_case_order', 'sw_case_order', 'fp_case_count', 'sw_case_count']]
	return final_df

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

# order analysis
pos = load_csv(root, '/working/clean_pos.csv')
pos = check_type(pos)

# trimming and segmenting data
trim = drop_na(pos, ['social_worker'])
trim = segment_data(trim, 30, trim['duration'].max(), 'duration')

order = order_data_prep(trim) 

order_analysis = Analysis(order, 'duration', ['fp_case_order', 'sw_case_order'])
















