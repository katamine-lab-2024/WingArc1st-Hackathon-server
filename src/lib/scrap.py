import datetime
import json
import re

import requests
from bs4 import BeautifulSoup

# ギラヴァンツの選手一覧ページURL
GIRAVANZ_STUFF_PLAYER_URL = 'https://www.giravanz.jp/topteam/staff_player'

# ギラヴァンツのホームページURL(直近の試合結果取得用)
GIRAVANZ_HOME_URL = "https://www.giravanz.jp"

def get_giravanz_player_list() -> list[dict[str, str, str, str]]:
    req = requests.get(GIRAVANZ_STUFF_PLAYER_URL)
    req.encoding = req.apparent_encoding

    soup = BeautifulSoup(req.text, "html.parser")
    staff_player_item_list = soup.select("[class='p-topteam__list-item']")

    player_list = []
    for item in staff_player_item_list:
        name_ja = item.select_one("[class='p-topteam__list-item-name']").text
        name_en = item.select_one("[class='p-topteam__list-item-name-en']").text

        number = "No number"
        number_item_parent = item.select_one("[class='p-topteam__list-item-number']")
        if (number_item_parent != None):
            # 選手の背番号は画像で表示されているため、画像のURLから背番号を取得する
            number_item_src = number_item_parent.select_one("img").attrs['src']
            number = re.search(r'-([0-9]+)\.svg', number_item_src).group(1)

        img_src = GIRAVANZ_HOME_URL + item.select_one("figure").select_one("img").attrs['src']

        if (number != "No number"):
            player_list.append({
                "name_ja": name_ja,
                "name_en": name_en,
                "number": number,
                "img_src": img_src
            })

    return player_list

def get_giravanz_latest_game_result() -> dict[str, str, str, str, str, str, str, str]:
    req = requests.get(GIRAVANZ_HOME_URL)
    req.encoding = req.apparent_encoding

    soup = BeautifulSoup(req.text, "html.parser")
    latest_game_result_sec = soup.select_one("[class='p-home__latest']")

    season = latest_game_result_sec.select_one("[class='text-center']").text

    date_str = latest_game_result_sec.select_one("[class='p-home__latest-schedule-date']").contents[0].text
    kickoff_time_str = latest_game_result_sec.select_one("[class='kickoff']").text
    date = str(datetime.datetime.strptime(date_str + " " + kickoff_time_str, '%Y.%m.%d %H:%M'))

    stadium = latest_game_result_sec.select_one("[class='p-home__latest-schedule-venue u-margin__bottom-0']").contents[1].text
    gameside = latest_game_result_sec.select_one("[class='p-home__latest-schedule-venue u-margin__bottom-0']").contents[3].text

    latest_game_result = latest_game_result_sec.select_one("[class='p-home__latest-list']")
    if (gameside == "HOME"):
        opponent = latest_game_result.select("[class='p-home__latest-team-name']")[1].text
    elif (gameside == "AWAY"):
        opponent = latest_game_result.select("[class='p-home__latest-team-name']")[0].text

    score_home = latest_game_result.select("[class='p-home__latest-score-total']")[0].text
    score_away = latest_game_result.select("[class='p-home__latest-score-total']")[1].text

    result = judge_giravanz_latest_game_result(gameside, int(score_home), int(score_away))

    return {
        "season": season,
        "date": date,
        "stadium": stadium,
        "gameside": gameside,
        "opponent": opponent,
        "score_home": score_home,
        "score_away": score_away,
        "result": result
    }

def judge_giravanz_latest_game_result(gameside: str, score_home: int, score_away: int) -> str:
    if (gameside == "HOME"):
        if (score_home > score_away):
            return "WIN"
        elif (score_home < score_away):
            return "LOSE"
        else:
            return "DRAW"
    elif (gameside == "AWAY"):
        if (score_home < score_away):
            return "WIN"
        elif (score_home > score_away):
            return "LOSE"
        else:
            return "DRAW"

def download_giravanz_player_img(player_list: list[dict[str, str, str, str]]):
    for player in player_list:
        img = requests.get(player["img_src"])
        with open(f'./img/players-official/{player["number"]}.png', 'wb') as f:
            f.write(img.content)

def save_giravanz_player_list_json(player_list: list[dict[str, str, str, str]]):
    with open('./data/json/giravanz_player_list.json', 'w') as f:
        json.dump(player_list, f, indent=4, ensure_ascii=False)
