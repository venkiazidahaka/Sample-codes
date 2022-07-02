"""
撮影
↓
オブジェクトディテクション(pytorchとtensorflowを共存させるために別スレッドで動作させている)
（一番Z軸が高いものかつスコアが高いものを選択）
↓
選択したものを特定補範囲で切り取り
↓
切り取った画像をインスタンスセグメンテーションにて推論
↓
切り取り画像の真ん中にインスタンスセグメンテーションが作成したマスクが存在するか確認
↓
マスクが存在するならば角度を求める　なければそのままピッキングをする
（角度の求め方は現状は真ん中の点と輪郭抽出で得られたオブジェクトの輪郭の中心点の角度にて求めている）
↓
ピクセル mm　の変換およびディストーションなどの補正
↓
ロボットにx y z c の情報を移動量として送信


"""


import os
import datetime
import numpy as np
import open3d as o3d
import cv2
import pandas
import re
import pprint
import math
import socket
import time
import torch
from PIL import Image
from multiprocessing import Process, Manager

# Intel RealSense cross-platform open-source API
import pyrealsense2 as rs
from matplotlib import pyplot as plt
from pyntcloud import PyntCloud
from keras_retinanet import models
from keras_retinanet.utils.colors import label_color
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image

# module下のライブラリ
from modules.realsense import Realsense
import modules.convert as conv
import modules.image as imageLib
import modules.instanceSeg as IS
import modules.objectDetection as OD
import modules.image as im
import modules.calculations as cal
import modules.simple_Data_link_Robot_Move as sdlrm
import modules.filecontrol as fc


def crop_rect(img, rect):
    center, size, angle = rect
    center = tuple(map(int, center))  # float -> int
    size = tuple(map(int, size))  # float -> int
    h, w = img.shape[:2]  # 画像の高さ、幅

    # 画像を回転する。
    M = cv2.getRotationMatrix2D(center, angle, 1)
    rotated = cv2.warpAffine(img, M, (w, h))

    # 切り抜く。
    cropped = cv2.getRectSubPix(rotated, size, center)

    return cropped


