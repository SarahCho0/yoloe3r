#README.md 

# AI 기반 인테리어 시뮬레이션 프로젝트 (PE3R)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

이 프로젝트는 사용자가 제공한 방 이미지와 인테리어 스타일 선택을 바탕으로, Google Gemini 모델을 활용하여 공간을 분석하고, 
가구 수정 또는 전체 스타일 변경을 시뮬레이션하여 다양한 각도(정면, 좌/우측)의 이미지를 제공하는 AI 기반 인테리어 솔루션입니다.

# 프로젝트 파일 구조 및 역할
파일명,역할,상세 설명
config.py,환경 설정,"API 키, Gemini 모델명(REPORT_MODEL, STYLE_MODEL), 초기 입력 이미지 경로 및 중간 결과물 저장 경로(SELECTED_IMAGE_PATH) 등을 정의합니다."
main_report.py,1단계: 공간 분석 리포트 생성,"3장의 초기 이미지 중 최적의 1장을 선택하고, 해당 이미지를 바탕으로 Gemini에게 공간 구조, 스타일, 추천 항목에 대한 리포트 분석을 요청하고 JSON으로 저장합니다."
main_new_looks.py,2단계: 스타일 변경 시뮬레이션,"사용자가 선택한 스타일(또는 AI 추천 스타일)을 방 전체에 적용하여 새로운 이미지 1장을 생성하고, 추가로 좌/우 측면 뷰 이미지를 생성합니다."
main_modify_looks.py,2단계: 가구 수정 시뮬레이션,"사용자의 선택(user_choice.json)에 따라 AI 리포트 기반의 추가/제거/변경 작업을 순차적으로 수행하여 최종 이미지를 생성하고, 추가로 좌/우 측면 뷰 이미지를 생성합니다."
main_1img23.py,보조: 앵글 생성 모듈,"최종 결과 이미지를 입력받아, 동일한 방 구조를 유지한 채 **수평 각도(-30°, +30°)**만 변경한 2장의 측면 뷰 이미지를 생성하는 핵심 함수를 포함합니다."
user_choice.json,사용자 입력,"가구 추가/제거/변경 기능 적용 여부(use_add, use_remove, use_change)를 저장하는 파일입니다."
style_choice.json,사용자 입력,"선택한 인테리어 스타일(예: ""AI 추천"", ""모던"", ""미니멀리즘"" 등)을 저장하는 파일입니다."
parsed_report.json,중간 결과물,"main_report.py에서 생성된, 공간 분석 리포트의 파싱된 JSON 데이터입니다."
img4new3r_org.png,최종 결과물,스타일 변경 또는 가구 수정 작업 후의 최종 정면 뷰 이미지입니다.
img4new3r_left.png,최종 결과물,img4new3r_org.png를 기반으로 생성된 좌측 뷰 이미지입니다.
img4new3r_right.png,최종 결과물,img4new3r_org.png를 기반으로 생성된 우측 뷰 이미지입니다.


# 주요 기능

1.  최적 이미지 선택 (1단계): 사용자가 입력한 3장의 방 이미지 중 AI가 가장 적합한 1장(`selected_input_image.jpg`)을 선택합니다.
2.  공간 분석 리포트 생성 (1단계): 선택된 이미지를 기반으로 공간의 현재 스타일, 문제점, 가구 추가/제거/변경에 대한 추천 사항을 분석하고 파싱된 JSON 파일(`parsed_report.json`)로 저장합니다.
3.  인테리어 시뮬레이션 (2단계):
   - 스타일 변경 (`main_new_looks.py`): `style_choice.json`에 따라 방 전체 스타일을 새로운 스타일로 변경합니다.
   - 가구 부분 수정 (`main_modify_looks.py`): `user_choice.json`에 따라 AI 추천 가구의 추가, 제거, 변경 작업을 순차적으로 적용합니다.
4.  3-Angle 뷰 생성 (2단계): 최종 결과 이미지(`img4new3r_org.png`)를 기반으로, 동일한 구조와 스타일을 유지한 채 수평 각도만 변경한 "좌측(-30°)" 및 "우측(+30°)" 뷰 이미지를 추가 생성합니다.


# 기술 스택

| 분류     | 기술               | 상세                                                                    |
| :---    | :---              | :---                                                                   |
| 언어     | Python            | 모든 스크립트 작성에 사용                                                    |
| AI 모델  | Google Gemini API | `gemini-2.5-flash` (리포트 분석), `gemini-2.5-flash-image` (이미지 생성/수정) |
| 라이브러리 | `google-genai`    | Gemini 모델과의 통신                                                       |
| 라이브러리 | `Pillow`          | 이미지 로드 및 저장 등 기본 처리                                               |


# 설치 및 실행 방법

## 1. 의존성 설치

프로젝트에 필요한 Python 패키지를 설치합니다.
```bash
pip install -r requirements.txt

## 2. 환경 설정
config.py 파일을 열어 Google GenAI API 키와 초기 입력 이미지 경로를 설정해야 합니다.

[Python]
# config.py
API_KEY = "YOUR_GOOGLE_GENAI_API_KEY_HERE"# 3장의 최초 입력 이미지 경로를 실제 경로로 변경하세요.
INITIAL_IMAGE_PATHS = [
    "path/to/your/initial_image_1.jpg", 
    "path/to/your/initial_image_2.jpg",
    "path/to/your/initial_image_3.jpg"
]
# ...

## 3. 워크플로우 실행
단계 1: 공간 분석 및 리포트 생성
먼저 main_report.py를 실행하여 분석을 시작합니다.

[Bash]
python main_report.py
# 결과: selected_input_image.jpg, parsed_report.json 등이 생성됩니다.

단계 2: 사용자 선택 파일 준비
프론트엔드 또는 수동으로 시뮬레이션 옵션을 style_choice.json 및 user_choice.json에 저장합니다.
style_choice.json{"selected_style": "AI 추천"} - 방 전체 스타일 변경 시 사용
user_choice.json{"use_add": true, "use_remove": false, "use_change": true} - 가구 부분 수정 시 사용

단계3: 시뮬레이션 실행 (둘 중 하나 선택)

A. 전체 스타일 변경 시뮬레이션 (style_choice.json 사용)
[Bash]
python main_new_looks.py

B. 가구 부분 수정 시뮬레이션 (user_choice.json 사용)
[Bash]
python main_modify_looks.py

# 최종 결과물
시뮬레이션이 완료되면, 프로젝트 루트 디렉토리에 3장의 최종 이미지 파일이 생성됩니다.
img4new3r_org.png (정면 뷰)
img4new3r_left.png (좌측 뷰)
img4new3r_right.png (우측 뷰)
