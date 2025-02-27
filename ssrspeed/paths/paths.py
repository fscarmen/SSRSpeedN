import os
import sys

_ = os.sep
ABS_PATH = os.path.abspath(__file__).split(_)
ROOT_PATH = _.join(ABS_PATH[0:-3]) + _
KEY_PATH = {
    "data": f"{ROOT_PATH}data",
    "logs": f"{ROOT_PATH}data{_}logs{_}",
    "results": f"{ROOT_PATH}data{_}results{_}",
    "tmp": f"{ROOT_PATH}data{_}tmp{_}",
    "uploads": f"{ROOT_PATH}data{_}tmp{_}uploads{_}",
    "config.json": f"{ROOT_PATH}data{_}tmp{_}config.json",
    "ssrspeed.example.json": f"{ROOT_PATH}data{_}ssrspeed.example.json",
    "ssrspeed.json": f"{ROOT_PATH}data{_}ssrspeed.json",
    "resources": f"{ROOT_PATH}resources{_}",
    "clients": f"{ROOT_PATH}resources{_}clients{_}",
    "static": f"{ROOT_PATH}resources{_}static{_}",
    "custom": f"{ROOT_PATH}resources{_}static{_}custom{_}",
    "fonts": f"{ROOT_PATH}resources{_}static{_}fonts{_}",
    "logos": f"{ROOT_PATH}resources{_}static{_}logos{_}",
    "templates": f"{ROOT_PATH}resources{_}templates{_}",
    "ssrspeed": f"{ROOT_PATH}ssrspeed{_}",
}


def root():
    p = ROOT_PATH
    os.chdir(p)
    sys.path.insert(0, p)


if __name__ == "__main__":
    print(ROOT_PATH)
    print(KEY_PATH)
