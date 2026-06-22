from PIL import Image
from vision import identify_clothing

img = Image.open("test.png")

print(identify_clothing(img))