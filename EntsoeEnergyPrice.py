#!/usr/bin/env python
# coding: utf-8

# # Energy Price
# 
# The code is for an application that retrieves price information from the Entsoe transparency portal. It fetches price data starting from a requested date up to the current date. The values are converted from Megawatt-hour (MWh) to Kilowatt-hour (kWh).
# 
# The code imports the necessary libraries, defines the URL for accessing the price data, and defines two functions: **update_dataset** for updating the dataset and **convert_date** for converting values to date format.
# 
# Next, the code reads a CSV file named 'EntsoeEnergyPrice.csv' into a DataFrame called **df** and converts the **'Date'** column to date format.
# 
# Then, it determines the oldest and most recent dates present in the dataset, as well as today's date. The code checks if the dataset needs to be updated based on the difference between the most recent date and today.
# 
# After that, it creates lists of dates: **datesL** for the most recent dates and **datesE** for the oldest dates. The code retrieves the price information by calling the update_dataset function with the appropriate dates and updates the **df_comb** DataFrame.
# 
# Following that, the code performs data cleaning steps such as renaming columns, splitting columns, and converting price units.
# 
# Finally, the code concatenates the original DataFrame (**df**) with the updated DataFrame (**df_comb**), corrects the date formatting, and saves the resulting DataFrame to a CSV file named **'EntsoeEnergyPrice.csv'**.
# 
# *It's important to note that the code assumes the existence of the 'EntsoeEnergyPrice.csv' CSV file and may require modifications or additional dependencies to run correctly.*

# #### Importing Libraries

# In[1]:


import pandas as pd
import numpy as np
from datetime import timedelta, datetime


# #### Define the url

# In[2]:


# URL
start_url = 'https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show?name=&defaultValue=false&viewType=TABLE&areaType=BZN&atch=false&dateTime.dateTime='
end_url = '+00:00|CET|DAY&biddingZone.values=CTY|10YNL----------L!BZN|10YNL----------L&resolution.values=PT60M&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)'


# #### Functions

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


# In[4]:


def convert_date(value):
    try:
        return pd.to_datetime(value).date()
    except ValueError:
        return np.nan   


# #### Read the csv file

# In[5]:


# Read the original dataset
df = pd.read_csv('EntsoeEnergyPrice2.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.head()


# #### Define the Date

# In[6]:


df['Date'] = pd.to_datetime(df['Date'])

# The earliest date in the dataset
min_date = df['Date'].min().date()

# The latest date in the dataset
max_date = df['Date'].max().date()

# Today's date
today = datetime.today().date()

print('Earliest date found in the dataset:', min_date)
print('Latest date found in the dataset:', max_date)
print('Today\'s date:', today)


# In[7]:


# Create list of the days that are missing
datesL = []  # Latest Dates
datesE = []  # Earliest Dates

# Create a temporary DataFrame to store the daily price 
df_comb = pd.DataFrame() 

# Days of difference between today and latest date
dif_days = (today - max_date).days

# Check if the dataset is updated
if dif_days != 0:
    
    # Create Latest Dates
    datesL = [(max_date + timedelta(days=i+1)).strftime("%d-%m-%Y") for i in range(dif_days)]
    
    # Updated the Latest Dates
    df_comb = update_dataset(datesL, "%d-%m-%Y", df_comb)
    
    # Print some information about the latest dates
    print('The difference between the latest date and today is:', dif_days, 'days')
    print("The list of latest days to be collected.")
    print(datesL)
    print('\n')
    
    # Create Earliest Dates
    datesE = [(min_date - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(1, 71)] # Change the days range
    
    # Updated the Earliest Dates
    if min_date >= pd.to_datetime("2012-01-01").date():
        df_comb = update_dataset(datesE, "%d-%m-%Y", df_comb)
    
    # Print some information about the Earliest dates    
    print("The list of Earliest days to be collected.")
    print(datesE)
    print('\n')
    
else:
    # Print some information about the latest dates
    print('The dataset is updated with the most recent data!')
    print('\n')
    
    # Create Earliest Dates
    datesE = [(min_date - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(1, 11)]
    
    # Updated the Earliest Dates
    if min_date >= pd.to_datetime("2012-01-01").date():
        df_comb = update_dataset(datesE, "%d-%m-%Y", df_comb)    
    
    # Print some information about the Earliest dates
    print("The list of Earliest days to be collected.")
    print(datesE)


# #### Cleaning the data

# In[8]:


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

# Converting MWh to kWh and Drop the old colunm
df_comb['Import Grid (EUR/kWh)'] = df_comb['[EUR / MWh]'] / 1000
df_comb.drop('[EUR / MWh]', axis=1, inplace=True)

# Creating a new column "Export Grid (EUR/kWh)" that is a copy of 'Import Grid (EUR/kWh)'
df_comb['Export Grid (EUR/kWh)'] = df_comb['Import Grid (EUR/kWh)']

# Replace values greater than zero with NaN in the "Export Grid (EUR/kWh)" column
df_comb.loc[df_comb['Import Grid (EUR/kWh)'] < 0, 'Import Grid (EUR/kWh)'] = np.nan

# Replace values less than or equal to zero with NaN in the "Import Grid (EUR/kWh)" column
df_comb.loc[df_comb['Export Grid (EUR/kWh)'] > 0, 'Export Grid (EUR/kWh)'] = np.nan
df_comb.loc[df_comb['Export Grid (EUR/kWh)'] < 0, 'Export Grid (EUR/kWh)'] = df_comb['Export Grid (EUR/kWh)'] * (-1)


# #### Concatenate the Dataframes

# In[9]:


# Append the information from the temporary DataFrame to the combined DataFrame
df = pd.concat([df, df_comb], ignore_index=True)


# #### Correction of the Date

# In[10]:


df['Date'] = df['Date'].apply(convert_date)


# #### Salving the date in a CSV file

# In[11]:


# Save to a CSV file
df.to_csv('EntsoeEnergyPrice.csv', index=False)

