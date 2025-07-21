from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional
import pandas as pd

app = FastAPI()

# Load CSVs
province_df = pd.read_csv("data/CambodiaProvinceList2023.csv", dtype=str)
district_df = pd.read_csv("data/CambodiaDistrictList2023.csv", dtype=str)
commune_df = pd.read_csv("data/CambodiaCommuneList2023.csv", dtype=str)
village_df = pd.read_csv("data/CambodiaVillagesList2023.csv", dtype=str)

# Redirect 404 to /docs
@app.exception_handler(404)
def not_found_redirect(request, exc):
    return RedirectResponse(url="/docs")

# Redirect / to /docs
@app.get("/")
def redirect_to_docs():
   return RedirectResponse(url="/docs")

@app.get("/locations")
def get_locations(
    province: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    commune: Optional[str] = Query(None)
):
    # 1. No query — return all provinces
    if province is None:
        return province_df[["code", "name_en", "name_km"]].to_dict(orient="records")

    # 2. province only — return all districts
    if province and district is None and commune is None:
        districts = district_df[district_df["province_code"] == province]
        return districts[["code", "name_en", "name_km"]].to_dict(orient="records")

    # 3. province + district — return all communes
    if province and district and commune is None:
        communes = commune_df[
            (commune_df["province_code"] == province) &
            (commune_df["district_code"] == district)
        ]
        return communes[["code", "name_en", "name_km"]].to_dict(orient="records")

    # 4. province + district + commune — return all villages
    if province and district and commune:
        villages = village_df[
            (village_df["province_code"] == province) &
            (village_df["district_code"] == district) &
            (village_df["commune_code"] == commune)
        ]
        return villages[["code", "name_en", "name_km"]].to_dict(orient="records")

    # If invalid combo
    raise HTTPException(status_code=400, detail="Invalid query combination")