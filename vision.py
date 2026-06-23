from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def identify_clothing(image_base64):

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
Analyze this fashion item.

Return ONLY JSON:

{
  "garmentType":"",
  "primaryColor":"",
  "secondaryColor":"",
  "style":"",
  "occasion":"",
  "material":"",
  "pattern":""
}

Be highly specific.

Examples:
- lehenga
- kurti
- saree
- jeans
- blazer
- dress
- shirt
- trousers

Do not use generic words like outfit or clothing.
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content