# 주정차 금지구역 좌표 클릭용 스크립트

import cv2

coords = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        coords.append((x, y))
        print(f"클릭한 좌표: ({x}, {y})")

        # 클릭 표시
        cv2.circle(param, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Click on image", param)

img = cv2.imread("data/road_background.png")
if img is None:
    print("이미지 로드 실패! 경로를 확인하세요.")
    exit()

cv2.imshow("Click on image", img)
cv2.setMouseCallback("Click on image", click_event, img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 좌표 출력
print("최종 클릭된 좌표:", coords)

if len(coords) >= 2:
    annotated = img.copy()

    # 좌표 → 사각형 범위 계산
    xs = [pt[0] for pt in coords]
    ys = [pt[1] for pt in coords]
    x1, y1 = min(xs), min(ys)
    x2, y2 = max(xs), max(ys)

    # 사각형 그리기
    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # 텍스트 추가
    cv2.putText(annotated, "NO PARKING ZONE", (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # 이미지 저장
    cv2.imwrite("data/clicked_zone.png", annotated)
    print("클릭된 이미지 저장됨: data/clicked_zone.png")
