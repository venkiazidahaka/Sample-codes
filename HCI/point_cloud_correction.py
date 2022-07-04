import numpy as np
import open3d as o3d
import cv2
from PIL import Image
import pyvista as pv
from matplotlib import pyplot as plt
# module下のライブラリ
from modules.realsense import Realsense

from collections import defaultdict
# from OOP.modules.AI.semanticSegmentaion import SemanTicSegmentation as SS
from OOP.modules.AI.new_semanticSegmentation import SemanTicSegmentation as SS


def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    return [locs for key, locs in tally.items()
            if len(locs) > 0]


# Point CLoudからケーブルの部分だけを取る
# cube_boundary=[cube_boundary_bottom=-0.195, cube_boundary_top=-0.125,
#               cube_boundary_back=-0.005,
#               cube_boundary_right=0.035, cube_boundary_left=-0.035]


def exctract_cable(pcd, rgbd, cube_boundary=[-0.195, -0.125, -0.005, 0.035, -0.035]):
    # o3d.visualization.draw_geometries([pcd])
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)

    new_points = []
    new_colors = []
    for i, point in enumerate(points):
        if point[2] > cube_boundary[0] and point[2] < cube_boundary[1] and point[0] < cube_boundary[2] and point[1] < cube_boundary[3] and point[1] > cube_boundary[4]:
            # colors[i] = [0, 0, 1]
            new_colors.append(colors[i])
            new_points.append(point)
    # print(new_colors)
    new_points = np.asarray(new_points)
    new_pcd = pv.PolyData(new_points)
    new_pcd['colors'] = new_colors
    # new_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)
    # o3d.visualization.draw_geometries([pcd])

    return new_pcd, new_points, new_colors

# ケーブルの部分のpoint-cloudからWireの色によってPoint cloudを取る


def isolate_wires(new_points, new_colors, cable_colors=[[255, 0, 0], [255, 255, 255], [0, 0, 0]]):
    change_colors = []
    red_points = []
    red_colors = []
    white_points = []
    white_colors = []
    black_points = []
    black_colors = []
    change_points = []
    for i, every_color in enumerate(new_colors):
        if every_color[0] == 1:
            # changed_color = [0.17647059, 0.09803922, 0.22745098]
            change_colors.append(cable_colors[0])
            change_points.append(new_points[i])
            red_points.append(new_points[i])
            red_colors.append(cable_colors[0])
        elif every_color[2] == 1:
            changed_color = cable_colors[1]
            change_colors.append(changed_color)
            change_points.append(new_points[i])
            white_points.append(new_points[i])
            white_colors.append([cable_colors[1]])
        elif every_color[1] == 1:
            changed_color = cable_colors[2]
            change_colors.append(changed_color)
            change_points.append(new_points[i])
            black_points.append(new_points[i])
            black_colors.append(cable_colors[2])
    ##################################################################
    new_red_points = np.asarray(red_points)
    new_red_pcd = pv.PolyData(new_red_points)
    new_red_pcd['colors'] = red_colors
    # new_red_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)
    ##################################################################
    new_white_points = np.asarray(white_points)
    new_white_pcd = pv.PolyData(new_white_points)
    new_white_pcd['colors'] = white_colors
    # new_white_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)
    ##################################################################
    new_black_points = np.asarray(black_points)
    new_black_pcd = pv.PolyData(new_black_points)
    new_black_pcd['colors'] = black_colors
    # new_black_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)
    ##################################################################
    new_points = np.asarray(change_points)
    new_pcd = pv.PolyData(new_points)
    new_pcd['colors'] = change_colors
    # new_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)

    pcd_list = [new_red_pcd, new_white_pcd, new_black_pcd]
    pcd_points_list = [red_points, white_points, black_points]

    return pcd_list, pcd_points_list


