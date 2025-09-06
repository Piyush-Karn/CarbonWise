# import os
# import re
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# # Load multiple API keys like DETAILS_API_KEY1, DETAILS_API_KEY2...
# API_KEYS = [v for k, v in os.environ.items() if k.startswith("DETAILS_API_KEY")]

# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# def call_openrouter_api(system_prompt: str, user_content: str) -> int:
#     """
#     Call OpenRouter API with fallback across multiple API keys.
#     Returns a single integer (carbon footprint estimate in kg).
#     """
#     headers_template = {"Content-Type": "application/json"}
#     data = {
#     "model": "qun-3-2b",
#     "messages": [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_content},
#     ],
#     }

#     last_error = None
#     for idx, api_key in enumerate(API_KEYS, start=1):
#         headers = headers_template.copy()
#         headers["Authorization"] = f"Bearer {api_key}"

#         try:
#             response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=20)

#             try:
#                 resp_json = response.json()
#             except ValueError:
#                 last_error = f"[Key {idx}] Invalid JSON response"
#                 continue

#             if response.status_code == 200 and "choices" in resp_json:
#                 raw_output = resp_json["choices"][0]["message"]["content"].strip()

#                 # ✅ Extract last integer in text
#                 numbers = re.findall(r"\d+", raw_output)
#                 if numbers:
#                     return int(numbers[-1])  # Final carbon estimate in kg
#                 else:
#                     last_error = f"[Key {idx}] No integer found in output: {raw_output}"
#                     continue
#             else:
#                 last_error = f"[Key {idx}] API failed: {response.status_code} - {response.text}"
#                 continue

#         except requests.exceptions.RequestException as e:
#             last_error = f"[Key {idx}] Network/API error: {e}"
#             continue

#     raise Exception(f"❌ All API keys failed.\nLast error: {last_error}")


# def estimate_carbon(product_description: str) -> int:
#     """
#     Estimate carbon footprint of a product using LLM.
#     Returns an integer value (kg of CO₂e).
#     """
#     print("🌍 Estimating carbon footprint...")

#     system_prompt = """
#     You are an expert in carbon footprint estimation.
#     Use the following approximate emission factors (cradle-to-gate averages):
#     - Stainless steel: 6.15 kg CO₂e per kg
#     - Plastic (generic): 2.5 kg CO₂e per kg
#     - Glass: 1.2 kg CO₂e per kg
#     - Aluminum: 16.5 kg CO₂e per kg
#     - Wood: 0.5 kg CO₂e per kg
#     - Paper/Cardboard: 1.1 kg CO₂e per kg

#     Steps:
#     1. Estimate the approximate weight (in kg) of the product from description.
#     2. Multiply by the relevant emission factor.
#     3. Round to the nearest integer (kg CO₂e).

#     Return only ONE integer number. No units, no text.
#     If material is unclear, choose the closest match.
#     If multiple items (like a set), multiply by the quantity.
#     For any smartphone, cap the estimate at 50 - 100 kg.
#     """
#     return call_openrouter_api(system_prompt, product_description)


import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# --- Setup ---
# Load environment variables from the .env file
load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API")
if not api_key:
    raise ValueError("❌ GOOGLE_API key not found. Please make sure it's set in your .env file.")
genai.configure(api_key=api_key)


def call_gemini_api(system_prompt: str, user_content: str) -> int:
    """
    Call Gemini API for carbon footprint estimation.
    Returns a single integer (carbon footprint estimate in kg).
    """
    # Combine system + user prompt since Gemini works better with unified instructions
    prompt = f"{system_prompt.strip()}\n\nProduct Description: {user_content.strip()}"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        # ✅ Extract last integer in text
        numbers = re.findall(r"\d+", raw_output)
        if numbers:
            return int(numbers[-1])  # Final carbon estimate in kg
        else:
            raise ValueError(f"No integer found in output: {raw_output}")

    except Exception as e:
        raise Exception(f"❌ Gemini API error: {e}")


def estimate_carbon(product_description: str) -> int:
    """
    Estimate carbon footprint of a product using Gemini.
    Returns an integer value (kg of CO₂e).
    """
    print("🌍 Estimating carbon footprint...")

    system_prompt = """
    You are an expert in carbon footprint estimation.
    Use the following approximate emission factors (cradle-to-gate averages):
    - Stainless steel: 6.15 kg CO₂e per kg
    - Plastic (generic): 2.5 kg CO₂e per kg
    - Glass: 1.2 kg CO₂e per kg
    - Aluminum: 16.5 kg CO₂e per kg
    - Wood: 0.5 kg CO₂e per kg
    - Paper/Cardboard: 1.1 kg CO₂e per kg

    Steps:
    1. Estimate the approximate weight (in kg) of the product from description.
    2. Multiply by the relevant emission factor.
    3. Round to the nearest integer (kg CO₂e).

    Special rules:
    - For any smartphone, cap the estimate between 50 and 100 kg.
    - For any laptop, cap the estimate between 200 and 400 kg.
    - For clothing (t-shirt, jeans), expect 10–50 kg depending on type.
    - For furniture (tables, chairs), expect 20–200 kg depending on size.
    - If material is unclear, choose the closest match.
    - If multiple items (like a set), multiply by the quantity.

    Return only ONE integer number. No units, no text.
    """

    return call_gemini_api(system_prompt, product_description)


# Example usage
if __name__ == "__main__":
    try:
        desc = "Product: Stainless Steel Spoon Set, Material: Stainless Steel, Weight: 25g each, Quantity: 12"
        carbon_value = estimate_carbon(desc)
        print(f"✅ Estimated Carbon Footprint: {carbon_value} kg CO₂e")
    except Exception as e:
        print(str(e))
