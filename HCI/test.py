from waitress import serve
import os
from datetime import datetime
import json
import math
from modules import logger
from modules import config as cfg
from modules.pudu_connect import PUDUBOT, BELLABOT
from modules.operations import Operations
from multiprocessing import Process, process, Value, Array, Manager
from modules.connection import KAWASAKI_CLIENT
import requests
from flask import Flask, request
import numpy as np
from glob import glob
import time
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
from dotenv import load_dotenv
load_dotenv()

TSI1M1LP = {"x": -4.89,
            "y": 0.90,
            "angle": 2.13}  # Tray_SingleItem1_Main1_Load_Point

SpSI2M2LP = {"x": -3.77,
             "y": 0.88,
             "angle": 1.57}  # Soup_SingleItem2_Main2_Load_Point

SDLP = {"x": -1.00,
        "y": 0.72,
        "angle": 1.52}  # Salad_Desert_Load_Point

CP1 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_1

CP2 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_2

CP3 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_3

CP4 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_4

CP5 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_5

CP6 = {"x": -0.98,
        "y": -0.04,
        "angle": 1.55}  # Check_Point_6

CP7 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_7

CP8 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_8

CP9 = {"x": 0,
       "y": 0,
       "angle": 0}  # Check_Point_9

CP10 = {"x": 0,
        "y": 0,
        "angle": 0}  # Check_Point_10

PD1_ChP = {"x": 0,
           "y": 0,
           "angle": 0}  # PuduBot1_Charge_point

PD2_ChP = {"x": 0,
           "y": 0,
           "angle": 0}  # PuduBot2_Charge_point

PD3_ChP = {"x": 0,
           "y": 0,
           "angle": 0}  # PuduBot3_Charge_point

PD4_ChP = {"x": 0,
           "y": 0,
           "angle": 0}  # PuduBot4_Charge_point

PD5_ChP = {"x": 0,
           "y": 0,
           "angle": 0}  # PuduBot5_Charge_point

PD6_ChP = {"x": 0,
           "y": 0,
           "angle": 0}  # PuduBot6_Charge_point

#-------------------------------------------#
#-----シャッター前待機位置-------------------#
#-------------------------------------------#
D1 = {"x": 0,
      "y": 0,
      "angle": 0}

D2 = {"x": 0,
      "y": 0,
      "angle": 0}

ks1 = KAWASAKI_CLIENT()
ks2 = KAWASAKI_CLIENT()
ks3 = KAWASAKI_CLIENT()

pd1_order_bound_flag = 0
pd2_order_bound_flag = 0
pd3_order_bound_flag = 0
pd4_order_bound_flag = 0
pd5_order_bound_flag = 0
pd6_order_bound_flag = 1

nk1_busy_flag = 0
nk2_busy_flag = 0

nk_delivery_flag = 0

pd1_available_flag = 1
pd2_available_flag = 1
pd3_available_flag = 1
pd4_available_flag = 1
pd5_available_flag = 1
pd6_available_flag = 1

kitchen_enter_exit_checkpoint_busy_flag = 0
kitchen_enter_exit_wait_checkpoint_busy_flag = 0
kitchen_path_busy_flag = 0

main_wait_busy_flag = 0
main_busy_flag = 0

salad_dessert_wait_busy_flag = 0
salad_dessert_busy_flag = 0

single_item1_wait_busy_flag = 0
single_item1_busy_flag = 0

soup_wait_busy_flag = 0
soup_busy_flag = 0 

show_status_flag = 0

api_sever_active_flag = 1


