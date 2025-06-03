# main.py
# YOLOv8 + ByteTrack 기반 차량 탐지 및 추적 실행 스크립트
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ByteTrack"))

import cv2
from detector import detect_vehicles
from tracker import VehicleTracker

video_path = "data/cctv_with_car.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ 영상 파일 열기 실패")
    exit()

tracker = VehicleTracker(frame_rate=cap.get(cv2.CAP_PROP_FPS))

paused = False
speed = 1.0
base_delay = 30

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break

        # 차량 감지 (YOLO)
        boxes = detect_vehicles(frame)

        # 차량 추적 (ByteTrack)
        tracked = tracker.update(boxes, frame)

        # 추적 결과 시각화
        for (x1, y1, x2, y2, track_id) in tracked:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # 재생 속도 표시
        cv2.putText(frame, f"Speed: {speed:.1f}x", (frame.shape[1] - 200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("CCTV simulation video", frame)

    key = cv2.waitKey(int(base_delay / speed)) & 0xFF

    if key == 27:  # ESC → 종료
        break
    elif key == ord(' '):
        paused = not paused
    elif key in [ord('+'), ord('=')]:
        speed = min(speed + 0.5, 10.0)
    elif key in [ord('-'), ord('_')]:
        speed = max(speed - 0.1, 0.1)

cap.release()
cv2.destroyAllWindows()
