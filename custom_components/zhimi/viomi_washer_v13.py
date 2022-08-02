# Generated by https://github.com/Yonsm/MiService
# http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:washer:0000A01F:viomi-v13:2

from enum import Enum


class Device_Information:
    Device_Manufacturer = (1, 1)
    Device_Model = (1, 2)
    Device_Serial_Number = (1, 3)
    Current_Firmware_Version = (1, 4)


class Washer:
    Switch_Status = (2, 1)  # bool  # rwn
    Status = (2, 2)  # uint8  # rn
    Mode = (2, 3)  # uint8  # rwn
    Device_Fault = (2, 4)  # uint8  # rn
    Left_Time = (2, 5)  # uint16  # rn
    Target_Temperature = (2, 6)  # uint8  # rwn
    Spin_Speed = (2, 7)  # uint16  # rwn
    Drying_Time = (2, 8)  # uint8  # rwn
    Rinsh_Times = (2, 9)  # uint8  # rwn
    Speed_Level = (2, 10)  # uint8  # rwn
    Door_State = (2, 11)  # uint8  # rn
    Power_Consumption = (2, 12)  # uint16  # rn
    Water_Consumption = (2, 13)  # uint16  # rn
    Working_Time = (2, 14)  # uint16  # rn

    Start_Wash = [2, 1]  # in=[3]  # out=[3]
    Pause = [2, 2]  # in=[3]  # out=[3]


class Physical_Control_Locked:
    Physical_Control_Locked = (3, 1)  # bool  # rwn


class 自定义属性:
    洗涤剂是否投放 = (4, 1)  # bool  # rnw
    洗涤剂投放量 = (4, 2)  # uint8  # rnw
    洗涤剂消耗量 = (4, 3)  # （ml）  # uint8  # rn
    柔顺剂是否投放 = (4, 4)  # 【暂无】  # bool  # rnw
    柔顺剂投放量 = (4, 5)  # 【暂无】  # uint8  # rnw
    柔顺剂消耗量 = (4, 6)  # （ml）【暂无】  # uint8  # rn
    disinfectant = (4, 7)  # bool  # rnw
    消毒剂投放量 = (4, 8)  # 【暂无】  # uint8  # rnw
    消毒剂消耗量 = (4, 9)  # （ml）【暂无】  # uint8  # rn
    预约完成时间戳 = (4, 10)  # 1. 下行非0表示开始预约；2. 下行0表示取消预约  # uint32  # rnw
    模式 = [4, 11]  # --值参考标准  # uint8
    耗电量 = [4, 12]  # (千瓦时)--值参考标准  # uint16
    耗水量 = [4, 13]  # (升)--值参考标准  # uint8
    工作时长 = [4, 14]  # --值参考标准  # uint16
    洗涤剂将耗尽 = (4, 15)  # bool  # rn
    柔顺剂将耗尽 = (4, 16)  # 【暂无】  # bool  # rn
    消毒剂将耗尽 = (4, 17)  # 【暂无】  # bool  # rn


class 用户按键上报:
    按键属性 = (5, 1)  # rn
    按键值 = (5, 2)  # uint8  # rn
    按键时长 = (5, 3)  # (毫秒)  # uint16  # rn


class Washer_Status(Enum):
    Off = 0
    Idle = 17
    Delay = 4
    Busy = 25
    Paused = 26
    Fault = 27


class Washer_Mode(Enum):
    _0 = 0
    _1 = 1
    _2 = 2
    _3 = 3
    Spin = 4
    Dry_Air_Wash = 5
    _6 = 6
    _7 = 7
    _8 = 8
    _9 = 9
    _10 = 10
    Shirt = 11
    _12 = 12
    Underwear = 13
    Wool = 14
    Down_Coat = 15
    _16 = 16
    _17 = 17
    _18 = 18
    _19 = 19
    _20 = 20
    _21 = 21
    _22 = 22
    _23 = 23


class Washer_Device_Fault(Enum):
    _0 = 0
    _1 = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5
    _6 = 6
    _7 = 7
    _8 = 8
    _9 = 9
    _10 = 10
    _11 = 11
    _12 = 12
    _13 = 13
    _14 = 14
    _15 = 15
    _16 = 16
    _17 = 17
    _18 = 18
    _19 = 19
    _20 = 20
    _21 = 21
    _22 = 22
    _23 = 23
    _24 = 24
    _25 = 25
    _26 = 26
    _27 = 27
    _28 = 28


class Washer_Left_Time(Enum):
    MIN = 0
    MAX = 1440


class Washer_Target_Temperature(Enum):
    _0 = 0
    _30 = 30
    _40 = 40
    _60 = 60
    _90 = 90


class Washer_Spin_Speed(Enum):
    _0 = 0
    _400 = 400
    _600 = 600
    _800 = 800
    _1000 = 1000
    _1200 = 1200
    _1400 = 1400


class Washer_Drying_Time(Enum):
    _0 = 0
    _1 = 1
    _30 = 30
    _60 = 60
    _90 = 90
    _120 = 120
    _180 = 180
    _240 = 240


class Washer_Rinsh_Times(Enum):
    _0 = 0
    _1 = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5
    _6 = 6
    _7 = 7


class Washer_Speed_Level(Enum):
    Level1 = 1
    Level2 = 2
    Level3 = 3
    Level4 = 4
    Level5 = 5


class Washer_Door_State(Enum):
    Open = 1
    Closed = 2


class Washer_Power_Consumption(Enum):
    MIN = 0
    MAX = 20000


class Washer_Water_Consumption(Enum):
    MIN = 0
    MAX = 1000


class Washer_Working_Time(Enum):
    MIN = 0
    MAX = 1440


class 自定义属性_洗涤剂投放量(Enum):
    _0 = 0
    _1 = 1
    _2 = 2


class 自定义属性_洗涤剂消耗量(Enum):
    MIN = 0
    MAX = 200


class 自定义属性_柔顺剂投放量(Enum):
    少量 = 0
    标准 = 1
    多量 = 2


class 自定义属性_柔顺剂消耗量(Enum):
    MIN = 0
    MAX = 200


class 自定义属性_消毒剂投放量(Enum):
    少量 = 0
    标准 = 1
    多量 = 2


class 自定义属性_消毒剂消耗量(Enum):
    MIN = 0
    MAX = 200


class 自定义属性_预约完成时间戳(Enum):
    MIN = 0
    MAX = 4294836225


class 自定义属性_模式(Enum):
    MIN = 0
    MAX = 100


class 自定义属性_耗电量(Enum):
    MIN = 0
    MAX = 65535


class 自定义属性_耗水量(Enum):
    MIN = 0
    MAX = 255


class 自定义属性_工作时长(Enum):
    MIN = 0
    MAX = 65535


class 用户按键上报_按键值(Enum):
    MIN = 0
    MAX = 255


class 用户按键上报_按键时长(Enum):
    MIN = 0
    MAX = 65535


ALL_SVCS = (Device_Information, Washer, Physical_Control_Locked, 自定义属性, 用户按键上报)

