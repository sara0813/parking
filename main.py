# main.py
# YOLOv8 + ByteTrack 기반 차량 탐지 및 주정차 위반 판별 스크립트

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ByteTrack"))

import cv2
from detector import detect_vehicles
from tracker import VehicleTracker
from violation_checker import ViolationChecker

video_path = "data/cctv_with_car.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("영상 파일 열기 실패")
    exit()

fps = 30
tracker = VehicleTracker(frame_rate=fps)
checker = ViolationChecker()

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

        # 추적 결과 시각화 + 위반 판단
        for (x1, y1, x2, y2, track_id) in tracked:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # 불법주정차 판단
            status = checker.update(track_id, (x1, y1, x2, y2))
            if status == "warning":
                cv2.putText(frame, "WARNING", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                print(f"⚠️ 차량 {track_id} 정차 경고 (3초 이상)")
            elif status == "violation":
                cv2.putText(frame, "VIOLATION", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                print(f"❌ 차량 {track_id} 불법주정차! (5초 이상) → 고지서 전송")

        # 금지구역 시각화
        from violation_checker import NO_PARKING_ZONE
        zx1, zy1, zx2, zy2 = NO_PARKING_ZONE
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 0, 255), 2)
        cv2.putText(frame, "NO PARKING ZONE", (zx1, zy1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

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
