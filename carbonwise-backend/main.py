from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from collections import OrderedDict
import uvicorn

from carbon_estimator import estimate_carbon

app = FastAPI(title="CarbonWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Models ---
class ProductAnalysisRequest(BaseModel):
    url: str

class Recommendation(BaseModel):
    product_name: str
    image_url: Optional[str]
    material: Optional[str]
    carbon_footprint: Optional[float]
    link: Optional[str]

class ProductAnalysisResponse(BaseModel):
    success: bool
    product_name: str
    image_url: Optional[str]
    carbon_footprint: Optional[float]
    material: Optional[str]
    weight_value: Optional[str]
    weight_unit: Optional[str]
    materials: List[Tuple[str, str]]
    weights: List[Tuple[str, str]]
    net_quantities: List[Tuple[str, str]]
    recommendations: List[Recommendation]
    error: Optional[str] = None

# --- Helpers ---
def find_best_material_match(text_to_search: str, known_materials: list) -> Optional[str]:
    if not text_to_search or not isinstance(text_to_search, str):
        return None
    lower_text = text_to_search.lower()
    for m in known_materials:
        if m == lower_text:
            return m
            
    material_regex = re.compile('|'.join(re.escape(m) for m in known_materials))
    match = material_regex.search(lower_text)
    return match.group(0) if match else None

def convert_to_kg(value: float, unit: Optional[str]) -> float:
    if unit is None:
        return value
    unit = unit.lower()
    if unit in ['g', 'gm', 'grams']:
        return value / 1000.0
    if unit in ['oz', 'ounce', 'ounces']:
        return value * 0.0283495
    if unit in ['lb', 'lbs', 'pound', 'pounds']:
        return value * 0.453592
    return value

# --- Web Scraper ---
def extract_specs(driver) -> dict:
    materials_found, weights, quantities = [], OrderedDict(), OrderedDict()
    priority_groups = [
        ["#productDetails_techSpec_section_1 tr", "#productDetails_techSpec_section_2 tr"],
        ["table.a-keyvalue tr"],
        ["#productOverview_feature_div table tr"],
        ["#detailBullets_feature_div li", "#productDetails_detailBullets_sections1 tr"]
    ]
    for selectors in priority_groups:
        rows = []
        for sel in selectors:
            try:
                rows.extend(driver.find_elements(By.CSS_SELECTOR, sel))
            except Exception:
                pass
        for row in rows:
            try:
                if row.tag_name.lower() == "tr":
                    cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 2:
                        continue
                    key, val = cells[0].text.strip(), cells[1].text.strip()
                else:
                    txt = row.text.strip()
                    if ":" not in txt:
                        continue
                    key, val = [p.strip() for p in txt.split(":", 1)]
                lk = key.lower()
                if val:
                    if "material" in lk:
                        materials_found.append(val)
                    elif "weight" in lk and key not in weights:
                        weights[key] = val
                    elif ("quantity" in lk or "unit count" in lk) and key not in quantities:
                        quantities[key] = val
            except Exception:
                continue
    return {"materials_found": materials_found, "weights": weights, "quantities": quantities}

def parse_weight(weight_str):
    if not weight_str:
        return None, None
    match = re.search(r"([\d.,]+)\s*([a-zA-Z]+)", weight_str)
    if match:
        return match.group(1).replace(",", ""), match.group(2)
    return weight_str, None

def scrape_amazon_product(url: str, headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)

        name = driver.find_element(By.ID, "productTitle").text.strip()
        image_url = driver.find_element(By.ID, "landingImage").get_attribute("src")

        picked = extract_specs(driver)
        first_weight_val = next(iter(picked["weights"].values()), None)
        first_quantity_val = next(iter(picked["quantities"].values()), "1")
        weight_value_str, weight_unit = parse_weight(first_weight_val)
        weight_value = float(weight_value_str) if weight_value_str else 1.0

        net_quantity_match = re.search(r'\d+', str(first_quantity_val))
        net_quantity = int(net_quantity_match.group()) if net_quantity_match else 1

        driver.quit()
        return {
            "name": name,
            "image_url": image_url,
            "materials_found": picked["materials_found"],
            "weights": list(picked["weights"].items()),
            "net_quantities": list(picked["quantities"].items()),
            "weight_value": weight_value,
            "weight_unit": weight_unit,
            "net_quantity": net_quantity,
        }
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        raise e

# --- Carbon Logic ---
def calculate_carbon_footprint(material: Optional[str], weight_in_kg: float, net_quantity: float, product_data: dict, ef_df: pd.DataFrame):
    # If we found a direct material match in our database, use it for a precise calculation.
    if material:
        ef_row = ef_df[ef_df['material_clean'] == material]
        if not ef_row.empty:
            emission_factor = float(ef_row.iloc[0]['kg CO2 eq/kg'])
            return weight_in_kg * net_quantity * emission_factor

    # Fallback to LLM estimation if material is unknown or not in our database.
    try:
        print("⚠️ Material not in dataset. Attempting carbon estimation via LLM...")
        # Create a detailed description for the LLM
        description = f"Product: {product_data.get('name', 'N/A')}, Weight: {weight_in_kg:.3f} kg, Quantity: {net_quantity}"
 
        if product_data.get('materials_found'):
            materials_str = ", ".join(product_data['materials_found'])
            description += f", Scraped Material Info: {materials_str}"
            print("Using LLM estimator")

        return float(estimate_carbon(description))
    except Exception as e:
        print(f"Carbon estimator LLM failed: {e}. Using default fallback.")
        print("Using Fallback")
        return weight_in_kg * net_quantity * 2.5

def get_recommendations(product_name: str, analyzed_carbon_footprint: float) -> List[Recommendation]:
    try:
        products_df = pd.read_csv('amazon_products.csv')
        ef_df = pd.read_csv('emission_factor_dataset.csv', sep='\t')
        
        ef_df.rename(columns={ef_df.columns[0]: 'Material', ef_df.columns[2]: 'kg CO2 eq/kg'}, inplace=True)
        ef_df['material_clean'] = ef_df['Material'].str.strip().str.lower()

        product_categories = products_df['Search Query'].dropna().unique()
        sorted_categories = sorted(product_categories, key=len, reverse=True)
        
        matched_category = None
        lower_product_name = product_name.lower()
        for category in sorted_categories:
            if category.lower() in lower_product_name:
                matched_category = category
                break
        
        if not matched_category:
            return []

        category_products_df = products_df[products_df['Search Query'] == matched_category].copy()
        category_products_df = category_products_df[category_products_df['Title'] != product_name]
        
        if category_products_df.empty:
            return []
            
        category_products_df['material_clean'] = category_products_df['Material'].str.strip().str.lower()
        merged_df = pd.merge(
            category_products_df,
            ef_df[['material_clean', 'kg CO2 eq/kg']],
            on='material_clean',
            how='left'
        )
        merged_df['kg CO2 eq/kg'].fillna(2.5, inplace=True)

        weights = pd.to_numeric(merged_df['Weight Value'], errors='coerce')
        quantities = pd.to_numeric(merged_df['Net Quantity'], errors='coerce')
        emission_factors = pd.to_numeric(merged_df['kg CO2 eq/kg'], errors='coerce')

        merged_df['carbon_footprint'] = (weights * quantities * emission_factors).round(3)
        merged_df.dropna(subset=['carbon_footprint'], inplace=True)
        
        if analyzed_carbon_footprint is not None:
             merged_df = merged_df[merged_df['carbon_footprint'] < analyzed_carbon_footprint]

        sorted_recommendations = merged_df.sort_values(by='carbon_footprint').head(10)
        
        final_list = [
            Recommendation(
                product_name=row['Title'],
                image_url=row['img_url'],
                material=row['Material'],
                carbon_footprint=row['carbon_footprint'],
                link=row['Link']
            ) for _, row in sorted_recommendations.iterrows()
        ]
        return final_list

    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []


# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "CarbonWise API is running!"}

@app.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(request: ProductAnalysisRequest):
    try:
        product_data = scrape_amazon_product(request.url)
        weight_in_kg = convert_to_kg(product_data["weight_value"], product_data.get("weight_unit"))

        ef_df = pd.read_csv('emission_factor_dataset.csv', sep='\t')
        ef_df.rename(columns={ef_df.columns[0]: 'Material', ef_df.columns[2]: 'kg CO2 eq/kg'}, inplace=True)
        ef_df['material_clean'] = ef_df['Material'].str.strip().str.lower()
        known_materials = sorted(ef_df['material_clean'].dropna().unique(), key=len, reverse=True)
        
        best_material_match = next((find_best_material_match(m, known_materials) for m in product_data["materials_found"] if find_best_material_match(m, known_materials)), None)

        carbon_footprint = calculate_carbon_footprint(
            best_material_match, weight_in_kg,
            product_data["net_quantity"], product_data, ef_df
        )

        final_materials = [("Primary Material", best_material_match)] if best_material_match else [
            ("Scraped Text", m) for m in product_data.get('materials_found', [])
        ]
        
        recommendations = get_recommendations(product_data["name"], carbon_footprint)

        return ProductAnalysisResponse(
            success=True,
            product_name=product_data["name"],
            image_url=product_data["image_url"],
            carbon_footprint=round(carbon_footprint, 3),
            material=best_material_match or (product_data["materials_found"][0] if product_data["materials_found"] else "Unknown"),
            weight_value=f"{weight_in_kg:.3f}",
            weight_unit="kg",
            materials=final_materials,
            weights=product_data["weights"],
            net_quantities=product_data["net_quantities"],
            recommendations=recommendations
        )
    except Exception as e:
        return ProductAnalysisResponse(
            success=False, product_name="Error", error=str(e), image_url=None,
            carbon_footprint=None, material=None, weight_value=None, weight_unit=None,
            materials=[], weights=[], net_quantities=[], recommendations=[]
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

