"""
utils/style_catalog.py

- 인테리어 스타일 목록을 한 곳에서 관리하는 모듈입니다.
- 한글/영문 이름, 간단한 slug(영문 키)를 함께 저장해 둡니다.
- 나중에 프롬프트 생성, 사용자 입력 검증 등에 재사용할 수 있습니다.
"""

from typing import List, Dict, Optional

# 1) 전체 카탈로그 ---------------------------------------------------------

INTERIOR_STYLES: List[Dict[str, str]] = [
    {"id": 1, "slug": "modern", "ko": "모던", "en": "Modern Interior"},
    {"id": 2, "slug": "minimalist", "ko": "미니멀리즘", "en": "Minimalist Interior"},
    {"id": 3, "slug": "scandinavian", "ko": "스칸디나비아/북유럽", "en": "Scandinavian Home"},
    {"id": 4, "slug": "industrial_loft", "ko": "인더스트리얼", "en": "Industrial Loft"},
    {"id": 5, "slug": "classic", "ko": "클래식", "en": "Classic Interior Design"},
    {"id": 6, "slug": "modern_classic", "ko": "모던 클래식", "en": "Modern Classic Home"},
    {"id": 7, "slug": "vintage", "ko": "빈티지", "en": "Vintage Home Decor"},
    {"id": 8, "slug": "retro", "ko": "레트로", "en": "Retro Style Interior"},
    {"id": 9, "slug": "natural_zen", "ko": "내추럴/젠", "en": "Natural Zen Interior"},
    {"id": 10, "slug": "japandi", "ko": "재팬디", "en": "Japandi Style"},
    {"id": 11, "slug": "rustic", "ko": "러스틱", "en": "Rustic Farmhouse"},
    {"id": 12, "slug": "farmhouse", "ko": "팜하우스", "en": "Modern Farmhouse"},
    {"id": 13, "slug": "shabby_chic", "ko": "셰비 시크", "en": "Shabby Chic Style"},
    {"id": 14, "slug": "art_deco", "ko": "아르데코", "en": "Art Deco Design"},
    {"id": 15, "slug": "mid_century_modern", "ko": "미드 센추리 모던", "en": "Mid-Century Modern Home"},
    {"id": 16, "slug": "boho_chic", "ko": "보헤미안/보호", "en": "Boho Chic Interior"},
    {"id": 17, "slug": "greek_revival", "ko": "그리스 리바이벌", "en": "Greek Revival Interior"},
    {"id": 18, "slug": "art_nouveau", "ko": "아르누보", "en": "Art Nouveau Interior"},
    {"id": 19, "slug": "coastal", "ko": "코스탈/해안", "en": "Coastal Home Decor"},
    {"id": 20, "slug": "swiss_chalet", "ko": "스위스 샬레", "en": "Swiss Chalet Interior"},
    {"id": 21, "slug": "egyptian", "ko": "이집트", "en": "Egyptian Home Decor"},
    {"id": 22, "slug": "asian_zen", "ko": "젠 아시아", "en": "Asian Zen Decor"},
    {"id": 23, "slug": "maximalist", "ko": "맥시멀리즘", "en": "Maximalist Decor"},
    {"id": 24, "slug": "kitsch", "ko": "키치", "en": "Kitsch Decor Style"},
    {"id": 25, "slug": "biophilic", "ko": "바이오필릭", "en": "Biophilic Design Home"},
    {"id": 26, "slug": "color_block", "ko": "컬러 블록", "en": "Color Block Interior"},
    {"id": 27, "slug": "monochromatic", "ko": "모노크로매틱", "en": "Monochromatic Room"},
    {"id": 28, "slug": "pop_art", "ko": "팝 아트", "en": "Pop Art Interior"},
    {"id": 29, "slug": "grandmillennial", "ko": "그랜디시", "en": "Grandmillennial Style"},
    {"id": 30, "slug": "masculine", "ko": "매시큘린", "en": "Masculine Interior Design"},
    {"id": 31, "slug": "feminine", "ko": "페미닌", "en": "Feminine Room Decor"},
]

# 2) 빠른 검색을 위한 보조 자료구조 --------------------------------------

_KO_NAME_TO_STYLE = {s["ko"]: s for s in INTERIOR_STYLES}
_EN_NAME_TO_STYLE = {s["en"]: s for s in INTERIOR_STYLES}
_SLUG_TO_STYLE = {s["slug"]: s for s in INTERIOR_STYLES}


def list_styles_for_cli() -> str:
    """
    터미널/콘솔에서 사용자에게 보여줄 때 쓰기 좋은 문자열을 반환합니다.
    예)
      [1] 모던 (Modern Interior)
      [2] 미니멀리즘 (Minimalist Interior)
      ...
    """
    lines = []
    for s in INTERIOR_STYLES:
        lines.append(f"[{s['id']}] {s['ko']} ({s['en']})")
    return "\n".join(lines)


def find_style(name_or_id: str | int) -> Optional[Dict[str, str]]:
    """
    숫자(id), 한글 이름, 영문 이름, slug 중 어떤 걸 넣어도
    해당 스타일 dict를 찾아 반환합니다. 없다면 None.
    """
    # id로 조회
    if isinstance(name_or_id, int):
        for s in INTERIOR_STYLES:
            if s["id"] == name_or_id:
                return s
        return None

    # 문자열인 경우
    key = str(name_or_id).strip()

    # 숫자 형태의 문자열일 수도 있음
    if key.isdigit():
        return find_style(int(key))

    # 한글, 영문, slug 모두 지원
    if key in _KO_NAME_TO_STYLE:
        return _KO_NAME_TO_STYLE[key]
    if key in _EN_NAME_TO_STYLE:
        return _EN_NAME_TO_STYLE[key]
    if key in _SLUG_TO_STYLE:
        return _SLUG_TO_STYLE[key]

    return None


def normalize_to_ko_name(name_or_id: str | int) -> str:
    """
    내부적으로는 항상 '한글 이름'으로 스타일을 다루고 싶을 때 사용합니다.
    - 입력: id / slug / 한글 이름 / 영문 이름
    - 출력: 대응되는 한글 이름
    - 못 찾으면 ValueError 발생
    """
    style = find_style(name_or_id)
    if style is None:
        raise ValueError(f"정의되지 않은 인테리어 스타일입니다: {name_or_id}")
    return style["ko"]


def is_valid_style(name_or_id: str | int) -> bool:
    """이 값이 스타일 카탈로그 안에 존재하는지 여부만 bool로 리턴."""
    return find_style(name_or_id) is not None


def format_style_list_for_prompt() -> str:
    """
    LLM 프롬프트에 그대로 붙여넣기 좋은 스타일 목록입니다.
    예)
    - 모던 (Modern Interior)
    - 미니멀리즘 (Minimalist Interior)
    ...
    """
    lines = []
    for s in INTERIOR_STYLES:
        lines.append(f"- {s['ko']} ({s['en']})")
    return "\n".join(lines)
