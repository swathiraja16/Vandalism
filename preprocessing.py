import math
import os
import time
import pandas as pd
from sklearn.utils import shuffle

def calculate_crm_feature(row, data):
    vandal = 0
    d = data.loc[(data['username'] == row['username']) & (data['revtime'] <= row['revtime'])]
    d.sort_values(['username', 'revtime'], ascending=True)
    if len(d) > 1:
        last_edited_page = d.iloc[[d.shape[0]-1]]
        if is_meta(last_edited_page.iloc[0]['pagetitle'].lower()) and is_meta(row['pagetitle'].lower()) and last_edited_page.iloc[0]['pagetitle'] == row['pagetitle']:
            vandal = 0
        else:
            vandal = 1
        return vandal
    return vandal

        
def calculate_fm_feature(row, data):
    vandal = 0
    # checks feature fm
    d = data.loc[(data['username'] == row['username']) and (data['revtime'] <= row['revtime'])]
    d.sort_values(['username', 'revtime'], ascending=True)

    for r in d.iterrows():
        if is_meta(r['pagetitle'].lower()):
            vandal = 0
        else:
            vandal = 1
        return vandal
    return vandal

def calculate_crm_vfs_feature(row, data):
    d = data.loc[(data['username'] == row['username']) & (data['revtime'] <= row['revtime'])]
    d.sort_values(['username', 'revtime'], ascending=True)
    
    three_min = 180000
    fifteen_min = 900000
    if len(d) > 1:
        last_edited_page = d.iloc[[d.shape[0]-1]]
        if is_meta(last_edited_page.iloc[0]['pagetitle'].lower()) & is_meta(row['pagetitle'].lower()) and last_edited_page.iloc[0]['pagetitle'] == row['pagetitle']:
                interval = row['revtime'] - last_edited_page.iloc[0]['revtime']

                if interval < three_min:
                    return 0, 1, 1
                elif interval >= three_min & interval <= fifteen_min:
                    return 1, 0 , 1
                else:
                    return 1, 1, 0
    return 0, 0, 0


def calculate_ntus_feature(row, data):
    #ntus :Whether or not the user edited a new page which is within 3 hops or less of the previous page and the time gap between the two edits exceeds 15 minutes. 
    vandal = 0
    d = data.loc[(data['username'] == row['username']) & (data['revtime'] <= row['revtime'])]
    d.sort_values(['username', 'revtime'], ascending=True)
    fifteen_min = 900000
    pagetitle = row['pagetitle']
    hop = len(d)
    if hop > 1:
        last_edited_page = d.iloc[[d.shape[0]-1]]
        hop_time_diff = row['revtime'] - last_edited_page.iloc[0]['revtime']

        if last_edited_page.iloc[0]['pagetitle'] != pagetitle and hop_time_diff >= fifteen_min:
            vandal = 0
        else:
            vandal = 1
        return vandal

    if hop > 2:
        second_last_page = d.iloc[[d.shape[0]-2]]
        hop_time_diff = row['revtime'] - second_last_page.iloc[0]['revtime']

        if second_last_page.iloc[0]['pagetitle'] != pagetitle and hop_time_diff >= fifteen_min:
            vandal = 0
        else:
            vandal = 1
        return vandal

    if hop > 3:
        third_last_page = d.iloc[[d.shape[0]-3]]
        hop_time_diff = row['revtime'] - third_last_page.iloc[0]['revtime']

        if third_last_page.iloc[0]['pagetitle'] != pagetitle and hop_time_diff >= fifteen_min:
            vandal = 0
        else:
            vandal =1
        return vandal
    return vandal

def is_meta(page):
    if page.startswith('user:') or page.startswith('user talk:') or page.startswith('talk:'):
        return 1
    else:
        return 0
    
def convert_to_millis(row, column):
    if row[column] == '-':
        return -1
    timestamp = pd.Timestamp(row[column])
    if type(timestamp) == pd.Timestamp:
        timestamp = pd.Timestamp(row[column])
        return timestamp.value
    else:
        return -1

def perform_preprocessing(merged_data, data):
    # sorting data on page title ,uname, rev time
    print "Sorting data"
    merged_data.sort_values(['pagetitle', 'username', 'revtime'], ascending=True)
    # computing features 
    print "fm"
    merged_data['fm'] = merged_data.apply(lambda row: calculate_fm_feature(row, data), axis=1)
    print "crm vfs"
    merged_data[['crmv', 'crmf', 'crms']] = merged_data.apply(lambda row: pd.Series(calculate_crm_vfs_feature(row, data)), axis=1)
    print "ntus"
    merged_data['ntus'] = merged_data.apply(lambda row: calculate_ntus_feature(row, data), axis=1)
    print "crm"
    merged_data['crm'] = merged_data.apply(lambda row: calculate_crm_feature(row, data), axis=1)
    
    # randomizing
    merged_data = shuffle(merged_data)
    write_to_file(merged_data)

def write_to_file(merged_data):
    # storing the preprocessed dataset
    print "storing preprocessed data."
    merged_data.to_csv('processed_data.csv', sep=',', encoding='utf-8', index=False)

    
def main():
    # access benign and vandal datasets
    #start = time.time()
    directory = os.path.join("vews_dataset_v1.1/")
    benign_data = pd.DataFrame()
    vandal_data = pd.DataFrame()
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".csv"):
                data = pd.read_csv(root + file_name, sep=',', usecols=['username', 'revid', 'revtime', 'pagetitle',
                                                                     'isReverted', 'revertTime'])
        
                data['revtime'] = data.apply(lambda row: convert_to_millis(row, 'revtime'), axis=1)
                data['revertTime'] = data.apply(lambda row: convert_to_millis(row, 'revertTime'), axis=1)
                if file_name.startswith("benign"):
                    data['vandal'] = 0
                    benign_data = benign_data.append(data, ignore_index=True)
                elif file_name.startswith('vandal'):
                    data['vandal'] = 1
                    vandal_data = vandal_data.append(data, ignore_index=True)

    # Merge benign and vandal data
    print "Merging benign and vandal datasets"
    merged_data = benign_data.append(vandal_data, ignore_index=True)
    perform_preprocessing(merged_data, data)
    
main()

