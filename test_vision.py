import base64

from vision import identify_clothing

with open("test.png", "rb") as f:
    image_bytes = f.read()

base64_image = base64.b64encode(
    image_bytes
).decode("utf-8")

image_url = (
    f"data:image/png;base64,{base64_image}"
)

print(
    identify_clothing(image_url)
)