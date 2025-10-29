import json
import re
from pathlib import Path


LAYOUT_PATH = Path("data/fao-marine-stocks-layout.txt")
EXPORT_PATH = Path("data/fao-region-summary.json")
JS_EXPORT_PATH = Path("static/js/fao-region-summary.js")


def clean_species_list(raw_text: str) -> list[str]:
    """Convert comma-separated species string into clean list."""
    # Remove parenthetical scientific names
    text = re.sub(r"\([^)]*\)", "", raw_text)
    # Replace " and " with comma for consistent splitting
    text = text.replace(" and ", ", ")
    # Split on commas
    items = [item.strip() for item in text.split(",")]
    # Remove empty strings and basic trailing punctuation
    cleaned = []
    for item in items:
        stripped = item.strip().strip(".")
        if not stripped:
            continue
        stripped = stripped.replace("(", "").replace(")", "")
        cleaned.append(stripped)
    return cleaned


def extract_area_chunks(text: str):
    area_pattern = re.compile(
        r"PART D\.(\d+)[^\n]*?Area (\d+): ([^\n]+)", re.MULTILINE
    )
    matches = list(area_pattern.finditer(text))
    processed = set()

    for idx, match in enumerate(matches):
        area_idx = int(match.group(1))
        area_code = match.group(2)
        key = (area_idx, area_code)
        if key in processed:
            continue
        processed.add(key)

        raw_name = match.group(3).strip()
        raw_name = re.sub(r"\s+\d+$", "", raw_name).strip()

        end_idx = idx + 1
        while end_idx < len(matches):
            next_match = matches[end_idx]
            next_idx = int(next_match.group(1))
            next_area_code = next_match.group(2)
            if next_idx != area_idx or next_area_code != area_code:
                break
            end_idx += 1

        start = match.end()
        end = matches[end_idx].start() if end_idx < len(matches) else len(text)
        chunk = text[start:end]
        yield area_idx, area_code, raw_name, chunk


def extract_table_numbers(line: str):
    return [float(value) for value in re.findall(r"\d+\.\d+|\d+", line)]


def find_table_values(chunk: str, area_idx: int):
    table_pattern = re.compile(rf"\n\s*TABLE D\.{area_idx}\.2", re.MULTILINE)
    table_match = table_pattern.search(chunk)
    total_stocks = None
    percentages = {}

    if table_match:
        table_text = chunk[table_match.end():]
        for line in table_text.splitlines():
            if line.strip().startswith("Total"):
                numbers = extract_table_numbers(line)
                if len(numbers) >= 6:
                    total_stocks = int(numbers[0])
                    percentages = {
                        "underfished_pct": numbers[1],
                        "max_sustainably_fished_pct": numbers[2],
                        "overfished_pct": numbers[3],
                        "sustainable_pct": numbers[4],
                        "unsustainable_pct": numbers[5],
                    }
                break

    landings_pattern = re.compile(rf"\n\s*TABLE D\.{area_idx}\.3", re.MULTILINE)
    landings_match = landings_pattern.search(chunk)
    landings = None

    if landings_match:
        landings_text = chunk[landings_match.end():]
        for line in landings_text.splitlines():
            stripped = line.strip()
            if stripped and re.match(r"^\d", stripped):
                numbers = extract_table_numbers(stripped)
                if len(numbers) >= 6:
                    landings = {
                        "landings_mt": numbers[0],
                        "landings_underfished_pct": numbers[1],
                        "landings_max_sustainably_fished_pct": numbers[2],
                        "landings_overfished_pct": numbers[3],
                        "landings_sustainable_pct": numbers[4],
                        "landings_unsustainable_pct": numbers[5],
                    }
                break

    return total_stocks, percentages, landings


def find_main_species(chunk: str, area_code: str):
    species_pattern = re.compile(
        rf"The main species(?: in terms of landings)? for Area {area_code}.*? are (.+?)\.",
        re.IGNORECASE | re.DOTALL,
    )
    match = species_pattern.search(chunk)
    if not match:
        return None
    raw_list = match.group(1).replace("\n", " ")
    return clean_species_list(raw_list)


def build_region_summary():
    text = LAYOUT_PATH.read_text(encoding="utf-8")
    regions = []

    for area_idx, area_code, raw_name, chunk in extract_area_chunks(text):
        total_stocks, percentages, landings = find_table_values(chunk, area_idx)
        species = find_main_species(chunk, area_code)

        region = {
            "area_code": area_code,
            "name": raw_name,
            "total_stocks": total_stocks,
            "percentages": percentages or None,
            "landings": landings or None,
            "main_species": species,
        }
        regions.append(region)

    EXPORT_PATH.write_text(json.dumps(regions, indent=2), encoding="utf-8")

    js_content = (
        "// Auto-generated by scripts/extract_fao_regions.py\n"
        "const FAO_REGION_SUMMARY = "
        + json.dumps(regions, indent=2)
        + ";\n"
    )
    JS_EXPORT_PATH.write_text(js_content, encoding="utf-8")

    print(
        f"Exported data for {len(regions)} regions to {EXPORT_PATH} "
        f"and {JS_EXPORT_PATH}"
    )


if __name__ == "__main__":
    build_region_summary()