def food_pickup(pd_instance, robot1, robot2, robot3, order_dic, i):
    """Food pickup operation"""
    print("Starting food pickup")
    global main_wait_busy_flag
    global main_busy_flag

    global salad_dessert_wait_busy_flag
    global salad_dessert_busy_flag

    global api_sever_active_flag

    global kitchen_enter_exit_checkpoint_busy_flag

    dest_dic = pd_instance.get_destinations()

    pd_instance.call_robot(dest_dic, dest_name = "CP8")
    
    while main_busy_flag != 0:
        pd_instance.call_robot(dest_dic, dest_name = "CP8")
        time.sleep(0.5)

    main_busy_flag = 0
    ##########################################################################
    #-------------------------メイン-----------------------------------------#
    ##########################################################################

    salad_dic = order_dic["Salads"]
    main_dic = order_dic["Mains"]
    main1=main_dic["M1"]
    main2=main_dic["M2"]

    enter_kitchen(pd_instance = pd_instance)

    robot1.connect()
    robot1.send(str(i))
    print(str(i))
    robot1.disconnect()
    robot1.open()

    robot2.connect()
    robot2.send(str(i))
    print(str(i))
    robot2.disconnect()
    robot2.open()

    main1_pickup(pd_instance = pd_instance,
                kawasaki_instance = robot1, main1 = main1)

    safety_check(robot = robot2)

    main2_pickup(pd_instance = pd_instance,
                kawasaki_instance = robot2, main2 = main2)
    
    main_busy_flag = 0
    ##########################################################################
    #-------------------------サラダ-----------------------------------------#
    ##########################################################################
    while salad_dessert_busy_flag != 0:
        pd_instance.call_robot(dest_dic, dest_name = "SpSI2M2LP")
        time.sleep(0.5)

    salad_dessert_busy_flag = 1

    salad_pickup(pd_instance = pd_instance,
                    kawasaki_instance = robot3, salad_dic = salad_dic)

    salad_dessert_busy_flag = 0

    salad_exit_kitchen(pd_instance = pd_instance)


def food_delivery(pd_instance, table):

    global nk1_busy_flag
    global nk2_busy_flag
    global nk_delivery_flag

    pickup_point = pd_instance.home

    if nk_delivery_flag == 1:
        data = pickup_point+table
        while True:
            if nk1_busy_flag == 0:

                nk1_busy_flag = 1
                requests.post(url=nyokkey_url+"/nk1", data=data)
                nk1_busy_flag = 0

                return "nyokkey1 in charge of delivery"

            if nk2_busy_flag == 0:

                nk2_busy_flag = 1
                requests.post(url=nyokkey_url+"/nk2", data=data)
                nk2_busy_flag = 0

                return "nyokkey2 in charge of delivery"


def outside_door(pd_instance, door_wait_time=0.2):
    """Stop in front of the kitchen exit door for 5s and go to the nearest check-point"""
    #################################################################
    #-------------------------------------------#
    #-------------シャッター1の動作--------------#
    #-------------------------------------------#
    #################################################################
    dest_dic = pd_instance.get_destinations()
    pd_instance.call_robot(dest_dic, dest_name="D2")
    robot_not_arrived = check_robot_arrived(pd_instance, D2)

    while robot_not_arrived:
        pd_instance.call_robot(dest_dic, dest_name="D2")
        robot_not_arrived = check_robot_arrived(pd_instance, D2)
        time.sleep(0.5)
        count = count+1

    time.sleep(door_wait_time)

    pd_instance.call_robot(dest_dic, dest_name="CP1")
    robot_not_arrived = check_robot_arrived(pd_instance, CP1)

    while robot_not_arrived:
        pd_instance.call_robot(dest_dic, dest_name="CP1")
        robot_not_arrived = check_robot_arrived(pd_instance, CP1)
        time.sleep(0.5)

def check_robot_arrived(pd_instance, point, threshold=0.1, angle_threshold=0.175):
    """Check if robot has arrived in certain range of given position"""
    _, _, _, robot_pos = pd_instance.get_robot_status()

    x_diff = robot_pos["x"]-point["x"]
    y_diff = robot_pos["y"]-point["y"]

    distance = abs(math.sqrt((x_diff)**2)+((y_diff)**2))
    angle_diff = abs(robot_pos["angle"]-point["angle"])

    if distance < threshold and angle_diff < angle_threshold:
        robot_not_arrived = False
    else:
        robot_not_arrived = True

    return robot_not_arrived

def salad_exit_kitchen(pd_instance):
    """Enter the kitchen after loading salads"""
    
    global kitchen_enter_exit_checkpoint_busy_flag
    global kitchen_path_busy_flag
    global salad_dessert_busy_flag

    dest_dic = pd_instance.get_destinations()

    pd_instance.call_robot(dest_dic, dest_name="SDLP")
    while kitchen_enter_exit_checkpoint_busy_flag != 0:    
        time.sleep(1)

    pd_instance.call_robot(dest_dic, dest_name="CP6")
    kitchen_enter_exit_checkpoint_busy_flag = 1
    salad_dessert_busy_flag = 0

    pd_instance.call_robot(dest_dic, dest_name="CP10")
    time.sleep(5)
    kitchen_enter_exit_checkpoint_busy_flag = 0
    while kitchen_path_busy_flag != 0:
        time.sleep(0.5)
    
    pd_instance.call_robot(dest_dic, dest_name=pd_instance.home)
    print("Exiting kitchen")

