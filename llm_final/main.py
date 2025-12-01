# main.py - 인테리어 AI 최종 실행 통합 스크립트
import os
import time
import json
from google import genai
from google.genai import types # 이미지 생성을 위해 필요
from PIL import Image # 이미지 저장을 위해 필요
import io # 이미지 저장을 위해 필요
import time

# ----------------------------------------------------
# 0. 설정 및 모듈 임포트
# ----------------------------------------------------

# ⚠️ API 요청 빈도 제한(429) 에러 방지를 위해 대기 시간을 10초로 늘립니다.
time.sleep(10)


# (1) 프로젝트 설정값 임포트
# API_KEY, 모델명, 입력/출력 경로 등 모든 설정값은 config.py에서 관리합니다.
try:
    from config import (
        API_KEY, 
        REPORT_MODEL, 
        STYLE_MODEL, 
        INITIAL_IMAGE_PATHS, 
        SELECTED_IMAGE_PATH
    )
except ImportError:
    print("❌ 오류: config.py 파일을 찾을 수 없거나 필요한 상수가 정의되지 않았습니다.")
    exit()




# (2) 핵심 기능 모듈 임포트
# 각 단계별로 필요한 함수들을 가져옵니다.

# [1단계] 최적 이미지 선택
from utils.image_selector import select_best_image 

# [2단계] 리포트 분석
from client.report_client import run_report_model
from prompt.report_prompt import report_prompt  # 프롬프트 내용
from utils.report_parser import parse_report_output # 리포트 파싱 함수

# [3단계] 스타일 변환 (1장)
# style_client는 별도로 없고, main_style.py 내부에 로직이 있다고 가정합니다. 
# 여기서는 편의상 main_style에서 핵심 로직을 함수화했다고 가정하고 임포트합니다.
from prompt.style_prompt import generate_style_prompt
# from client.style_client import run_style_model # (가정: run_style_model 함수가 있다고 가정)

# [4단계] 추가 뷰 생성 (2장)
# 이전에 작성한 make_one_image_to_three 함수를 client 폴더에서 임포트합니다.
# (사용자가 'client/view_client.py'에 저장했다고 가정)
try:
    from main_1img23 import make_one_image_to_three
except ImportError:
    print("⚠️ 경고: view_client.py를 찾을 수 없습니다. 4단계는 실행되지 않을 수 있습니다.")
    # 임시로 더미 함수를 정의하거나, 코드를 직접 붙여넣을 수 있지만, 여기서는 정상 임포트 가정

# ----------------------------------------------------
# A. 헬퍼 함수: 스타일 변환 실행 (main_style.py 로직을 단순화)
# ----------------------------------------------------
def run_style_image_generation(api_key: str, model_name: str, input_image_path: str, target_style: str, target_objects: str) -> str:
    """
    스타일 변환 이미지를 1장 생성하는 함수입니다. (main_style.py의 핵심 로직)
    """
    print("\n--- 🔵 3단계: 스타일 변환 이미지 (1/3) 생성 시작 ---")
    
    max_retries = 2
    last_error = None
    
    # 1. 스타일 프롬프트 생성
    prompt = generate_style_prompt(
        target_style=target_style,
        target_objects=target_objects
    )
    
    # 2. Gemini 이미지 생성 클라이언트 초기화 및 호출
    client = genai.Client(api_key=api_key)
    output_path = "styled_output.jpg"
    
    try:
        with open(input_image_path, "rb") as f:
            img_bytes = f.read()

        print(f"  -> 스타일 프롬프트 적용: {target_style}")
        
        # 모델 호출 (run_style_model 함수가 하는 역할)
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=1.3 # 스타일 변환은 창의성이 어느 정도 필요하다고 가정
            )
        )
        
        # 3. 이미지 저장
        if response.parts and response.parts[0].inline_data:
            image_data = response.parts[0].inline_data.data
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"  ✅ 스타일 변환 이미지 저장 완료: {output_path}")
            return output_path
        else:
            print("  ❌ 오류: 스타일 변환 모델이 이미지를 반환하지 않았습니다.")
            print(f"  (텍스트 응답: {response.text[:100]}...)")
            return ""

    except Exception as e:
        print(f"  ❌ 스타일 변환 중 에러 발생: {e}")
        return ""
    
def choose_style_from_recommendations(recommended_styles):
    """
    리포트에서 파싱한 추천 스타일 3개 중에서
    사용자가 번호로 하나를 고르는 함수.
    """
    if not recommended_styles:
        return ""  # 추천이 없으면 빈 문자열 반환

    print("\n리포트가 추천한 인테리어 스타일 3가지입니다:\n")
    for idx, item in enumerate(recommended_styles, start=1):
        style = item.get("style") or item.get("name") or item.get("raw_name")
        reason = item.get("reason", "")
        print(f"  {idx}. {style}  -  {reason}")

    while True:
        choice = input(f"\n원하는 스타일 번호를 입력하세요 (1~{len(recommended_styles)}): ").strip()
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(recommended_styles):
                selected = recommended_styles[num - 1]
                style = selected.get("style") or selected.get("name") or selected.get("raw_name")
                print(f"\n✅ 선택된 스타일: {style}")
                return style

        print("⚠️ 잘못 입력했습니다. 제시된 번호 중에서 다시 입력해주세요.")


