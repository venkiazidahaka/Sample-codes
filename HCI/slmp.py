import socket


class Slmp():
    # defaultの設定値
    _defaults = {
        "HOST": "192.168.0.39",  # 接続先IPアドレス
        "PORT": 5020,  # 接続先ポート番号
        "BUFSIZE": 4096,  # バッファサイズ
        "subHeader1": 0x50,  # サブヘッダー
        "subHeader2": 0x60,  # サブヘッダー
        "requestNetworkNum": 0x00,  # 要求先ネットワーク番号
        "stationNum": 0xFF,  # 要求先局番
        "requestUnitIOnum1": 0xFF,  # 要求先ユニットI/O番号1
        "requestUnitIOnum2": 0x03,  # 要求先ユニットI/O番号2
        "requestMultiDropNum": 0x00,  # 要求先マルチドロップ局番
    }

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)  # set up default values
        self.__dict__.update(kwargs)  # and update with user overrides
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print(self.__dict__)
        # **kwargsのインスタンス作成サンプル
        #slmp = Slmp(HOST = "192.168.3.24")

    # 接続
    def connect(self):
        self.sock.connect((self.__dict__["HOST"], self.__dict__["PORT"]))
        self.sock.settimeout(3)
        print("接続完了")

    # 接続終了

    def disconnect(self):
        self.sock.close()
        print("接続終了")

    # 読み込み
    def read(self, device, device_count=1):

        device_type = device[0]
        device_number = int(device[1:])

        # 引数例外処理
        try:
            assert 0 < device_number, "デバイス番号は0以上の値を入力してください"
            assert device_number < 65535, "デバイス番号は65535以下の値を入力してください"
            assert device_count in [1, 2], "デバイスカウントは１または2を入力してください"
            assert device_type in ["M", "X", "Y", "B", "V", "L", "W", "D", "T", "C", "m", "x",
                                   "y", "b", "v", "l", "d", "t", "c"], "read関数ではM,D,X,Y,B,T,V,L,W以外のデバイスは現在対応していません"
        except AssertionError as err:
            print('AssertionError :', err)
            return 0

        # データ長初期化(後で決定)
        dataLength1 = 0
        dataLength2 = 0

        # デバイス番号の電文を作成
        device_number_1 = 0x00
        device_number_2 = 0x00
        device_number_3 = 0x00
        hex_device_number = hex(device_number)
        if 65535 < device_number:
            device_number_3 = int("0x"+hex_device_number[2:4], 16)
            device_number_2 = int("0x"+hex_device_number[4:6], 16)
            device_number_1 = int("0x"+hex_device_number[6:], 16)
        elif 4095 < device_number and device_number <= 65535:
            device_number_2 = int("0x"+hex_device_number[2:4], 16)
            device_number_1 = int("0x"+hex_device_number[4:], 16)
        elif 255 < device_number and device_number <= 4095:
            device_number_2 = int("0x"+hex_device_number[2:3], 16)
            device_number_1 = int("0x"+hex_device_number[3:], 16)
        elif device_number < 255:
            device_number_1 = int("0x"+hex_device_number[2:], 16)

        # サブコマンド・デバイスコード決定
        if device_type == "M" or device_type == "m":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x90
        elif device_type == "X" or device_type == "x":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x9C
        elif device_type == "Y" or device_type == "y":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x9D
        elif device_type == "L" or device_type == "l":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x92
        elif device_type == "F" or device_type == "f":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x93
        elif device_type == "V" or device_type == "v":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x94
        elif device_type == "B" or device_type == "b":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0xA0
        elif device_type == "D" or device_type == "d":
            subcommand1 = 0x00
            subcommand2 = 0x00
            device_code = 0xA8
        elif device_type == "T" or device_type == "t":
            subcommand1 = 0x00
            subcommand2 = 0x00
            device_code = 0xC2
        elif device_type == "C" or device_type == "c":
            subcommand1 = 0x00
            subcommand2 = 0x00
            device_code = 0xC5

        # 電文を作成
        data = [
            self.__dict__["subHeader1"], self.__dict__["subHeader2"],  # サブヘッダー
            self.__dict__["requestNetworkNum"],  # 要求先ネットワーク番号
            self.__dict__["stationNum"],  # 要求先局番
            self.__dict__["requestUnitIOnum1"], self.__dict__[
                "requestUnitIOnum2"],  # 要求先ユニットI/O番号
            self.__dict__["requestMultiDropNum"],
            dataLength1, dataLength2,      # 要求データ長 (後で設定)
            0x20, 0x00,      # 監視タイマ
            0x01, 0x04,      # コマンド
            # サブコマンド   0x00,0x00 →ワードデバイスから読み込む　　　　0x01,0x00 →ビットデバイスから読み込む
            subcommand1, subcommand2,
            # 先頭デバイス番号  0x01,0x00,0x00  →D001から読み込んでいる
            device_number_1, device_number_2, device_number_3,
            device_code,           # デバイスコード    A8→デバイスコードD
            device_count, 0x00       # デバイス点数
        ]

        # データ長決定
        # ビット演算子で長さを決めている　&の両辺を二進数に変えて両方が1のものが　＝の左辺となる
        data[7] = len(data[9:]) & 0xFF
        data[8] = (len(data[9:]) >> 16) & 0xFF

        # 送信
        self.sock.send(bytes(data))

        # 読み込み値を受信
        res = self.sock.recv(self.__dict__["BUFSIZE"])

        # 読み込んだ値を10進数に変換
        return_value = [format(i, '02X') for i in res]
        # ワードデバイス
        # デバイスD
        if device_type == "D" or device_type == "d":
            output = ""
            # 10進数に変換　マイナスの値(最後のビットがON)も考慮に入れる
            for i in range(device_count):
                n = 2 * i
                for k in range(2):
                    output = output + return_value[(-1 - k) - n]
            output = int("0x" + output, 16)
            if device_count == 1:
                sign_conp = output & 0x8000
                if sign_conp == 0:
                    pass
                else:
                    # print(output)
                    output = -32768 + (-32768 + output)
            elif device_count == 2:
                sign_conp = output & 0x80000000
                if sign_conp == 0:
                    pass
                else:
                    # print(output)
                    output = -2147483648 + (-2147483648 + output)

        # デバイスT ※タイマーは現在時間を取得している
        if device_type == "T" or device_type == "t":
            output = ""
            # 10進数に変換　
            for i in range(device_count):
                n = 2 * i
                for k in range(2):
                    output = output + return_value[(-1 - k) - n]
            output = int("0x" + output, 16)

        # デバイスC #カウンターは現在カウント数を取得している
        if device_type == "C" or device_type == "c":
            output = ""
            # 10進数に変換　
            for i in range(device_count):
                n = 2 * i
                for k in range(2):
                    output = output + return_value[(-1 - k) - n]
            output = int("0x" + output, 16)

        # ビットデバイス
        if device_type == "M" or device_type == "m":
            if return_value[-1] == "10":
                output = 1
            else:
                output = 0
        elif device_type == "X" or device_type == "x":
            if return_value[-1] == "10":
                output = 1
            else:
                output = 0
        elif device_type == "Y" or device_type == "y":
            if return_value[-1] == "10":
                output = 1
            else:
                output = 0
        elif device_type == "L" or device_type == "l":
            if return_value[-1] == "10":
                output = 1
            else:
                output = 0
        elif device_type == "F" or device_type == "f":
            if return_value[-1] == "10":
                output = 1
            else:
                output = 0
        elif device_type == "V" or device_type == "v":
            if return_value[-1] == "10":
                output = 1
            else:
                output = 0
        elif device_type == "B" or device_type == "b":
            if return_value[-1] == "10":
                output = 1
            else:
                output = 0

        return output

    # 書き込み
    def write(self, device, value, device_count=1):
        device_type = device[0]
        device_number = int(device[1:])

        # 引数例外処理
        try:
            assert 0 < device_number, "デバイス番号は0以上の値を入力してください"
            assert device_number < 65535, "デバイス番号は65535以下の値を入力してください"
            assert device_count in [1, 2], "デバイスカウントは１または2を入力してください"
            assert device_type in ["M", "D", "X", "Y", "B", "T", "V", "L", "W", "m", "d", "x",
                                   "y", "b", "t", "v", "l", "e"], "write関数ではM,D,X,Y,B,T,V,L,W以外のデバイスは現在対応していません"
            if device_count == 1:
                assert value < 65535, "書き込める値は-32768以上、65535以下の値です "
                assert -32769 < value, "書き込める値は-32768以上、65535以下の値です "
            elif device_count == 2:
                assert value < 4294967295, "書き込める値は-2147483648以上、4294967294以下の値です "
                assert -2147483649 < value, "書き込める値は-2147483648以上、4294967294以下の値です "
        except AssertionError as err:
            print('AssertionError :', err)
            return 0

        # データ長初期化(後で決定)
        dataLength1 = 0
        dataLength2 = 0

        # デバイス番号の電文を作成
        device_number_1 = 0x00
        device_number_2 = 0x00
        device_number_3 = 0x00
        hex_device_number = hex(device_number)
        if 65535 < device_number:
            device_number_3 = int("0x"+hex_device_number[2:4], 16)
            device_number_2 = int("0x"+hex_device_number[4:6], 16)
            device_number_1 = int("0x"+hex_device_number[6:], 16)
        elif 4095 < device_number and device_number <= 65535:
            device_number_2 = int("0x"+hex_device_number[2:4], 16)
            device_number_1 = int("0x"+hex_device_number[4:], 16)
        elif 255 < device_number and device_number <= 4095:
            device_number_2 = int("0x"+hex_device_number[2:3], 16)
            device_number_1 = int("0x"+hex_device_number[3:], 16)
        elif device_number < 255:
            device_number_1 = int("0x"+hex_device_number[2:], 16)

        # 送信する値の電文を作成
        if device_type == "D":
            # 32ビットか　16ビットかによってマイナス符号のビット番号を変更
            # マイナスの値の場合はすべてのビットを反転させる必要がある
            if device_count == 1:
                if value < 0:
                    hex_value = 32768 + 32768 - abs(value)
                else:
                    hex_value = value
            else:
                if value < 0:
                    hex_value = 4294967296 - abs(value)
                else:
                    hex_value = value
            str_hex_value = hex(hex_value)

            # 送信する値の電文を作成
            # デバイスが16ビットの場合
            if device_count == 1:
                value_number_1 = 0x00
                value_number_2 = 0x00
                # 電文の値によって使用する電文のバッファ数を変える
                if 4095 < hex_value and hex_value <= 65535:
                    value_number_2 = int("0x"+str_hex_value[2:4], 16)
                    value_number_1 = int("0x"+str_hex_value[4:], 16)
                elif 255 < hex_value and hex_value <= 4095:
                    value_number_2 = int("0x"+str_hex_value[2:3], 16)
                    value_number_1 = int("0x"+str_hex_value[3:], 16)
                elif hex_value < 255:
                    value_number_1 = int("0x"+str_hex_value[2:], 16)
                value_list = [value_number_1, value_number_2]
            # デバイスが32ビットの場合 device_count は 2の場合
            else:
                value_number_1 = 0x00
                value_number_2 = 0x00
                value_number_3 = 0x00
                value_number_4 = 0x00
                # 8桁
                if 268435455 < hex_value and hex_value <= 4294967295:
                    value_number_4 = int("0x"+str_hex_value[2:4], 16)
                    value_number_3 = int("0x"+str_hex_value[4:6], 16)
                    value_number_2 = int("0x"+str_hex_value[6:8], 16)
                    value_number_1 = int("0x"+str_hex_value[8:], 16)
                # 7桁
                elif 16777215 < hex_value and hex_value <= 268435455:
                    value_number_4 = int("0x"+str_hex_value[2:3], 16)
                    value_number_3 = int("0x"+str_hex_value[3:5], 16)
                    value_number_2 = int("0x"+str_hex_value[5:7], 16)
                    value_number_1 = int("0x"+str_hex_value[7:], 16)
                # 6桁
                elif 1048575 < hex_value and hex_value <= 16777215:
                    value_number_3 = int("0x"+str_hex_value[2:4], 16)
                    value_number_2 = int("0x"+str_hex_value[4:6], 16)
                    value_number_1 = int("0x"+str_hex_value[6:], 16)
                # 5桁
                elif 65535 < hex_value and hex_value <= 1048575:
                    value_number_3 = int("0x"+str_hex_value[2:3], 16)
                    value_number_2 = int("0x"+str_hex_value[3:5], 16)
                    value_number_1 = int("0x"+str_hex_value[5:], 16)
                # 4桁
                if 4095 < hex_value and hex_value <= 65535:
                    value_number_2 = int("0x"+str_hex_value[2:4], 16)
                    value_number_1 = int("0x"+str_hex_value[4:], 16)
                    print(value_number_2)
                # 3桁
                elif 255 < hex_value and hex_value <= 4095:
                    value_number_2 = int("0x"+str_hex_value[2:3], 16)
                    value_number_1 = int("0x"+str_hex_value[3:], 16)
                # 2桁 & 1桁
                elif hex_value < 255:
                    value_number_1 = int("0x"+str_hex_value[2:], 16)
                value_list = [value_number_1, value_number_2,
                              value_number_3, value_number_4]

        # ビットデバイス
        if device_type == "M":
            if value == 1:
                value_list = [0x10]
            else:
                value_list = [0x00]
        elif device_type == "X":
            if value == 1:
                value_list = [0x10]
            else:
                value_list = [0x00]
        elif device_type == "Y":
            if value == 1:
                value_list = [0x10]
            else:
                value_list = [0x00]
        elif device_type == "L":
            if value == 1:
                value_list = [0x10]
            else:
                value_list = [0x00]
        elif device_type == "V":
            if value == 1:
                value_list = [0x10]
            else:
                value_list = [0x00]
        elif device_type == "B":
            if value == 1:
                value_list = [0x10]
            else:
                value_list = [0x00]

        # サブコマンド デバイスコードの決定
        if device_type == "M" or device_type == "m":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x90
        elif device_type == "X" or device_type == "x":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x9C
        elif device_type == "Y" or device_type == "y":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x9D
        elif device_type == "L" or device_type == "l":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x92
        elif device_type == "F" or device_type == "f":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x93
        elif device_type == "V" or device_type == "v":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0x94
        elif device_type == "B" or device_type == "b":
            subcommand1 = 0x01
            subcommand2 = 0x00
            device_code = 0xA0
        elif device_type == "D" or device_type == "d":
            subcommand1 = 0x00
            subcommand2 = 0x00
            device_code = 0xA8
        elif device_type == "T" or device_type == "t":
            subcommand1 = 0x00
            subcommand2 = 0x00
            device_code = 0xC2
        elif device_type == "C" or device_type == "c":
            subcommand1 = 0x00
            subcommand2 = 0x00
            device_code = 0xC5

        # 電文の作成
        data = [
            self.__dict__["subHeader1"], self.__dict__["subHeader2"],  # サブヘッダー
            self.__dict__["requestNetworkNum"],  # 要求先ネットワーク番号
            self.__dict__["stationNum"],  # 要求先局番
            self.__dict__["requestUnitIOnum1"], self.__dict__[
                "requestUnitIOnum2"],  # 要求先ユニットI/O番号
            self.__dict__["requestMultiDropNum"],
            dataLength1, dataLength2,      # 要求データ長 (後で設定)
            0x20, 0x00,      # 監視タイマ
            0x01, 0x14,      # コマンド
            # サブコマンド   0x00,0x00 →ワードデバイスから読み込む　　　　0x01,0x00 →ビットデバイスから読み込む
            subcommand1, subcommand2,
            # 先頭デバイス番号  0x01,0x00,0x00  →D001から読み込んでいる
            device_number_1, device_number_2, device_number_3,
            device_code,           # デバイスコード    A8→デバイスコードD
            device_count, 0x00,       # デバイス点数
        ]
        for values in value_list:
            data.append(values)

       # データ長決定
        # ビット演算子で長さを決めている　&の両辺を二進数に変えて両方が1のものが　＝の左辺となる
        data[7] = len(data[9:]) & 0xFF
        data[8] = (len(data[9:]) >> 16) & 0xFF

        # 送信
        self.sock.send(bytes(data))

        # 受信 送信時もSLMPの仕様で受信が必要
        self.sock.recv(self.__dict__["BUFSIZE"])

        return 0


# test SLMP
if __name__ == "__main__":
    ins = Slmp()
    ins.connect()
    # print(ins.write("D2000",-10000))
    print(ins.read("C5"))
    # print(bin(10))
    # print(hex())
    # print(0x1630)