def special_wire_filter(black_pixels, red_pixels,
                        white_pixels, rgbd, pinhole_camera_intrinsic):
    depths = np.asarray(rgbd.depth)
    colors = np.asarray(rgbd.color)
    # print(len(black_pixels))

    for black_pixel in black_pixels:
        colors[black_pixel[0]][black_pixel[1]] = [0, 255, 0]
    for red_pixel in red_pixels:
        colors[red_pixel[0]][red_pixel[1]] = [0, 0, 255]
    for white_pixel in white_pixels:
        colors[white_pixel[0]][white_pixel[1]] = [255, 0, 0]

    color_o3d_img = o3d.geometry.Image(colors)
    depth_o3d_img = o3d.geometry.Image(depths)

    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d_img, depth_o3d_img, convert_rgb_to_intensity=False)
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd, pinhole_camera_intrinsic)

    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0],
                   [0, 0, -1, 0], [0, 0, 0, 1]])
    # o3d.visualization.draw_geometries([pcd])

    return pcd


def remove_pcd_point_outliers(pcd_points_list, color="red", degree=3):

    new_points_list = []
    change_colors = []
    x_list = []
    y_list = []
    z_list = []
    if color == "red":
        i = 0
        color = [255, 0, 0]
    elif color == "white":
        i = 1
        color = [0, 255, 0]
    elif color == "black":
        i = 2
        color = [0, 0, 0]
    for pcd_point in pcd_points_list[i]:
        x_list.append(pcd_point[0])
        y_list.append(pcd_point[1])
        z_list.append(pcd_point[2])

    # y_z_list = np.array([y_list, z_list])
    # coordinate_list = np.reshape(
    #     y_z_list, (y_z_list.shape[1], y_z_list.shape[0]))
    ###########################################################################################
    new_x_list_x_y = []
    new_y_list_x_y = []

    index_list_x_y = []
    # plt.scatter(x_list, y_list)
    # plt.show()

    for dup in sorted(list_duplicates(x_list)):
        index = dup[int(len(dup) / 2)]
        index_list_x_y.append(index)

    for index in index_list_x_y:
        new_x_list_x_y.append(x_list[index])
        new_y_list_x_y.append(y_list[index])

    # plt.scatter(new_x_list_x_y, new_y_list_x_y)
    # plt.show()
    poly_x_y = np.polyfit(new_x_list_x_y,
                          new_y_list_x_y, degree)
    plo_x_y = np.poly1d(poly_x_y)
    new_x = np.linspace(min(new_x_list_x_y), max(new_x_list_x_y) + 100, 3000)
    new_y = plo_x_y(new_x)
    # plt.plot(new_x_list_x_y, new_y_list_x_y, "o", new_x, new_y)
    # plt.show()
    ###########################################################################################
    new_y_list_y_z = []
    new_z_list_y_z = []

    index_list_y_z = []
    # plt.scatter(y_list, z_list)
    # plt.show()

    for dup in sorted(list_duplicates(y_list)):
        index = dup[int(len(dup) / 2)]
        index_list_y_z.append(index)

    for index in index_list_y_z:
        new_y_list_y_z.append(y_list[index])
        new_z_list_y_z.append(z_list[index])

    # plt.scatter(new_y_list_y_z, new_z_list_y_z)
    # plt.show()
    poly_y_z = np.polyfit(new_y_list_y_z,
                          new_z_list_y_z, degree)
    plo_y_z = np.poly1d(poly_y_z)
    new_y = np.linspace(min(new_y_list_y_z), max(new_y_list_y_z) + 100, 3000)
    new_z = plo_y_z(new_y)
    # plt.plot(new_y_list_y_z, new_z_list_y_z, "o", new_y, new_z)
    # plt.show()
    ############################################################################################
    new_x_list_x_z = []
    new_z_list_x_z = []

    index_list_x_z = []
    # plt.scatter(x_list, z_list)
    # plt.show()

    for dup in sorted(list_duplicates(z_list)):
        index = dup[int(len(dup) / 2)]
        index_list_x_z.append(index)

    for index in index_list_x_z:
        new_x_list_x_z.append(x_list[index])
        new_z_list_x_z.append(z_list[index])

    # plt.scatter(new_x_list_x_z, new_z_list_x_z)
    # plt.show()
    poly_x_z = np.polyfit(new_x_list_x_z,
                          new_z_list_x_z, degree)
    plo_x_z = np.poly1d(poly_x_z)
    new_x = np.linspace(min(new_x_list_x_z), max(new_x_list_x_z) + 100, 3000)
    new_z = plo_x_z(new_x)
    # plt.plot(new_x_list_x_z, new_z_list_x_z, "o", new_x, new_z)
    # plt.show()
    for x in x_list:
        y = plo_x_y(x)
        z = plo_y_z(y)
        point = [x, y, z]
        new_points_list.append(point)
        change_colors.append(color)
    ##################################################################
    new_points = np.asarray(new_points_list)
    new_pcd = pv.PolyData(new_points)
    new_pcd['colors'] = change_colors
    # new_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)

    plo_list = [plo_x_y, plo_y_z, plo_x_z]

    return new_points, change_colors, plo_list


