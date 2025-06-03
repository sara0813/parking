# YOLOv8 모델을 이용해 이미지에서 차량(car, motorcycle, bus, truck)만 감지하는 함수 정의

from ultralytics import YOLO
import cv2

# 모델 로딩 (가볍고 빠른 yolov8n)
model = YOLO("yolov8n.pt")

VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

def detect_vehicles(frame):
    """
    YOLO로 차량만 감지 (해상도 축소 적용 + 원본 좌표 복원)
    """
    original_h, original_w = frame.shape[:2]
    resized_frame = cv2.resize(frame, (640, 360))  # 축소 입력

    results = model(resized_frame, verbose=False)[0]

    scale_x = original_w / 640
    scale_y = original_h / 360

    boxes = []
    for box in results.boxes:
        cls_id = int(box.cls)
        if cls_id in VEHICLE_CLASSES:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # 원래 크기로 복원
            x1 = int(x1 * scale_x)
            y1 = int(y1 * scale_y)
            x2 = int(x2 * scale_x)
            y2 = int(y2 * scale_y)
            boxes.append((x1, y1, x2, y2))

    return boxes
