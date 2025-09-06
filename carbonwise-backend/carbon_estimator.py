import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# Load multiple API keys like DETAILS_API_KEY1, DETAILS_API_KEY2...
API_KEYS = [v for k, v in os.environ.items() if k.startswith("DETAILS_API_KEY")]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter_api(system_prompt: str, user_content: str) -> int:
    """
    Call OpenRouter API with fallback across multiple API keys.
    Returns a single integer (carbon footprint estimate in kg).
    """
    headers_template = {"Content-Type": "application/json"}
    data = {
    "model": "meta-llama/llama-4-maverick:free",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ],
    }

    last_error = None
    for idx, api_key in enumerate(API_KEYS, start=1):
        headers = headers_template.copy()
        headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=20)

            try:
                resp_json = response.json()
            except ValueError:
                last_error = f"[Key {idx}] Invalid JSON response"
                continue

            if response.status_code == 200 and "choices" in resp_json:
                raw_output = resp_json["choices"][0]["message"]["content"].strip()

                # ✅ Extract last integer in text
                numbers = re.findall(r"\d+", raw_output)
                if numbers:
                    return int(numbers[-1])  # Final carbon estimate in kg
                else:
                    last_error = f"[Key {idx}] No integer found in output: {raw_output}"
                    continue
            else:
                last_error = f"[Key {idx}] API failed: {response.status_code} - {response.text}"
                continue

        except requests.exceptions.RequestException as e:
            last_error = f"[Key {idx}] Network/API error: {e}"
            continue

    raise Exception(f"❌ All API keys failed.\nLast error: {last_error}")


def estimate_carbon(product_description: str) -> int:
    """
    Estimate carbon footprint of a product using LLM.
    Returns an integer value (kg of CO₂e).
    """
    print("🌍 Estimating carbon footprint...")

    system_prompt = (
        "You are an expert in sustainability and carbon emissions. "
        "Given a product description with material, weight, and quantity, "
        "estimate the total carbon footprint in **kilograms of CO₂e**. "
        "Respond with ONLY one integer number (no units, no words, no explanation)."
        "Return only one integer number in kilograms (kg CO₂e). "
        "Do not calculate in grams. Do not explain. "
        "If unsure, approximate and round to the nearest integer."
        "for any Mobile Phone -Smartphone keep the estimation range under 100 Kg"
    )

    return call_openrouter_api(system_prompt, product_description)


# Example usage
if __name__ == "__main__":
    desc = "Product: Stainless Steel Spoon Set, Material: Stainless Steel, Weight: 25g each, Quantity: 12"
    try:
        carbon_value = estimate_carbon(desc)
        print(f"✅ Estimated Carbon Footprint: {carbon_value} kg CO₂e")
    except Exception as e:
        print(str(e))
