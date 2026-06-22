from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": """
You are a fashion stylist.

Occasion: Wedding

Wardrobe:
- Purple lehenga with gold embroidery work
- Gold heels
- Gold clutch

Suggest one outfit recommendation.
"""
        }
    ]
)

print(response.choices[0].message.content)