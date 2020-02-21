### Pa. DDAP inspection scraper

Python script built with Scrapy to scrape inspections from Pa. Department of Drug and Alcohol Programs website.

#### Requirements

- Python 3.6+

#### Install

1. Open the terminal. Clone the project repo:

    `git clone https://github.com/SimmonsRitchie/ddap_scraper.git`

2. If you don't have pipenv installed on your machine, run:

    `pip install pipenv`

3. Navigate into the project directory:

    `cd ddap_scraper`
     
4. Use pipenv to create a virtual environment and install the project 
dependencies. Run:

    `pipenv install`

#### Run

This project uses Scrapy and takes advantage of its excellent CLI.

In the terminal, navigate to the project's root directory and then into the ddap directory:

`cd ddap`

To begin the scrape and generate a CSV of scraped data, run:

`scrapy crawl inspections -o scraped_data.csv`

To generate a JSON or XML file, just swap the file extension. Eg.

`scrapy crawl inspections -o scraped_data.json`

