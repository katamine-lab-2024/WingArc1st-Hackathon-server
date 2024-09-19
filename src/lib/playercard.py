import easyocr
import cv2
import os
import numpy as np
from typing import Optional
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

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

def get_bestshot_frame(frames: list) -> int:
    _, bestshot_index, _ = get_motion_score(frames)
    return bestshot_index

def create_player_card(input_image, player_name, player_number, game_name):
    template_path = './data/card/template.jpg'
    logo_path = './data/card/logo.png'

    rgb_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    player_image = Image.fromarray(rgb_image)

    template_image = Image.open(template_path)
    mask = Image.open("./data/card/mask.jpg").convert("L")
 
    player_image = player_image.resize((440, 782))
    player_image_width, player_image_height = player_image.size
    center_x, center_y = player_image_width // 2, player_image_height // 2
    card_width, card_height = 440, 782
    left = center_x - card_width // 2
    top = center_y - card_height // 2
    right = center_x + card_width // 2
    bottom = center_y + card_height // 2
    processed_player_image = player_image.crop((left, top, right, bottom))
 
    # テンプレートと合成
    card_image = Image.composite(processed_player_image, template_image, mask)
 
    # ロゴの透明化処理
    logo_image = Image.open(logo_path).convert("RGBA")
    logo_data = logo_image.getdata()
 
    # 白い部分を透明化
    new_logo_data = []
    for item in logo_data:
        # 完全な白 (255, 255, 255) を透明にする
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_logo_data.append((255, 255, 255, 0))  # 透明化
        else:
            new_logo_data.append(item)
 
    logo_image.putdata(new_logo_data)
 
    resize_logo_image = logo_image.resize((80, 80))
    # ロゴを貼り付ける位置を設定
    logo_x, logo_y = 28, 660  # 適当な位置を指定（変更可能）
    card_image.paste(resize_logo_image, (logo_x, logo_y), resize_logo_image)
 
    # フォント設定
    font_path = "C:/Windows/Fonts/meiryo.ttc"
    player_font = ImageFont.truetype(font_path, size=30)
    match_font = ImageFont.truetype(font_path, size=12)
    backnum_font = ImageFont.truetype(font_path, size=30)
 
    # 選手名を回転させて描画
    text_img = Image.new('RGBA', (616, 440), (255, 255, 255, 0))  # 適当なサイズを指定
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((35, 400), player_name, font=player_font, fill=(230, 180, 34, 255))  # 選手名を描画
 
    # テキスト画像を回転させる
    rotated_text_img = text_img.rotate(270, expand=True)
 
    # 回転させたテキスト画像をカードに貼り付け
    card_image.paste(rotated_text_img, (10, 10), rotated_text_img)
 
    # その他のテキストを描画
    card_draw = ImageDraw.Draw(card_image)
    card_draw.text((200, 755), game_name, font=match_font, fill=(230, 180, 34, 128))  # 試合情報を描画
    card_draw.text((15, 470), player_number, font=backnum_font, fill=(230, 180, 34, 70))  # 背番号を描画

    return cv2.cvtColor(np.array(card_image), cv2.COLOR_RGB2BGR)

# フレーム画像を指定ディレクトリに保存
def save_frames_to_directory(frames: list, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    
    for i, frame in enumerate(frames):
        file_path = os.path.join(output_dir, f"frame_{i:04d}.jpg")
        
        cv2.imwrite(file_path, frame)

def create_player_card_video(input_frames, player_name, player_number, game_name) -> list:  
    deco_frames = []
    
    for frame in input_frames:
        deco_frame = create_player_card(frame, player_name, player_number, game_name)
        deco_frames.append(deco_frame)

    return deco_frames

def frames_to_video(frames: list, output_path: str, fps: int = 30) -> None:
    height, width, _ = frames[0].shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for image in frames:
        if image.shape[1] != width or image.shape[0] != height:
            raise ValueError("フレームと画像のサイズが一致していません。")
        out.write(image)

    out.release()
