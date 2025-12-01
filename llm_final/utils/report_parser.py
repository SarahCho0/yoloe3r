# utils/report_parser.py

import re
from typing import Dict, Any, List, Union

# (현재는 스타일 카탈로그를 직접 쓰고 있지는 않지만,
#  나중에 추천 스타일을 정규화할 때 쓸 수 있으니 일단 남겨둠)
# from utils.style_catalog import normalize_to_ko_name


def parse_report_output(result_text: str) -> Dict[str, Union[str, Dict, List]]:
    """
    LLM의 인테리어 리포트 결과(result_text)를
    현재 report_prompt.py 템플릿에 맞춰 파싱한다.

    템플릿 구조 (요약):
    - # 전체적인 분위기는 **{분위기1}하고 {분위기2}한 {분위기3} 스타일**입니다.
    - ## 1. 분위기 정의 및 유형별 확률
        - {분위기1}({확률1}%): {설명1}
        - {분위기2}({확률2}%): {설명2}
        - {분위기3}({확률3}%): {설명3}
    - ## 2. 분위기 판단 근거
        - 가구 배치 및 공간 분석 : {근거1}
        - 색감 및 질감: {근거2}
        - 소재: {근거3}
    - ## 3-1. 현재 분위기에 맞춰 추가하면 좋을 가구 추천
        - {추가 가구} : {근거}
    - ## 3-2. 제거하면 좋을 가구 추천
        - {제거 가구} : {근거}
    - ## 3-3. 분위기별 바꿨으면 하는 가구 추천
        - {변경 가구} -> {추천 가구} : {근거}
    - #6. 이런 스타일 어떠세요?
        - {추천 분위기} : {소개+추천 근거}
    - ## 정리
        - {요약1}
        - {요약2}
        - {요약3}
    """

    llm_output = result_text
    parsed_data: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # 1. 전체적인 분위기 한 줄 (# ... 스타일)
    # ------------------------------------------------------------------
    # ex) # 전체적인 분위기는 **차분하고 따뜻한 북유럽 스타일**입니다.
    match_style = re.search(
        r"#\s*전체적인 분위기는\s*\*\*(.*?)\s*스타일\*\*",
        llm_output,
        re.DOTALL,
    )
    if match_style:
        general = match_style.group(1).strip()
        parsed_data["general_style"] = general

        # 분위기1/2/3 추출 (예: "차분하고 따뜻한 북유럽")
        # "차분", "따뜻", "북유럽" 같은 단어 리스트로 뽑아낸다.
        moods = re.findall(r"([가-힣\s]+?)(?:하고|한|\s*$)", general)
        parsed_data["mood_words"] = [m.strip() for m in moods if m.strip()]

    # ------------------------------------------------------------------
    # 2. 분위기 정의 및 유형별 확률 (## 1.)
    # ------------------------------------------------------------------
    mood_section_match = re.search(
        r"##\s*1\. 분위기 정의 및 유형별 확률(.*?)(?=##\s*2\. 분위기 판단 근거)",
        llm_output,
        re.DOTALL,
    )
    if mood_section_match:
        mood_section = mood_section_match.group(1)

        # - {분위기}({확률}%): {설명}
        PATTERN_MOOD_DETAIL = r"-\s*(.*?)\s*\((\d+)%\):\s*(.*)"
        mood_matches = re.findall(PATTERN_MOOD_DETAIL, mood_section)

        parsed_data["mood_details"] = []
        for mood, pct, desc in mood_matches:
            parsed_data["mood_details"].append(
                {
                    "word": mood.strip(),
                    "percentage": int(pct),
                    "description": desc.strip(),
                }
            )

    # ------------------------------------------------------------------
    # 3. 분위기 판단 근거 (## 2.)
    # ------------------------------------------------------------------
    basis_section_match = re.search(
        r"##\s*2\. 분위기 판단 근거(.*?)(?=##\s*3-1\. 현재 분위기에 맞춰 추가하면 좋을 가구 추천)",
        llm_output,
        re.DOTALL,
    )
    if basis_section_match:
        basis_section = basis_section_match.group(1)

        # - 키 : 값
        PATTERN_BASIS = r"-\s*(.*?):\s*(.*)"
        basis_matches = re.findall(PATTERN_BASIS, basis_section)

        parsed_data["basis"] = {}
        key_mapping = {
            "가구 배치 및 공간 분석": "furniture_layout",
            "색감 및 질감": "color_texture",
            "소재": "material",
        }

        for key, value in basis_matches:
            k = key.strip()
            v = value.strip()
            if k in key_mapping:
                parsed_data["basis"][key_mapping[k]] = v
            else:
                # 매핑에 없는 키는 원문 그대로도 보존
                parsed_data["basis"][k] = v

    # ------------------------------------------------------------------
    # 4. 3-1. 현재 분위기에 맞춰 추가하면 좋을 가구 추천
    # ------------------------------------------------------------------
    add_section_match = re.search(
        r"##\s*3-1\. 현재 분위기에 맞춰 추가하면 좋을 가구 추천(.*?)(?=##\s*3-2\. 제거하면 좋을 가구 추천)",
        llm_output,
        re.DOTALL,
    )
    if add_section_match:
        add_section = add_section_match.group(1)

        # - {추가 가구} : {근거}
        PATTERN_ADD = r"-\s*(.*?):\s*(.*)"
        add_matches = re.findall(PATTERN_ADD, add_section)

        parsed_data["recommendations_add"] = []
        for item, reason in add_matches:
            parsed_data["recommendations_add"].append(
                {
                    "item": item.strip(),
                    "reason": reason.strip(),
                }
            )

    # ------------------------------------------------------------------
    # 5. 3-2. 제거하면 좋을 가구 추천
    # ------------------------------------------------------------------
    rem_section_match = re.search(
        r"##\s*3-2\. 제거하면 좋을 가구 추천(.*?)(?=##\s*3-3\. 분위기별 바꿨으면 하는 가구 추천)",
        llm_output,
        re.DOTALL,
    )
    if rem_section_match:
        rem_section = rem_section_match.group(1)

        # - {제거 가구} : {근거}
        PATTERN_REM = r"-\s*(.*?):\s*(.*)"
        rem_matches = re.findall(PATTERN_REM, rem_section)

        # 템플릿 상 한 줄만 나오지만, 혹시 모를 확장을 고려해 리스트로 저장
        parsed_data["recommendations_remove"] = []
        for item, reason in rem_matches:
            parsed_data["recommendations_remove"].append(
                {
                    "item": item.strip(),
                    "reason": reason.strip(),
                }
            )

    # ------------------------------------------------------------------
    # 6. 3-3. 분위기별 바꿨으면 하는 가구 추천
    # ------------------------------------------------------------------
    change_section_match = re.search(
        r"##\s*3-3\. 분위기별 바꿨으면 하는 가구 추천(.*?)(?=#\s*6\. 이런 스타일 어떠세요\?|##\s*정리|$)",
        llm_output,
        re.DOTALL,
    )
    if change_section_match:
        change_section = change_section_match.group(1)

        # - {변경 가구} -> {추천 가구} : {근거}
        PATTERN_CHANGE = r"-\s*(.*?)\s*->\s*(.*?)\s*:\s*(.*)"
        change_matches = re.findall(PATTERN_CHANGE, change_section)

        parsed_data["recommendations_change"] = []
        for src, dst, reason in change_matches:
            parsed_data["recommendations_change"].append(
                {
                    "from_item": src.strip(),
                    "to_item": dst.strip(),
                    "reason": reason.strip(),
                }
            )

    # ------------------------------------------------------------------
    # 7. #6. 이런 스타일 어떠세요? (추천 스타일)
    # ------------------------------------------------------------------
    parsed_data["recommended_styles"] = parse_recommended_styles(llm_output)

    # ------------------------------------------------------------------
    # 8. 정리 (## 정리)
    # ------------------------------------------------------------------
    sum_section_match = re.search(r"##\s*정리(.*)", llm_output, re.DOTALL)
    if sum_section_match:
        sum_section = sum_section_match.group(1)

        # "- 문장" 형태의 모든 줄을 뽑아온다.
        lines = re.findall(r"-\s*(.*)", sum_section)

        parsed_data["summary"] = {}
        for idx, sentence in enumerate(lines):
            key = f"summary{idx + 1}"
            parsed_data["summary"][key] = sentence.strip()

    return parsed_data


