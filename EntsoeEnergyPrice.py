#!/usr/bin/env python
# coding: utf-8

# # Energy Price
# 
# This application retrieves the price information provided by the Entsoe transparency portal, 
# starting from the requested date up to today's date. The values are transformed from MWh to KWh.

# #### Importing Libraries

# In[1]:


import pandas as pd
from datetime import timedelta, datetime


# #### Define the url

# In[2]:


# URL
start_url = 'https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show?name=&defaultValue=false&viewType=TABLE&areaType=BZN&atch=false&dateTime.dateTime='
end_url = '+00:00|CET|DAY&biddingZone.values=CTY|10YNL----------L!BZN|10YNL----------L&resolution.values=PT60M&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)'


# #### Function Update Dataset

# In[3]:


def update_dataset(dates, url_format, df_comb):
    for actual_date in dates:
        # Create a URL with the new date
        url = start_url + actual_date.replace("-", ".") + end_url

        # Copy the information from the URL into a temporary DataFrame
        df_temp = pd.read_html(url)[0]

        # Add a Date column to the temporary DataFrame
        df_temp['Date'] = pd.to_datetime(actual_date, format=url_format).strftime("%Y-%m-%d")

        # Append the information from the temporary DataFrame to the combined DataFrame
        df_comb = pd.concat([df_comb, df_temp], ignore_index=True)

    return df_comb


# #### Read the csv file

# In[4]:


# Read the original dataset
df = pd.read_csv('EntsoeEnergyPrice.csv', parse_dates=['Date'], dayfirst=True)


# #### Define the Date

# In[5]:


# Read the original dataset
df = pd.read_csv('EntsoeEnergyPrice.csv', parse_dates=['Date'], dayfirst=True)

# The earliest date in the dataset
min_date = df['Date'].min().date()

# The latest date in the dataset
max_date = df['Date'].max().date()

# Today's date
today = datetime.today().date()

print('Earliest date found in the dataset:', min_date)
print('Latest date found in the dataset:', max_date)
print('Today\'s date:', today)

# Create list of the days that are missing
datesL = []  # Latest Dates
datesE = []  # Earliest Dates

# Days of difference between today and latest date
dif_days = (today - max_date).days

# Check if the dataset is updated
if dif_days != 0:
    print('The difference between the latest date and today is:', dif_days, 'days')
else:
    print('The dataset is updated!')


# In[6]:


# Updated the dates of interest
# Latest Dates
if dif_days != 0:
    datesL = [(max_date + timedelta(days=i+1)).strftime("%d-%m-%Y") for i in range(dif_days)]

# Earliest Dates
datesE = [(min_date - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(1, 61)]

print("The list of days with data to be collected.")
print(datesL)
print(datesE)


# #### Get the Price information based on the dates

# In[6]:


# Create a temporary DataFrame to store the daily price 
df_comb = pd.DataFrame()  # Temporary DataFrame to combine the prices with the original

# Updating the dataset with latest dates
if dif_days != 0:
    df_comb = update_dataset(datesL, "%d-%m-%Y", df_comb)

# Updating the dataset with earliest dates
if min_date >= pd.to_datetime("2012-01-01").date():
    df_comb = update_dataset(datesE, "%d-%m-%Y", df_comb)


# #### Cleaning the data

# In[7]:


# Drop the first level of columns
df_comb.columns = df_comb.columns.droplevel()

# Rename the columns
column_mapping = {
    "index": "Index",
    "MTU": "start-end [time]",
    "Day-ahead Price": "Import Grid (EUR/kWh)",
    "": "Date"
}

df_comb.rename(columns=column_mapping, inplace=True)

# Split the hours in start and end
df_comb[['Hour', 'End']] = df_comb['start-end [time]'].str.split('-', expand=True)

# Remove blank spaces
df_comb['Hour'] = df_comb['Hour'].str.strip()
df_comb['End'] = df_comb['End'].str.strip()

# Remove the original column
df_comb.drop('start-end [time]', axis=1, inplace=True)
df_comb.drop('End', axis=1, inplace=True)

# Creating a new column "Price" and converting MWh to kWh
df_comb['Import Grid (EUR/kWh)'] = df_comb['[EUR / MWh]'] / 1000
df_comb.drop('[EUR / MWh]', axis=1, inplace=True)

df_comb['Export Grid (EUR/kWh)'] = df_comb['Import Grid (EUR/kWh)']

# Replace values greater than zero with 'ZERO' in the "Export Grid (EUR/kWh)" column
df_comb.loc[df_comb['Import Grid (EUR/kWh)'] < 0, 'Import Grid (EUR/kWh)'] = 0

# Replace values less than or equal to zero with zero in the "Import Grid (EUR/kWh)" column
df_comb.loc[df_comb['Export Grid (EUR/kWh)'] > 0, 'Export Grid (EUR/kWh)'] = 0
df_comb.loc[df_comb['Export Grid (EUR/kWh)'] < 0, 'Export Grid (EUR/kWh)'] = df_comb['Export Grid (EUR/kWh)'] * (-1)


# #### Salving the date in a CSV file

# In[10]:


# Append the information from the temporary DataFrame to the combined DataFrame
df = pd.concat([df, df_comb], ignore_index=True)

# Save to a CSV file
df.to_csv('EntsoeEnergyPrice.csv', index=False)

