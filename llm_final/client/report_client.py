from google import genai
from google.genai import types

def run_report_model(api_key, model_name, image_path, prompt):
    client = genai.Client(api_key=api_key)

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(
                data=img_bytes,
                mime_type="image/jpeg"
            ),
            prompt
        ]
    )

    return response.text
