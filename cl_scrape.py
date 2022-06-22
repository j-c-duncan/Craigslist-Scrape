#! Python 3
# Scrape housing prices from craigslist
# following instruction by: https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981

from requests import get
import datetime

ext = datetime.datetime.now
print(ext)

#get the first page of sterling housing prices
response = get('https://washingtondc.craigslist.org/search/nva/roo?hasPic=1&availabilityMode=0')
print(type(response))

from bs4 import BeautifulSoup
html_soup = BeautifulSoup(response.text, 'html.parser')

#get the macro container for the ousing posts
posts =  html_soup.find_all('li', class_='result-row')
print(type(posts)) # to double check we get a resultset
print(len(posts)) # verify 120 elements per page

#TODO: build out the loop
from time import sleep, time
import re
from random import randint
from warnings import warn
#from Ipython.core.display import clear_output
import numpy as np

#find the toal number of posts to limit the pagination
result_num = html_soup.find('div', class_= 'search-legend')
results_total = int(result_num.find('span', class_='totalcount').text)

pages = np.arange(0, results_total+1, 120)

iterations = 0

post_timing = []
post_hoods = []
post_title_texts = []
bedroom_counts = []
sqfts = []
post_links = []
post_prices = []

for page in pages:
    #get request
    response = get('https://washingtondc.craigslist.org/search/nva/roo?'
                    + 's='
                    + str(page)
                    + 'hasPic=1'
                    + '&availabilityMode=0')
    sleep(randint(1,5))
    
    #throw warning for status codes that are not 200
    if response.status_code != 200:
        warn('request: {}; Status code {}'.format(requests, response.status_code))
        
    #define html text
    page_htmlk = BeautifulSoup(response.text, 'html.parser')
        
    #define the posts
    posts = html_soup.find_all('li', class_='result-row')
        
    #extract data item-wise
    for post in posts:
            
        if post.find('span', class_='result-hood') is not None:
            #posting date
            #grab the datetime element 0 for date and 1 for time
            post_datetime = post.find('time', class_='result-date')['datetime']
            post_timing.append(post_datetime)
                
            #neighborhoods
            post_hood = post.find('span', class_='result-hood').text
            post_hoods.append(post_hood)
                
            #title text
            post_title = post.find('a', class_='result-title hdrlnk')
            post_title_text = post_title.text
            post_title_texts.append(post_title_text)
                
            #post link
            post_link = post_title['href']
            post_links.append(post_link)
               
            #remove the /n whitespace from each side, removes currency symbol and turns it into an int
            post_price = post.a.text.strip()
            post_prices.append(post_price)
                
            if post.find('span', class_='housing')is not None:
                    
                #if the first element is accidentally square footage
                if 'ft2' in post.find('span', class_='housing').text.split()[0]:
                    #make bedroom nan
                    bedroom_count = np.nan
                    bedroom_counts.append(bedroom_count)
                    #make sqft the first element
                    sqft = int(post.find('span', class_='housing').text.split()[0][:-3])
                    sqfts.append(sqft)
                        
                #if the length og the housing details element is more than 2
                elif len(post.find('span', class_='housing').text.split()) >2:
                    #therefore element 0 will be bedroom count
                    bedroom_count = post.find('span', class_='housing').text.replace('br','').split()[0]
                    bedroom_counts.append(bedroom_count)
                        
                    #and sqft will be number 3, so set these here and append
                    sqft = int(post.find('span', class_='housing').text.split()[2][:-3])
                    sqfts.append(sqft)
                #if there is num bedrooms but no sqft
                elif len(post.find('span', class_='housing').text.split()) == 2:
                        
                    #therefore element = will be bedroom count
                    bedroom_count = post.find('span', class_= 'housing').text.replace('br', '').split()[0]
                    bedroom_counts.append(bedroom_count)
                        
                    #and sqft will be number 3
                    sqft = np.nan
                    sqfts.append(sqft)
                        
                # if none of those conditions catch, make bedroom nan    
                else:
                    bedroom_count = np.nan
                    bedroom_counts.append(bedroom_count)
                        
                    sqft = np.nan
                    sqfts.append(sqft)
                    
                    post_datetime = np.nan
                    post_timing.append(post_datetime)
                    post_hood = np.nan
                    post_hoods.append(post_hood)
                    post_title_text = np.nan
                    post_title_texts.append(post_title_text)
                    post_link = np.nan
                    post_links.append(post_link)
                    post_price = np.nan
                    post_prices.append(post_price)
        
    iterations += 1
    print('Page ' + str(iterations) + " scraped successfully!")
            
print('\n')
print('Scrape complete!')

#verify the length of each list
print(len(post_timing))
print(len(post_hoods))
print(len(post_title_texts))
print(len(post_links))
print(len(post_prices))

#Make dataframe
import pandas as pd

apts = pd.DataFrame(
    {
    'posted': post_timing,
    'neighborhood': post_hoods,
    'post title': post_title_texts,
    'URL': post_links,
    'price': post_prices
    }
                    )
print(apts.info())
apts.head(10)
cur_dtl = datetime.datetime.today()
dt_str1 = '{:%d_%m_%Y_%H:%M}'.format(cur_dtl)
file_name = 'apts_' + dt_str1
print(dt_str1)

apts.to_csv('apts.csv')

import apts_charts.py
apts_charts()


#TODO: automate with tkinter so it will scrape based on other housing searches... 