def compile_cable_pcd(black_new_points, black_change_colors, red_new_points, red_change_colors, white_new_points, white_change_colors):

    new_points_list = []
    change_colors = []
    for i, points in enumerate(red_new_points):
        new_points_list.append(points)
        change_colors.append(red_change_colors[i])
    for i, points in enumerate(black_new_points):
        new_points_list.append(points)
        change_colors.append(black_change_colors[i])
    for i, points in enumerate(white_new_points):
        new_points_list.append(points)
        change_colors.append(white_change_colors[i])
    new_points = np.asarray(new_points_list)
    new_pcd = pv.PolyData(new_points)
    new_pcd['colors'] = change_colors
    # print(new_points)
    # new_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)

    return new_pcd, new_points, change_colors

# Point CLoudから青板の部分だけを取る
# cube_boundary=[cube_boundary_bottom=-0.215, cube_boundary_top=-0.205,
#               cube_boundary_back=-0.025,cube_boundary_front=0.091,
#               cube_boundary_right=-0.055, cube_boundary_left=0.049]


def isolate_board(pcd, cube_boundary=[-0.215, -0.205, -0.025, 0.091, -0.055, 0.0495]):
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)
    new_points = []
    new_colors = []
    for i, point in enumerate(points):
        if point[2] > cube_boundary[0] and point[2] < cube_boundary[1] and point[0] > cube_boundary[2] and point[0] < cube_boundary[3] and point[1] > cube_boundary[4] and point[1] < cube_boundary[5]:

            new_colors.append(colors[i])
            new_points.append(point)

    new_points = np.asarray(new_points)
    new_pcd = pv.PolyData(new_points)

    new_pcd['colors'] = new_colors
    # new_pcd.plot(scalars='colors', rgb=True, eye_dome_lighting=True)
    # o3d.visualization.draw_geometries([pcd])

    return new_pcd, new_points, new_colors


def alter_pcd(pcd, scalar):

    pcd = pcd.scale(scalar, [0, 0, 0])

    return pcd


def add_color_to_pcd(pcd, change_colors):

    pcd.colors = o3d.utility.Vector3dVector(change_colors)
    # o3d.visualization.draw_geometries([pcd])

    return pcd


