# skin_tone.py

import cv2
import numpy as np


def analyze_skin_tone(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return {
            "tone": "Unknown",
            "recommendedColors": []
        }

    # Convert BGR → RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    h, w, _ = image.shape

    # Take center area of face image
    center = image[
        h//3:h//3*2,
        w//3:w//3*2
    ]

    avg_color = np.mean(center, axis=(0, 1))

    red = avg_color[0]
    green = avg_color[1]
    blue = avg_color[2]

    print("Average RGB:", red, green, blue)

    if red > blue + 15:
        tone = "Warm"
        colors = ["Gold", "Olive", "Cream", "Rust"]

    elif blue > red + 15:
        tone = "Cool"
        colors = ["Silver", "Lavender", "Royal Blue", "Emerald"]

    else:
        tone = "Neutral"
        colors = ["Beige", "White", "Grey", "Black"]

    return {
        "tone": tone,
        "recommendedColors": colors
    }