# main.py
# YOLOv8 + ByteTrack 기반 차량 탐지 및 주정차 위반 판별 및 고지서 발급 및 영상 저장 스크립트

import sys
import os
import time
import cv2
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "ByteTrack"))

from detector import detect_vehicles
from tracker import VehicleTracker
from violation_checker import ViolationChecker

TICKET_TEMPLATE_PATH = "data/ticket_template.png"
TICKET_OUTPUT_DIR = "tickets"
FRAME_OUTPUT_DIR = "saved_frames"
VIDEO_OUTPUT_PATH = "data/output_video.mp4"

os.makedirs(TICKET_OUTPUT_DIR, exist_ok=True)
os.makedirs(FRAME_OUTPUT_DIR, exist_ok=True)

video_path = "data/cctv_with_car.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Failed to open video file")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"✅ FPS detected: {fps:.2f}")

# 출력 영상 저장 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(VIDEO_OUTPUT_PATH, fourcc, fps, (frame_width, frame_height))

tracker = VehicleTracker(frame_rate=fps)
checker = ViolationChecker()

paused = False
speed = 1.0
base_delay = 1000 / fps
frame_idx = 0
boxes = []
issued_tickets = set()

def save_ticket_image(frame, track_id, stopped_sec):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"ticket_{track_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(TICKET_OUTPUT_DIR, filename)

    if os.path.exists(TICKET_TEMPLATE_PATH):
        ticket = cv2.imread(TICKET_TEMPLATE_PATH)
    else:
        ticket = frame.copy()

    ticket = cv2.resize(ticket, (640, 360))

    cv2.putText(ticket, f"ID: {track_id}", (70, 145), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(ticket, f"Stopped: {stopped_sec:.1f}s", (70, 205), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(ticket, f"Time: {timestamp}", (70, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    cv2.imwrite(filepath, ticket)
    print(f"Ticket saved: {filepath}")

def save_frame_image(frame):
    filename = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(FRAME_OUTPUT_DIR, filename)
    cv2.imwrite(filepath, frame)
    print(f"✅ Frame saved: {filepath}")

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % 5 == 0:
            boxes = detect_vehicles(frame)

        tracked = tracker.update(boxes, frame)

        for (x1, y1, x2, y2, track_id) in tracked:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            result = checker.update(track_id, (x1, y1, x2, y2))
            if result is None:
                continue

            status, stopped_sec = result

            if status == "warning":
                cv2.putText(frame, "WARNING", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                print(f"⚠️ Vehicle {track_id} WARNING: over 4 sec stop")

            elif status == "violation":
                cv2.putText(frame, "VIOLATION", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                if track_id not in issued_tickets:
                    print(f"❌ Vehicle {track_id} VIOLATION: over 8 sec → ticket sent")
                    save_ticket_image(frame, track_id, stopped_sec)
                    issued_tickets.add(track_id)

        from violation_checker import NO_PARKING_ZONE
        zx1, zy1, zx2, zy2 = NO_PARKING_ZONE
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 0, 255), 2)
        cv2.putText(frame, "NO PARKING ZONE", (zx1, zy1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.putText(frame, f"Speed: {speed:.1f}x", (frame.shape[1] - 200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # 출력
        cv2.imshow("CCTV simulation video", frame)
        out.write(frame)  # 영상 저장
        frame_idx += 1

    key = cv2.waitKey(int(base_delay / speed)) & 0xFF

    if key == 27:  # ESC
        break
    elif key == ord(' '):  # 일시정지/재생
        paused = not paused
    elif key in [ord('+'), ord('=')]:
        speed = min(speed + 0.5, 10.0)
    elif key in [ord('-'), ord('_')]:
        speed = max(speed - 0.1, 0.1)

cap.release()
out.release()
cv2.destroyAllWindows()
