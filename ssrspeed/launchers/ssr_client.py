import json
import logging
import socket
import subprocess
import sys
from typing import Any, Dict, Union

import requests

from ssrspeed.launchers import BaseClient
from ssrspeed.paths import KEY_PATH

logger = logging.getLogger("Sub")

CLIENTS_DIR = KEY_PATH["clients"]
CONFIG_FILE = KEY_PATH["config.json"]


class ShadowsocksR(BaseClient):
    def __init__(self):
        super(ShadowsocksR, self).__init__()
        self.useSsrCSharp: bool = False

    def _before_stop_client(self):
        if self.useSsrCSharp:
            self.__ssr_csharp_conf({})

    def __ssr_csharp_conf(self, config: Dict[str, Any]):
        with open(
            f"{CLIENTS_DIR}shadowsocksr-win/gui-config.json", "r", encoding="utf-8"
        ) as f:
            tmp_conf = json.loads(f.read())
        tmp_conf["localPort"] = self._localPort
        tmp_conf["sysProxyMode"] = 1
        tmp_conf["index"] = 0
        tmp_conf["proxyRuleMode"] = 0
        tmp_conf["configs"] = []
        config["protocolparam"] = config.get("protocol_param", "")
        config["obfsparam"] = config.get("obfs_param", "")
        tmp_conf["configs"].append(config)

        with open(
            f"{CLIENTS_DIR}shadowsocksr-win/gui-config.json", "w+", encoding="utf-8"
        ) as f:
            f.write(json.dumps(tmp_conf))

    def start_client(self, config: Dict[str, Any]):
        self._config = config
        # 	self._config["server_port"] = int(self._config["server_port"])
        with open(CONFIG_FILE, "w+", encoding="utf-8") as f:
            f.write(json.dumps(self._config))

        if self._process is None:

            if self._platform == "Windows":
                if self.useSsrCSharp:
                    self.__ssr_csharp_conf(config)
                    self._process = subprocess.Popen(
                        [f"{CLIENTS_DIR}shadowsocksr-win/shadowsocksr.exe"]
                    )
                    logger.info("shadowsocksr-C# started.")
                    return
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocksr-libev/ssr-local.exe",
                            "-u",
                            "-c",
                            CONFIG_FILE,
                            "-v",
                        ]
                    )
                    logger.info(
                        "Starting shadowsocksr-libev with server %s:%d"
                        % (config["server"], config["server_port"])
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocksr-libev/ssr-local.exe",
                            "-u",
                            "-c",
                            CONFIG_FILE,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    logger.info(
                        "Starting shadowsocksr-libev with server %s:%d"
                        % (config["server"], config["server_port"])
                    )

            elif self._platform == "Linux" or self._platform == "MacOS":
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [
                            "python3",
                            f"{CLIENTS_DIR}shadowsocksr/shadowsocks/local.py",
                            "-v",
                            "-c",
                            CONFIG_FILE,
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            "python3",
                            f"{CLIENTS_DIR}shadowsocksr/shadowsocks/local.py",
                            "-c",
                            CONFIG_FILE,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    "Starting shadowsocksr-Python with server %s:%d"
                    % (config["server"], config["server_port"])
                )

            else:
                logger.critical(
                    "Your system does not support it. Please contact the developer."
                )
                sys.exit(1)

    # 	print(self.__process.returncode)


class ShadowsocksRR(BaseClient):
    def __init__(self):
        super(ShadowsocksRR, self).__init__()
        self.__ssrAuth: str = ""

    def __win_conf(self):
        with open(
            f"{CLIENTS_DIR}shadowsocksr-win/gui-config.json", "r", encoding="utf-8"
        ) as f:
            tmp_conf = json.loads(f.read())
        self.__ssrAuth = tmp_conf["localAuthPassword"]
        tmp_conf["token"]["SpeedTest"] = "SpeedTest"
        tmp_conf["localPort"] = self._localPort
        tmp_conf["sysProxyMode"] = 1
        tmp_conf["index"] = 0
        tmp_conf["proxyRuleMode"] = 2
        tmp_conf["configs"] = []

        for item in self._config_list:
            try:
                item["protocolparam"] = item["protocol_param"]
            except KeyError:
                item["protocolparam"] = ""
            try:
                item["obfsparam"] = item["obfs_param"]
            except KeyError:
                item["obfsparam"] = ""
            tmp_conf["configs"].append(item)

        with open(
            f"{CLIENTS_DIR}shadowsocksr-win/gui-config.json", "w+", encoding="utf-8"
        ) as f:
            f.write(json.dumps(tmp_conf))

    def get_current_config(self) -> Union[bool, Any]:
        param = {"app": "SpeedTest", "token": "SpeedTest", "action": "cur_config"}
        i = 0

        while True:
            try:
                rep = requests.post(
                    "http://%s:%d/api?auth=%s"
                    % (self._localAddress, self._localPort, self.__ssrAuth),
                    params=param,
                    timeout=5,
                )
                break
            except (requests.exceptions.Timeout, socket.timeout):
                logger.error("Connect to ssr api server timeout.")
                i += 1
                if i >= 4:
                    return False
                continue
            # 	self.next_win_conf()
            # 	return False
            except:
                logger.exception("Get current config failed.")
                return False

        rep.encoding = "utf-8"
        if rep.status_code == 200:
            # 	logger.debug(rep.content)
            return rep.json()
        else:
            logger.error(rep.status_code)
            return False

    def next_win_conf(self) -> bool:
        param = {"app": "SpeedTest", "token": "SpeedTest", "action": "nextConfig"}
        i = 0

        while True:
            try:
                rep = requests.post(
                    "http://%s:%d/api?auth=%s"
                    % (self._localAddress, self._localPort, self.__ssrAuth),
                    params=param,
                    timeout=5,
                )
                break
            except (requests.exceptions.Timeout, socket.timeout):
                logger.error("Connect to ssr api server timeout.")
                i += 1
                if i >= 4:
                    return False
                continue
            # 	return False
            except:
                logger.exception("Request next config failed.")
                return False

        if rep.status_code == 403:
            return False
        else:
            return True

    def start_client(self, config: Dict[str, Any]):
        if self._process is None:

            if self._platform == "Windows":
                self.__win_conf()
                # 	sys.exit(0)
                self._process = subprocess.Popen(
                    [f"{CLIENTS_DIR}shadowsocksr-libev/ssr-local.exe"]
                )

            elif self._platform == "Linux" or self._platform == "MacOS":
                self._config = config
                self._config["server_port"] = int(self._config["server_port"])
                with open(CONFIG_FILE, "w+", encoding="utf-8") as f:
                    f.write(json.dumps(self._config))
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [
                            "python3",
                            f"{CLIENTS_DIR}shadowsocksr/shadowsocks/local.py",
                            "-c",
                            CONFIG_FILE,
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            "python3",
                            f"{CLIENTS_DIR}shadowsocksr/shadowsocks/local.py",
                            "-c",
                            CONFIG_FILE,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    "Starting shadowsocksr-Python with server %s:%d"
                    % (config["server"], config["server_port"])
                )

            else:
                logger.critical(
                    "Your system does not support it. Please contact the developer."
                )
                sys.exit(1)

    # 	print(self.__process.returncode)
