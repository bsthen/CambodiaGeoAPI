from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import pandas as pd
import asyncio

app = FastAPI( 
        title="Cambodia Geo Locations - API", 
        version="1.2.1", # អាប់ដេតជំនាន់ API
        summary="API សម្រាប់ស្វែងរកទិន្នន័យ ខេត្ត ស្រុក ឃុំ និងភូមិ នៅកម្ពុជា (Smart Search)",
        contact={
            "name": "bsthen",
            "url": "https://github.com/bsthen",
        },
        description="ប្រព័ន្ធផ្តល់ព័ត៌មានអំពីកូដ និងឈ្មោះតំបន់ភូមិសាស្ត្រ រួមមាន ខេត្ត ក្រុង ស្រុក ខណ្ឌ ឃុំ សង្កាត់ និងភូមិ នៅក្នុងព្រះរាជាណាចក្រកម្ពុជា។ \n\nប្រភពទិន្នន័យ៖ អគ្គនាយកដ្ឋានសេដ្ឋកិច្ចឌីជីថល [https://data.mef.gov.kh/](https://data.mef.gov.kh/)", 
        root_path_in_servers = True,
        root_path="/v1",
        terms_of_service="https://data.mef.gov.kh/terms-of-use",
    )

# 1. ផ្លាស់ប្តូរមក load ឯកសារ CSV ឆ្នាំ 2025 វិញ
province_df = pd.read_csv("data/CambodiaProvinceList2025.csv", dtype=str)
district_df = pd.read_csv("data/CambodiaDistrictList2025.csv", dtype=str)
commune_df = pd.read_csv("data/CambodiaCommuneList2025.csv", dtype=str)
village_df = pd.read_csv("data/CambodiaVillagesList2025.csv", dtype=str)

def clean_string(s: str) -> str:
    if not s:
        return ""
    return str(s).strip().lower().replace(" ", "")

@app.exception_handler(404)
async def not_found_redirect(request: Request, exc: HTTPException):
    return RedirectResponse(url="/v1/docs")

