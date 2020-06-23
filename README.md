# Info Season Animes
Scrapes informations from MyAnimeList for current season animes information.

## What it does:

This software has a simple proposal: getting informations about the animes season on MyAnimeList as a database.

The return is a JSON file:
- Common Title (String)
- English Title (String)
- Japanese Title (String)
- Description (String)
- Source (String)
- Genres (List)
- Currently Status (String)
- Episodes (Number)
- Current Episode (Number)
- Date First Episode (String)
- Date Next Episode (String)
- Date Last Episode (String)

OBS:
- Date is formated as: 'Month Day, Year'
Example: <Jun 21, 2020>

## Prerequisites

What things you need to install the software and how to install them

* Python 3.x
* Geckodriver
* Firefox
* Some Python libraries following

## Install the following Python libraries:

* **requests** - Requests is the only Non-GMO HTTP library for Python, safe for human consumption;
* **beautfulsoup4** - Library for pulling data out of HTML and XML files;
* **selenium** - An API to write functional/acceptance tests using Selenium WebDriver.

With:
```
pip install -r requirements.txt
```
### Geckodrier

[Find informatios for installion in the official repository.]
(https://github.com/mozilla/geckodriver/releases)

## Running the code
```
python scraper.py
```
