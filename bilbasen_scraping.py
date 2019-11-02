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

class CarConfigurator:
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
     
    def __init__(self, categ, brand, model, **kwargs):
        query_dict = dict()
        for key, val in kwargs.items():
            query_dict[key] = val

        for key, val in standard_config:
            if not query_dict.get(key):
                query_dict(key) = val

        self.new_path = os.path.join('/brugt', categ, brand, model)

    def add_entry(self, key, val):
        if not query_dict.get(key):
            query_dict(key) = val

    def query_tuples(self):
        return list(query_dict.item())

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
    parsed_content = sct.parse_content(response.content, xpath)
    formatted_content = [item.strip() for item in parsed_content if item.strip()]
    print(formatted_content)
    df = pd.DataFrame()
    for col in col_regex:
        regex = col_regex.get(col)
        col_vals = [val if regex.search(val) else '' for val in formatted_content]
        print(col_vals)
        df[col] = col_vals

    return df



url = 'https://www.bilbasen.dk/brugt/bil/Mazda/2?make=Mazda&model-Mazda=5&model-Mazda=6&Fuel=1&YearFrom=0&YearTo=0&PriceFrom=175000&PriceTo=250000&MileageFrom=-1&MileageTo=75000&IncludeEngrosCVR=true&IncludeLeasing=true'
#https://www.bilbasen.dk/brugt/bil/mazda/6?includeengroscvr=false&yearfrom=2012&mileageto=200000&pricefrom=0&includeleasing=false&fuel=1&cartypes=stationcar&includewithoutvehicleregistrationtax=false&includesellforcustomer=false&page=2
parsed_url = urlparse(url)

#parsed_query = parse_qs(parsed_url.query)
new_path, query_tuples = car_configurator('Bil', 'Mazda', '6',
        fuel='1')  
new_query = urlencode(query_tuples)
pu_replaced = parsed_url._replace(path=new_path, query=new_query)
new_url = pu_replaced.geturl()
resp = requests.get(new_url, headers={'User-Agent':'test'}) #random headers
#must be passed for getting response
xpath_headline = \
'//div[@class="col-xs-4"]//a[@class="listing-headline"]//text()'
xpath_heading = \
'//div[@class="col-xs-4"]//a[@class="listing-heading dark Link"]//text()'
xpath_description= \
'//div[@class="col-xs-4"]//div[@class="listing-description-short expandable-box"]//text()'
xpath_params = '//div[@class="col-xs-6"]//text()'

df_descriptions = format_content(resp, xpath_description, {'title': [0, 2],
    'descr': [1, 2]}) 
#df_params = format_content(resp, xpath_params, {'kml': [6, 6], 'km': [7, 6],
#     'Year': [8, 6], 'price': [9, 6], 'location': [10, 6]})

car_config_regex = {'kml': re.compile(r'[k][m][/][l]'), 
         'km': re.compile(r'[0-9]{2}[.][0-9]{3}$'),
         'Year': re.compile(r'[0-9]{4}$'),
         'price': re.compile(r'[0-9]{2}[.][0-9]{3}\s[k][r][.]$')}
 
df_params = format_content(resp, xpath_params, car_config_regex) 

df_params.loc[:, 'kml'] = df_params.kml.str[:-5].str.replace(',','.').astype(float)
df_params.loc[:, 'km'] = df_params.km.str.replace('.','').astype(int)
df_params.loc[:, 'Year'] = df_params.Year.astype(int)
df_params.loc[:, 'price'] = df_params.price.str[:-4].str.replace('.','').astype(int)
