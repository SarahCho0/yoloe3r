# utils/style_parser.py

import re

def parse_style_input(prompt: str) -> dict:
    """
    style 프롬프트에서 target_style 및 target_objects를 추출하여 dict로 반환.
    너가 ipynb에서 사용하던 regex 구조를 그대로 유지한다.
    """
    
    parsed_input = {}

    # 1. target_style 값 추출.
    PATTERN_STYLE = r"스타일을\s*([가-힣a-zA-Z\s&]+)\s*스타일로 변환하세요"
    match_style = re.search(PATTERN_STYLE, prompt)

    if match_style:
        parsed_input['target_style'] = match_style.group(1).strip()

    # 2. target_objects 값 추출.
    PATTERN_OBJECTS = r"스타일을 변경해야 하는 객체:\s*(.*?)\s*스타일 변경 예시:"
    match_objects = re.search(PATTERN_OBJECTS, prompt, re.DOTALL)

    if match_objects:
        objects_raw = match_objects.group(1).strip()

        # 줄바꿈 기준으로 객체 리스트 생성.
        parsed_input['target_objects'] = [
            obj.strip()
            for obj in objects_raw.split('\n')
            if obj.strip()
        ]

    return parsed_input


# 테스트용(나중에 주석 처리 가능)
#if __name__ == "__main__":
    test_prompt = """
    스타일을 modern minimalism 스타일로 변환하세요.

    스타일을 변경해야 하는 객체:
    소파
    테이블
    침대

    스타일 변경 예시:
    - 예시1
    - 예시2
    """

    print(parse_style_input(test_prompt))
