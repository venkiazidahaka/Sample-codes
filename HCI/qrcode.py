import gtts
from playsound import playsound
from pyzbar.pyzbar import decode, ZBarSymbol
import cv2
import time
import requests
import os
from lbb_test import LBB_SEND
import base64
from datetime import datetime

lbb = LBB_SEND()


def audio(text):

    tts = gtts.gTTS(text, lang="ja")
    tts.save("audio.mp3")
    playsound("audio.mp3")
    # time.sleep(5)
    os.remove("audio.mp3")


def approximate_time(time):
    min = time.split(":")[1]
    hour = time.split(":")[0]
    if int(min) >= 30:
        new_min = "30"

    else:
        new_min = "00"

    new_time = hour+":"+new_min

    return new_time


def compare_time(now, reserved_time):
    n_h = int(now.split(":")[0])
    n_m = int(now.split(":")[1])
    r_h = int(reserved_time.split(":")[0])
    r_m = int(reserved_time.split(":")[1])
    if n_h < r_h:
        return "early"

    elif n_h > r_h:
        return "late"

    elif n_h == r_h and n_m < r_m:
        return "early"

    elif n_h == r_h and n_m > r_m:
        return "late"


def play_audio_and_notify(data):
    audio(data+"番のお客様ですね。")
    order_dic = lbb.get_orders()
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    time = dt.strftime("%H:%M")
    new_time = approximate_time(time)
    today_check_flag = 0
    if data in order_dic[date][new_time]:
        audio("少々お待ちください店員が迎えに参ります。")
        notify(data+"のお客様はいらっしゃっているので迎えに行ってください。")
    else:
        if today_check_flag == 0:
            for time_list in order_dic[date].keys():
                if data in order_dic[date][time_list]:
                    punctuality = compare_time(new_time, time_list)
                    if punctuality == "early":
                        audio(time_list+"予約のお客様ですね。お客様の順ではございませんので、" +
                              time_list+"までお待ちください。" + time_list+"になったら、もう一度QRコードをスキャンしてください。")
                        today_check_flag = 0
                        break

                    elif punctuality == "late":
                        audio(time_list+"予約のお客様ですね。申し訳ありませんが"+time_list +
                              "過ぎていますので、ご入室は出来ません。ご理解程よろしくお願いします。")
                        today_check_flag = 0
                        break

                else:
                    today_check_flag = 1

        if today_check_flag == 1:
            audio("申し訳ございません。お客様の予約を本日でございませんので、お手数をおかけしますが、もう一度ご確認をお願いします。")


def notify(text):
    token = 'n7klwRNSSdBlXdftqAVrO2OvBPmePVV5NlmC5TB7nFn'

    payload = {'message': text}
    r = requests.post('https://notify-api.line.me/api/notify',
                      headers={'Authorization': 'Bearer {}'.format(token)}, params=payload)


def main():
    cap = cv2.VideoCapture(
        "rtsp://admin:admin@192.168.0.105:554/live/ch1", cv2.CAP_FFMPEG)
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    qrcode_read_flag = 0
    while qrcode_read_flag == 0:
        ret, frame = cap.read()
        # print("streaming")
        # gray_img = cv2.cvtColor(frame, 0)
        qrcode = decode(frame)

        if len(qrcode) != 0:
            cap.release()
            qrcode_read_flag = 1
            data_64 = qrcode[0].data.decode("utf-8")
            base64_bytes = data_64.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            data_string = message_bytes.decode('ascii')
            if len(data_string.split("_")) == 1:
                audio("正しいQRコードをスキャンしてください。")

            else:
                data = data_string.split("_")[-1]
                play_audio_and_notify(data)

        # print(qrcode)
        cv2.imshow("Video", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    if qrcode_read_flag == 1:
        main()


if __name__ == "__main__":
    main()