if __name__ == '__main__':
    ##############################
    #       #保存先の指定 作成
    ###############################
    rootDirPath = "F:/18HCI01/image/instance_segmentation/"
    date_now = datetime.datetime.now()
    dayDirPath = rootDirPath + date_now.strftime('%Y%m%d') + "/"
    print("dayDirPath", dayDirPath)
    # dayDirPath = rootDirPath + str(date_now.year) + \
    #     str(date_now.month) + str(date_now.day) + "/"
    fc.makeDir(dayDirPath)
    savename = date_now.strftime('%Y%m%d%H%M%S')
    print("savename", savename)
    output_image_base_dir_path = dayDirPath + savename + "/"
    os.makedirs(output_image_base_dir_path, exist_ok=True)
    predict_dir_path = dayDirPath + "predict/"
    os.makedirs(predict_dir_path, exist_ok=True)

    ###############################################
    # 撮影
    ##############################################
    rls = Realsense()
    img, pcd, rgbd, _ = rls.single_shot()
    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    ###########################################################
    # オブジェクトディテクションを別スレッドで実行
    # 別スレッドで雨後さなければpytorchをのちに実行する場合にcudaのメモリリークエラーが発生してしまうため
    # tensorflowを別スレッドで実行(スレッド終了時にメモリが解放される)
    ###########################################################
    manager = Manager()
    result_list = manager.list()  # 共有変数のリストを作成(マルチスレッドを使う場合共有変数を作成しなければ戻り値を受け取れない)
    # マルチプロセスを作成(オブジェクトディテクションの推論プログラム)
    p = Process(target=OD.infer_by_retinanet_pick_top, args=(
        img, result_list))
    # スレッド実行
    p.start()
    # 処理終了待ち
    p.join()
    print("result_list", result_list[:])
    print("result_list0", result_list[0])
    print("result_list1", result_list[1])
    # p.kill()
    cv2.imwrite(output_image_base_dir_path + "origin_" +
                savename + ".png", cv2.cvtColor(result_list[1], cv2.COLOR_BGR2RGB))

    #############################################################
    # インスタンスセグメンテーションにかける最もz軸の高いかつスコアの高いケーブルを選択
    #############################################################
    rgbdDepth = np.asarray(rgbd.depth)
    rgbdColor = np.asarray(rgbd.color)
    # 画像の回転
    rgbdDepth_rotated = cv2.rotate(rgbdDepth, cv2.ROTATE_90_CLOCKWISE)
    rgbdColor_rotated = cv2.rotate(rgbdColor, cv2.ROTATE_90_CLOCKWISE)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixconvy = 4.653808367
    offset_y = int(conv.mm_to_pixel(2, pixconvy))
    zList = []
    # すべてのケーブルのz軸を取得
    for i in range(len(result_list[0])):

        cablePixelDepth = rgbdDepth_rotated[result_list[0][i + 1]
                                            ["y"] + offset_y][result_list[0][i + 1]["x"]]
        zList.append(cablePixelDepth)

    zMaxValue = min(zList)  # 最も高いz座標を取得
    ##############################################################################
    # zは０の場合
    if zMaxValue == 0:
        print("zList", zList)
        zero_flag = 0
        temp_zlist = zList
        print("temp_zlist", temp_zlist)
        temp_zlist.sort()
        print("sorted_temp_zlist", temp_zlist)
        for z in temp_zlist:
            if z != 0 and zero_flag == 0:
                zMaxValue = z
                zero_flag = 1
    ##############################################################################
    zIndex = zList.index(zMaxValue)

    x = result_list[0][zIndex + 1]["x"]
    y = result_list[0][zIndex + 1]["y"]

    x_for_distotion = x
    y_for_distotion = y
    Z = zMaxValue

    print("x,y", x, y)
    xlength = 40  # カットイメージのX量
    ylength = 180  # カットイメージのY量

    _, img_cut = im.image_slice(img, x,
                                y, xlength, ylength)
    cv2.imwrite(output_image_base_dir_path + "cutOrigin_" +
                savename + ".png", img_cut)

    # 画像の中心座標を出力
    x, y = im.output_center_coordinates(img_cut)
    print("center_x,center_y", x, y)
    ax = int(y)

    ##############################################
    # インスタンスセグメンテーションを実行
    ###########################################
    predict_pillow_img, colors = IS.predict(y, x,
                                            img_path=output_image_base_dir_path + "cutOrigin_" +
                                            savename + ".png",
                                            drawType="all")
    predict_img = np.array(predict_pillow_img)  # opencv形式に変換

    y_np = x
    x_np = y
    ###############################################################
    # 画像の真ん中にマスクがあるか確認する
    ##############################################################
    mask_exist = False
    mask_color = None
    for color in colors:
        if np.array_equal(predict_img[int(y_np + 10), int(x_np)], color) == True:
            print("画像の真ん中にマスクあり")
            mask_exist = True
            print("color", color)
            mask_color = color

    ##########################################
    # 対象のケーブルの角度を抽出
    ##########################################
    if mask_exist == True:
        copyImg = predict_img.copy()
        #################################################################################
        # インスタンスセグメンテーションの結果のマスクの色を白色にそれ以外を黒色に変換し、それを用いてオブジェクトの輪郭を抽出する
        ############################################################################
        im.changeColorByColor(copyImg, mask_color, [255, 255, 255])

        cv2.imwrite(output_image_base_dir_path + "mask_" +
                    savename + ".png", copyImg)
        gray = cv2.cvtColor(copyImg, cv2.COLOR_RGB2GRAY)  # グレイスケールに変換
        ret, thresh = cv2.threshold(gray, 127, 255, 0)  # 二値化
        # オブジェクトの輪郭を検出する contours オブジェクトの輪郭座標を保持している配列。
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # plt.imshow(contours)
        # plt.show()
        #####################################
        # 輪郭座標の中心座標を求める
        ######################################
        cnt = contours[0]
        M = cv2.moments(cnt)
        # 重心を求める
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        axis_point = [ax, cy]
        #########################################
        # 表示用
        ########################################
        predict_img[int(y_np + 5), int(x_np)] = [255, 255, 255]
        # print("rects[0][0][1]", rects[0][0][1])
        predict_img[cy, cx] = [0, 0, 0]

        predict_img[axis_point[1], axis_point[0]] = [255, 255, 255]

        cv2.line(predict_img, (int(y), int(x)), (cx, cy), (0, 0, 0),
                 thickness=1, lineType=cv2.LINE_8, shift=0)

        cv2.line(predict_img, (int(y), int(x)), (axis_point[0], axis_point[1]), (0, 0, 0),
                 thickness=1, lineType=cv2.LINE_8, shift=0)

        ##############################################
        # Cの計算
        ###############################################
        AI_line = cal.line_length(cy, cx, x, y)
        axis_line = cal.line_length(axis_point[1], axis_point[0], x, y)
        C = math.acos(axis_line / AI_line)
        C = -math.degrees(C)
        # ロボットの回転方向に合わせる
        if cx > y:
            C = -C

        print(C)
        # C = math.radians(C)

    else:
        print("Mask does not exist")
        C = 0

    ####################################################################
    # 画像を保存
    ####################################################################
    predict_img[int(y_np + 10), int(x_np)] = [255, 255, 255]
    cv2.imwrite(output_image_base_dir_path + "predict_" +
                savename + ".png", cv2.cvtColor(predict_img, cv2.COLOR_BGR2RGB))

    ###########################################################
    # ピクセルと現実のmmの変換
    ###########################################################
    pixconv = conv.pixel_conversion_rate(Z)
    # pixconv = 4.536
    ylength = conv.rotation_shift(C)
    print("ylength", ylength)
    ylength = conv.mm_to_pixel(ylength, pixconv)

    x_computation = ylength * math.sin(C)
    y_computation = ylength * math.cos(C)

    if C != 0:
        y_for_distotion = y_for_distotion - y_computation
        print("cy", cx)
        print("y", y)
        if cy < y:
            x_for_distotion = x_for_distotion + x_computation
        else:
            x_for_distotion = x_for_distotion - x_computation

    X, Y = conv.convert_Center(x_for_distotion, y_for_distotion, img)

    x_mm = conv.pixel_to_mm(X, pixconv)
    y_mm = conv.pixel_to_mm(Y, pixconv)

    # ディストーション補正
    dx = conv.error_computation(x_mm, cablePixelDepth * 1000)
    dy = conv.error_computation(y_mm, cablePixelDepth * 1000)

    ###########################################
    # ディストーションを補正に追加
    #############################################
    X, Y = conv.add_distortion(x_mm, y_mm, dx, dy)

    # ｚ座標を現実空間用に変換
    Z = Z * 1000
    #Z = Z + 2
    Z = Z - 7  # 針用
    print("Z", Z)
    if Z > 206.5 and Z <= 210.5:
        print("※高さが206.5を超えました")
        Z -= 5

    elif Z > 210.5 or Z <= 110.0:
        print("※z軸が可動範囲外の位置に移動しようとしました")
        Z = 150.00

    # x軸の閾値を決定
    if X <= -44.25 or 44.25 <= X:
        print("※x軸が可動範囲外の位置に移動しようとしました")
        X = 0

    ################################################
    # ロボットを動かす
    ########################################
    # sdlrm.move_robot_data_link(X, Y, Z, C=C)
