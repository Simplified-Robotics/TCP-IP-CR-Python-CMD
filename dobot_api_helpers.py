import threading
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType
from time import sleep
import numpy as np

ports = {
    "dashboard": 29999,
    "move_port": 30003,
    "feed_port": 30004
}

robot_modes = {
    1: "ROBOT_MODE_INIT",  # initialization
    2: "ROBOT_MODE_BRAKE_OPEN",  # The brake release
    3: "Reserved",
    4: "ROBOT_MODE_DISABLED",  # Disabled (brake is not released)
    5: "ROBOT_MODE_ENABLE"	,  # Enable (idle)
    6: "ROBOT_MODE_BACKDRIVE",  # Dragging state
    7: "ROBOT_MODE_RUNNING"	,  # Running state
    8: "ROBOT_MODE_RECORDING",  # Dragging recording
    9: "ROBOT_MODE_ERROR",  # Alarm state
    10:	"ROBOT_MODE_PAUSE",  # pause state
    11:	"ROBOT_MODE_JOG",  # jogging state
}


def GetPorts():
    return ports["dashboard"], ports["move_port"], ports["feed_port"]


def GetRobotModeIntFromReturn(mode_result):
    return mode_result.split('{')[1].split('}')[0]


def GetRobotModeStringFromInt(mode_int):
    return robot_modes[int(mode_int)]


def GetRobotModeFromReturn(mode_result):
    res_int = GetRobotModeIntFromReturn(mode_result)
    return GetRobotModeStringFromInt(res_int)


def GetRobotMode(dashboard: DobotApiDashboard):
    return GetRobotModeFromReturn(dashboard.RobotMode())


def GetSingleUpdate(feed: DobotApi):
    hasRead = 0
    while True:
        data = bytes()
        while hasRead < 1440:
            temp = feed.socket_dobot.recv(1440 - hasRead)
            if len(temp) > 0:
                hasRead += len(temp)
                data += temp

        hasRead = 0

        data = np.frombuffer(data, dtype=MyType)
        if hex((data['test_value'][0])) == '0x123456789abcdef':
            return data


def StartFeedUpdate(feed: DobotApi, sleep_duration=0.001, itemsToPrint=["tool_vector_actual"]):
    global current_actual
    hasRead = 0
    while True:
        data = GetSingleUpdate(feed)

        # Refresh Properties
        for item in itemsToPrint:
            print(item, data[item][0])

        sleep(sleep_duration)


def GetDashboard(ip_addr):
    return DobotApiDashboard(ip=ip_addr, port=ports["dashboard"])


def GetMove(ip_addr):
    return DobotApiMove(ip=ip_addr, port=ports["move_port"])


def GetFeed(ip_addr):
    return DobotApi(ip=ip_addr, port=ports["feed_port"])


def GetDashboardMoveAndFeedConnections(ip_addr):
    return GetDashboard(ip_addr), GetMove(ip_addr), GetFeed(ip_addr)
