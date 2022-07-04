from modules.Input.input import Input
from pynput.keyboard import Key, Listener
import keyboard
import math


class Keyboard(Input):

    def __init__(self, currentIns, coordinateControllerIns, connectionControllerIns):
        self.currentIns = currentIns
        self.coordinateControllerIns = coordinateControllerIns
        self.connectionControllerIns = connectionControllerIns

    # イベントハンドラの信号受信準備完了

    def start_lisner(self):
        def press(key):  # ボタン押下時の処理　イベントハンドラの使用上同スコープに関数を用意する必要あり

            if key == Key.enter:
                if self.currentIns.coordinate_mode == "直交" and self.currentIns.data_mode == "MXT":
                    self.connectionControllerIns.send()  # 現在位置を取得
                    print("現在位置取得")

                    print("self.currentIns.firstFlag",
                          self.currentIns.firstFlag)
                    print("Keyboardインスタンス内 self.currentIns.currentPosition",
                          self.currentIns.currentPosition)
                    print("a", math.degrees(
                        self.currentIns.currentPosition[3]))
                    print("b", math.degrees(
                        self.currentIns.currentPosition[4]))
                    print("c", math.degrees(
                        self.currentIns.currentPosition[5]))
                    # print(self.currentIns.currentPosition)
                    self.firstFlag = False
                # TODO JOINTモードなどの時の処理も実装する

                elif self.currentIns.data_mode == "realTimeMonitor":
                    self.connectionControllerIns.send()
                    if self.currentIns.monitoringFlag == False:
                        self.currentIns.monitoringFlag = True
                        print("モニター開始")
                        while self.currentIns.monitoringFlag == True:
                            print(self.currentIns.nextPosition)
                    else:
                        self.currentIns.monitoringFlag = False
                        print("モニター終了")

            elif keyboard.is_pressed("u") == True:
                if self.currentIns.unityFlag == True:
                    pass

            # x軸プラス
            elif key == Key.up and keyboard.is_pressed("x") == True and self.currentIns.firstFlag == False:
                print("x++")
                coordinate = "x"
                movement = 0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, self.currentIns.currentPosition, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # x軸マイナス
            elif key == Key.down and keyboard.is_pressed("x") == True and self.currentIns.firstFlag == False:
                print("x--")
                coordinate = "x"
                movement = -0.1

                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # y軸プラス
            elif key == Key.up and keyboard.is_pressed("y") == True and self.currentIns.firstFlag == False:
                print("y++")
                coordinate = "y"
                movement = 0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # y軸マイナス
            elif key == Key.down and keyboard.is_pressed("y") == True and self.currentIns.firstFlag == False:
                print("y--")
                coordinate = "y"
                movement = -0.1

                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # z軸プラス
            elif key == Key.up and keyboard.is_pressed("z") == True and self.currentIns.firstFlag == False:
                print("z++")
                coordinate = "z"
                movement = 0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # z軸マイナス
            elif key == Key.down and keyboard.is_pressed("z") == True and self.currentIns.firstFlag == False:
                print("z--")
                coordinate = "z"
                movement = -0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # a軸プラス
            elif key == Key.up and keyboard.is_pressed("a") == True and self.currentIns.firstFlag == False:
                print("a++")
                coordinate = "a"
                movement = 0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # a軸マイナス
            elif key == Key.down and keyboard.is_pressed("a") == True and self.currentIns.firstFlag == False:
                print("a--")
                coordinate = "a"
                movement = -0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # b軸プラス
            elif key == Key.up and keyboard.is_pressed("b") == True and self.currentIns.firstFlag == False:
                print("b++")
                coordinate = "b"
                movement = 0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # b軸マイナス
            elif key == Key.down and keyboard.is_pressed("b") == True and self.currentIns.firstFlag == False:
                print("b--")
                coordinate = "b"
                movement = -0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # c軸プラス
            elif key == Key.up and keyboard.is_pressed("c") == True and self.currentIns.firstFlag == False:
                print("c++")
                coordinate = "c"
                movement = 0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

            # c軸マイナス
            elif key == Key.down and keyboard.is_pressed("c") == True and self.currentIns.firstFlag == False:
                print("c--")
                coordinate = "c"
                movement = -0.1
                self.coordinateControllerIns.caliculate_coordinate(
                    coordinate, movement)  # 移動する次のポジションを決定
                self.connectionControllerIns.send()  # パケットの作成などは中で行ってくれる
                self.currentIns.updateCurrentPosition()  # 現在位置を更新

        def release(key):  # ボタンを放した時の処理　イベントハンドラの使用上同スコープに関数を用意する必要あり
            pass

        print("keyboard入力受付開始")
        with Listener(
                on_press=press,
                on_release=release) as listener:
            listener.join()

    def on_press(self, key):
        pass

    def on_release(self, key):
        pass