def enter_kitchen(pd_instance):
    """Enter the kitchen"""
    print("Entering kitchen")
    global kitchen_enter_exit_checkpoint_busy_flag
    global kitchen_enter_exit_wait_checkpoint_busy_flag
    global kitchen_path_busy_flag

    dest_dic = pd_instance.get_destinations()
    
    # pd_instance.call_robot(dest_dic, dest_name=pd_instance.home)

    while kitchen_enter_exit_wait_checkpoint_busy_flag == 1:
        print("CP8 busy")
        time.sleep(1)
    
    pd_instance.call_robot(dest_dic, dest_name="CP8")
    kitchen_enter_exit_wait_checkpoint_busy_flag = 1

    while kitchen_enter_exit_checkpoint_busy_flag == 1:
        print("CP6 busy")
        time.sleep(1)

    kitchen_path_busy_flag = 1
    time.sleep(1)
    pd_instance.call_robot(dest_dic, dest_name="CP6")
    kitchen_enter_exit_wait_checkpoint_busy_flag = 0

    robot_not_arrived = check_robot_arrived(pd_instance, CP6)
    while robot_not_arrived:
        print("Calling CP6")
        robot_not_arrived = check_robot_arrived(pd_instance, CP6,threshold=0.5,angle_threshold=0.5)
        time.sleep(1)
        pd_instance.call_robot(dest_dic, dest_name="CP6")
    
    kitchen_path_busy_flag = 0
    kitchen_enter_exit_checkpoint_busy_flag = 1

    pd_instance.call_robot(dest_dic, dest_name="CP1")
    kitchen_enter_exit_checkpoint_busy_flag = 0

def main1_pickup(pd_instance, kawasaki_instance, main1):
    """Pick up main1 from the main1 load point"""
    dest_dic = pd_instance.get_destinations()
    #################################################################
    #-------------------------------------------#
    #-------------メイン１の動作-----------------#
    #-------------------------------------------#
    #################################################################
    pd_instance.call_robot(dest_dic, dest_name="TSI1M1LP")
    robot_not_arrived = check_robot_arrived(pd_instance, TSI1M1LP)

    while robot_not_arrived:
        pd_instance.call_robot(dest_dic, dest_name="TSI1M1LP")
        robot_not_arrived = check_robot_arrived(pd_instance, TSI1M1LP)
        time.sleep(0.5)

    kawasaki_instance.connect()

    kawasaki_instance.send("M1LPA")
    print("M1LPA")
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "M1D":
        data = kawasaki_instance.recv()

    kawasaki_instance.send(main1)
    print(main1)
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "M1R":
        data = kawasaki_instance.recv()

    kawasaki_instance.send("M1L")
    print("M1L")
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "M1LO":
        data = kawasaki_instance.recv()

    kawasaki_instance.disconnect()
    kawasaki_instance.open()

def singleitem1_pickup(pd_instance, kawasaki_instance, singleitem1_dic):
    """Pick up singleitem1 from the singleitem1 load point"""
    dest_dic = pd_instance.get_destinations()
    #################################################################
    #-------------------------------------------#
    #---------------単品１の動作-----------------#
    #-------------------------------------------#
    #################################################################
    pd_instance.call_robot(dest_dic, dest_name="TSI1M1LP")
    robot_not_arrived = check_robot_arrived(pd_instance, TSI1M1LP)

    while robot_not_arrived:
        pd_instance.call_robot(dest_dic, dest_name="TSI1M1LP")
        robot_not_arrived = check_robot_arrived(pd_instance, TSI1M1LP)
        time.sleep(0.5)

    kawasaki_instance.connect()

    kawasaki_instance.send("SI1LPA")
    data = kawasaki_instance.recv()
    while data.decode("utf-8") != "SI1D":
        data = kawasaki_instance.recv()

    for singleitem1 in singleitem1_dic.keys():
        kawasaki_instance.send(singleitem1)
        data = kawasaki_instance.recv()
        while data.decode("utf-8") != "SI1C":
            data = kawasaki_instance.recv()

        kawasaki_instance.send(singleitem1_dic[singleitem1])
        data = kawasaki_instance.recv()
        while data.decode("utf-8") != "SI1D":
            data = kawasaki_instance.recv()

    kawasaki_instance.send("SI1O")
    data = kawasaki_instance.recv()

    while data.decode("utf-8") != "SI1R":
        data = kawasaki_instance.recv()

    kawasaki_instance.send("SI1L")
    data = kawasaki_instance.recv()

    while data.decode("utf-8") != "SI1LO":
        data = kawasaki_instance.recv()

    kawasaki_instance.disconnect()
    kawasaki_instance.open()

