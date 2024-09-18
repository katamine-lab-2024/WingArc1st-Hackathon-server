from PIL import Image, ImageDraw, ImageFont
 
def create_player_card(input_image, player_name, player_number, game_name):
    template_path = 'template.jpg'
    logo_path = 'logo.png'

    player_image = input_image
    template_image = Image.open(template_path)
    mask = Image.open("mask.jpg").convert("L")
 
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
    card_draw.text((200, 755), player_number, font=match_font, fill=(230, 180, 34, 128))  # 試合情報を描画
    card_draw.text((15, 470), game_name, font=backnum_font, fill=(230, 180, 34, 70))  # 背番号を描画

    return card_image

 