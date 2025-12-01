import re
from typing import Dict, Any, List, Union

# ----------------------------------------------------
# A. 텍스트 정제 함수
# ----------------------------------------------------
def clean_text(text: str) -> str:
    """
    분위기 설명이 깨지거나 중복될 때 이를 정리(cleaning)하는 함수.
    """
    if not text:
        return text

    # 1) 중괄호 제거
    text = text.replace("{", "").replace("}", "")

    # 2) 줄 중복 및 깨진 줄 정리
    lines = text.splitlines()
    unique_lines = []
    for line in lines:
        line = line.strip()
        if line and line not in unique_lines:
            unique_lines.append(line)

    # 3) 공백 중복 제거
    cleaned = " ".join(unique_lines)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned

# ----------------------------------------------------
# B. 가구 항목별 추출 함수 (이 함수는 report_parser에서 사용되어야 함)
# ----------------------------------------------------
# 참고: 이 함수는 원래 report_parser.py에 위치하는 것이 구조적으로 맞습니다.
# 다만, utils/mood_extractor.py에 임시로 넣어두는 경우입니다.
def extract_furniture_by_mood_and_action(llm_output: str) -> Dict[str, Union[Dict[str, List[str]], str]]:
    """
    ## 3 섹션에서 추천 및 변경 가구 항목을 분위기(Key)와 액션(Key)별로 추출합니다.
    - furniture_remove는 '제거 가구 명칭'만 추출합니다.
    - furniture_new_by_mood는 '분위기'를 Key로, '추천 가구'를 Value로 추출합니다.
    """
    parsed_items: Dict[str, Any] = {}

    # 1. 3-1. 공간에 어울리는 가구 추천 (추가 추천 가구)
    rec_add_section_match = re.search(r"## 3-1\. 공간에 어울리는 가구 추천(.*?)(?=## 3-2\. 제거하면 좋을 가구 추천)", llm_output, re.DOTALL)
    
    if rec_add_section_match:
        rec_section = rec_add_section_match.group(1)
        PATTERN_REC_ADD = r"-\s*([가-힣\s]+):\s*(.*?),\s*(.*)"
        rec_matches = re.findall(PATTERN_REC_ADD, rec_section)

        parsed_items['furniture_add_by_mood'] = {}
        for mood, item1, item2 in rec_matches:
            parsed_items['furniture_add_by_mood'][mood.strip()] = [
                item1.strip(),
                item2.strip()
            ]

    # 2. 3-2. 제거하면 좋을 가구 추천 (제거 가구 명칭만 추출)
    rem_section_match = re.search(r"## 3-2\. 제거하면 좋을 가구 추천\s*-\s*.*?기준:\s*([가-힣\s]+?),\s*.*?(?=## 3-3\. 분위기별 바꿨으면 하는 가구 추천)", llm_output, re.DOTALL)
    
    if rem_section_match:
        parsed_items['furniture_remove'] = rem_section_match.group(1).strip()


    # 3. 3-3. 분위기별 바꿨으면 하는 가구 추천 (분위기 Key -> 추천 가구 Value)
    change_section_match = re.search(r"## 3-3\. 분위기별 바꿨으면 하는 가구 추천(.*?)(?=## 4\. 공간 비율 및 동선 분석|$)", llm_output, re.DOTALL)
    
    if change_section_match:
        change_section = change_section_match.group(1)
        PATTERN_CHANGE = r"-\s*([가-힣\s]+?)\s*:\s*.*?\s*->\s*(.*)"
        change_matches = re.findall(PATTERN_CHANGE, change_section)

        parsed_items['furniture_new_by_mood'] = {}
        for mood, new_item in change_matches:
            parsed_items['furniture_new_by_mood'][mood.strip()] = new_item.strip()
            
    return parsed_items

# ----------------------------------------------------
# C. 분위기 설명 복구 및 추출 함수 (main_report.py에서 import 하는 함수)
# ----------------------------------------------------
def extract_mood_descriptions_from_broken_text(broken_text: str) -> Dict[str, str]:
    """
    깨진 딕셔너리 형태의 텍스트에서 '분위기 단어'와 '설명'만 복구하여 추출합니다.
    """
    cleaned_text = clean_text(broken_text)
    extracted_dict = {}

    # 패턴: Key가 '한글 단어'이고 Value가 콜론 다음에 오는 패턴
    PATTERN_MOOD_DESC = r'([가-힣\s]+한|[가-힣\s]+ㄴ|[가-힣\s]+):\s*(.*?)(?:,\s*|(?=\s*[가-힣\s]+:\s*|$))'

    matches = re.findall(PATTERN_MOOD_DESC, cleaned_text)

    # Key 필터링용
    MOOD_KEYS_FILTER = ["아늑한", "편안한", "심플한", "모던", "미니멀", "차분한", "따뜻한", "빈티지"]
    
    for key_match, value in matches:
        k = key_match.strip().replace('"', '')
        v = value.strip().replace('"', '')

        # 1. Key 필터링
        if not k or k not in MOOD_KEYS_FILTER:
            continue
        
        # 2. Value 정리 (다음 헤딩이나 키 앞에서 자르기)
        v = re.split(r'##\s*\d|\s*-\s*[가-힣\s]+:', v)[0].strip()
        
        # 3. Value가 가구 목록인지 확인하고, 가구 목록이라면 제외 (## 3-1 섹션 내용 필터링)
        if any(item in v for item in ['러그', '쿠션', '안락의자', '스툴', '모듈형']):
            continue

        if k and len(v) > 10:
            extracted_dict[k] = v

    return extracted_dict