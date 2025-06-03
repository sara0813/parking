#시뮬레이션 영상 제작 코드

import cv2
import numpy as np

car_path = 'data/car_with_plate.png' 
bg_video_path = 'data/cctv.mp4'
output_path = 'data/cctv_with_car.mp4'

# 차량 이미지 로드: 알파 채널 포함되도록
car = cv2.imread(car_path, cv2.IMREAD_UNCHANGED)
if car.shape[2] != 4:
    raise ValueError("❗ car_with_plate.png는 반드시 알파 채널(RGBA)을 포함해야 합니다.")

# 차량 크기 조정
target_width = 70
aspect_ratio = car.shape[0] / car.shape[1]
car = cv2.resize(car, (target_width, int(target_width * aspect_ratio)))

# 위치 지정
x = 820
y = 440

# 배경 영상 로드
cap = cv2.VideoCapture(bg_video_path)
bg_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
bg_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# 저장 설정
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (bg_w, bg_h))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 알파 채널 마스크 추출
    alpha = car[:, :, 3] / 255.0
    alpha_inv = 1.0 - alpha

    for c in range(3):  # RGB 채널
        frame[y:y+car.shape[0], x:x+car.shape[1], c] = (
            car[:, :, c] * alpha +
            frame[y:y+car.shape[0], x:x+car.shape[1], c] * alpha_inv
        )

    out.write(frame)

cap.release()
out.release()
print("✅ 영상 위에 차량 합성 완료!")