@app.get("/locations", tags=["Geo Locations"])
async def get_locations(
    province: Optional[str] = Query(None),
    p: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    d: Optional[str] = Query(None),
    commune: Optional[str] = Query(None),
    c: Optional[str] = Query(None),
):
    """
    ## 🔍 របៀបប្រើប្រាស់ Smart Search (2025 Data)
    អ្នកអាចស្វែងរកទិន្នន័យភូមិសាស្ត្រកម្ពុជាបានយ៉ាងបត់បែន ដោយប្រើប្រាស់ **លេខកូដ (Code)**, **ឈ្មោះភាសាអង់គ្លេស (EN)**, ឬ **ឈ្មោះភាសាខ្មែរ (KH)**។
    
    ### 📌 លក្ខខណ្ឌនៃការស្វែងរក (Query Options):
    - **Province / p**: តម្រងស្វែងរកកម្រិតខេត្ត (ឧទាហរណ៍៖ `17`, `Siemreap`, `សៀមរាប`)
    - **District / d**: តម្រងស្វែងរកកម្រិតស្រុក/ខណ្ឌ (ឧទាហរណ៍៖ `1703`, `Angkor Thum`, `អង្គរធំ`)
    - **Commune / c**: តម្រងស្វែងរកកម្រិតឃុំ/សង្កាត់ (ឧទាហរណ៍៖ `170301`, `Chob Ta Trav`, `ជប់តាត្រាវ`)

    ---
    ### 💡 ឧទាហរណ៍នៃការហៅប្រើប្រាស់ (Examples):
    1. **បង្ហាញខេត្តទាំងអស់**
       - `GET /v1/locations`
    2. **បង្ហាញស្រុកទាំងអស់នៅក្នុងខេត្ត (ប្រើឈ្មោះអង់គ្លេស ឬខ្មែរ ឬកូដ)**
       - `GET /v1/locations?province=Siemreap`
       - `GET /v1/locations?p=សៀមរាប`
    3. **បង្ហាញឃុំទាំងអស់នៅក្នុងស្រុក (ប្រើទម្រង់ខ្លី លាយគ្នាបាន)**
       - `GET /v1/locations?province=Siemreap&d=Angkor Thum`
    4. **បង្ហាញភូមិទាំងអស់នៅក្នុងឃុំ**
       - `GET /v1/locations?province=Siemreap&d=Angkor Thum&c=ជប់តាត្រាវ`
       - `GET /v1/locations?p=17&d=1703&c=170301`

    *ចំណាំ: ប្រសិនបើស្វែងរកមិនឃើញទិន្នន័យ ប្រព័ន្ធនឹងផ្តល់លទ្ធផលជា Array ទទេ `[]` ត្រឡប់ទៅវិញ។*
    """
    # ចាប់យកតម្លៃទម្រង់ពេញ ឬទម្រង់ខ្លី
    q_province = province or p
    q_district = district or d
    q_commune = commune or c
    
    def filter_locations():
        # --- ១. ករណីមិនទាន់បញ្ជូនអ្វីទាំងអស់ => បង្ហាញខេត្តទាំងអស់ ---
        if q_province is None:
            return province_df[["province_code", "province_kh", "province_en"]].to_dict(orient="records")

        # ស្វែងរកខេត្ត (រកតាម code, province_kh, ឬ province_en)
        cleaned_p = clean_string(q_province)
        matched_provinces = province_df[
            (province_df["province_code"] == q_province) |
            (province_df["province_kh"] == q_province) |
            (province_df["province_en"].str.strip().str.lower().str.replace(" ", "") == cleaned_p)
        ]
        
        if matched_provinces.empty:
            return []
        
        # យក province_code ពិតប្រាកដពីលទ្ធផលដែលរកឃើញ ដើម្បីយកទៅ filter ថ្នាក់បន្តបន្ទាប់
        target_province_code = matched_provinces.iloc[0]["province_code"]

        # --- ២. មានខេត្ត តែអត់ទាន់មានស្រុក និងឃុំ => បង្ហាញស្រុកទាំងអស់ក្នុងខេត្តនោះ ---
        if q_district is None and q_commune is None:
            filtered = district_df[district_df["province_code"] == target_province_code]
            return filtered[["district_code", "district_kh", "district_en"]].to_dict(orient="records")

        # ស្វែងរកស្រុកនៅក្នុងខេត្តដែលបានជ្រើសរើស
        cleaned_d = clean_string(q_district)
        matched_districts = district_df[
            (district_df["province_code"] == target_province_code) & 
            (
                (district_df["district_code"] == q_district) |
                (district_df["district_kh"] == q_district) |
                (district_df["district_en"].str.strip().str.lower().str.replace(" ", "") == cleaned_d)
            )
        ]
        
        if matched_districts.empty:
            return []
            
        target_district_code = matched_districts.iloc[0]["district_code"]

        # --- ៣. មានខេត្ត មានស្រុក តែអត់ទាន់មានឃុំ => បង្ហាញឃុំទាំងអស់ក្នុងស្រុកនោះ ---
        if q_commune is None:
            filtered = commune_df[
                (commune_df["province_code"] == target_province_code) &
                (commune_df["district_code"] == target_district_code)
            ]
            return filtered[["commune_code", "commune_kh", "commune_en"]].to_dict(orient="records")

        # ស្វែងរកឃុំនៅក្នុងស្រុកដែលបានជ្រើសរើស
        cleaned_c = clean_string(q_commune)
        matched_communes = commune_df[
            (commune_df["province_code"] == target_province_code) &
            (commune_df["district_code"] == target_district_code) &
            (
                (commune_df["commune_code"] == q_commune) |
                (commune_df["commune_kh"] == q_commune) |
                (commune_df["commune_en"].str.strip().str.lower().str.replace(" ", "") == cleaned_c)
            )
        ]
        
        if matched_communes.empty:
            return []
            
        target_commune_code = matched_communes.iloc[0]["commune_code"]

        # --- ៤. មានគ្រប់ទាំងអស់ (ខេត្ត ស្រុក ឃុំ) => បង្ហាញភូមិទាំងអស់នៅក្នុងឃុំនោះ ---
        filtered = village_df[
            (village_df["province_code"] == target_province_code) &
            (village_df["district_code"] == target_district_code) &
            (village_df["commune_code"] == target_commune_code)
        ]
        return filtered[["village_code", "village_kh", "village_en"]].to_dict(orient="records")

    return await asyncio.to_thread(filter_locations)