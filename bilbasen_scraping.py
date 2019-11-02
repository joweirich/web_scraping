"""
Scraping of bilbasen.dk
"""
import os
from urllib.parse import urlparse, parse_qsl, urlencode
from collections import defaultdict
import requests
import pandas as pd
import re
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor 
import scraping_tools as sct

standard_config = [('fuel', '0'),
                   ('yearfrom', '0'),
                   ('yearto', '0'),
                   ('pricefrom', '0'),
                   ('priceto', '10000000'),
                   ('mileagefrom', '-1'),
                   ('mileageto', '10000001'),
                   ('includeengroscvr', 'true'),
                   ('includeleasing', 'true'),
                   ('page', '1')] 
class CarConfigurator:
    

    def __init__(self, categ, brand, model, **kwargs):
        self.query_dict = dict()
        for key, val in kwargs.items():
            self.query_dict[key] = val

        for key, val in standard_config:
            if not self.query_dict.get(key):
                self.query_dict[key] = val

        self.new_path = os.path.join('/brugt', categ, brand, model)

    def add_entry(self, key, val):
        if not self.query_dict.get(key):
            self.query_dict[key] = val
    
    def replace_entry(self, key, val):
        if not self.query_dict.get(key):
            print('Warning, entry does not exist')
        
        self.query_dict[key] = val

    @property
    def query_tuples(self):
        return list(self.query_dict.items())

def car_configurator(categ, brand, model, **kwargs):
    """
    Create parsed query from car parameters
    """
    
    query_dict = dict()

    for key, val in kwargs.items():
        query_dict[key] = val

    for key, val in standard_config:
        if not query_dict.get(key):
            query_dict[key] = val

    query_tuples = list(query_dict.items())

    new_path = os.path.join('/brugt', categ, brand, model)

    return new_path, query_tuples

def format_content(response, xpath, col_regex):
    '''returns dataframe with data from response, based on given xpath'''
    parsed_content = sct.parse_content(response.content, xpath)
    #print(parsed_content)
    formatted_content = [item.strip() for item in parsed_content if
            item.strip()]
    #print(formatted_content)
    df = pd.DataFrame()

    for col in col_regex:
        regex = col_regex.get(col)
        print('regex', regex)
        col_vals = [val for val in formatted_content if regex.search(val)]
        print(col_vals)
        print(f'len of col_vals {len(col_vals)}')
        df[col] = col_vals
        print(df)

    return df



url = 'https://www.bilbasen.dk/brugt/bil/Mazda/2?make=Mazda&model-Mazda=5&model-Mazda=6&Fuel=1&YearFrom=0&YearTo=0&PriceFrom=175000&PriceTo=250000&MileageFrom=-1&MileageTo=75000&IncludeEngrosCVR=true&IncludeLeasing=true'
car_config_regex = {'kml': re.compile(r'[k][m][/][l]'), 
         'km': re.compile(r'[0-9]{1}[.][0-9]{3}$'),
         'Year': re.compile(r'[0-9]{4}$'),
         'price': re.compile(r'[0-9]{2}[.][0-9]{3}\s[k][r][.]$')}
 
Mazda6 = CarConfigurator('Bil', 'Mazda', '6',
        fuel='1', mileagefrom = 1000 )  

#must be passed for getting response
xpath_headline = \
'//div[@class="col-xs-4"]//a[@class="listing-headline"]//text()'
xpath_heading = \
'//div[@class="col-xs-4"]//a[@class="listing-heading dark Link"]//text()'
xpath_description= \
'//div[@class="col-xs-4"]//div[@class="listing-description-short expandable-box"]//text()'
xpath_params = '//div[@class="col-xs-6"]//text()'

df_result = pd.DataFrame() 

for page in range(1,10):
    Mazda6.replace_entry('page', page)
    parsed_url = urlparse(url)
    new_query = urlencode(Mazda6.query_tuples)
    pu_replaced = parsed_url._replace(path=Mazda6.new_path, query=new_query)
    new_url = pu_replaced.geturl()
    try:
        resp = requests.get(new_url, headers={'User-Agent':'test'}) #random headers
        df_descriptions = format_content(resp, xpath_description, {'title': [0, 2], 'descr': [1, 2]}) 
#df_params = format_content(resp, xpath_params, {'kml': [6, 6], 'km': [7, 6],
#     'Year': [8, 6], 'price': [9, 6], 'location': [10, 6]})
        df_params = format_content(resp, xpath_params, car_config_regex) 
        df.append(df_params)
    except Exception as e:
        print(e.__class__.__name__)    

df_result.loc[:, 'kml'] = df_results.kml.str[:-5].str.replace(',','.').astype(float)
df_result.loc[:, 'km'] = df_result.km.str.replace('.','').astype(int)
df_result.loc[:, 'Year'] = df_result.Year.astype(int)
df_result.loc[:, 'price'] = df_result.price.str[:-4].str.replace('.','').astype(int)
 
