#!/usr/bin/env python
"""
Author: Javi Millán

Scrape the Malaysian Food Composition Database

"""
# This code retrieves a .csv and json with all entries in the Malaysian Food Composition Database.

## import statements
import textwrap
import json
import requests
import re
import pandas as pd
import time


# Define variables for each of the modules A, B, C.
### Shared properties ###
my_headers = {'User-Agent': 'Mozilla/5.0'}
title_tags = "<h3>"
begin_JSON_tag, end_JSON_tag = "var product_nutrients =  ", ";\\n"

### A) Current module ###
# Set up request parameters
identifier_site_A = "https://myfcd.moh.gov.my/myfcdcurrent/index.php/ajax/datatable_data"
pattern_A = "R\d+\d+\d+\d+\d+\d+" # Identifier for each food item
url1_A, url2_A = "https://myfcd.moh.gov.my/myfcdcurrent/index.php/site/detail_product/", "/0/168/-1/0/0" # Each pattern goes inbetween these

### B) Industry module ###
identifier_site_B = "https://myfcd.moh.gov.my/myfcdindustri//static/DataTables-1.10.12/examples/server_side/scripts/server_processing.php"
pattern_B = "\d+\d+\d+\d+\d+\d+\d+" # Identifier for each food item
url1_B, url2_B = "https://myfcd.moh.gov.my/myfcdindustri/index.php/site/detail_product/", "/0/10/-1/0/0/" # Each pattern goes inbetween these

### C) 1997 module ###
identifier_site_C = "https://myfcd.moh.gov.my/myfcd97/index.php/ajax/datatable_data"
pattern_C = "\d+\d+\d+\d+\d+\d+" # Identifier for each food item
url1_C, url2_C = "https://myfcd.moh.gov.my/myfcd97/index.php/site/detail_product/", "/0/10/-1/0/0/" # Each pattern goes inbetween these


# Functions
## Function that returns all food item sites (urls). Identifier site is where the JS table data is stored.
def requestFoodItems(headers, identifier, pattern, url1, url2):
    r = requests.get(identifier, headers=headers)
    parsed = r.text
    matches = re.findall(pattern, parsed)
    urls = []
    # Assemble each identifier's URL
    progress = 0
    for match in matches:  
        progress += 1
        url = "".join(("".join((url1, match)), url2))
        urls.append(url)
        print("Gathering all food item URLS... {}/{}".format(progress, len(matches)))
    return urls


## A function that creates the nutrition dictionary that will gather and store the data scraped from the website

def make_nutrition_tables(urls, headers, make_dummy_dict, fix_nutrient_name = False):
    nutrition = dict()
    # Analyze each URL (each food)
    progress_urls = 0
    for url in urls:
        time.sleep(2)
        progress_urls += 1
        print("Requesting url #{}/{}".format(progress_urls, len(urls)))
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
        print("Creating food item dictionary...")
        if(make_dummy_dict == True): # In Modules B) and C) they did not add key names. To work as a dictionary, I will add dummy key names           
            i = 0
            nutriJSONdict = dict()
            for item in nutriJSON:
                dummy = i
                i = i+1
                nutriJSONdict[dummy] = item
            nutriJSON = nutriJSONdict
            print("Added item #{} to the dictionary...".format(i))
        # Create list to store nutritional values for this item
        nutrients = list()
        # Retrieve the subdictionary entry containing the value of each nutrient
        for nutrient in nutriJSON.keys():
            value = nutriJSON[nutrient]["value"]
            if(fix_nutrient_name == True): # The JSON from C) Module 1997 doesn´t name each nutrient entry by its name, but the name can be found as a key.
                nutrient = nutriJSON[nutrient]["name"]
            nutrientValue = (nutrient, value)
            nutrients.append(nutrientValue)
            print("Food item: {}, nutrient: {} successfully added to dictionary".format(name, nutrient))
        # Append each entry to the nutrition dictionary
        nutrition[name] = dict(nutrients)
    print("Finished scraping this module.")
    return nutrition

# Main

def main():
    """
    Scrape the Malaysian Food Composition Database
    
    """
    delim = '-' * 79
    print(textwrap.dedent(
        """
        Title:\t\tScrape the Malaysian Food Composition Database
        Author:\t\tJavi Millán
        Date:\t\tSeptember 2021
        Important:\tRequests are slowed down to play nice with the website. Code will take some minutes.
        {}""".format(delim)
    ))
    
    # Request all urls
    print("Requesting urls for module A)")
    urls_A = requestFoodItems(my_headers, identifier_site_A, pattern_A, url1_A, url2_A)
    print("Requesting urls for module B)")
    urls_B = requestFoodItems(my_headers, identifier_site_B, pattern_B, url1_B, url2_B)
    print("Requesting urls for module C)")
    urls_C = requestFoodItems(my_headers, identifier_site_C, pattern_C, url1_C, url2_C)
    
    # Fill up nutrition dictionary
    print("Creating nutrition dictionary for all modules")
    nutrition = make_nutrition_tables(urls_A, my_headers, make_dummy_dict = False)
    nutrition_B = make_nutrition_tables(urls_B, my_headers, make_dummy_dict = True) 
    nutrition_C = make_nutrition_tables(urls_C, my_headers, make_dummy_dict = True, fix_nutrient_name =True)
    nutrition.update(nutrition_B)
    nutrition.update(nutrition_C)
    # Create a data frame and export it in csv
    nutritionDf = pd.DataFrame(nutrition)
    nutritionDf.to_csv("fctMalaysia.csv")
    # Create a JSON and export it too
    with open("fctJSON", "w") as json_file:
            json.dump(nutrition, json_file)
    print("Successfully exported fctJSON.JSON and fctMalaysia.csv.")

if __name__ == "__main__":
    main()
