# Scraping the Food Composition Tables:
## [Malaysian Food Composition Database (MYFCD)](https://myfcd.moh.gov.my/myfcdcurrent/)

## Introduction
This code retrieves a .csv and json with all entries in the Malaysian Food Composition Database. I wrote this code to help some colleagues with their analyses: the Malaysian Food Composition tables are not available for download, but they can be consulted at [MyFCD](https://myfcd.moh.gov.my/myfcdcurrent/). The code opens the 3 modules in the MyFCD website, scrapes all relevant data from the food composition tables, and returns the relevant nutritional information for each entry in a .csv file (and a JSON too).

There are three sources: 
* [The current Malaysian FCD](https://myfcd.moh.gov.my/myfcdcurrent), with around 170 entries at the moment
* [The Industry module](https://myfcd.moh.gov.my/myfcdindustri), with around 330 entries at the moment
* [The 1997 Module](https://myfcd.moh.gov.my/myfcd97), with more than 1030 entries 

## A) Scraping the current Malaysian FCD Module
Request al URLs contained in the dynamic javascript table at MyFCD.
Inspecting the html of the FCD, I found all item identifiers are stored under this [site](https://myfcd.moh.gov.my/myfcdcurrent/index.php/ajax/datatable_data).

All links to the food items look like this:
`https://myfcd.moh.gov.my/myfcdcurrent/index.php/site/detail_product/RXXXXXX/0/168/-1/0/0`,
where RXXXXXX is each individual identifier, and X any digit 0-9.

## B) Scraping the Industry Module
Process is similar to before, but the website with all identifiers is [here](https://myfcd.moh.gov.my/myfcdindustri//static/DataTables-1.10.12/examples/server_side/scripts/server_processing.php) in this case. The URLs look like this:
`https://myfcd.moh.gov.my/myfcdindustri/index.php/site/detail_product/XXXXXXX/0/10/-1/0/0/`, where X is any digit from 0-9.

## C) Scraping the 1997 Module
Process is similar to before, but the website with all identifiers is [here](https://myfcd.moh.gov.my/myfcd97/index.php/ajax/datatable_data) in this case. The URLs look like this:
`hhttps://myfcd.moh.gov.my/myfcd97/index.php/site/detail_product/XXXXXX/0/10/-1/0/0/`, where X is any digit from 0-9.