def parse_recommended_styles(llm_output: str) -> List[Dict[str, str]]:
    """
    리포트 텍스트에서

    #6. 이런 스타일 어떠세요?
    - {추천 분위기} : {추천 분위기 소개와 추천 근거(한 문장)}

    블록을 찾아서 추천 스타일과 이유를 파싱한다.
    (템플릿 상 1개지만, 혹시 여러 줄이 나와도 리스트로 처리)
    """
    # #6. 섹션 전체 블록 추출
    section_pattern = re.compile(
        r"^#\s*6\.\s*이런 스타일 어떠세요\?\s*$"
        r"(?P<body>.*?)(?=^##\s*정리|^#\s*정리|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    m = section_pattern.search(llm_output)
    if not m:
        return []

    body = m.group("body").strip()
    if not body:
        return []

    # "- 스타일 : 이유" 형식 한 줄씩 파싱
    bullet_pattern = re.compile(
        r"^\s*-\s*(?P<style>[^:]+?)\s*:\s*(?P<reason>.+)$",
        re.MULTILINE,
    )

    items: List[Dict[str, str]] = []
    for b in bullet_pattern.finditer(body):
        style = b.group("style").strip()
        reason = b.group("reason").strip()
        items.append(
            {
                "style": style,
                "reason": reason,
            }
        )

    return items
