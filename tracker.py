# ByteTrack을 기반으로 차량 추적을 수행하는 VehicleTracker 클래스 정의

import sys
import os
import argparse
import numpy as np
import math

# ByteTrack yolox 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "ByteTrack"))

from yolox.tracker.byte_tracker import BYTETracker

class VehicleTracker:
    def __init__(self, frame_rate):
        args = argparse.Namespace(
            track_thresh=0.5,
            match_thresh=0.9,
            track_buffer=90,
            frame_rate=frame_rate,
            mot20=False,
            aspect_ratio_thresh=1.6
        )
        self.tracker = BYTETracker(args)
        self.track_id_map = {}         # 새 ID -> 기존 ID
        self.track_last_centers = {}   # track_id -> (cx, cy)

    def map_track_id(self, track_id, cx, cy):
        curr_center = (cx, cy)
        min_dist = float('inf')
        mapped_id = track_id

        for prev_id, prev_center in self.track_last_centers.items():
            dist = math.hypot(cx - prev_center[0], cy - prev_center[1])
            if dist < 30 and dist < min_dist:
                min_dist = dist
                mapped_id = prev_id

        if mapped_id != track_id:
            self.track_id_map[track_id] = mapped_id
            print(f"🔁 Remap: {track_id} → {mapped_id}")

        self.track_last_centers[mapped_id] = curr_center
        return mapped_id

    def update(self, detections, frame):
        """
        detections: [(x1, y1, x2, y2), ...]
        return: [(x1, y1, x2, y2, track_id), ...]
        """
        height, width = frame.shape[:2]
        img_info = (height, width)

        dets = []
        for (x1, y1, x2, y2) in detections:
            dets.append([x1, y1, x2, y2, 0.9])  # confidence 임의 설정

        outputs = self.tracker.update(np.array(dets), img_info, img_size=(height, width))

        result = []
        for track in outputs:
            tlbr = track.tlbr  # numpy 배열: [x1, y1, x2, y2]
            track_id = track.track_id
            x1, y1, x2, y2 = map(int, tlbr)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            real_id = self.map_track_id(track_id, cx, cy)
            result.append((x1, y1, x2, y2, real_id))

        return result
