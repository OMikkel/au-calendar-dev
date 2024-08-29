# AU Calendar Middleware

## Features

- Automatically downloads your personal calendar

- Adds readable adresses to all building numbers (if available)

- Updates the notes with location and building number in case the location property should fail

- Only needs your icalKey from https://mitstudie.au.dk ![icalKey image](https://imgur.com/o7xToCZ)


## Guide

1. Grab your icalKey from https://mitstudie.au.dk ![icalKey image](https://imgur.com/o7xToCZ)

2. Go to your calendar and create a subscription calendar with the following link https://au.omikkel.com/calendar?icalKey=[Your key]


## Additional Features

### Endpoints

If you want to colorcode lectures seperately from study cafe events you should use one of the following endpoints below instead.

https://au.omikkel.com/calendar/[endpoint]

| Endpoint | Description |
|----------|-------------|
| / | Get all events |
| /study-cafe | Get all study cafe relevant events (excludes programmeringscafe) |
| /theory | Get all team study relevant events (TØ) |
| /lectures | Get all lecture relevant events |
| /overflow | Get all events with the above events removed |


### Arguments

If you want to further filter your events you can use the below arguments. The arguments q and e takes a list of words and it will search for the words seperately.

These arguments only work on the base / endpoint

#### Example 

https://...../calendar?q=Holdundervisning,Praktisk&e=Programmeringscafé this will retrieve all calendar events that either contain Holdundervisning or Praktisk in the title or description. At the same time it will remove all events that contains programmeringscafé.

| Arguments | Description |
| --------- | ----------- |
| q | Use this argument in the url to select events that match the word(s) specified, it searches title and description |
| e | Same as q but excludes instead |
| icalKey | This is important otherwise it wont retrieve your calendar events |



