Sixads Assignment
====================

## Author

__Ahsanuzzaman Khan__

## Project Description
You need to create a simple application which:

1. Using Youtube API (https://developers.google.com/youtube/v3/) scrapes channel videos with tags and stats. Also you need to track changes of video stats every N minutes in order to see how videos are performing. Please pick the interval to scan stats which, according to you, is efficient and smart. You can hardcode channel ID in code, that’s not important.
2. Create DB scheme and save scraped data. Please consider, that we will want to scan a
lot of channels, so queries to aggregate and select data shouldn’t take long. Use any database you feel right.
3. Create mini API, where you can filter videos:
- By tags.
- By video performance (first hour views divided by channels all videos first hour views median)

### Bonus points for:
- pseudo algorithm for fetching as many youtube channels as possible. 
- unit tests

## Overview:
According to the usecase, I've hardcoded `CHANNEL_ID` into environment file. Just after intitating this project, background tasks (`Celery`) will run to start scraping videos from that channel(s). I know there are lots of way to improvement. However, to start with I hope this project is good to go.

- Reason to use PostgreSQL: Just because of `Full Text search` which is implemented by `tag wise filtering`.
- Scrapping videos statistics: I have used `one` hour duration. Each hour my system will try to crawl each video's statistics with `celery beat schedule`.
- The system will always calculate `median` based on last statistics scrapped by system. Because, I don't think it would be wise, if we keep history of each video's statistics without very good reason. Till now, we don't have any reason to keep those.

## Thought
For fetching as many channels as possible we can maintain an unvisited channels list (database table) and call it from our background task to scap as many videos as possible.


## Requirements
- Python 3.8
- PostgreSQL
- Django
- Django REST Framework
- Faker
- Docker
- Celery
- Redis

## Developer requirements
- Factory Boy
- Pytest Django

## Installation
- Install `docker`
- Download this git repo
- Then go to project directory
- And run `make setup`

## To Run project
Go to project folder and run 
- `make runserver`

## Test project
Go to project folder and run 
- `make test`

## Project urls
- For displaying videos: `http://localhost:8000/`
- For fetching videos: `http://localhost:8000/videos/`

## Improvements
- Query can be optimized because as we crawl lots of videos, we need to find out how to optimise our query for selection.
- Find a way how to crawl as many channels as possible.
