# tracker.py
# ByteTrack을 기반으로 차량 추적을 수행하는 VehicleTracker 클래스 정의

import sys
import os
import argparse
import numpy as np

# ByteTrack yolox 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "ByteTrack"))

from yolox.tracker.byte_tracker import BYTETracker

class VehicleTracker:
    def __init__(self, frame_rate=30):
        args = argparse.Namespace(
            track_thresh=0.5,
            match_thresh=0.8,
            track_buffer=30,
            frame_rate=frame_rate,
            mot20=False,
            aspect_ratio_thresh=1.6
        )
        self.tracker = BYTETracker(args)

    def update(self, detections, frame):
        """
        detections: [(x1, y1, x2, y2), ...]
        return: [(x1, y1, x2, y2, track_id), ...]
        """
        height, width = frame.shape[:2]
        img_info = (height, width)

        # ByteTrack 입력 형식: [x1, y1, x2, y2, conf]
        dets = []
        for (x1, y1, x2, y2) in detections:
            dets.append([x1, y1, x2, y2, 0.9])  # confidence 임의 설정

        outputs = self.tracker.update(np.array(dets), img_info, img_size=(height, width))

        result = []
        for track in outputs:
            tlbr = track.tlbr  # numpy 배열: [x1, y1, x2, y2]
            track_id = track.track_id
            x1, y1, x2, y2 = map(int, tlbr)
            result.append((x1, y1, x2, y2, track_id))

        return result