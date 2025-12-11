"""Utility helpers for scraping live FPL price alerts."""
from __future__ import annotations
import re
import time
from typing import Dict, List, Optional, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

URL = "https://www.fplalerts.com/videprinter/"
DEFAULT_TIMEOUT = 10

from .api_client import bootstrap_static

def get_all_players() -> List[Dict[str, Any]]:
    """
    Fetch all player profiles.
    Currently sources data from the FPL API via bootstrap-static.
    """
    bootstrap = bootstrap_static()
    return bootstrap.get("elements", [])


def _parse_player_and_team(raw_text: str) -> Dict[str, Optional[str]]:
    """Split the combined player / team text returned by the videprinter."""
    if "(" not in raw_text or not raw_text.endswith(")"):
        return {"player": raw_text.strip(), "team": None}
    
    player_part, team_part = raw_text.rsplit("(", 1)
    return {
        "player": player_part.strip(),
        "team": team_part.rstrip(")").strip() or None,
    }


def _parse_price(price_text: str) -> Optional[float]:
    """Extract numeric price from text like '£3.8M'."""
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", price_text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def scrape_fpl_alerts(
    *,
    headless: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
    url: str = URL,
) -> List[Dict[str, Optional[str]]]:
    """Scrape price changes and status updates from the FPL Alerts videprinter using Selenium."""
    
    # Setup Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for the page to load and price changes to appear
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p[style*="color:white"]'))
            )
        except:
            pass
        
        # Give it a bit more time for all content to load
        time.sleep(2)
        
        # Get the page source after JavaScript has executed
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        entries: List[Dict[str, Optional[str]]] = []
        current_date = None
        
        # Find all paragraphs (date markers, price changes, and status updates)
        all_paragraphs = soup.find_all('p')
        
        for paragraph in all_paragraphs:
            full_text = paragraph.get_text(" ", strip=True)
            
            # Check if this is a date marker (green text with asterisks)
            if '****' in full_text and any(month in full_text for month in 
                ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']):
                # Extract date from text like "******* Wednesday 19 November 2025 *******"
                date_match = re.search(r'(\w+day)\s+(\d+)\s+(\w+)\s+(\d{4})', full_text)
                if date_match:
                    day_name, day, month, year = date_match.groups()
                    current_date = f"{day_name} {day} {month} {year}"
                continue
            
            # Check if this is a STATUS update
            if "FPL: STATUS" in full_text:
                # Find player name (yellow span)
                yellow_span = paragraph.find('span', style=lambda s: s and 'color:yellow' in s if s else False)
                # Find status info (cyan span) - try multiple color variations
                cyan_span = (
                    paragraph.find('span', style=lambda s: s and 'color:cyan' in s if s else False) or
                    paragraph.find('span', style=lambda s: s and 'cyan' in s.lower() if s else False) or
                    paragraph.find('span', style=lambda s: s and '#00' in s if s else False)  # Cyan hex colors
                )
                
                if yellow_span:
                    player_info = _parse_player_and_team(yellow_span.get_text(strip=True))
                    status_text = cyan_span.get_text(strip=True) if cyan_span else "Status unknown"
                    
                    entries.append({
                        "type": "status",
                        "date": current_date,
                        "player": player_info["player"],
                        "team": player_info["team"],
                        "status": status_text,
                        "raw_text": full_text,
                    })
                continue
            
            # Check if this is a price change entry
            if "FPL: PRICE CHANGE" not in full_text:
                continue
            
            # Find all spans with color:yellow (player name and price)
            yellow_spans = paragraph.find_all('span', style=lambda s: s and 'color:yellow' in s if s else False)
            # Find span with color:#FF0000 (fallen) or green (risen)
            movement_span = (
                paragraph.find('span', style=lambda s: s and '#FF0000' in s if s else False) or
                paragraph.find('span', style=lambda s: s and 'green' in s.lower() if s else False)
            )
            
            if len(yellow_spans) < 2 or not movement_span:
                continue
            
            # First yellow span is player/team, second is price
            player_info = _parse_player_and_team(yellow_spans[0].get_text(strip=True))
            movement = movement_span.get_text(strip=True).lower()
            price_text = yellow_spans[1].get_text(strip=True)
            
            entries.append({
                "type": "price_change",
                "date": current_date,
                "player": player_info["player"],
                "team": player_info["team"],
                "movement": movement,
                "price_text": price_text,
                "price_value": _parse_price(price_text),
                "raw_text": full_text,
            })
        
        return entries
        
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    try:
        alerts = scrape_fpl_alerts()

        if not alerts:
            print("No alerts found on the page.")
        else:
            print(f"Found {len(alerts)} alert(s)\n")

            from itertools import groupby

            for date, group in groupby(alerts, key=lambda item: item.get("date")):
                header = date if date else "Date Unknown"
                print(f"\n📅 {header}")

                for alert in group:
                    player = alert.get("player")
                    team = alert.get("team")
                    summary = f"{player} ({team})" if team else player

                    if alert.get("type") == "price_change":
                        movement = alert.get("movement")
                        price = alert.get("price_text")
                        arrow = "📉" if movement == "fallen" else "📈" if movement == "risen" else "➡️"
                        print(f"  {arrow} {summary}: {movement} to {price}")
                    else:
                        status = alert.get("status")
                        print(f"  🏥 {summary}: {status}")

            price_changes = [a for a in alerts if a.get("type") == "price_change"]
            status_updates = [a for a in alerts if a.get("type") == "status"]
            fallen = [a for a in price_changes if a.get("movement") == "fallen"]
            risen = [a for a in price_changes if a.get("movement") == "risen"]

            print("\n📊 Summary:")
            print(f"  • Price Changes: {len(price_changes)} (↓ {len(fallen)} fallen, ↑ {len(risen)} risen)")
            print(f"  • Status Updates: {len(status_updates)}")

    except Exception as exc:
        print(f"Error: {exc}")



#change for commit 