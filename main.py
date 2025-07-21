from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import pandas as pd
import asyncio

app = FastAPI()

app = FastAPI( 
        title="Khmer Geo Locations API", 
        version="1.0.1", 
        description="This is the API for Geo Location, which provides information about provinces, districts, communes, and villages in Cambodia. Source data is from the General Department of Digital Economy (https://data.mef.gov.kh/)", 
        root_path_in_servers = True,
        root_path="/v1"
    )

# Load CSV files once into memory at startup
province_df = pd.read_csv("data/CambodiaProvinceList2023.csv", dtype=str)
district_df = pd.read_csv("data/CambodiaDistrictList2023.csv", dtype=str)
commune_df = pd.read_csv("data/CambodiaCommuneList2023.csv", dtype=str)
village_df = pd.read_csv("data/CambodiaVillagesList2023.csv", dtype=str)

@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse(url="/v1/docs")

@app.get("/locations")
async def get_locations(
    province: Optional[int] = Query(None),
    district: Optional[int] = Query(None),
    commune: Optional[int] = Query(None),
):
    
    # Info
    """
    Get locations based on the provided filters.
    - `province`: Filter by province code (optional).
    - `district`: Filter by district code (optional).
    - `commune`: Filter by commune code (optional).
    
    Returns a list of locations matching the filters.
    
    Example usage: https://api.khmer.asia/v1/locations?province=12&district=1210&commune=121001
    """
    
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
