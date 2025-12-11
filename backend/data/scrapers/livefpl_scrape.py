"""
    LiveFPL scraper - scrapes fantasy football data from plan.livefpl.net
    This module scrapes:
    - Differentials (low-owned players you have)
    - Threats (high-owned players you don't have)
    - Captain performance info
    - Gameweek summary with rank movement
    - Individual player points
"""
import json
from typing import Dict, Any, Optional
from playwright.sync_api import Playwright, sync_playwright, TimeoutError

def extract_player_details(card) -> Dict[str, Any]:
    """Extract player name, points, and ownership from a player card."""
    try:
        name_elem = card.locator("h5.player-name")
        name = name_elem.text_content().strip() if name_elem.count() > 0 else "Unknown"

        points_elem = card.locator("p.player-played").first
        points_text = (
            points_elem.text_content().strip() if points_elem.count() > 0 else "0"
        )
        points = int(points_text) if points_text.isdigit() else 0

        ownership_elem = card.locator("p.player-played.lower")
        ownership_text = (
            ownership_elem.text_content().strip()
            if ownership_elem.count() > 0
            else "0%"
        )

        return {"name": name, "points": points, "ownership": ownership_text}
    except Exception as e:
        return {"name": "Error", "points": 0, "ownership": "0%", "error": str(e)}


def extract_gameweek_summary(page) -> Dict[str, Any]:
    """Extract gameweek summary including rank movement."""
    try:
        summary = {}

        up_arrow = page.locator("#upsummary")
        down_arrow = page.locator("#downsummary")

        if up_arrow.count() > 0 and up_arrow.get_attribute("style") != "display: none;":
            summary["rank_direction"] = "up"
        elif (
            down_arrow.count() > 0
            and down_arrow.get_attribute("style") != "display: none;"
        ):
            summary["rank_direction"] = "down"
        else:
            summary["rank_direction"] = "unchanged"

        pre_summary = page.locator("#presummary")
        if pre_summary.count() > 0:
            summary["status"] = pre_summary.text_content().strip()

        arrow_text = page.locator("#greenred")
        if arrow_text.count() > 0:
            summary["arrow_type"] = arrow_text.text_content().strip()

        margin_text = page.locator("#marginsummary")
        if margin_text.count() > 0:
            summary["margin"] = margin_text.text_content().strip()

        pts_elem = page.locator("#ptssummary")
        if pts_elem.count() > 0:
            pts_text = pts_elem.text_content().strip()
            summary["gameweek_points"] = pts_text

        safety_elem = page.locator("#safetysummary")
        if safety_elem.count() > 0:
            safety_text = safety_elem.text_content().strip()
            summary["safety_score"] = safety_text

        return summary
    except Exception as e:
        return {"error": str(e)}

def extract_team_players(page) -> list:
    """Extract individual player points from your team."""
    try:
        players = []
        player_cards = page.locator("div.player-details[id$='-visibility']").all()

        for card in player_cards:
            try:
                style = card.get_attribute("style")
                if style and "display:none" in style.replace(" ", ""):
                    continue

                name_elem = card.locator("h5.player-name")
                if name_elem.count() > 0:
                    player_name = name_elem.text_content().strip()
                else:
                    continue

                pts_elem = card.locator("p.player-played, p.player-live").first
                if pts_elem.count() > 0:
                    player_points = pts_elem.text_content().strip()
                else:
                    player_points = "0"

                if not player_name:
                    continue

                players.append({"name": player_name, "points": player_points})
            except Exception:
                continue

        return players
    except Exception as e:
        return {"error": str(e)}

def scrape_livefpl_data(
    entry_id: int, headless: bool = True, timeout: int = 180000
) -> Dict[str, Any]:

    """
    Scrape FPL data from plan.livefpl.net for a given entry ID.

    Args:
        entry_id: FPL manager entry ID
        headless: Run browser in headless mode (default: True)
        timeout: Maximum time to wait for page load in milliseconds (default: 180000)

    Returns:
        Dict containing gameweek_summary, captain, team_players, differentials, threats
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://plan.livefpl.net/rank")

        page.get_by_role("textbox", name="Enter your FPL id").click()
        page.get_by_role("textbox", name="Enter your FPL id").fill(str(entry_id))
        page.get_by_role("button", name="Enter id").click()

        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except:
            pass

        try:
            page.wait_for_selector("#differentials_summary", timeout=timeout)
        except TimeoutError:
            pass

        try:
            page.wait_for_selector("#danger_summary", timeout=10000)
        except TimeoutError:
            pass

        
        try:
            ad_frame = page.frame_locator("[id^='google_ads_iframe_']")
            ad_close_button = ad_frame.get_by_role("button", name="Close ad")
            ad_close_button.click(timeout=5000)
        except Exception:
            pass

        # Extract differentials
        differentials = []
        differential_cards = page.locator(
            "#differentials_summary div.player-details"
        ).all()
        for card in differential_cards:
            player_data = extract_player_details(card)
            differentials.append(player_data)

        
        threats = []
        threat_cards = page.locator("#danger_summary div.player-details").all()
        for card in threat_cards:
            player_data = extract_player_details(card)
            threats.append(player_data)

        team_players = extract_team_players(page)
        gameweek_summary = extract_gameweek_summary(page)

        
        captain_info = {}
        try:
            cap_name_elem = page.locator("#cap-name")
            if cap_name_elem.count() > 0:
                captain_info["caption"] = cap_name_elem.text_content().strip()

            cap_result_elem = page.locator("#cap-result")
            if cap_result_elem.count() > 0:
                captain_info["result"] = cap_result_elem.text_content().strip()
        except Exception as e:
            captain_info["error"] = str(e)

        output_data = {
            "gameweek_summary": gameweek_summary,
            "captain": captain_info,
            "team_players": team_players if isinstance(team_players, list) else [],
            "differentials": differentials,
            "threats": threats,
        }

        context.close()
        browser.close()

        return output_data

def main():
    """CLI interface for the scraper."""
    import sys

    if len(sys.argv) > 1:
        entry_id = int(sys.argv[1])
    else:
        entry_id = 1605977  #fayyad manager id, will later be get request from frontend

    data = scrape_livefpl_data(entry_id)
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
