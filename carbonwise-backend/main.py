from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from collections import OrderedDict
import uvicorn

app = FastAPI(title="CarbonWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ProductAnalysisRequest(BaseModel):
    url: str

class ProductAnalysisResponse(BaseModel):
    success: bool
    product_name: str
    image_url: Optional[str]
    carbon_footprint: Optional[float]
    material: Optional[str]
    weight_value: Optional[str]
    weight_unit: Optional[str]
    materials: List[tuple]
    weights: List[tuple]
    net_quantities: List[tuple]
    error: Optional[str] = None

# Your existing scraper functions (copy from scraper.py)
def extract_specs(driver):
    materials = OrderedDict()
    weights = OrderedDict()
    quantities = OrderedDict()

    priority_groups = [
        ["#productDetails_techSpec_section_1 tr", "#productDetails_techSpec_section_2 tr"],
        ["table.a-keyvalue tr"],
        ["#productOverview_feature_div table tr", "table.a-normal.a-spacing-micro tr"],
        ["#productDetails_detailBullets_sections1 tr", "#detailBullets_feature_div li"]
    ]

    def handle_pair(k, v, target_dict):
        if k not in target_dict and v:
            target_dict[k] = v

    for selectors in priority_groups:
        rows = []
        for sel in selectors:
            try:
                rows.extend(driver.find_elements(By.CSS_SELECTOR, sel))
            except Exception:
                pass

        for row in rows:
            if row.tag_name.lower() == "tr":
                cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    key = cells[0].text.strip()
                    val = cells[1].text.strip()
                else:
                    continue
            else:
                txt = row.text.strip()
                if ":" in txt:
                    key, val = [p.strip() for p in txt.split(":", 1)]
                else:
                    continue

            lk = key.lower()
            if "material" in lk:
                handle_pair(key, val, materials)
            elif "weight" in lk:
                handle_pair(key, val, weights)
            elif "net quantity" in lk or "unit count" in lk or "quantity" in lk:
                handle_pair(key, val, quantities)

    return {"materials": materials, "weights": weights, "quantities": quantities}

def parse_weight(weight_str):
    if not weight_str:
        return None, None
    match = re.search(r"([\d.,]+)\s*([a-zA-Z]+)", weight_str)
    if match:
        value = match.group(1).replace(",", "")
        unit = match.group(2)
        return value, unit
    return weight_str, None

def scrape_amazon_product(url: str, headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)

        name = "Not Found"
        try:
            name = driver.find_element(By.ID, "productTitle").text.strip()
        except:
            pass

        image_url = None
        try:
            image_el = driver.find_element(By.ID, "landingImage")
            image_url = image_el.get_attribute("src")
        except:
            try:
                image_el = driver.find_element(By.CSS_SELECTOR, "#imgTagWrapperId img")
                image_url = image_el.get_attribute("src")
            except:
                pass

        picked = extract_specs(driver)
        first_weight_val = next(iter(picked["weights"].values()), None)
        weight_value, weight_unit = parse_weight(first_weight_val)

        driver.quit()

        return {
            "name": name,
            "image_url": image_url,
            "materials": list(picked["materials"].items()),
            "weights": list(picked["weights"].items()),
            "net_quantities": list(picked["quantities"].items()),
            "weight_value": weight_value,
            "weight_unit": weight_unit,
        }
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        raise e

def calculate_carbon_footprint(material: str, weight_value: float, net_quantity: int):
    try:
        ef_df = pd.read_csv('emission_factor_dataset.csv', sep='\t')
        ef_matches = ef_df[ef_df.iloc[:, 0].str.strip() == str(material).strip()]
        
        if not ef_matches.empty:
            emission_factor = float(ef_matches.iloc[0, 2])
            result = weight_value * net_quantity * emission_factor
            return result
        else:
            return weight_value * net_quantity * 2.5
    except Exception:
        return weight_value * net_quantity * 2.5

@app.get("/")
async def root():
    return {"message": "CarbonWise API is running!"}

@app.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(request: ProductAnalysisRequest):
    try:
        product_data = scrape_amazon_product(request.url)
        
        material = None
        if product_data["materials"]:
            material = product_data["materials"][0][1]
        
        weight_value = product_data["weight_value"]
        if weight_value:
            try:
                weight_value = float(weight_value)
            except:
                weight_value = 1.0
        else:
            weight_value = 1.0
        
        net_quantity = 1
        if product_data["net_quantities"]:
            try:
                qty_str = product_data["net_quantities"][0][1]
                net_quantity = int(re.search(r'\d+', str(qty_str)).group())
            except:
                net_quantity = 1
        
        carbon_footprint = None
        if material:
            carbon_footprint = calculate_carbon_footprint(material, weight_value, net_quantity)
        
        return ProductAnalysisResponse(
            success=True,
            product_name=product_data["name"],
            image_url=product_data["image_url"],
            carbon_footprint=carbon_footprint,
            material=material,
            weight_value=str(weight_value),
            weight_unit=product_data["weight_unit"],
            materials=product_data["materials"],
            weights=product_data["weights"],
            net_quantities=product_data["net_quantities"]
        )
    
    except Exception as e:
        return ProductAnalysisResponse(
            success=False,
            product_name="Error",
            image_url=None,
            carbon_footprint=None,
            material=None,
            weight_value=None,
            weight_unit=None,
            materials=[],
            weights=[],
            net_quantities=[],
            error=str(e)
        )

@app.post("/recommendations")
async def get_recommendations(material: str):
    try:
        df = pd.read_csv('amazon_products.csv')
        ef_df = pd.read_csv('emission_factor_dataset.csv', sep='\t')
        main_list = {}

        if df.shape[1] >= 6:
            column_3_list = df.iloc[:, 2].tolist()
            if material in column_3_list:
                matching_rows = df[df.iloc[:, 2] == material]
                
                for idx, row in matching_rows.iterrows():
                    ef_matches = ef_df[ef_df.iloc[:, 0].str.strip() == str(material).strip()]
                    
                    if not ef_matches.empty:
                        emission_factor = float(ef_matches.iloc[0, 2])
                        value_4 = float(row.iloc[3])
                        value_5 = float(row.iloc[4])
                        result = value_4 * value_5 * emission_factor
                        main_list[row.iloc[5]] = [result]
                
                main_list = dict(sorted(main_list.items(), key=lambda item: item[1]))
        
        return {
            "success": True,
            "recommendations": main_list,
            "total_analyzed": len(main_list)
        }
    
    except Exception as e:
        return {
            "success": False,
            "recommendations": {},
            "total_analyzed": 0,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)