# Energy-Price-ENTSOE

The code is for an application that retrieves price information from the Entsoe transparency portal. It fetches price data starting from a requested date up to the current date. The values are converted from Megawatt-hour (MWh) to Kilowatt-hour (kWh).

The code imports the necessary libraries, defines the URL for accessing the price data, and defines two functions: **update_dataset** for updating the dataset and **convert_date** for converting values to date format.

Next, the code reads a CSV file named 'EntsoeEnergyPrice.csv' into a DataFrame called **df** and converts the **'Date'** column to date format.

Then, it determines the oldest and most recent dates present in the dataset, as well as today's date. The code checks if the dataset needs to be updated based on the difference between the most recent date and today.

After that, it creates lists of dates: **datesL** for the most recent dates and **datesE** for the oldest dates. The code retrieves the price information by calling the update_dataset function with the appropriate dates and updates the **df_comb** DataFrame.

Following that, the code performs data cleaning steps such as renaming columns, splitting columns, and converting price units.

Finally, the code concatenates the original DataFrame (**df**) with the updated DataFrame (**df_comb**), corrects the date formatting, and saves the resulting DataFrame to a CSV file named **'EntsoeEnergyPrice.csv'**.

*It's important to note that the code assumes the existence of the 'EntsoeEnergyPrice.csv' CSV file and may require modifications or additional dependencies to run correctly.*
