from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
from vision import identify_clothing
from PIL import Image
from skin_tone import analyze_skin_tone
from fastapi import UploadFile, File
import io
import json
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://fashion-stylist-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Fashion Stylist AI Backend Running"
    }

@app.post("/analyze-face")
async def analyze_face(face: UploadFile = File(...)):

    temp_path = "temp_face.jpg"

    with open(temp_path, "wb") as buffer:
        buffer.write(await face.read())

    result = analyze_skin_tone(temp_path)

    return result


@app.post("/recommend")
async def recommend_style(
    occasion: str = Form(...),
    face: UploadFile | None = File(None),
    wardrobe: list[UploadFile] = File(...)
):
    try:
        # Validate wardrobe count
        if len(wardrobe) < 2 or len(wardrobe) > 6:
            return {
                "looks": [],
                "error": "Please upload between 2 and 6 wardrobe items."
            }

       

        prompt = f"""
You are an expert celebrity fashion stylist.

Occasion: {occasion}

The user has uploaded:
- Multiple wardrobe items
{"- A face photo" if face else ""}

Tasks:

1. Identify EVERY uploaded wardrobe image individually.

Example:
Item 1 = Burgundy off shoulder maxi dress
Item 2 = Black leather boots
Item 3 = Black strappy heels

2. Identify ALL possible complete outfits from the uploaded wardrobe.

3. Score each outfit based on how suitable it is for the selected occasion.

4. Rank the outfits from BEST to WORST.

5. Return ONLY the TOP 3 highest-scoring looks.

6. The SAME wardrobe and SAME occasion MUST always produce the SAME ranking and recommendations.

7. Do NOT randomly change the order of looks.

8. For EACH look:
   - Use ONLY the uploaded wardrobe items.
   - Return usedWardrobeItems as objects.
   - Each object must contain:
       • itemNumber
       • itemDescription
   - itemDescription MUST describe the SAME uploaded item.
   - Never invent descriptions that do not match the item number.
   - Never use generic phrases such as
     "selected wardrobe pieces".

9. Recommend shoes, bags and accessories.

10. Suggest makeup suitable for the user.

11. Suggest hairstyle suitable for the face shape.

12. Explain why each look suits the user and occasion.

13. Give a confidence score from 0–100.

14. Recommend any missing item that could improve the outfit.

15. Mention the fashion vibe.

16. Suggest whether the look is trendy,
    timeless or experimental.

17. Give one short pro stylist tip.

18. Decide which look is BEST.

19. Decide which look is the ALTERNATIVE.

20. bestLook and alternativeLook MUST NEVER be the same.

Return ONLY VALID JSON in this exact format:

{{
    "looks": [
        {{
            "title": "",
            "fashionVibe": "",
            "usedWardrobeItems": [
        {{
            "itemNumber": 1,
            "itemDescription": ""
        }}
            ],
            "shoes": "",
            "bag": "",
            "accessories": "",
            "makeup": "",
            "hairstyle": "",
            "stylistTip": "",
            "reason": "",
            "missingItem": "",
            "trendCategory": "",
            "colorPalette": [
                "White",
                "Olive Green",
                "Charcoal",
                "Beige"
            ],
            "confidence": 0,
            "suitabilityScore": 0
        }},
        {{
            "title": "",
            "fashionVibe": "",
            "usedWardrobeItems": [
        {{
            "itemNumber": 1,
            "itemDescription": ""
        }}
            ],
            "shoes": "",
            "bag": "",
            "accessories": "",
            "makeup": "",
            "hairstyle": "",
            "stylistTip": "",
            "reason": "",
            "missingItem": "",
            "trendCategory": "",
            "colorPalette": [
                "White",
                "Olive Green",
                "Charcoal",
                "Beige"
            ],
            "confidence": 0,
            "suitabilityScore": 0
        }},
        {{
            "title": "",
            "fashionVibe": "",
            "usedWardrobeItems": [
        {{
            "itemNumber": 1,
            "itemDescription": ""
        }}
            ],
            "shoes": "",
            "bag": "",
            "accessories": "",
            "makeup": "",
            "hairstyle": "",
            "stylistTip": "",
            "reason": "",
            "missingItem": "",
            "trendCategory": "",
            "colorPalette": [
                "White",
                "Olive Green",
                "Charcoal",
                "Beige"
            ],
            "confidence": 0,
            "suitabilityScore": 0
        }}
    ],

    "stylistVerdict": {{
        "bestLook": 1,
        "alternativeLook": 2,
        "reason": ""
    }}
}}

Rules:
- Return VALID JSON only.
- No markdown.
- No explanation outside JSON.
- Generate EXACTLY 3 looks.
- confidence must be between 0 and 100.
- Return EXACTLY 4 COLOR NAMES.
- Never return HEX codes.
- trendCategory must be one of:
  "Trendy", "Timeless", "Experimental".
- stylistTip should be one practical sentence.
- missingItem can be empty.
- bestLook and alternativeLook must be numbers 1–3.
- bestLook must represent the strongest recommendation.
- alternativeLook must represent another suitable choice.
- stylistVerdict.reason should explain in SIMPLE language why the best look is recommended.
Occasion ranking guidelines:

Wedding:
- Traditional ethnic outfits score highest.
- Elegant Indo-western outfits score second.
- Casual western outfits score lowest.

Party:
- Festive and glamorous outfits score highest.
- Trendy statement outfits score second.
- Simple outfits score lowest.

Office:
- Professional and polished outfits score highest.
- Smart casual looks score second.
- Experimental fashion scores lowest.

Casual:
- Comfortable and versatile outfits score highest.
- Trendy everyday outfits score second.
- Formal outfits score lowest.

- suitabilityScore must be between 0 and 100.
- Sort looks by suitabilityScore in descending order.
- Look 1 must always have the highest suitabilityScore.
- bestLook must always correspond to the highest suitabilityScore.
- alternativeLook must be the second highest suitabilityScore.
"""

        wardrobe_descriptions = []

        for item in wardrobe:
            image_bytes = await item.read()

            img = Image.open(
                io.BytesIO(image_bytes)
            ).convert("RGB")

            description = identify_clothing(img)

            wardrobe_descriptions.append(description)

        wardrobe_text = ""

        for i, desc in enumerate(wardrobe_descriptions, start=1):
            wardrobe_text += f"Item {i}: {desc}\n"

        groq_prompt = f"""
You are an expert celebrity fashion stylist.

Occasion: {occasion}

Wardrobe:
{wardrobe_text}

{prompt}

Return ONLY valid JSON.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": groq_prompt
                }
            ],
            temperature=0.1
        )

        result = response.choices[0].message.content.strip()

        print("\n===== GROQ RESPONSE =====")
        print(result)
        print("=========================\n")

        # Remove markdown code fences if Groq returns them
        if result.startswith("```json"):
            result = result.replace("```json", "", 1)

        if result.startswith("```"):
            result = result.replace("```", "", 1)

        if result.endswith("```"):
            result = result.rsplit("```", 1)[0]

        result = result.strip()

        parsed = json.loads(result)
        if "looks" not in parsed:
             raise ValueError("Missing looks field")

        parsed["looks"] = sorted(
            parsed["looks"],
            key=lambda x: x.get("suitabilityScore", 0),
            reverse=True
        )

        if len(parsed["looks"]) != 3:
            raise ValueError("Groq did not return 3 looks")

        max_items = len(wardrobe)

        for look in parsed["looks"]:
            look.setdefault("suitabilityScore", 0)
            look.setdefault("confidence", 0)
            look.setdefault("usedWardrobeItems", [])

            look["usedWardrobeItems"] = [
                item
                for item in look["usedWardrobeItems"]
                if isinstance(item, dict)
                and isinstance(item.get("itemNumber"), int)
                and 1 <= item["itemNumber"] <= max_items
            ]

            if not look["usedWardrobeItems"]:
                raise ValueError(
                     "Groq returned invalid usedWardrobeItems"
                 )

        parsed.setdefault("stylistVerdict", {})

        parsed["stylistVerdict"]["bestLook"] = parsed[
           "stylistVerdict"
        ].get("bestLook", 1)

        parsed["stylistVerdict"]["alternativeLook"] = parsed[
            "stylistVerdict"
        ].get("alternativeLook", 2)

        parsed["stylistVerdict"]["reason"] = parsed[
            "stylistVerdict"
        ].get(
             "reason",
             "Look 1 is the strongest recommendation."
        )

        return parsed
    except Exception as e:
        print("ERROR:", e)

        fallback_look = {
            "title": "Elegant Evening",
            "fashionVibe": "Classic Glam",
            "usedWardrobeItems": [
        {
            "itemNumber": 1,
            "itemDescription": "Uploaded wardrobe item"
        }
            ],
            "shoes": "Neutral heels",
            "bag": "Structured clutch",
            "accessories": "Minimal jewelry",
            "makeup": "Soft glam makeup",
            "hairstyle": "Loose curls",
            "stylistTip": (
                "Choose one statement accessory "
                "to elevate the look."
            ),
            "reason": (
                "This combination balances elegance "
                "and comfort for the occasion."
            ),
            "missingItem": "",
            "trendCategory": "Timeless",
            "colorPalette": [
                "Black",
                "Gold",
                "Ivory",
                "Burgundy"
            ],
            "confidence": 90,
            "suitabilityScore": 90
        }

        return {
            "looks": [
                fallback_look,
                fallback_look.copy(),
                fallback_look.copy()
            ],
            "stylistVerdict": {
                "bestLook": 1,
                "alternativeLook": 2,
                "reason": (
                    "This is the safest and most "
                    "versatile recommendation "
                    "for the selected occasion."
                )
            },
            "error": (
                "Unable to generate recommendations "
                "right now."
            )
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )