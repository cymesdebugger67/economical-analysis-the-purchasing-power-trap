from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from typing import Optional

import requests


CPI_TABLE_URL = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP22.px"
PPP_TABLE_URL = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP24.px"
WAGE_SCHEDULE_URL = "https://nwpc.dole.gov.ph/wp-content/uploads/2026/11/2-Summary-of-DMWR-per-Wage-Order-by-Region_Non-Agriculture-1989-to-Nov_6_2026.pdf"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _selected_code(variable: dict, label: str) -> str:
    matches = [code for code, text in zip(variable["values"], variable["valueTexts"]) if text == label]
    if len(matches) != 1:
        raise ValueError(f"Expected one code for {label!r}, found {len(matches)}")
    return matches[0]


def _query_table(session: requests.Session, url: str, commodities: Optional[list[str]]) -> dict:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    metadata = response.json()
    variables = {variable["code"]: variable for variable in metadata["variables"]}
    geography = [_selected_code(variables["Geolocation"], label) for label in (
        "PHILIPPINES", "..Region XI (Davao Region)")]
    selections = {"Geolocation": geography,
                  "Year": [_selected_code(variables["Year"], str(year)) for year in range(2018, 2026)],
                  "Period": [_selected_code(variables["Period"], month) for month in
                             ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")]}
    if commodities is not None:
        selections["Commodity Description"] = [_selected_code(variables["Commodity Description"], label)
                                              for label in commodities]
    for name, variable in variables.items():
        if name not in selections and len(variable["values"]) == 1:
            selections[name] = variable["values"]
    for name, values in selections.items():
        if not set(values).issubset(set(variables[name]["values"])):
            raise ValueError(f"Missing requested {name} values")
    query = {"query": [{"code": variable["code"], "selection": {"filter": "item", "values": selections[variable["code"]]}}
                       for variable in metadata["variables"]], "response": {"format": "json"}}
    response = session.post(url, json=query, timeout=90)
    response.raise_for_status()
    observations = json.loads(response.content.decode("utf-8-sig"))
    if not isinstance(observations, dict) or not isinstance(observations.get("data"), list):
        raise ValueError("PSA API did not return observation records")
    return {"metadata": metadata, "query": query, "observations": observations, "url": url}


def acquire_official_sources(raw_directory: Path) -> dict:
    raw_directory.mkdir(parents=True, exist_ok=True)
    commodities = [
        "0 - ALL ITEMS",
        "01 - FOOD AND NON-ALCOHOLIC BEVERAGES",
        "04 - HOUSING, WATER, ELECTRICITY, GAS, AND OTHER FUELS",
        "07 - TRANSPORT",
    ]
    with requests.Session() as session:
        cpi = _query_table(session, CPI_TABLE_URL, commodities)
        ppp = _query_table(session, PPP_TABLE_URL, None)
        response = session.get(WAGE_SCHEDULE_URL, timeout=60)
        response.raise_for_status()
        if not response.content.startswith(b"%PDF"):
            raise ValueError("NWPC schedule response is not a PDF")
    outputs = {"cpi": cpi, "ppp": ppp}
    manifest = {"retrieved_on": date.today().isoformat(), "sources": {}}
    for name, content in outputs.items():
        path = raw_directory / f"psa_{name}_2018_2025.json"
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["sources"][name] = {"url": content["url"], "file": path.name,
                                      "sha256": file_sha256(path), "observations": len(content["observations"]["data"]),
                                      "table_updated": content["metadata"].get("updated")}
    schedule_path = raw_directory / "nwpc_non_agriculture_schedule_2026_11_06.pdf"
    schedule_path.write_bytes(response.content)
    manifest["sources"]["wages"] = {"url": WAGE_SCHEDULE_URL, "file": schedule_path.name,
                                       "sha256": file_sha256(schedule_path)}
    (raw_directory / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
