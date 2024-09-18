import random
import json

import cv2

DUMMY_DATA = [27, 23, 50, 13, 33, 34, 14, 17, 20, 21, 10]
DUMMY_ATARI = 5

# ガチャ機構の第一段階
def _gacha_1st_stage():
    r = random.randint(1, 20)
    if r == 7:
        return 'UR'
    return 'R'

# ガチャ
def gacha() -> dict[str, str, str, str, str]:
    rarity = _gacha_1st_stage()
    # print(rarity)
    with open('uploads/db.json', 'r') as f:
        db: list = json.load(f)
        random.shuffle(db)
        for item in db:
            if item['rarity'] == rarity:
                return item

def gacha10() -> list[dict[str, str, str, str, str]]:
    result = []
    for _ in range(10):
        result.append(gacha())
    return result

# result = gacha()
# img = cv2.imread('uploads/' + result['card_img'])
# cv2.imshow('result', img)
# cv2.waitKey(0)
