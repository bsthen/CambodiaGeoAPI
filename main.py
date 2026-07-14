from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import pandas as pd
import asyncio

app = FastAPI( 
        title="Cambodia Geo Locations - API", 
        version="1.0.6",
        summary="API for Geo Location in Cambodia",
        contact={
            "name": "bsthen",
            "url": "https://github.com/bsthen",
        },
        description="Geo Location, which provides information about provinces, districts, communes, and villages in Cambodia. \n\nSource data is from the General Department of Digital Economy (https://data.mef.gov.kh/)", 
        root_path_in_servers = True,
        root_path="/v1",
        terms_of_service="https://data.mef.gov.kh/terms-of-use",
    )

# Load CSV files once into memory at startup
province_df = pd.read_csv("data/CambodiaProvinceList2023.csv", dtype=str)
district_df = pd.read_csv("data/CambodiaDistrictList2023.csv", dtype=str)
commune_df = pd.read_csv("data/CambodiaCommuneList2023.csv", dtype=str)
village_df = pd.read_csv("data/CambodiaVillagesList2023.csv", dtype=str)

@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse(url="/v1/docs")

@app.get("/locations", tags="Geo Location APIs")
async def get_locations(
    province: Optional[str] = Query(None),
    p: Optional[str] = Query(None, description="Short for province code"),
    district: Optional[str] = Query(None),
    d: Optional[str] = Query(None, description="Short for district code"),
    commune: Optional[str] = Query(None),
    c: Optional[str] = Query(None, description="Short for commune code"),
):
    
    # Info
    """
    Get locations based on the provided filters.
    - `province`: Filter by province code (optional).
    - `district`: Filter by district code (optional).
    - `commune`: Filter by commune code (optional).
    
    Returns a list of locations matching the filters.
    
    Example usage: https://cambodia-geo-api.bsthen.com/v1/locations?province=12&district=1210&commune=121001
    """
    
    active_province = province or p
    active_district = district or d
    active_commune = commune or c
    
    # Define blocking filter logic
    def filter_locations():
        if active_province is None:
            return province_df[["code", "name_en", "name_km"]].to_dict(orient="records")

        if active_province and active_district is None and active_commune is None:
            filtered = district_df[district_df["province_code"] == active_province]
            return filtered[["code", "name_en", "name_km"]].to_dict(orient="records")

        if active_province and active_district and active_commune is None:
            filtered = commune_df[
                (commune_df["province_code"] == active_province) &
                (commune_df["district_code"] == active_district)
            ]
            return filtered[["code", "name_en", "name_km"]].to_dict(orient="records")

        if active_province and active_district and active_commune:
            filtered = village_df[
                (village_df["province_code"] == active_province) &
                (village_df["district_code"] == active_district) &
                (village_df["commune_code"] == active_commune)
            ]
            return filtered[["code", "name_en", "name_km"]].to_dict(orient="records")

        raise HTTPException(status_code=400, detail="Invalid query combination")

    # Run pandas filtering in background thread to avoid blocking
    return await asyncio.to_thread(filter_locations)
