API_KEY = "YOUR_API_KEY_HERE"  # 여기에 실제 API 키 입력

# 3장의 최초 입력 이미지 경로
INITIAL_IMAGE_PATHS = [
    "C:/SW 지능정보 아카데미/PE3R/이미지/my3_angle/my3.jpg", 
    "C:/SW 지능정보 아카데미/PE3R/이미지/my3_angle/30degree.png",
    "C:/SW 지능정보 아카데미/PE3R/이미지/my3_angle/-30degree.png"
]

# 3장 중 AI가 선택한 '최적 이미지'가 임시로 저장될 경로
# 이후 모든 프로세스(Report, Style)는 이 경로를 사용합니다.
SELECTED_IMAGE_PATH = "selected_input_image.jpg"




REPORT_MODEL = "gemini-2.5-flash" # 리포트 생성 모델
STYLE_MODEL = "gemini-2.5-flash-image"  # 이미지 출력 모델
