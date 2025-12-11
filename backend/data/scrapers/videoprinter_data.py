import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://o8bbxwfg8k.execute-api.eu-west-1.amazonaws.com/dev/api/videprinter"

def parse_price_change(soup_element):
    """Parse a price change event from the HTML element."""
    text = soup_element.get_text()
    
    # Extract player name and team
    yellow_spans = soup_element.find_all("span", style=lambda s: s and "yellow" in s)
    player_name = yellow_spans[0].get_text(strip=True) if yellow_spans else None
    new_price = yellow_spans[-1].get_text(strip=True) if len(yellow_spans) > 1 else None
    
    # Extract team from player name (format: "Player Name (Team)")
    team = None
    if player_name and "(" in player_name and ")" in player_name:
        match = re.search(r"\(([^)]+)\)", player_name)
        if match:
            team = match.group(1)
            player_name = player_name.split("(")[0].strip()
    
    # Determine if rise or fall
    change_type = "rise" if "risen" in text.lower() else "fall"
    
    # Clean price (remove £ symbol)
    if new_price:
        new_price = new_price.replace("£", "").replace("M", "").strip()
        try:
            new_price = float(new_price)
        except ValueError:
            pass
    
    return {
        "type": "price_change",
        "player": player_name,
        "team": team,
        "change_type": change_type,
        "new_price": new_price
    }

def parse_status(soup_element):
    """Parse a player status update from the HTML element."""
    yellow_spans = soup_element.find_all("span", style=lambda s: s and "yellow" in s)
    cyan_spans = soup_element.find_all("span", style=lambda s: s and "cyan" in s)
    
    player_name = yellow_spans[0].get_text(strip=True) if yellow_spans else None
    status_info = cyan_spans[0].get_text(strip=True) if cyan_spans else None
    
    # Extract team from player name
    team = None
    if player_name and "(" in player_name and ")" in player_name:
        match = re.search(r"\(([^)]+)\)", player_name)
        if match:
            team = match.group(1)
            player_name = player_name.split("(")[0].strip()
    
    return {
        "type": "status",
        "player": player_name,
        "team": team,
        "status": status_info
    }

def parse_goal(soup_element):
    """Parse a goal event from the HTML element."""
    text = soup_element.get_text()
    yellow_spans = soup_element.find_all("span", style=lambda s: s and "yellow" in s)
    cyan_spans = soup_element.find_all("span", style=lambda s: s and "cyan" in s)
    
    # Extract teams and score
    teams = [span.get_text(strip=True) for span in cyan_spans]
    home_team = teams[0] if len(teams) > 0 else None
    away_team = teams[1] if len(teams) > 1 else None
    
    # Extract score
    score_match = re.search(r"(\d+)-(\d+)", text)
    home_score = int(score_match.group(1)) if score_match else None
    away_score = int(score_match.group(2)) if score_match else None
    
    # Extract scorer
    scorer = yellow_spans[0].get_text(strip=True) if yellow_spans else None
    
    # Extract scorer points: "Player 5 pts. Tot 6 Pts"
    scorer_points = None
    scorer_total = None
    pts_match = re.search(r"(-?\d+)\s*pts\.\s*Tot\s*(\d+)\s*Pts", text)
    if pts_match:
        scorer_points = int(pts_match.group(1))
        scorer_total = int(pts_match.group(2))
    
    # Extract assist if present
    assist = None
    assist_points = None
    assist_total = None
    if "ASSIST:" in text:
        for i, span in enumerate(yellow_spans):
            if i > 0:  # First is scorer
                assist = span.get_text(strip=True)
                break
        # Extract assist points
        assist_match = re.search(r"ASSIST:.*?(-?\d+)\s*pts\.\s*Tot\s*(\d+)\s*Pts", text)
        if assist_match:
            assist_points = int(assist_match.group(1))
            assist_total = int(assist_match.group(2))
    
    return {
        "type": "goal",
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "scorer": scorer,
        "scorer_points": scorer_points,
        "scorer_total": scorer_total,
        "assist": assist,
        "assist_points": assist_points,
        "assist_total": assist_total
    }

