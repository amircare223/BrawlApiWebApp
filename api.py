import requests
from fastapi import FastAPI, Query
from typing import Optional
app = FastAPI()
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjZhYmI0ZDczLTdkNzItNDNlMi1iMjhjLTdiOTE2NGIxMzY5YyIsImlhdCI6MTc1NDIxODkwMiwic3ViIjoiZGV2ZWxvcGVyLzA4NDY1Mzc0LWQ5YWQtNjExOS01ZjRlLWU3OTY2NWU3ZjZmYSIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiODMuMjI1LjE4LjkyIl0sInR5cGUiOiJjbGllbnQifV19.ow-aMIwfLmQ-spxefs907EvvaS6sqFuOG-Hg72BAcbs7268ZBWW_iUpkxIKrwr-in1cIi94QIq9T-B-qmHD0Hg"
def get_brawler_info(name: str):
    url = "https://api.brawlapi.com/v1/brawlers"
    response = requests.get(url)
    data = response.json()
    for brawler in data['list']:
        if brawler['name'].lower() == name.lower():
            return {
                "name": brawler['name'],
                "class": brawler['class']['name'],
                "rarity": brawler['rarity']['name'],
                "image": brawler['imageUrl'],
                "description": brawler['description'],
                "starPowers": [
                    {"name": sp["name"], "description": sp["description"]}
                    for sp in brawler['starPowers']
                ],
                "gadgets": [
                    {"name": gd["name"], "description": gd["description"]}
                    for gd in brawler['gadgets']
                ]
            }
    return {"error": "Brawler not found"}

def transform_id(id: int, key: int):
    if key == 0:
        url = "https://api.brawlapi.com/v1/brawlers"
        response = requests.get(url)
        data = response.json()
        for brawler in data['list']:
            if brawler['id'] == id:
                return brawler['name']
    elif key == 1:
        url = "https://api.brawlapi.com/v1/maps"
        response = requests.get(url)
        data = response.json()
        for map in data['list']:
            if map['id'] == id:
                return map['name']
    elif key == 2:
        url = "https://api.brawlapi.com/v1/events"
        response = requests.get(url)
        data = response.json()
        for event in data.get("active", []):
            maps = event["map"]
            if maps["id"] == id:
                return maps["name"]
    return None



def get_map_info(name: str):
    url = "https://api.brawlapi.com/v1/maps"
    response = requests.get(url)
    data = response.json()
    for map in data['list']:
        if map['name'].lower() == name.lower():
            return {
                "name": map["name"],
                "image": map["imageUrl"],
                "gamemode": map["gameMode"]["name"],
                "gamemodeImage": map["gameMode"]["imageUrl"],
                "Id": map["id"]
            }
    return {"error": "Map not found"}

def get_event_info(event_id: str):
    url = "https://api.brawlapi.com/v1/events"
    response = requests.get(url)
    data = response.json()
    for event in data.get("active", []):
        maps = event["map"]
        if str(maps["id"]) == str(event_id):
            stats = maps["stats"]
            events_list = []
            for b in stats:
                events_list.append({
                    "brawler": transform_id(b["brawler"], 0),
                    "winRate": b["winRate"],
                    "useRate": b["useRate"]
                })
            return {
                "id": maps["id"],
                "name": maps["name"],
                "image": maps["imageUrl"],
                "gamemode": maps["gameMode"]["name"],
                "gamemodeImage": maps["gameMode"]["imageUrl"],
                "startTime": event["startTime"],
                "endTime": event["endTime"],
                "stats": events_list
            }
    return {"error": "Event not found"}



def get_official_player_info(tag: str):
    url = f"https://api.brawlstars.com/v1/players/%23{tag}"  # %23 is URL encoding for #
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Player not found or invalid token"}
    data = response.json()
    brawlers_list = []
    for b in data.get("brawlers", []):
        brawlers_list.append({
            "id": b["id"],
            "name": b["name"],
            "power": b["power"],
            "rank": b["rank"],
            "trophies": b["trophies"],
            "highestTrophies": b["highestTrophies"],
            "gears": b.get("gears", []),
            "starPowers": b.get("starPowers", []),
            "gadgets": b.get("gadgets", [])
        })

    icon_info = check_brawlstars_icon(tag, token)
    return {
        "tag": data.get("tag"),
        "name": data.get("name"),
        "nameColor": data.get("nameColor"),
        "icon": icon_info,  # returns name and imageUrl
        "trophies": data.get("trophies"),
        "highestTrophies": data.get("highestTrophies"),
        "expLevel": data.get("expLevel"),
        "expPoints": data.get("expPoints"),
        "club": {
            "tag": data.get("club", {}).get("tag"),
            "name": data.get("club", {}).get("name")
        },
        "3vs3Victories": data.get("3vs3Victories"),
        "soloVictories": data.get("soloVictories"),
        "duoVictories": data.get("duoVictories"),
        "bestRoboRumbleTime": data.get("bestRoboRumbleTime"),
        "bestTimeAsBigBrawler": data.get("bestTimeAsBigBrawler"),
        "brawlers": brawlers_list
    }

def check_brawlstars_icon(tag: str, token: str):
    url = f"https://api.brawlstars.com/v1/players/%23{tag}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error:", response.json())
        return
    data = response.json()
    icon_id = data.get("icon", {}).get("id")
    # Use Brawlify CDN for icons
    return {
        "imageUrl": f"https://cdn.brawlify.com/profile-icons/regular/{icon_id}.png"
    }

def club_info(tag: str, token: str):
    url = f"https://api.brawlstars.com/v1/clubs/%23{tag}"
    url2 = f"https://api.brawlapi.com/v1/icons"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    response2 = requests.get(url2)
    data2 = response2.json()
    if response.status_code != 200:
        return {"error": "Club not found or invalid token"}
    data = response.json()
    badgeId = data.get("badgeId")
    club_icons = data2.get("club", [])
    badgeImage = "https://cdn.brawlify.com/profile-icons/regular/0.png"
    for icon in club_icons:
        if isinstance(icon, dict) and icon.get("id") == badgeId:
            badgeImage = icon.get("imageUrl")
            break

    return {
        "tag": data.get("tag"),
        "badgeImage": badgeImage,
        "badgeId": badgeId,
        "name": data.get("name"),
        "type": data.get("type"),
        "trophies": data.get("trophies"),
        "requiredTrophies": data.get("requiredTrophies"),
        "members": data.get("members", [])
    }

# Example usage:
# check_brawlstars_icon("YOUGY2R8Y", token)

@app.get("/event")
def fetch_event(id: str = Query(..., description="Enter event id")):
    data = get_event_info(id)
    return data

@app.get("/club")
def fetch_club(tag: str = Query(..., description="Enter club tag without #")):
    data = club_info(tag, token)
    return data


@app.get("/brawler")
def fetch_brawler(name: str = Query(..., description="Enter brawler name")):
    data = get_brawler_info(name)
    return data

@app.get("/map")
def fetch_map(name: str = Query(..., description="Enter map name")):
    data = get_map_info(name)
    return data

@app.get("/event")
def fetch_events():
    data = get_event_info()
    return data

@app.get("/player")
def fetch_player(tag: str = Query(..., description="Enter player tag without #")):
    data = get_official_player_info(tag)
    return data
