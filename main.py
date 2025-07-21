from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import pandas as pd
import asyncio

app = FastAPI()

# Load CSV files once into memory at startup
province_df = pd.read_csv("data/CambodiaProvinceList2023.csv", dtype=str)
district_df = pd.read_csv("data/CambodiaDistrictList2023.csv", dtype=str)
commune_df = pd.read_csv("data/CambodiaCommuneList2023.csv", dtype=str)
village_df = pd.read_csv("data/CambodiaVillagesList2023.csv", dtype=str)

@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse(url="/docs")

@app.get("/v1/2023/locations")
async def get_locations(
    province: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    commune: Optional[str] = Query(None),
):
    # Define blocking filter logic
    def filter_locations():
        if province is None:
            return province_df[["code", "name_en", "name_km"]].to_dict(orient="records")

        if province and district is None and commune is None:
            filtered = district_df[district_df["province_code"] == province]
            return filtered[["code", "name_en", "name_km"]].to_dict(orient="records")

        if province and district and commune is None:
            filtered = commune_df[
                (commune_df["province_code"] == province) &
                (commune_df["district_code"] == district)
            ]
            return filtered[["code", "name_en", "name_km"]].to_dict(orient="records")

        if province and district and commune:
            filtered = village_df[
                (village_df["province_code"] == province) &
                (village_df["district_code"] == district) &
                (village_df["commune_code"] == commune)
            ]
            return filtered[["code", "name_en", "name_km"]].to_dict(orient="records")

        raise HTTPException(status_code=400, detail="Invalid query combination")

    # Run pandas filtering in background thread to avoid blocking
    return await asyncio.to_thread(filter_locations)