def point_cloud_correction(predict_img, rgbd, pinhole_camera_intrinsic):
    blank_img = np.zeros((720, 1280, 3), np.uint8)
    predict_img = cv2.resize(predict_img, (600, 500),
                             interpolation=cv2.INTER_NEAREST)
    blank_img[100:600, 100:700] = predict_img  # 画像をリサイズしてもとの画像のピクセル範囲に合わす

    black_pixels = np.argwhere(blank_img[:, :, 1] == 128)  # black
    red_pixels = np.argwhere(blank_img[:, :, 2] == 128)  # red
    white_pixels = np.argwhere(blank_img[:, :, 0] == 128)  # white
    pcd = special_wire_filter(black_pixels, red_pixels,
                              white_pixels, rgbd, pinhole_camera_intrinsic)  # ピクセルの位置を取ってｐｃｄのポイントと合わしてpcdを作成する

    pcd = alter_pcd(pcd, 1000)  # pcdをスケールする

    new_pcd, new_points, new_colors = exctract_cable(
        pcd, rgbd)  # pcdからケーブルの範囲を別にする
    pcd_list, pcd_points_list = isolate_wires(
        new_points, new_colors)  # 分けたｐｃｄスペースからケーブルの部分だけ取る

    # 一つずつのケーブルのpcdを扱う
    red_new_points, red_change_colors, red_plo_list = remove_pcd_point_outliers(
        pcd_points_list, degree=2)
    white_new_points, white_change_colors, white_plo_list = remove_pcd_point_outliers(
        pcd_points_list, color="white", degree=3)
    black_new_points, black_change_colors, black_plo_list = remove_pcd_point_outliers(
        pcd_points_list, color="black", degree=3)
    new_pcd, new_points, change_colors = compile_cable_pcd(
        black_new_points, black_change_colors, red_new_points, red_change_colors, white_new_points, white_change_colors)

    # pcdの保存とopen3Dに変換
    new_pcd.save("F:/18HCI01/pcd/exp/cable.ply")
    pcd = o3d.io.read_point_cloud("F:/18HCI01/pcd/exp/cable.ply")

    pcd = add_color_to_pcd(
        pcd, change_colors)

    cable_plo_list = [black_plo_list, white_plo_list, red_plo_list]
    points_list = [black_new_points, white_new_points, red_new_points]
    pixel_list = create_pixel_points_list(
        points_list, pinhole_camera_intrinsic)

    return pixel_list, points_list, new_pcd, pcd, cable_plo_list


def pointToPicel(point, z, c, f):

    pixel = int((point * f / z) + c)

    return pixel


def point_to_pixel(point, camera_intrinsic):

    fx = camera_intrinsic.intrinsic_matrix[0][0]
    fy = camera_intrinsic.intrinsic_matrix[1][1]
    cx = camera_intrinsic.intrinsic_matrix[0][2]
    cy = camera_intrinsic.intrinsic_matrix[1][2]
    x = point[0]
    y = point[1]
    depthNum = point[2]
    pixelX = pointToPicel(x, depthNum, cx, fx)
    pixelY = pointToPicel(y, depthNum, cy, fy)

    pixel = [pixelX, pixelY, depthNum]

    return pixel


def create_pixel_points_list(new_points, camera_intrinsic):
    pixel_list = []
    for colored_points in new_points:
        for points in colored_points:
            # print(points)
            pixel = point_to_pixel(points, camera_intrinsic)
            pixel_list.append(pixel)

    return pixel_list


if __name__ == '__main__':
    # rls = Realsense()
    # sS = SS()

    # img, use_pcd, rgbd, _, pinhole_camera_intrinsic = rls.single_shot()  # 撮影する

    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # img = Image.fromarray(img)
    # predict_img = sS.predict(img)  # 推論する
    # pixel_list, points_list, new_pcd, pcd, cable_plo_list = point_cloud_correction(
    #     predict_img, rgbd, pinhole_camera_intrinsic)
    # pcd = o3d.io.read_point_cloud("F:/18HCI01/pcd/exp/original_pcd.ply")
    # o3d.visualization.draw_geometries([pcd])
    # pcd = o3d.io.read_point_cloud("F:/18HCI01/pcd/exp/exp.ply")
    # o3d.visualization.draw_geometries([pcd])

    # pcd = o3d.io.read_point_cloud(
    #     "F:/18HCI01/pcd/exp20210115/20210115133055/20210115_133114_562537_z_496_disparityShift_215.ply")
    # o3d.visualization.draw_geometries([pcd])
