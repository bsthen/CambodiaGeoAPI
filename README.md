# 🇰🇭 Cambodia Geo Locations API

A public FastAPI-powered API for retrieving **geographic administrative data of Cambodia**, including **provinces**, **districts**, **communes**, and **villages**.

> 📍 Powered by official data from the [General Department of Digital Economy](https://data.mef.gov.kh/)

---

## 🚀 Demo (local)

**Base URL:**

[http://localhost:8000/v1/](http://localhost:8000/v1/)

**Interactive Docs:**

[http://localhost:8000/v1/docs/](http://localhost:8000/v1/docs/)

**Interactive ReDoc:**

[http://localhost:8000/v1/redoc/](http://localhost:8000/v1/redoc/)

---

## 🚀 Demo (public)

**Base URL:**

[https://cambodia-geo-api.bsthen.com/v1/](https://cambodia-geo-api.bsthen.com/v1/)

**Interactive Docs:**

[https://cambodia-geo-api.bsthen.com/v1/docs/](https://cambodia-geo-api.bsthen.com/v1/docs/)

**Interactive ReDoc:**

[https://cambodia-geo-api.bsthen.com/v1/redoc/](https://cambodia-geo-api.bsthen.com/v1/redoc/)

---

## 📦 Features

- ✅ Get all provinces in Cambodia
- ✅ Drill down from province → district → commune → village
- ✅ Khmer and English names
- ✅ Fast and lightweight (CSV-based, cached in memory)

---

## 📚 API Usage

### `GET /locations`

Retrieve geographic information based on optional filters.

#### 🔸 Parameters

| Name      | Type     | Description                          |
|-----------|----------|--------------------------------------|
| province  | `string` | (optional) Province code             |
| district  | `string` | (optional) District code             |
| commune   | `string` | (optional) Commune code              |

#### 🔸 Examples

**1. Get all provinces:**

`GET /v1/locations`

**2. Get all districts in a province:**

`GET /v1/locations?province=12`

**3. Get all communes in a district:**

`GET /v1/locations?province=12&district=1210`

**4. Get all villages in a commune:**

`GET /v1/locations?province=12&district=1210&commune=121001`

---

## 📄 Source Data

- All data is sourced from: **[https://data.mef.gov.kh](https://data.mef.gov.kh/)**
  Specifically:
  - `CambodiaProvinceList2023.csv`
  - `CambodiaDistrictList2023.csv`
  - `CambodiaCommuneList2023.csv`
  - `CambodiaVillagesList2023.csv`

---

## 👨‍💻 Developer Info

- **Author**: [bsthen](https://github.com/bsthen)
- **Version**: `1.0.6`
- **License**: MIT
- **Contact**: via GitHub

---

## 🛠️ Development

### Requirements

- Python 3.8+
- FastAPI
- pandas
- uvicorn

### Install and run locally

```bash
git clone https://github.com/bsthen/CambodiaGeoAPI.git
cd CambodiaGeoAPI

# (optional) create virtual environment
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload

```

## 📬 Feedback & Contributions

Feel free to:

- ⭐ Star the repo
- 🐛 Report issues
- 🤝 Submit pull requests
