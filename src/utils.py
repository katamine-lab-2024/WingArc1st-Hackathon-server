import cv2

# 動画をフレームごとに分割する
def split_video_into_frames(input: str) -> list:
    cap = cv2.VideoCapture(input)

    frames = []
    while True:
        ret, frame = cap.read()
        if ret == True:
            frames.append(frame)
        else:
            break

    return frames

if __name__ == '__main__':
    frames = split_video_into_frames('./data/video/5.mp4')

    for frame in frames:
        cv2.imshow('frame', frame)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break
