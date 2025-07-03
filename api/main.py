from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import pandas as pd
from mangum import Mangum
import os

app = FastAPI()

base_path = os.path.dirname(__file__)

province_df = pd.read_csv(os.path.join(base_path, "data/CambodiaProvinceList2023.csv"), dtype=str)
district_df = pd.read_csv(os.path.join(base_path, "data/CambodiaDistrictList2023.csv"), dtype=str)
commune_df = pd.read_csv(os.path.join(base_path, "data/CambodiaCommuneList2023.csv"), dtype=str)
village_df = pd.read_csv(os.path.join(base_path, "data/CambodiaVillagesList2023.csv"), dtype=str)

@app.get("/locations")
def get_locations(
    province: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    commune: Optional[str] = Query(None)
):
    if province is None:
        return province_df[["code", "name_en", "name_km"]].to_dict(orient="records")

    if province and district is None and commune is None:
        districts = district_df[district_df["province_code"] == province]
        return districts[["code", "name_en", "name_km"]].to_dict(orient="records")

    if province and district and commune is None:
        communes = commune_df[
            (commune_df["province_code"] == province) &
            (commune_df["district_code"] == district)
        ]
        return communes[["code", "name_en", "name_km"]].to_dict(orient="records")

    if province and district and commune:
        villages = village_df[
            (village_df["province_code"] == province) &
            (village_df["district_code"] == district) &
            (village_df["commune_code"] == commune)
        ]
        return villages[["code", "name_en", "name_km"]].to_dict(orient="records")

    raise HTTPException(status_code=400, detail="Invalid query combination")

# 👇 Required for Vercel
handler = Mangum(app)