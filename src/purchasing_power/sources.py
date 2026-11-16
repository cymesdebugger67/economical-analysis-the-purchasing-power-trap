from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Optional

import requests


CPI_TABLE_URL = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP22.px"
PPP_TABLE_URL = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP24.px"
WAGE_SCHEDULE_URL = "https://nwpc.dole.gov.ph/wp-content/uploads/2026/11/2-Summary-of-DMWR-per-Wage-Order-by-Region_Non-Agriculture-1989-to-Nov_6_2026.pdf"
FIES_TABLE_URL = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1E/IE/0071E3ATME0.px"
FIES_CATALOG_URL = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1E/IE/"
FIES_CATEGORIES = (
    "Total Family Expenditure (in millions)",
    "Food and Non-Alcoholic Beverages",
    "Clothing and Footwear",
    "Housing, Water, Electricity, Gas and Other Fuels",
    "Health",
    "Transport",
    "Information and Communication",
    "Education",
)
WAGE_ORDER_URLS = {
    "19": "https://nwpc.dole.gov.ph/wp-content/uploads/2023/04/reg-11-wo-19.pdf",
    "20": "https://nwpc.dole.gov.ph/wp-content/uploads/2024/11/reg-11-wo-20.pdf",
    "21": "https://nwpc.dole.gov.ph/wp-content/uploads/2023/04/Published-WO-No.-RB-XI-21.pdf",
    "22": "https://nwpc.dole.gov.ph/wp-content/uploads/2024/02/Wage-Order-No.-RB-XI-22.pdf",
    "23": "https://nwpc.dole.gov.ph/wp-content/uploads/2025/02/Wage-Order-No.-RB-XI-23.pdf",
}


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
    if (raw_directory / "source_manifest.json").exists():
        raise FileExistsError("Captured source vintage exists; use a separate directory for a new vintage")
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


def acquire_fies(raw_directory: Path) -> dict:
    raw_directory.mkdir(parents=True, exist_ok=True)
    manifest_path = raw_directory / "fies_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if file_sha256(raw_directory / manifest["file"]) != manifest["sha256"]:
            raise ValueError("Captured FIES source checksum mismatch")
        return manifest
    with requests.Session() as session:
        catalog_response = session.get(FIES_CATALOG_URL, timeout=30)
        catalog_response.raise_for_status()
        catalog = next(item for item in catalog_response.json() if item["id"] == "0071E3ATME0.px")
        response = session.get(FIES_TABLE_URL, timeout=30)
        response.raise_for_status()
        metadata = response.json()
        variables = {variable["code"]: variable for variable in metadata["variables"]}
        geographies = [_selected_code(variables["Region, Province, and HUC"], label)
                       for label in ("PHILIPPINES", "REGION XI - DAVAO REGION")]
        categories = [_selected_code(variables["Major Expenditure Group"], label)
                      for label in FIES_CATEGORIES]
        income_groups = [_selected_code(variables["Indicator"], label)
                         for label in ("All Income Groups",) + tuple(f"{rank}{suffix} Decile" for rank, suffix in
                                                                      ((1, "st"), (2, "nd"), (3, "rd"), (4, "th"),
                                                                       (5, "th"), (6, "th"), (7, "th"), (8, "th"),
                                                                       (9, "th"), (10, "th")))]
        selected = {"Region, Province, and HUC": geographies,
                    "Major Expenditure Group": categories, "Indicator": income_groups}
        query = {"query": [{"code": variable["code"], "selection": {"filter": "item", "values": selected[variable["code"]]}}
                           for variable in metadata["variables"]], "response": {"format": "json"}}
        response = session.post(FIES_TABLE_URL, json=query, timeout=90)
        response.raise_for_status()
        observations = json.loads(response.content.decode("utf-8-sig"))
    if not isinstance(observations, dict) or len(observations.get("data", [])) != 176:
        raise ValueError("FIES API did not return the 176 requested values")
    payload = {"url": FIES_TABLE_URL, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
               "catalog_updated": catalog.get("updated"), "metadata": metadata, "query": query,
               "observations": observations}
    path = raw_directory / "psa_fies_2023_expenditure.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {"url": FIES_TABLE_URL, "file": path.name, "sha256": file_sha256(path),
                "observations": len(observations["data"]), "retrieved_at_utc": payload["retrieved_at_utc"],
                "catalog_updated": payload["catalog_updated"]}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def acquire_wage_order_documents(raw_directory: Path) -> dict:
    directory = raw_directory / "wage_orders"
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["orders"].values():
            if file_sha256(directory / entry["file"]) != entry["sha256"]:
                raise ValueError("Captured original wage-order checksum mismatch")
        return manifest
    manifest = {"manifest_created_at_utc": datetime.now(timezone.utc).isoformat(), "orders": {}}
    with requests.Session() as session:
        for order, url in WAGE_ORDER_URLS.items():
            path = directory / f"rb_xi_{order}.pdf"
            if not path.exists():
                response = session.get(url, timeout=60)
                response.raise_for_status()
                if not response.content.startswith(b"%PDF"):
                    raise ValueError(f"Original order {order} response is not a PDF")
                path.write_bytes(response.content)
            if not path.read_bytes().startswith(b"%PDF"):
                raise ValueError(f"Original order {order} is not a PDF")
            manifest["orders"][order] = {"url": url, "file": path.name, "sha256": file_sha256(path)}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
