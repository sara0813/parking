# ticket_generator.py
import cv2

def generate_ticket(frame, track_id, stopped_sec, output_path):
    ticket = frame.copy()
    cv2.putText(ticket, f"Violation ID: {track_id}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.putText(ticket, f"Stopped: {stopped_sec:.1f}s", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.imwrite(output_path, ticket)

