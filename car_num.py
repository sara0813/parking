# 자동차 이미지에 번호판 합성

import cv2
import numpy as np

# 경로
car_path = 'data/car.png'
plate_path = 'data/num.png'
output_path = 'data/car_with_plate.png'

# 이미지 불러오기 (둘 다 RGBA)
car = cv2.imread(car_path, cv2.IMREAD_UNCHANGED)
plate = cv2.imread(plate_path, cv2.IMREAD_UNCHANGED)

# RGBA 확인
if car.shape[2] != 4:
    raise ValueError("❗ car.png는 투명 배경(RGBA) 이미지여야 합니다.")
if plate.shape[2] != 4:
    raise ValueError("❗ num.png도 알파 포함 RGBA 이미지여야 합니다.")

# 번호판 크기 조정
target_plate_width = int(car.shape[1] * 0.5)
aspect_ratio = plate.shape[0] / plate.shape[1]
plate_resized = cv2.resize(plate, (target_plate_width, int(target_plate_width * aspect_ratio)))

# 위치 설정
x_offset = int(car.shape[1] * 0.25)
y_offset = int(car.shape[0] * 0.7)

# 흰색 박스 만들기 (RGBA)
white_box = np.ones_like(plate_resized, dtype=np.uint8) * 255
white_box[:, :, 3] = 255  # 알파 채널 100%

# 차 복사
car_copy = car.copy()

# 1️⃣ 먼저 흰 박스 블렌딩
roi = car_copy[y_offset:y_offset + white_box.shape[0], x_offset:x_offset + white_box.shape[1]]
alpha = white_box[:, :, 3] / 255.0
for c in range(3):
    roi[:, :, c] = (
        white_box[:, :, c] * alpha + roi[:, :, c] * (1 - alpha)
    )
roi[:, :, 3] = 255

# 2️⃣ 그 위에 번호판 이미지 붙이기
plate_rgb = plate_resized[:, :, :3]
plate_alpha = plate_resized[:, :, 3] / 255.0
for c in range(3):
    roi[:, :, c] = (
        plate_rgb[:, :, c] * plate_alpha + roi[:, :, c] * (1 - plate_alpha)
    )
roi[:, :, 3] = 255

# 결과 저장 (RGBA 유지)
cv2.imwrite(output_path, car_copy)
print(f"번호판 합성 완료: {output_path}")