def parse_card(soup_element, card_type):
    """Parse a yellow/red card or saves event."""
    text = soup_element.get_text()
    yellow_spans = soup_element.find_all("span", style=lambda s: s and "yellow" in s)
    
    player_info = yellow_spans[0].get_text(strip=True) if yellow_spans else None
    
    # Extract player and team
    player = None
    team = None
    if player_info and "(" in player_info:
        match = re.search(r"(.+?)\s*\(([^)]+)\)", player_info)
        if match:
            player = match.group(1).strip()
            team = match.group(2).strip()
    
    # Extract points: "-1 pts. Tot -1 Pts" or "1 pts. Tot 7 Pts"
    points = None
    total_points = None
    pts_match = re.search(r"(-?\d+)\s*pts\.\s*Tot\s*(-?\d+)\s*Pts", text)
    if pts_match:
        points = int(pts_match.group(1))
        total_points = int(pts_match.group(2))
    
    return {
        "type": card_type,
        "player": player,
        "team": team,
        "points": points,
        "total_points": total_points
    }

def parse_bonus(soup_element):
    """Parse bonus points allocation."""
    text = soup_element.get_text()
    yellow_spans = soup_element.find_all("span", style=lambda s: s and "yellow" in s)
    cyan_spans = soup_element.find_all("span", style=lambda s: s and "cyan" in s)
    
    teams = [span.get_text(strip=True) for span in cyan_spans]
    home_team = teams[0] if len(teams) > 0 else None
    away_team = teams[1] if len(teams) > 1 else None
    
    # Extract players and their bonus points: "Player 3 pts. Tot 18 Pts"
    bonus_players = []
    all_matches = re.findall(r"([A-Za-z\.\s'-]+?)\s*(\d+)\s*pts\.\s*Tot\s*(\d+)\s*Pts", text)
    for match in all_matches:
        player_name = match[0].strip()
        bonus_pts = int(match[1])
        total_pts = int(match[2])
        bonus_players.append({
            "player": player_name,
            "bonus_points": bonus_pts,
            "total_points": total_pts
        })
    
    return {
        "type": "bonus",
        "home_team": home_team,
        "away_team": away_team,
        "players": bonus_players
    }

def parse_team_news(soup_element):
    """Parse team news/lineup."""
    text = soup_element.get_text(strip=True)
    cyan_spans = soup_element.find_all("span", style=lambda s: s and "cyan" in s)
    
    team_info = cyan_spans[0].get_text(strip=True) if cyan_spans else text
    
    return {
        "type": "team_news",
        "content": team_info
    }

def fetch_updates():
    """Fetch and parse all updates from the videprinter API."""
    response = requests.get(URL)
    response.raise_for_status()
    
    data = response.json()
    html_content = data.get("details", "")
    timestamp = data.get("tme", "")
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    updates = []
    current_date = None
    
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        
        # Check for date markers
        if "******* " in text:
            date_match = re.search(r"\*{7}\s*(.+?)\s*\*{7}", text)
            if date_match:
                current_date = date_match.group(1)
            continue
        
        # Skip empty paragraphs
        if not text:
            continue
        
        event = None
        
        if "PRICE CHANGE" in text:
            event = parse_price_change(p)
        elif "STATUS" in text:
            event = parse_status(p)
        elif text.startswith("GOAL:"):
            event = parse_goal(p)
        elif text.startswith("YELLOW:"):
            event = parse_card(p, "yellow_card")
        elif text.startswith("RED:"):
            event = parse_card(p, "red_card")
        elif text.startswith("BONUS:"):
            event = parse_bonus(p)
        elif text.startswith("SAVES:"):
            event = parse_card(p, "saves")  # Similar structure to cards
        elif "TEAM NEWS" in text:
            event = parse_team_news(p)
        elif text.startswith("FPL: KO") or text.startswith("FPL: HT") or text.startswith("FPL: FT"):
            # Match updates (Kick-off, Half-time, Full-time)
            event = {"type": "match_update", "content": text.replace("FPL: ", "")}
        
        if event:
            event["date"] = current_date
            updates.append(event)
    
    return {
        "timestamp": timestamp,
        "updates": updates
    }


if __name__ == "__main__":
    data = fetch_updates()
    print(json.dumps(data, indent=2, ensure_ascii=False))