def main2_pickup(pd_instance, kawasaki_instance, main2):
    """Pick up main2 from the main2 load point"""
    dest_dic = pd_instance.get_destinations()
    #################################################################
    #-------------------------------------------#
    #-------------メイン2の動作------------------#
    #-------------------------------------------#
    #################################################################
    pd_instance.call_robot(dest_dic, dest_name="SpSI2M2LP")
    robot_not_arrived = check_robot_arrived(pd_instance, SpSI2M2LP)

    while robot_not_arrived:
        pd_instance.call_robot(dest_dic, dest_name="SpSI2M2LP")
        robot_not_arrived = check_robot_arrived(pd_instance, SpSI2M2LP)
        time.sleep(0.5)

    kawasaki_instance.connect()

    kawasaki_instance.send("M2LPA")
    print("M2LPA")
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "M2D":
        data = kawasaki_instance.recv()

    kawasaki_instance.send(main2)
    print(main2)
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "M2R":
        data = kawasaki_instance.recv()

    kawasaki_instance.send("M2L")
    print("M2l")
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "M2LO":
        data = kawasaki_instance.recv()

    kawasaki_instance.disconnect()
    kawasaki_instance.open()

def salad_pickup(pd_instance, kawasaki_instance, salad_dic):
    """Pick up various salads from the salad load point"""

    dest_dic = pd_instance.get_destinations()
    #################################################################
    #-------------------------------------------#
    #-------------サラダの動作-------------------#
    #-------------------------------------------#
    #################################################################
    pd_instance.call_robot(dest_dic, dest_name="SDLP")
    robot_not_arrived = check_robot_arrived(pd_instance, SDLP)

    while robot_not_arrived:
        pd_instance.call_robot(dest_dic, dest_name="SDLP")
        robot_not_arrived = check_robot_arrived(pd_instance, SDLP)
        time.sleep(0.5)

    time.sleep(2)

    kawasaki_instance.connect()

    kawasaki_instance.send("SLPA")
    print("SLPA")
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "SD":
        data = kawasaki_instance.recv()

    for salad in salad_dic.keys():
        kawasaki_instance.send(salad)
        print(salad)
        data = kawasaki_instance.recv()
        print(data.decode("utf-8"))
        while data.decode("utf-8") != "SD":
            data = kawasaki_instance.recv()

    kawasaki_instance.send("SO")
    print("SO")
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "SR":
        data = kawasaki_instance.recv()

    kawasaki_instance.send("SL")
    print("SL")
    data = kawasaki_instance.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "SLO":
        data = kawasaki_instance.recv()

    kawasaki_instance.disconnect()
    kawasaki_instance.open()

def initialize_robot(name=[], kw_host=[], kw_port=[], pd_home_list=[]):
    """Initialize the robots to be used"""
    global ks1
    ks1.set_host_port(kw_host[0], kw_port[0])

    global ks2
    ks2.set_host_port(kw_host[1], kw_port[1])

    global ks3
    ks3.set_host_port(kw_host[2], kw_port[2])

    global pd1
    pd1 = PUDUBOT()
    pd1.set_robot(name[0])
    pd1.set_home(pd_home_list[0])

    global pd2
    pd2 = PUDUBOT()
    pd2.set_robot(name[1])
    pd2.set_home(pd_home_list[1])

    global pd3
    pd3 = PUDUBOT()
    pd3.set_robot(name[2])
    pd3.set_home(pd_home_list[2])

    global pd4
    pd4 = PUDUBOT()
    pd4.set_robot(name[3])
    pd4.set_home(pd_home_list[3])

    global pd5
    pd5 = PUDUBOT()
    pd5.set_robot(name[4])
    pd5.set_home(pd_home_list[4])

    global pd6
    pd6 = PUDUBOT()
    pd6.set_robot(name[5])
    pd6.set_home(pd_home_list[5])

    global pd_instance_list
    pd_instance_list = [pd1, pd2, pd3, pd4, pd5, pd6]

