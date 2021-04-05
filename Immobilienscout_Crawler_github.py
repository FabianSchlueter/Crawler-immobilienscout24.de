# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 23:34:05 2021

@author: Fabian Schlueter
"""
#%% Import packages.

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import json
from datetime import datetime
import time
import pandas as pd
import numpy as np
#%%
# Set search urls and names for the data output
# URL: Order by date desc and add '&pagenumber=' at end
df_search = pd.DataFrame(np.array([
                                    ['Duesseldorf', 'https://www.immobilienscout24.de/Suche/de/nordrhein-westfalen/duesseldorf/wohnung-mieten?sorting=2&pagenumber=']
                                   ]),
                   columns=[
                            'filename', 
                            'url_master'
                            ])
# Storage of output files
path_main = r"C:\Users\Fabian\Immobilienscout\\"

def captcha_check(html):
    html_red = html.split('</title>')[0].split('<title>')[1]
    if 'Ich bin kein Roboter - ImmobilienScout24' in html_red:
        input("Please solve the captcha and accept cookies. Then press any key to continue.")
        print('Continuing search.')

#%%
# Open webbrowser
driver=webdriver.Chrome(r"C:\Users\Fabian\Downloads\chromedriver_win32\chromedriver.exe")

# Loop over every pair of search parameters
for filename, url_master in zip(list(df_search['filename']), list(df_search['url_master'])):
    print('Search in ' + filename + ' with url ' + url_master)
    # Open output from previous search if existing. New results will be appended.
    path = path_main + filename + ".xlsx"
    try:
        df = pd.read_excel(path)
    except FileNotFoundError: 
        df = pd.DataFrame()
    
    # Open first result page to get the number of result pages
    i = 1
    url = url_master + str(i)
    driver.get(url)
    WebDriverWait( driver, 5)
    html = driver.page_source
    # Check for captcha. If captcha then solve it manually
    captcha_check(html)
#%%
    # Get number of result pages
    # If the number cannot be found then it is always 1
    try:
        html = driver.page_source
        html_red = html.split('</a></li><li class="p-items p-next vertical-center-container">')[0]
        html_red = html_red[-3:]
        html_red = html_red.split('>')[1]
        num_pag = int(html_red)
    except:
        num_pag = 1

    print('Number of SRP: ' + str(num_pag))
    
#%%
    # Loop over all result pages
    for i in range(1, num_pag+1):
        print(datetime.now().strftime("%H:%M:%S"))
        print('Reading SRP number ' + str(i))
        url = url_master + str(i)
        # Open result page
        driver.get(url)
        WebDriverWait( driver, 5)
        html = driver.page_source
        # Check for captcha. If captcha then solve it manually
        captcha_check(html)

        # Make list of all offers
        offer_list = []
        offers = driver.find_elements_by_xpath("//*[contains(@id,'result-')]")
        for o in offers:
            offer_list.append(o.get_attribute('id'))
        
        # Reduce offer list to offers that are not already downloaded in previous execution. Those are listed in df["url"].
        offer_list_unreduced = offer_list # for debugging
        try:
            offer_list = [item for item in offer_list if "https://www.immobilienscout24.de/expose/" + item.split("-")[2] not in list(df["url"])]
        except:
            print("First results for this search.")
    
        
        if len(offer_list) == 0:
            print('No new offers in offer list at SRP number ' + str(i))
            break
        # Loop over all offers in offer list
        for o in offer_list:
            url = "https://www.immobilienscout24.de/expose/" + o.split("-")[2]
            try:
                driver.get(url)
                WebDriverWait( driver, 5 )
                html = driver.page_source
                # Check for captcha. If captcha then solve it manually
                captcha_check(html)

                time.sleep(2)
                
                html = driver.page_source   
                # All features are writte in json format within html source code
                # Get the json part
                html_red = html.split('keyValues = ')[1]
                html_red = html_red.split(r'};')[0] + r'}'
                # Feature "Online since" is out of json part
                html_since = html.split('exposeOnlineSince: "')[1]
                html_since = html_since.split(r'",')[0]
                
                # Dictionary for storing data
                re_dict = {}
            
                re_dict = json.loads(html_red)
            
                re_dict["url"] = url
                re_dict['date'] = datetime.now().strftime("%Y-%m-%d")
                re_dict['time'] = datetime.now().strftime("%H:%M:%S")
                re_dict['OnlineSince'] = html_since
            
            
                re_re_dict = {}
                re_re_dict["URL"] = re_dict
                # Transpose dict and store in datafram
                df_append = pd.DataFrame(re_re_dict).T
                # Append to main dataframe
                df=df.append(df_append)
                
            except Exception as e: 
                    print(str(e) + 'for offer ' + o.split("-")[1])
    
        print(datetime.now().strftime("%H:%M:%S"))
        print('Appended data from SRP number ' + str(i) + '. No of offers: ' + str(len(offer_list)))
    
    df.drop_duplicates(subset ="url", inplace=True) 
    df.to_excel(path, index=False)  