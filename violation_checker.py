# violation_checker.py
# 금지구역 내 차량 정지 시간 추적 및 위반 판단 모듈

import time

NO_PARKING_ZONE = (809, 409, 859, 535)

class ViolationChecker:
    def __init__(self):
        self.vehicle_status = {}  # track_id: { 'last_center': (x, y), 'stopped_since': float }
        self.last_output = {}

    def is_inside_zone(self, box):
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        zx1, zy1, zx2, zy2 = NO_PARKING_ZONE
        return zx1 <= cx <= zx2 and zy1 <= cy <= zy2

    def is_stopped(self, prev_center, curr_center, threshold=10):
        dx = abs(prev_center[0] - curr_center[0])
        dy = abs(prev_center[1] - curr_center[1])
        return dx < threshold and dy < threshold

    def update(self, track_id, box):
        curr_time = time.time()
        cx = int((box[0] + box[2]) / 2)
        cy = int((box[1] + box[3]) / 2)
        curr_center = (cx, cy)

        if not self.is_inside_zone(box):
            self.vehicle_status.pop(track_id, None)
            self.last_output[track_id] = None
            return None, 0.0  # ✅ 반드시 tuple로 반환

        info = self.vehicle_status.get(track_id)
        if info is None:
            self.vehicle_status[track_id] = {
                'last_center': curr_center,
                'stopped_since': None
            }
            return None, 0.0  # ✅ 초기 등록 시도 시에도 튜플 반환

        prev_center = info['last_center']
        if self.is_stopped(prev_center, curr_center):
            if info['stopped_since'] is None:
                info['stopped_since'] = curr_time
        else:
            info['stopped_since'] = None

        info['last_center'] = curr_center

        if info['stopped_since'] is None:
            return None, 0.0

        stopped_sec = curr_time - info['stopped_since']
        print(f"[track {track_id}] stopped_sec={stopped_sec:.2f}")

        if stopped_sec >= 8:
            if self.last_output.get(track_id) != "violation":
                print(f"❌ Vehicle {track_id} VIOLATION: over 8 sec → ticket sent")
                self.last_output[track_id] = "violation"
            return "violation", stopped_sec
        elif stopped_sec >= 4:
            if self.last_output.get(track_id) != "warning":
                print(f"⚠️ Vehicle {track_id} WARNING: over 4 sec stop")
                self.last_output[track_id] = "warning"
            return "warning", stopped_sec
        else:
            self.last_output[track_id] = None
            return None, stopped_sec
