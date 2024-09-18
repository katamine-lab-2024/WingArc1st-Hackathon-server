import easyocr
import cv2
from typing import Optional
from collections import Counter
import numpy as np

# 動画をフレームごとに分割する
def split_video_into_frames(input: str, frame_skip: int = 1) -> list:
    cap = cv2.VideoCapture(input)

    frames = []
    frame_count = 0
    while True:
        if frame_count % frame_skip != 0:
            ret, _ = cap.read()
            if ret == False:
                break
            frame_count += 1
            continue

        ret, frame = cap.read()
        if ret == True:
            frames.append(frame)
        else:
            break
        
        frame_count += 1

    return frames

# 選手の画像から選手番号を検出
def detect_player_number_from_image(img) -> Optional[int]:
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, binary_img = cv2.threshold(gray_img, 128, 255, cv2.THRESH_BINARY)
    # masked_img = cv2.medianBlur(binary_img, 31)

    # # ノイズ除去のためにモルフォロジー演算を適用（例: 開閉処理）
    # kernel = np.ones((2, 2), np.uint8)
    # cleaned_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)

    # mask = (cleaned_img == 0).astype(np.uint8)  # 黒い部分を検出し、uint8型に変換

    # # 黒い部分を白に変更するために、黒い部分のマスクを白に変更
    # result_img = np.copy(binary_img)  # 元の2値化画像をコピー
    # result_img[mask == 0] = 255  # 黒い部分を白に変更

    number = None
    most_probable = 0
    for (_, text, prob) in reader.readtext(gray_img):
        if text.isnumeric() and prob > most_probable:
            number = int(text)
            most_probable = prob

    return number

# 選手の動画を分割したフレームから選手番号を検出
def detect_player_number_from_frames(frames: list) -> Optional[int]:
    detect_number_list = []
    for frame in frames:
        detect_number = detect_player_number_from_image(frame)
        detect_number_list.append(detect_number)

    counts = Counter(filter(None, detect_number_list))
    most_common = counts.most_common(1)
    if len(most_common) == 0:
        return None
    else:
        return most_common[0][0]

# 動きからのスコアを導出
def get_motion_score(frames: list) -> tuple[list, int, int]:
    prev_frame = frames.pop(0)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    index = 0
    max_motion_score_frame = 0
    motion_score_list = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        motion_score = cv2.countNonZero(thresh)
        motion_score_list.append(motion_score)
        if motion_score > motion_score_list[max_motion_score_frame]:
            max_motion_score_frame = index

        prev_gray = gray

        index += 1

    return motion_score_list, max_motion_score_frame, motion_score_list[max_motion_score_frame]
