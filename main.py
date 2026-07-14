from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import pandas as pd
import asyncio

app = FastAPI( 
        title="Cambodia Geo Locations - API", 
        version="1.1.0", # អាប់ដេតជំនាន់ API
        summary="API for Geo Location in Cambodia (2025 Data)",
        contact={
            "name": "bsthen",
            "url": "https://github.com/bsthen",
        },
        description="Geo Location, which provides information about provinces, districts, communes, and villages in Cambodia. \n\nSource data is from the General Department of Digital Economy (https://data.mef.gov.kh/)", 
        root_path_in_servers = True,
        root_path="/v1",
        terms_of_service="https://data.mef.gov.kh/terms-of-use",
    )

# 1. ផ្លាស់ប្តូរមក load ឯកសារ CSV ឆ្នាំ 2025 វិញ
province_df = pd.read_csv("data/2025/CambodiaProvinceList2025.csv", dtype=str)
district_df = pd.read_csv("data/2025/CambodiaDistrictList2025.csv", dtype=str)
commune_df = pd.read_csv("data/2025/CambodiaCommuneList2025.csv", dtype=str)
village_df = pd.read_csv("data/2025/CambodiaVillagesList2025.csv", dtype=str)

@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse(url="/v1/docs")

@app.get("/locations", tags=["Geo Location APIs"])
async def get_locations(
    province: Optional[str] = Query(None),
    p: Optional[str] = Query(None, description="Short for province code"),
    district: Optional[str] = Query(None),
    d: Optional[str] = Query(None, description="Short for district code"),
    commune: Optional[str] = Query(None),
    c: Optional[str] = Query(None, description="Short for commune code"),
):
    
    # ចាប់យកតម្លៃទម្រង់ពេញ ឬទម្រង់ខ្លី
    active_province = province or p
    active_district = district or d
    active_commune = commune or c
    
    # Define blocking filter logic
    def filter_locations():
        # កាលណាអត់ទាន់មានការបញ្ជូន code អ្វីទាំងអស់ => បង្ហាញខេត្តទាំងអស់
        if active_province is None:
            return province_df[["province_code", "province_kh", "province_en"]].to_dict(orient="records")

        # មានខេត្ត តែអត់ទាន់មានស្រុក និងឃុំ => បង្ហាញស្រុកទាំងអស់នៅក្នុងខេត្តនោះ
        if active_province and active_district is None and active_commune is None:
            filtered = district_df[district_df["province_code"] == active_province]
            return filtered[["district_code", "district_kh", "district_en"]].to_dict(orient="records")

        # មានខេត្ត មានស្រុក តែអត់ទាន់មានឃុំ => បង្ហាញឃុំទាំងអស់នៅក្នុងស្រុកនោះ
        if active_province and active_district and active_commune is None:
            filtered = commune_df[
                (commune_df["province_code"] == active_province) &
                (commune_df["district_code"] == active_district)
            ]
            return filtered[["commune_code", "commune_kh", "commune_en"]].to_dict(orient="records")

        # មានគ្រប់ទាំងអស់ (ខេត្ត ស្រុក ឃុំ) => បង្ហាញភូមិទាំងអស់នៅក្នុងឃុំនោះ
        if active_province and active_district and active_commune:
            filtered = village_df[
                (village_df["province_code"] == active_province) &
                (village_df["district_code"] == active_district) &
                (village_df["commune_code"] == active_commune)
            ]
            return filtered[["village_code", "village_kh", "village_en"]].to_dict(orient="records")

        raise HTTPException(status_code=400, detail="Invalid query combination")

    # Run pandas filtering in background thread to avoid blocking
    return await asyncio.to_thread(filter_locations)