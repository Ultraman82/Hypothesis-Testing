import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


def get_list_of_university_towns():   
    df = pd.read_csv('university_towns.txt', sep=r'\s{2,}', header=None).astype(str)
    df.columns = ["RegionName"]
    df["State"] = None
    state = ''
    for i in range(0,len(df)):    
        if '[edit]' in df.RegionName[i]:         
            state = df.RegionName[i].split('[')[0]     
            df = df.drop([i])    
        else:
            df['State'][i] = state
    df.RegionName = df.RegionName.str.split('\s\(').str[0]
    return df
get_list_of_university_towns()

df = pd.read_excel('gdplev.xls', index_col = 0, skiprows= 219, usecols=[4,6]).dropna().astype(float)
df.columns = ["GDP"]

def get_recession_start():

    for i in range(2,len(df)):
        if (df.GDP[i] < df.GDP[i-1]) and (df.GDP[i-1] < df.GDP[i-2]):
            #if (i-3) != -1 and df.GDP[i-3] < df.GDP[i-2]:
                return df.index[i]
get_recession_start()

def get_recession_end():
    rec = False    
    for i in range(2,len(df)):
        if (df.GDP[i] < df.GDP[i-1]) and (df.GDP[i-1] < df.GDP[i-2]):
            rec = True
            if ((df.GDP[i] > df.GDP[i-1]) and (df.GDP[i-1] > df.GDP[i-2])) and (rec == True):
                return df.index[i]
get_recession_end()   

def convert_housing_data_to_quarters():
    df = pd.read_csv('City_Zhvi_AllHomes.csv', index_col = 0).set_index(['State'])
    df['State'] = pd.Series(states)
    df = df.drop(df.columns[1:49], axis=1).set_index(['State','RegionName'])
    df = df.groupby(pd.PeriodIndex(df.columns, freq='q'), axis=1).mean() 
    df.columns = df.columns.strftime('%Yq%q')           
    return df
convert_housing_data_to_quarters()

def run_ttest():
    uni_town = get_list_of_university_towns().set_index(['State', 'RegionName']).index
    df = convert_housing_data_to_quarters()
    rec_start = get_recession_start()
    rec_end = get_recession_end()   
    df = df.loc[:, rec_start:rec_end]
    df['Growth'] = (df[rec_start] - df[rec_end]) > 0
    dfnu = df.drop(uni_town).dropna()
    dfu = df.loc[uni_town].dropna() 
    result = ttest_ind(dfu.Growth, dfnu.Growth)
    if result.pvalue>0.01:
        return (True, result.pvalue, "university town")
    else:
        return (False, result.pvalue, "non-university town")
run_ttest()    



