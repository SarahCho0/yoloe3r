# main_report.py  (1단계~2단계만 실행하는 스크립트)

import time
import json

from config import (
    API_KEY,
    REPORT_MODEL,
    INITIAL_IMAGE_PATHS,
    SELECTED_IMAGE_PATH,
)

# [1단계] 최적 이미지 선택
from utils.image_selector import select_best_image

# [2단계] 리포트 분석
from prompt.report_prompt import report_prompt
from client.report_client import run_report_model
from utils.report_parser import parse_report_output


def main():
    print("==============================================================")
    print("        🏠 인테리어 AI 분석 (1~2단계 전용) 시작               ")
    print("==============================================================")

    # ----------------------------------------------------
    # 1단계: 최적의 입력 이미지 선택 (Data Preparation)
    #    → main.py와 동일한 로직
    # ----------------------------------------------------
    print("\n--- 🔍 1단계: 최적 입력 이미지 선택 ---")

    final_input_path = select_best_image(
        api_key=API_KEY,
        model_name=REPORT_MODEL,          # 가구 세는 데는 gemini-2.0-flash 사용 (config 설정)
        input_paths=INITIAL_IMAGE_PATHS,  # config에 정의된 3장
        selected_output_path=SELECTED_IMAGE_PATH,
    )

    if not final_input_path:
        print("🚨 모든 프로세스가 중단됩니다. 유효한 입력 이미지를 확인하세요.")
        return

    print(f"  ✅ 1단계 완료: 선택된 이미지 → {final_input_path}")

    # ----------------------------------------------------
    # 2단계: 공간 분석 리포트 생성 (Report Generation)
    #    → main.py와 동일한 로직
    # ----------------------------------------------------
    print("\n--- 🟡 2단계: 공간 분석 리포트 생성 ---")

    try:
        # Gemini에 이미지 + 분석용 프롬프트 전달
        raw_report_text = run_report_model(
            api_key=API_KEY,
            model_name=REPORT_MODEL,
            image_path=final_input_path,  # 1단계에서 선택된 이미지 사용
            prompt=report_prompt,
        )

        # (안전하게 API 쿨다운, main.py와 맞춰줌)
        time.sleep(10)

        # 전체 리포트 파싱
        parsed_data = parse_report_output(raw_report_text)

        # 2-1) 리포트 원본 txt 저장
        report_output_path = "report_analysis_result.txt"
        with open(report_output_path, "w", encoding="utf-8") as f:
            f.write(raw_report_text)

        # 2-2) 파싱된 전체 데이터를 JSON으로 저장
        parsed_json_path = "parsed_report.json"
        with open(parsed_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=4)

        # --------------------------------------------------
        # (선택) 디버깅용 출력: 일부 섹션만 콘솔에 보여주기
        # --------------------------------------------------
        print("\n📌 3-1. 공간에 어울리는 가구 추천(추가):")
        print(json.dumps(parsed_data.get("recommendations_add", []),
                         indent=4, ensure_ascii=False))

        print("\n📌 3-2. 제거하면 좋을 가구:")
        print(json.dumps(parsed_data.get("recommendations_remove", []),
                         indent=4, ensure_ascii=False))

        print("\n📌 3-3. 분위기별 바꿨으면 하는 가구 추천:")
        print(json.dumps(parsed_data.get("recommendations_change", []),
                         indent=4, ensure_ascii=False))

        print("\n📌 파싱된 전체 JSON 구조:\n")
        print(json.dumps(parsed_data, indent=4, ensure_ascii=False))
        print("\n" + "=" * 80 + "\n")

        print(f"  ✅ AI 분석 리포트 원본 저장 완료: {report_output_path}")
        print(f"  ✅ 파싱된 리포트 JSON 저장 완료: {parsed_json_path}")
        print(f"  ✅ 파싱된 메인 스타일: {parsed_data.get('general_style', 'N/A')}")

    except Exception as e:
        print(f"  ❌ 2단계 (리포트 분석) 중 에러 발생: {e}")
        # 여기서는 1~2단계만 목적이므로, 에러 시 그냥 종료
        return

    print("\n🎉 1~2단계 분석 완료! → report_analysis_result.txt / parsed_report.json 저장 완료\n")


if __name__ == "__main__":
    main()
