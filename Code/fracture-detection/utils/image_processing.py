

import cv2
import numpy as np


def canny_on_gray(roi: np.ndarray):
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return gray, edges


def analyze_contours(
    roi: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    img_detailed: np.ndarray,
    px_to_mm: float,
) -> dict:

    gray_roi, edges = canny_on_gray(roi)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    entry = {"Shift (px)": None, "Shift (mm)": None, "Shape Diff": None}

    if len(contours) >= 2:        
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        cnt1, cnt2 = contours
        centroids = []
        for cnt in [cnt1, cnt2]:
            M = cv2.moments(cnt)
            if M["m00"] != 0:                
                cx = int(M["m10"] / M["m00"]) + x1
                cy = int(M["m01"] / M["m00"]) + y1
                centroids.append((cx, cy))
                cv2.circle(img_detailed, (cx, cy), 6, (255, 0, 0), -1)
        if len(centroids) == 2:
            (xA, yA), (xB, yB) = centroids
            shift = np.sqrt((xB - xA) ** 2 + (yB - yA) ** 2)
            entry["Shift (px)"] = round(float(shift), 2)
            entry["Shift (mm)"] = round(float(shift) * px_to_mm, 2)            
            cv2.line(img_detailed, (xA, yA), (xB, yB), (0, 255, 0), 2)            
            shift_mm = entry["Shift (mm)"]
            mid_x = (xA + xB) // 2
            mid_y = (yA + yB) // 2 - 10            
            cv2.putText(
                img_detailed, f"{shift_mm:.2f} mm", (mid_x, mid_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA
            )
            cv2.putText(
                img_detailed, f"{shift_mm:.2f} mm", (mid_x, mid_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA
            )           
            entry["Shape Diff"] = round(
                float(cv2.matchShapes(cnt1, cnt2, cv2.CONTOURS_MATCH_I1, 0.0)), 3
            )
    else:
        
        dx = int((x2 - x1) * 0.8)
        dy = int((y1 - y2) * 0.8)
        shift = np.sqrt(dx ** 2 + dy ** 2)
        entry["Shift (px)"] = round(float(shift), 2)
        entry["Shift (mm)"] = round(float(shift) * px_to_mm, 2)
        entry["Shape Diff"] = "N/A"

    return entry
