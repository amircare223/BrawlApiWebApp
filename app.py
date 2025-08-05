from flask import Flask, render_template, request
import requests
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def safe_get(obj, key, default=None):
    return obj[key] if isinstance(obj, dict) and key in obj else default

def get_meta(plrtag, selectedmap):
    url_player = f"http://localhost:8000/player?tag={plrtag}"
    url_map = f"http://localhost:8000/map?name={selectedmap}"
    url_events = "https://api.brawlify.com/v1/events"

    try:
        logging.info(f"Fetching player data from {url_player}")
        response_player = requests.get(url_player)
        response_player.raise_for_status()
        player_data = response_player.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Player endpoint error: {e}")
        return {"error": f"Failed to connect to player endpoint: {e}"}

    try:
        logging.info(f"Fetching map data from {url_map}")
        response_map = requests.get(url_map)
        response_map.raise_for_status()
        map_data = response_map.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Map endpoint error: {e}")
        return {"error": f"Failed to connect to map endpoint: {e}"}

    try:
        logging.info(f"Fetching events data from {url_events}")
        response_events = requests.get(url_events)
        response_events.raise_for_status()
        events_data = response_events.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Events API error: {e}")
        return {"error": f"Failed to connect to events API: {e}"}

    logging.info("Searching for matching event...")
    event_id = safe_get(map_data, "Id")
    logging.debug(f"Local map ID: {event_id}")

    found_event = False
    active = safe_get(events_data, "active", {})
    for event in active:
        map_info = safe_get(event, "map", {})
        current_event_id = safe_get(map_info, "id")
        logging.debug(f"Checking event map ID: {current_event_id} against local map ID: {event_id}")

        if str(current_event_id) == str(event_id):
            logging.info(f"Match found for event: {safe_get(event, 'name')}")
            found_event = True

            metaBrawlers = safe_get(map_info, "stats", [])
            logging.debug(f"Meta brawlers for this event: {metaBrawlers}")

            for brawler in metaBrawlers:
                meta_id = safe_get(brawler, "brawler")
                meta_name = safe_get(brawler, "name")

                for b in safe_get(player_data, "brawlers", []):
                    player_id = safe_get(b, "id")
                    player_name = safe_get(b, "name")

                    if str(player_id) == str(meta_id) or player_name == meta_name:
                        use_rate = safe_get(brawler, "useRate", 0)
                        win_rate = safe_get(brawler, "winRate")
                        image_url = safe_get(b, "imageUrl")

                        if use_rate <= 0.5:
                            logging.info(f"Skipping {player_name} due to low use rate ({use_rate}%)")
                            continue  # Skip this brawler

                        confidence = "low" if use_rate < 1 else "high"

                        logging.info(f"Match found: {player_name} with use rate {use_rate}%")
                        return {
                            "brawler": player_name,
                            "winRate": win_rate,
                            "useRate": use_rate,
                            "imageUrl": image_url,
                            "confidence": confidence
                        }


            break

    if not found_event:
        logging.warning("No matching event found with the given map ID.")
    else:
        logging.warning("Matching event found, but no brawler match detected.")

    return {"error": "No meta data found for the specified event and player."}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        plrtag = request.form.get("plrtag")
        selectedmap = request.form.get("selectedmap")
        result = get_meta(plrtag, selectedmap)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
