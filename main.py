import cv2
from detector import detect_vehicles
from tracker import VehicleTracker 

video_path = "data/cctv_with_car.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("영상 파일 열기 실패")
    exit()

tracker = VehicleTracker(frame_rate=cap.get(cv2.CAP_PROP_FPS))

paused = False
speed = 1.0
base_delay = 30  # 30ms = 약 33FPS

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO로 차량 감지
        boxes = detect_vehicles(frame)

        # 박스 시각화
        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Car", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # 재생 속도 표시
        cv2.putText(frame, f"Speed: {speed:.1f}x", (frame.shape[1] - 200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("CCTV simulation video", frame)

    key = cv2.waitKey(int(base_delay / speed)) & 0xFF

    if key == 27:  # ESC → 종료
        break
    elif key == ord(' '):  # Spacebar → 일시정지 토글
        paused = not paused
    elif key in [ord('+'), ord('=')]:  # 속도 증가
        speed = min(speed + 0.5, 10.0)
    elif key in [ord('-'), ord('_')]:  # 속도 감소
        speed = max(speed - 0.1, 0.1)

cap.release()
cv2.destroyAllWindows()
