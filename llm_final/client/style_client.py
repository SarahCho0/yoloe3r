# file: client/style_client.py

from google import genai
from google.genai import types

def run_style_model(api_key, model_name, image_path, prompt):
    client = genai.Client(api_key=api_key)

    # 이미지 파일 읽기
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    # 2.5-flash-image 모델은 generate_content 방식으로 이미지 입력해야 함!
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

    # 출력된 이미지 바이트 추출
    image_bytes = response.candidates[0].content.parts[0].inline_data.data

    return image_bytes
