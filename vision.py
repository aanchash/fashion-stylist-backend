from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)


def identify_clothing(image):
    inputs = processor(images=image, return_tensors="pt")

    output = model.generate(**inputs)

    caption = processor.decode(
        output[0],
        skip_special_tokens=True
    )

    return caption