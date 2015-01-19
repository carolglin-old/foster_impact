import pandas as pd
import numpy as np

root = '/Users/carollin/Dev/foster_impact/data' 

# load and trim data

def load_csv(filepath):
	data = pd.read_csv(root+filepath, na_values=['na'])
	return data

def segment_data(df, lower_val, upper_val, column_to_segment):
	column = getattr(df, column_to_segment)
	seg_data = df[(column>=lower_value) & (column<=upper_value)]
	return seg_data

def drop_na(df, column_list):
	clean_data = df.dropna(subset=column_list, how='any')
	return clean_data

def num_change(orig_df, new_df):
	n_before = len(orig_df)
	n_after = len(new_df)
	n_change = n_before - n_after
	return n_change

def uniques_to_list(df, column):
	uniques = df.groupby(column).size()
	uniques = pd.DataFrame(uniques, columns=['count']).reset_index()
	uniques_list = uniques[column].tolist()
	return uniques_list

# add columns

def add_count_column(df, column_to_count, new_column_name):
	count = df.groupby(column_to_count).size()
	count_df = pd.DataFrame(count, columns=[new_column_name]).reset_index()
	merged_df = pd.merge(df, count_df, how='left', on=column_to_count)
	return merged_df

def add_order_column(df, column_to_order, date):
	new_df = df.sort([column_to_order, date])
	ordered = new_df.groupby(column_to_order).cumcount()
	return ordered

def add_avg_column(df, column_to_group, column_to_avg, new_column_name):
	avg = df.groupby(column_to_group)[column_to_avg].mean()
	avg_df = pd.DataFrame(avg.values, index=avg.index, columns=[new_column_name]).reset_index()
	merged_df = pd.merge(df, avg_df, how='left', on=column_to_group)
	return merged_df

def subt_day_column(date_column1, date_column2):
	diff = ((date_column1 - date_column2) / np.timedelta64(1, 'D'))
	return diff

def categ_to_bool(cell, hastrait, notrait):
	if cell == hastrait:
		return 1
	elif cell == notrait:
		return 0
	else:
		return 'Error'

# figgeting with types

def check_type(column_list, end_type):
	for column in column_list:
		if column.dtypes == end_type:
			pass
		else:
			change_type(column, end_type)

def change_type(column, end_type):
	if end_type == 'float':
		column = column.astype(float)
	elif end_type == 'date':
		column = pd.to_datetime(column)
	elif end_type == 'int':
		column = column.astype(int)

# knock off unused columns for analysis

def create_final_df(df, required_columns):
	final_df = pd.DataFrame()
	for i in required_columns:
		final_df[i] = df[i]
	return final_df