def robot_arm_server():
    """Connect to the Robo arm Server"""
    global ks1
    ks1.open()

    global ks2
    ks2.open()

    global ks3
    ks3.open()

def safety_check(robot):
    """配膳ロボット動いたら大丈夫かをロボットアーム確認する"""

    robot.connect()

    robot.send("SFC")
    print("SFC")
    data = robot.recv()
    print(data.decode("utf-8"))
    while data.decode("utf-8") != "SFCOK":
        data = robot.recv()

    robot.disconnect()
    robot.open()

def start_cooking(robot1, robot2,order_data):

    global main_busy_flag

    robot1.connect()

    robot1.send("OL")
    data=robot1.recv()
    while data.decode("utf-8") != "OLC":
        data=robot1.recv()
    
    robot1.send(str(len(order_data)))
    print(str(len(order_data)))
    data=robot1.recv()

    for i,order_dic in enumerate(order_data): 
    
        main_dic = order_dic["Mains"]
        name = main_dic["Name"]
        
        while data.decode("utf-8") != str(i):
            data=robot1.recv()
    
        robot1.send(name)

    robot1.disconnect()
    robot1.open()

    robot2.connect()

    robot2.send("OL")
    print("sent OL to robo2")
    data=robot2.recv()
    while data.decode("utf-8") != "OLC":
        data=robot2.recv()
    
    robot2.send(str(len(order_data)))
    print(str(len(order_data)))
    data=robot2.recv()

    for i,order_dic in enumerate(order_data): 
    
        main_dic = order_dic["Mains"]
        name = main_dic["Name"]
        
        while data.decode("utf-8") != str(i):
            data=robot2.recv()
    
        robot2.send(name)

    robot2.disconnect()
    robot2.open()

if __name__ == "__main__":
    kw_host = ["192.168.0.10", "192.168.0.20", "192.168.0.30"]
    kw_port = [8500, 8500, 8500]

    bl_name = ["bellabot1", "bellabot2"]
    name = ["pudubot1", "pudubot2", "pudubot3",
            "pudubot4", "pudubot5", "pudubot6"]
    pd_home_list = ["PD1_home", "PD2_home", "PD3_home", "PD4_home", "PD5_home", "PD6_home"]

    initialize_robot(name=name,
                     kw_host=kw_host, kw_port=kw_port, pd_home_list=pd_home_list)

    robot_arm_server()
    print("Connected to server")
    base_dics = [{"Salads": {"S1": "1"},
                "Mains": {"Name": "CS1V1", "M1": "P1", "M2": "MS1"},
                 "Other": {},
                 },
                 {"Salads": {"S1": "1"},
                "Mains": {"Name": "CS1V1", "M1": "P1", "M2": "MS1"},
                 "Other": {},
                 },
                 {"Salads": {"S1": "1"},
                "Mains": {"Name": "CS1V1", "M1": "P1", "M2": "MS1"},
                 "Other": {},
                 },
                 {"Salads": {"S1": "1"},
                "Mains": {"Name": "CS1V1", "M1": "P1", "M2": "MS1"},
                 "Other": {},
                 }]
    
    # base_dics = [{"Salads": {"S1": "1"},
    #             "Mains": {"Name": "CS1V1", "M1": "P1", "M2": "MS1"},
    #              "Other": {},
    #              },
    #              {"Salads": {"S1": "1"},
    #             "Mains": {"Name": "CS1V1", "M1": "P1", "M2": "MS1"},
    #              "Other": {},
    #              }]

    start_cooking(robot1=ks1,robot2=ks2,order_data=base_dics)

    for i,base_dic in enumerate(base_dics):
        food_pickup(pd_instance=pd6, robot1=ks1, robot2=ks2,
                    robot3=ks3, order_dic=base_dic,i=i)
