#!/usr/bin/env python
# coding: utf-8

# # Energy Price
# 
# This application retrieves the price information provided by the Entsoe transparency portal, 
# starting from the requested date up to today's date. The values are transformed from MWh to KWh.

# #### Importing Libraries

# In[9]:


import pandas as pd
import requests
import csv
from datetime import timedelta, datetime


# #### Define the url

# In[10]:


# URL
start_url = 'https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show?name=&defaultValue=false&viewType=TABLE&areaType=BZN&atch=false&dateTime.dateTime='
end_url = '+00:00|CET|DAY&biddingZone.values=CTY|10YNL----------L!BZN|10YNL----------L&resolution.values=PT60M&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)'


# #### Read the csv file

# In[11]:


df = pd.read_csv('EntsoeEnergyPrice.csv', parse_dates=['Date'], dayfirst=True)


# #### Define the Date

# In[12]:


# The earliest date in the dataset
min_date = pd.to_datetime(df['Date'].min(), format='%Y-%m-%d').date()

# The latest date in dataset
max_date = pd.to_datetime(df['Date'].max(), format='%Y/%m/%d').date()

# Today date
today = datetime.today().date()

print('Earliest date found in the dataset:', min_date)
print('Latest date found in the dataset:', max_date)
print('Today\'s date:', today)


# In[13]:


# Create list of the days that are missing
datesL = [] # Lastest Dates
datesE = [] # Earlist Dates

# Days of difference between today and lastest date
dif_days = (today - max_date).days

# Check if the dataset is updated
if dif_days != 0:
    print('The difference between the latest date and today is:', dif_days, 'days')
else:
    print('The dataset is updated!')

# Updated the dates of interesting
# Lastest Dates
if dif_days != 0:
    for i in range(dif_days):
        max_date += timedelta(days=1)
        datesL.append(max_date.strftime("%d-%m-%Y"))
        
# Earlist Dates
for i in range(7):
    min_date = min_date - timedelta(days=1)
    datesE.append(min_date.strftime("%d-%m-%Y"))

    
print(min_date)
print(max_date)    
    
print(datesL)
print(datesE)


# #### Get the Price information based on the dates

# In[14]:


# Create a temporary DataFrame to store the daily price 
df_comb = pd.DataFrame() # Temporary DataFrame combine the prices with the original
df_tempE = pd.DataFrame() # Temporary DataFrame for prices (earliest dates)
df_tempL = pd.DataFrame() # Temporary DataFrame for prices (latest dates)

# Updating the dataset with latest dates
if dif_days != 0:
    for actual_date in datesL:
        # Create a URL with the new date
        url = start_url + actual_date.replace("-", ".") + end_url

        # Copy the information from the URL into a temporary DataFrame
        df_tempL = pd.read_html(url)[0]

        # Add a Date column to the temporary DataFrame
        df_tempL['Date'] = actual_date

        # Append the information from the temporary DataFrame to the combined DataFrame
        df_comb = pd.concat([df_comb, df_tempL], ignore_index=True)
        
# Updating the dataset with earliest dates
for actual_date in datesE:
    # Create a URL with the new date
    url = start_url + actual_date.replace("-", ".") + end_url

    # Copy the information from the URL into a temporary DataFrame
    df_tempE = pd.read_html(url)[0]

    # Add a Date column to the temporary DataFrame
    df_tempE['Date'] = actual_date

    # Append the information from the temporary DataFrame to the combined DataFrame
    df_comb = pd.concat([df_comb, df_tempE], ignore_index=True)


# #### Cleaning the data

# In[15]:


#Drop the first level of columns
df_comb.columns = df_comb.columns.droplevel()

#Rename the Columns
df_comb = df_comb.rename(columns={
    "index": "Index",
    "MTU": "start-end [time]",
    "Day-ahead Price": "Import Grid (EUR/kWh)",
    "": "Date"
})

#Split the hours in start e end
df_comb[['Hour', 'End']] = df_comb['start-end [time]'].str.split('-', expand=True)

#Remove blank spaces
df_comb['Hour'] = df_comb['Hour'].str.strip()
df_comb['End'] = df_comb['End'].str.strip()

#Remove the original column
df_comb.drop('start-end [time]', axis=1, inplace=True)
df_comb.drop('End', axis=1, inplace=True)

#Creating a new column Price and converting the MWh to KWh
df_comb['Import Grid (EUR/kWh)'] = df_comb['[EUR / MWh]'] / 1000
df_comb = df_comb.drop('[EUR / MWh]', axis=1)

# Append the information from the temporary DataFrame to the original
df = pd.concat([df, df_comb], ignore_index=True)


# #### Salving the date in a CSV file

# In[16]:


# Save in a csv file
df.to_csv('EntsoeEnergyPrice.csv', index=False)

