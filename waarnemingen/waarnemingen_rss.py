import feedparser
from bs4 import BeautifulSoup
from html import unescape
import csv
from pathlib import Path

XML_FILE = Path("waarnemingen_rarities.xml")
CSV_FILE = Path("waarnemingen_rarities.csv")


def parse_description(desc_html: str):
    """
    Parse the Waarnemingen <description> HTML and extract:
    num_observations, rarity, location_name, location_url, notes
    """
    desc_unescaped = unescape(desc_html)
    soup = BeautifulSoup(desc_unescaped, "html.parser")

    num_observations = ""
    rarity = ""
    location = ""
    location_url = ""
    notes = ""

    # 1) Number of observations – usually in the first <a> tag text like "8 observations"
    first_a = soup.find("a")
    if first_a and "observations" in first_a.get_text():
        parts = first_a.get_text(strip=True).split()
        if parts and parts[0].isdigit():
            num_observations = parts[0]

    # 2) Rarity & Notes & Location using text nodes
    #    Iterate over all "stripped strings" and inspect content
    for text in soup.stripped_strings:
        t = text.strip()

        # Rarity: "Rarity: very rare"
        if t.lower().startswith("rarity"):
            # everything after ":" is the value
            if ":" in t:
                rarity = t.split(":", 1)[1].strip()

        # Notes: "Notes: ..."
        elif t.lower().startswith("notes"):
            if ":" in t:
                notes = t.split(":", 1)[1].strip()

    # 3) Location: handle both "Location: AN, LI, NA"
    #    and "Location: <a href='...'>Oostduinkerke...</a>"
    loc_text_node = None
    for text in soup.find_all(string=True):
        if "Location:" in text:
            loc_text_node = text
            break

    if loc_text_node:
        # Case 1: "Location: AN, LI, NA" is all in one string
        full = loc_text_node.strip()
        if ":" in full and full.split(":", 1)[1].strip():
            location = full.split(":", 1)[1].strip()
        else:
            # Case 2: "Location: " then an <a> with the real name
            parent = loc_text_node.parent

            # Collect siblings after the "Location:" text until <br> or end
            parts = []
            for sib in loc_text_node.next_siblings:
                # Stop at a <br> tag – that's end of the location block
                if getattr(sib, "name", None) == "br":
                    break
                # If it's a tag (like <a>), take its text
                if hasattr(sib, "get_text"):
                    parts.append(sib.get_text(strip=True))
                    # If it's the <a>, also capture its href
                    if sib.name == "a" and "href" in sib.attrs:
                        location_url = sib["href"]
                else:
                    # If it's a plain text node
                    parts.append(str(sib).strip())

            location = " ".join(p for p in parts if p).strip()

    # Normalize location_url to full URL if present
    if location_url and location_url.startswith("/"):
        location_url = "https://waarnemingen.be" + location_url

    return num_observations, rarity, location, location_url, notes


def parse_waarnemingen_rss_to_csv():
    if not XML_FILE.exists():
        print(f"❌ XML file not found: {XML_FILE.resolve()}")
        return

    feed = feedparser.parse(str(XML_FILE))

    print("🕊️ Parsing local Waarnemingen rarities RSS...")
    print(f"Found {len(feed.entries)} items.\n")

    rows = []

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        desc_html = entry.description

        # --- 1. Title → date, english_name, sci_name ---
        date_str = ""
        english_name = ""
        sci_name = ""

        if ": " in title:
            date_part, rest = title.split(": ", 1)
            date_str = date_part.strip()
            species_part = rest.strip()

            if " - " in species_part:
                english_name, sci_name = species_part.split(" - ", 1)
                english_name = english_name.strip()
                sci_name = sci_name.strip()
            else:
                english_name = species_part.strip()
        else:
            english_name = title.strip()

        # --- 2. Description HTML → rarity, location, notes etc. ---
        num_obs, rarity, location, location_url, notes = parse_description(desc_html)

        rows.append(
            {
                "date": date_str,
                "english_name": english_name,
                "sci_name": sci_name,
                "rarity": rarity,
                "location": location,
                "location_url": location_url,
                "num_observations": num_obs,
                "notes": notes,
                "item_link": link,
            }
        )

    # --- 3. Write to CSV ---
    fieldnames = [
        "date",
        "english_name",
        "sci_name",
        "rarity",
        "location",
        "location_url",
        "num_observations",
        "notes",
        "item_link",
    ]

    CSV_FILE = Path("waarnemingen_rarities.csv")
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Saved {len(rows)} rows to {CSV_FILE.resolve()}")




if __name__ == "__main__":
    parse_waarnemingen_rss_to_csv()
