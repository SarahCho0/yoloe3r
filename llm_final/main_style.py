from config import API_KEY, STYLE_MODEL, STYLE_IMAGE_PATH
from prompt.style_prompt import generate_style_prompt
from client.style_client import run_style_model
from utils.style_parser import parse_style_input

def main():
    target_style = input("원하는 스타일을 입력하세요: ")

    target_objects = input("스타일을 적용할 특정 가구가 있으면 입력하세요 (없으면 Enter): ")

    if target_objects.strip() == "":
        target_objects_text = "전체 공간"
    else:
        target_objects_text = target_objects

    # ✔ 1) 스타일 프롬프트 생성
    prompt = generate_style_prompt(
        target_style=target_style,
        target_objects=target_objects_text
    )

    # ✔ 2) 방금 생성한 prompt 내부를 다시 파싱하여 값 확인
    parsed = parse_style_input(prompt)
    print("🔍 파싱된 스타일 값:", parsed)

    # ✔ 3) Gemini 실행
    result_bytes = run_style_model(API_KEY, STYLE_MODEL, STYLE_IMAGE_PATH, prompt)

    # ✔ 4) 출력 저장
    output_path = "styled_output.jpg"
    with open(output_path, "wb") as f:
        f.write(result_bytes)

    print(f"🎉 스타일 변환 완료! → {output_path}")

if __name__ == "__main__":
    main()
