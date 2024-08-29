import re
import json
import requests
from flask import Flask, request, Response

app = Flask(__name__)

locations = json.load(open("locations.json", "r"))["locations"]
metadata = {
    "version": "",
    "prodid": ""
}
buildingCache = {}

def downloadCalendar(icalKey):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    calendar = requests.get(f"https://mitstudie.au.dk/calendar?icalkey={icalKey}&lang=da", headers=headers)

    if calendar.status_code == 200:
        return calendar.text
    else:
        return

def handleRequest(endpoint):
    queries = request.args.get("q")
    exclusions = request.args.get("e")
    icalKey = request.args.get("icalKey")

    if not icalKey:
        return Response("No icalKey specified")
    
    if queries:
        queries = queries.split(",")
    else:
        queries = []
    if exclusions:
        exclusions = exclusions.split(",")
    else:
        exclusions = []

    calendar = downloadCalendar(icalKey)

    if not calendar:
        return Response("Failed to get calendar")

    match endpoint:
        case "study-cafe":
            queries = ["Praktisk"]
            exclusions = ["Programmeringscafé"]
        case "theory":
            queries = ["Holdundervisning"]
            exclusions = []
        case "lectures":
            queries = ["Forelæsning"]
            exclusions = []
        case "overflow":
            queries = []
            exclusions = ["Praktisk", "Programmeringscafé", "Holdundervisning", "Forelæsning"]

    formattedCalendar = formatCalendar(calendar, queries, exclusions)

    return Response(formattedCalendar, mimetype="text/calendar")

def isContainingString(keywords, body):
    for keyword in keywords:
        if keyword in body:
            return True
    
    return False    

def getBuildingInfo(buildingNo):
    if buildingNo in buildingCache:
        return buildingCache[buildingNo]
    
    for location in locations:
        if location["id"] == buildingNo:
            return location

def setEventLocation(events):
    for event in events:
        match = re.match(r"(\d+)-(\d+)", event["LOCATION"])

        if match:
            buildingNo = match.group(1)
            _room_number = match.group(2)

            buildingInfo = getBuildingInfo(buildingNo)
            
            if not buildingInfo:
                print("Building not found " + buildingNo)
                break
            
            buildingCache[buildingNo] = buildingInfo
            event["LOCATION"] = buildingInfo["address"].split(" ,")[0] + " (" + event["LOCATION"] + ")"
            event["DESCRIPTION"] = f"{event['DESCRIPTION']}\\nAdresse: {buildingInfo["address"].replace(" ,", ",")}\\nLokation: {event["LOCATION"]}"

def constructCalendar(events):
    calendar = f"BEGIN:VCALENDAR\nVERSION:{metadata["version"]}\nPRODID:{metadata["prodid"]}\n"

    for event in events:
        calendar += f"BEGIN:VEVENT\nUID:{event['UID']}\nDTSTAMP:{event['DTSTAMP']}\nLOCATION:{event['LOCATION']}\nDTSTART:{event["DTSTART"]}\nDTEND:{event["DTEND"]}\nSUMMARY:{event['SUMMARY']}\nDESCRIPTION:{event["DESCRIPTION"]}\nEND:VEVENT\n"

    calendar += "END:VCALENDAR\n"

    return calendar

def formatCalendar(calendar, queries, exclusions):
    calendar = calendar.split("\n")
    metadata["version"] = calendar[1].replace("VERSION:", "")
    metadata["prodid"] = calendar[2].replace("PRODID:", "")
    
    calendar = calendar[3:len(calendar)-2]

    events = []
    cursor = 0

    while cursor < len(calendar):
        event = calendar[cursor:cursor+9]
        
        eventObj = {
            "UID": event[1].replace("UID:", ""),
            "DTSTAMP": event[2].replace("DTSTAMP:", ""),
            "LOCATION": event[3].replace("LOCATION:", ""),
            "DTSTART": event[4].replace("DTSTART:", ""),
            "DTEND": event[5].replace("DTEND:", ""),
            "SUMMARY": event[6].replace("SUMMARY:", ""),
            "DESCRIPTION": event[7].replace("DESCRIPTION:", "")
        }

        if isContainingString(queries, eventObj["SUMMARY"] + eventObj["DESCRIPTION"]) and not isContainingString(exclusions, eventObj["SUMMARY"] + eventObj["DESCRIPTION"]):
            events.append(eventObj)

        cursor  += 9

    setEventLocation(events)
    calendar = constructCalendar(events)

    print(f"Number of events processed: {len(events)}")

    return calendar






@app.route("/calendar")
def handleCalendar():
    return handleRequest("")

@app.route("/calendar/study-cafe")
def handleStudyCafe():
    return handleRequest("study-cafe")

@app.route("/calendar/theory")
def handleTheory():
    return handleRequest("theory")

@app.route("/calendar/lectures")
def handleLectures():
    return handleRequest("lectures")

@app.route("/calendar/overflow")
def handleOverflow():
    return handleRequest("overflow")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
