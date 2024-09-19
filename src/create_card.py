from lib.playercard import *
from lib.scrap import get_giravanz_latest_game_result
import json

def create_rarecard(movie_path: str) -> tuple[np.ndarray, list[np.ndarray]]:
    frames = split_video_into_frames(movie_path)

    # 数値読み取り
    skiped_frames = frames[0:len(frames)//2:10]
    number = detect_player_number_from_frames(skiped_frames)
    if number == None:
        number = 0

    # 選手名照合
    player_name_en = "ERROR"
    with open('data/json/giravanz_player_list.json') as f:
        player_dict = json.load(f)

        for player in player_dict:
            if int(player['number']) == number:
                player_name_en = player['name_en']
                break

    # 最新ゲームの内容を取得
    season = get_giravanz_latest_game_result()["season"]

    # 選手カード画像作成
    bestshot = get_bestshot_frame(frames)
    card_img = create_player_card(frames[bestshot], player_name_en, str(number), season)

    # 選手カード動画作成
    card_video = create_player_card_video(frames, player_name_en, str(number), season)

    return card_img, card_video
