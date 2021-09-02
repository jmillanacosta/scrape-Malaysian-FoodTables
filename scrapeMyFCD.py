#!/usr/bin/env python
# coding: utf-8

# # Scraping the Food Composition Tables from the [Malaysian Food Composition Database (MYFCD)](https://myfcd.moh.gov.my/myfcdcurrent/)
# 
# ## Introduction
# The Malaysian Food Composition tables are not available for download, but they can be consulted at [MyFCD](https://myfcd.moh.gov.my/myfcdcurrent/). This is a Python script that opens the MyFCD website, scrapes all data from the food composition tables, and returns the nutritional information for each entry in a .csv file.
# 
# It is convenient to run this script every time the MyFCD is updated in order to retrieve the latest food composition data.
# 
# There are two sources: 
# * [The current Malaysian FCD](https://myfcd.moh.gov.my/myfcdcurrent), with around 170 food items at the moment
# * [The Industry module](https://myfcd.moh.gov.my/myfcdindustri), with around 330 items at the moment

# ## Imports
# ### Libraries

import json
import requests
import re
import pandas as pd


# ## A) Scraping the current Malaysian FCD Module

# ### Request al URLs contained in the dynamic javascript table at MyFCD
# Inspecting the html of FCD, I found all item identifiers are stored under the site https://myfcd.moh.gov.my/myfcdcurrent/index.php/ajax/datatable_data.
# All links to the food items look like this:
# `https://myfcd.moh.gov.my/myfcdcurrent/index.php/site/detail_product/RXXXXXX/0/168/-1/0/0`,
# where RXXXXXX is each individual identifier, and X any digit 0-9. The code below generates all food item URLs:

# Set up request parameters
headers={'User-Agent': 'Mozilla/5.0'}
identifierSite = "https://myfcd.moh.gov.my/myfcdcurrent/index.php/ajax/datatable_data"
r = requests.get(identifierSite, headers=headers)
parsed = r.text
pattern = "R\d+\d+\d+\d+\d+\d+"
matches = re.findall(pattern, parsed)
# URLs to be generated contain matches inbetween strings url1 and url1
url1, url2 = "https://myfcd.moh.gov.my/myfcdcurrent/index.php/site/detail_product/", "/0/168/-1/0/0"
# Create list to store all URLs
urls = []
# Assemble each identifier's URL
for match in matches:
    url = "".join(("".join((url1, match)), url2))
    urls.append(url)


# ### Create the nutrition dictionary that will gather and store the data scraped from the website


nutrition = dict()
# Analyze each URL (each food)
for url in urls:
    # Request web
    my = requests.get(url, headers=headers)
    # Parse html to string
    parsed = str(my.content)
    # Food name is between headers <h3>
    nameIndex = ((len("<h3>") + parsed.find("<h3>")), (parsed.find("</h3")))
    name = parsed[nameIndex[0]:nameIndex[1]]
    ## Exclude the code at the end of the name
    indexCode = name.find("<")
    name = name[0:indexCode]
    # Retrieve the JSON containing nutrition values
    beginJSON = parsed.find("var product_nutrients =  ")
    beginJSON = beginJSON + len("var product_nutrients =  ")
    endJSON = parsed.find(";\\n", beginJSON)
    nutriJSON = parsed[beginJSON:endJSON]
    nutriJSON = json.loads(nutriJSON)
    # Create list to store nutritional values for this item
    nutrients = list()
    # Retrieve the subdictionary entry containing the value of each nutrient
    for nutrient in nutriJSON.keys():
        value = nutriJSON[nutrient]["value"]
        nutrientValue = (nutrient, value)
        nutrients.append(nutrientValue)
    # Append each entry to the nutrition dictionary
    nutrition[name] = dict(nutrients)


# # B) Scraping the Industry Module
# Process is similar to before, but the website with all identifiers is https://myfcd.moh.gov.my/myfcdindustri//static/DataTables-1.10.12/examples/server_side/scripts/server_processing.php in this case. The URLs look like this:
# `https://myfcd.moh.gov.my/myfcdindustri/index.php/site/detail_product/XXXXXXX/0/10/-1/0/0/`, where X is any digit from 0-9.


# Set up request parameters
headers={'User-Agent': 'Mozilla/5.0'}
identifierSite = "https://myfcd.moh.gov.my/myfcdindustri//static/DataTables-1.10.12/examples/server_side/scripts/server_processing.php"
r = requests.get(identifierSite, headers=headers)
parsed = r.text
pattern = "\d+\d+\d+\d+\d+\d+\d+"
matches = re.findall(pattern, parsed)
# URLs to be generated contain matches inbetween strings url1 and url1
url1, url2 = "https://myfcd.moh.gov.my/myfcdindustri/index.php/site/detail_product/", "/0/10/-1/0/0/"
# Create list to store all URLs
urls = []
# Assemble each identifier's URL
for match in matches:
    url = "".join(("".join((url1, match)), url2))
    urls.append(url)


nutritionIndustry = dict()
# Analyze each URL (each food)
for url in urls:
    # Request web
    # Request web
    my = requests.get(url, headers=headers)
    # Parse html to string
    parsed = str(my.content)
    # Food name is between headers <h3>
    nameIndex = ((len("<h3>") + parsed.find("<h3>")), (parsed.find("</h3")))
    name = parsed[nameIndex[0]:nameIndex[1]]
    ## Exclude the code at the end of the name
    indexCode = name.find("<")
    name = name[0:indexCode]
    # Retrieve the JSON containing nutrition values
    beginJSON = parsed.find("var product_nutrients =  ")
    beginJSON = beginJSON + len("var product_nutrients =  ")
    endJSON = parsed.find(";\\n", beginJSON)
    nutriJSON = parsed[beginJSON:endJSON]
    nutriJSON = json.loads(nutriJSON)
    # In this case, they did not add key names. To work as a dictionary, I will add dummy key names
    i = 0
    nutriJSONdict = dict()
    for item in nutriJSON:
        dummy = i
        i = i+1
        nutriJSONdict[dummy] = item
    nutriJSON = nutriJSONdict
    # Create list to store nutritional values for this item
    nutrients = list()
    # Retrieve the subdictionary entry containing the value of each nutrient
    for nutrient in nutriJSON.keys():
        value = nutriJSON[nutrient]["value"]
        nutrient = nutriJSON[nutrient]["name"]
        nutrientValue = (nutrient, value)
        nutrients.append(nutrientValue)
    # Append each entry to the nutrition dictionary
    nutritionIndustry[name] = dict(nutrients)


# # Export a csv combining both databases
# This csv will be formatted in R afterwards, but it is already utilizable and contrastable against MyFCD.

# Append the two databases into one dictionary
nutrition.update(nutritionIndustry)
# Create a data frame and export it in csv
nutritionDf = pd.DataFrame(nutrition)
nutritionDf.to_csv("fctMalaysia.csv")
# Create a JSON and export it too
with open("fctJSON", "w") as json_file:
        json.dump(nutrition, json_file)