# ----------------------------------------------------
# 최종 메인 함수
# ----------------------------------------------------
def main():
    
    print("==============================================================")
    print("        🏠 인테리어 AI 이미지 생성 파이프라인 시작             ")
    print("==============================================================")

    # ----------------------------------------------------
    # 1단계: 최적의 입력 이미지 선택 (Data Preparation)
    # ----------------------------------------------------
    print("\n--- 🔍 1단계: 최적 입력 이미지 선택 ---")
    
    final_input_path = select_best_image(
        api_key=API_KEY,
        model_name=REPORT_MODEL, # 가구 세는 데는 gemini-2.0-flash 사용 (config 설정)
        input_paths=INITIAL_IMAGE_PATHS,
        selected_output_path=SELECTED_IMAGE_PATH
    )
    
    if not final_input_path:
        print("🚨 모든 프로세스가 중단됩니다. 유효한 입력 이미지를 확인하세요.")
        return

    # ----------------------------------------------------
    # 2단계: 공간 분석 리포트 생성 (Report Generation)
    # ----------------------------------------------------
    print("\n--- 🟡 2단계: 공간 분석 리포트 생성 ---")
    
    try:
        # report_client.py의 run_report_model 함수 호출
        raw_report_text = run_report_model(
            api_key=API_KEY,
            model_name=REPORT_MODEL,
            image_path=final_input_path, # 1단계에서 선택된 이미지 사용
            prompt=report_prompt
        )
        
        # 파싱 로직
        parsed_data = parse_report_output(raw_report_text)
        
        # 리포트 결과 txt 저장 (예시)
        report_output_path = "report_analysis_result.txt"
        with open(report_output_path, "w", encoding="utf-8") as f:
            f.write(raw_report_text)

        # ② 파싱된 전체 데이터를 JSON으로 저장
        parsed_json_path = "parsed_report.json"
        with open(parsed_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=4)

        print(f"  ✅ AI 분석 리포트 원본 저장 완료: {report_output_path}")
        print(f"  ✅ 파싱된 리포트 JSON 저장 완료: {parsed_json_path}")
        print(f"  ✅ 파싱된 메인 스타일: {parsed_data.get('general_style', 'N/A')}")
        
    except Exception as e:
        print(f"  ❌ 2단계 (리포트 분석) 중 에러 발생: {e}")
        parsed_data = {}  # 에러 시 비워두기
        # 리포트 단계에서 오류가 나도 이미지 생성은 계속 진행 가능
        pass 

    # ----------------------------------------------------
    # 3단계: 스타일 변환 이미지 1장 생성 (1번 기능)
    # ----------------------------------------------------
    
    # 사용자로부터 원하는 스타일과 객체를 입력받습니다. (main_style.py 로직)
    # 2단계 리포트에서 추천된 스타일 3개 가져오기
    recommended_styles = parsed_data.get("recommended_styles") or []

    # 추천이 있으면 3개 중에서 번호 선택, 없으면 직접 입력으로 fallback
    selected_style = choose_style_from_recommendations(recommended_styles)
    if selected_style:
        target_style = selected_style
    else:
        target_style = input(
            "\n[필수] 원하는 스타일을 입력하세요 (예: 미니멀리즘, 북유럽): "
        ).strip() or "모던"

    # 적용 대상 가구는 기존 로직 그대로
    target_objects = input(
        "[선택] 스타일을 적용할 특정 가구 (없으면 Enter): "
    ).strip() or "모든 가구와 데코 요소"
    
    styled_image_path = run_style_image_generation(
        api_key=API_KEY,
        model_name=STYLE_MODEL,
        input_image_path=final_input_path, # 1단계에서 선택된 이미지 사용
        target_style=target_style,
        target_objects=target_objects
    )
    
    if not styled_image_path:
        print("🚨 스타일 변환 이미지를 생성하지 못하여 4단계가 중단됩니다.")
        return
        
    # ----------------------------------------------------
    # 4단계: 추가 뷰 이미지 2장 생성 (2번 기능)
    # ----------------------------------------------------
    print("\n--- 🟣 4단계: 추가 뷰 이미지 (2/3) 생성 시작 ---")
    
    # client/view_client.py의 make_one_image_to_three 함수 호출
    make_one_image_to_three(
        api_key=API_KEY,
        model_name=STYLE_MODEL, # 2번 기능은 3번 기능과 동일한 이미지 생성 모델 사용
        input_image_path=styled_image_path # 3단계 결과물을 입력으로 사용
    )
    
    # ----------------------------------------------------
    # 최종 결과 요약
    # ----------------------------------------------------
    print("\n==============================================================")
    print("              ✨ 파이프라인 최종 완료 ✨                    ")
    print(f" - 원본 이미지: {final_input_path}")
    print(f" - 리포트 결과: {report_output_path}")
    print(" - 최종 생성 이미지 (3장):")
    print(f"   1. 스타일 변환 (원본 구도): {styled_image_path}")
    print(f"   2. 좌측 뷰 (-30°): img4new3r_left.png")
    print(f"   3. 우측 뷰 (+30°): img4new3r_right.png")
    print("==============================================================")


if __name__ == "__main__":
    main()