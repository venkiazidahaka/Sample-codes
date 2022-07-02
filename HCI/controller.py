from modules.Input.input import Input
from modules.Input.keyboard import Keyboard
from modules.Input.robot import Robot
from modules.Input.commandPrompt import CommandPrompt
from modules.Input.unity import Unity


class Controller():

    def __init__(self, coordinateControllerIns=None, connectionControllerIns=None, connectionControllerIns2=None, inputIns=None, currentIns=None):
        self.coordinateControllerIns = coordinateControllerIns
        self.connectionControllerIns = connectionControllerIns
        self.connectionControllerIns2 = connectionControllerIns2
        self.inputIns = inputIns
        self.currentIns = currentIns

    def start(self):

        if isinstance(self.inputIns, Keyboard) == True or isinstance(self.inputIns, CommandPrompt) == True:  # 入力方式がKeyboardの時の処理
            self.connectionControllerIns.connect()  # 通信を接続
            self.inputIns.start_lisner()
        elif isinstance(self.inputIns, Robot) == True:  # 入力方式がKeyboardの時の処理
            self.connectionControllerIns.connect()  # 通信を接続
            if self.currentIns.connection_mode2 == "webSocket":
                self.connectionControllerIns2.connect()  # 通信を接続
            self.inputIns.start_lisner()
        elif isinstance(self.inputIns, Unity) == True:  # 入力方式がUnityの時の処理
            self.connectionControllerIns.connect()  # 通信を接続
            self.connectionControllerIns2.connect()  # 通信を接続
            self.inputIns.start_lisner()
        else:  # 入力方法がAIの時、Unityの時などのパターンを作る
            self.connectionControllerIns.connect()  # 通信を接続
            self.coordinateControllerIns.caliculate_coordinate("x", 0.1)
            print("keyboardインスタンスに入っていない")
            self.connectionControllerIns.send()

    def stop(self):
        pass
