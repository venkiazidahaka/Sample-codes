from modules import flat_cable_predict as fcp
from modules.realsense import Realsense
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import modules.image as im
import numpy as np
import modules.convert as conv
import socket
import modules.simple_Data_link_Robot_Move as sdlrm


def add_pic_offset(coordinates, x1=100, y1=100):
    """match the AI result with the original picture"""
    x = coordinates[1] + x1
    y = coordinates[0] + y1

    return x, y


def flat_cable_pixel_coordinates(pil_img):
    predict_img = fcp.flat_cable_predict(pil_img)

    predict_img = cv2.resize(predict_img, (900, 630),
                             interpolation=cv2.INTER_AREA)
    pixels = im.get_pixels(predict_img)

    sorted_color_list = im.color_sort(pixels)
    batches_list = im.array_batch_split(sorted_color_list)
    touch_points = []
    for batches in batches_list:
        points = im.mid_points(batches)
        # for point in points:
        # predict_img[points[5][0]][points[5][1]] = [255, 255, 255]
        coordinates = [points[5][0], points[5][1]]
        x, y = add_pic_offset(coordinates, 200, 50)
        touch_point = [x, y]
        touch_points.append(touch_point)
        img[y][x] = [255, 255, 255]
        # plt.imshow(img)
        # plt.show()

    # plt.imshow(predict_img)
    # plt.show()

    return touch_points


def flat_cable_mm_coordinates(touch_points, img):
    flat_cable_points = touch_points[2]
    x = flat_cable_points[0]
    y = flat_cable_points[1]
    z = 207
    pixconv = 4.653808367
    X, Y = conv.convert_Center(
        x, y, img)
    x_mm = conv.pixel_to_mm(X, pixconv)
    y_mm = conv.pixel_to_mm(Y, pixconv)

    return x_mm, y_mm, z


def flat_cable_calculations(pil_img):
    predict_img = fcp.flat_cable_predict(pil_img)
    img_list = im.seperate_image_by_masks(predict_img)
    tip = img_list[0]


if __name__ == "__main__":
    # host = "localhost"
    # host = "192.168.0.20"
    # send_port = 12345
    # # recv_port = 12343
    # recv_port = 12344
    # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect((host, send_port))

    # serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # serversock.bind((host, recv_port))  # IPとPORTを指定してバインドします
    # serversock.listen(10)  # 接続の待ち受けをします（キューの最大数を指定）

    # # print('Waiting for connections...')
    # clientsock, client_address = serversock.accept()  # 接続されればデータを接続

    # rls = Realsense()
    # img, _, _, depth, _ = rls.single_shot()
    # # print(depth)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # pil_img = Image.fromarray(img)
    # touch_points = flat_cable_pixel_coordinates(pil_img)
    # X, Y, Z = flat_cable_mm_coordinates(touch_points, img)
    # print(X, Y, Z)

    # return_msg = sdlrm.move_robot_data_link(Y, -X, Z)
    # client.send(return_msg.encode('utf-8'))
    rls = Realsense()
    img, _, _, depth, _ = rls.single_shot()
    # print(depth)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img)
    flat_cable_calculations(pil_img)
