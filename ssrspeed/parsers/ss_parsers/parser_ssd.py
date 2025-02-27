import copy
import json
import logging

logger = logging.getLogger("Sub")


class ParserShadowsocksD(object):
    def __init__(self, base_config):
        self.__config_list: list = []
        self.__baseConfig = base_config

    def __get_shadowsocks_base_config(self):
        return copy.deepcopy(self.__baseConfig)

    def parse_subs_config(self, config) -> list:
        ssd_config = json.loads(config)
        group = ssd_config.get("airport", "N/A")
        default_port = int(ssd_config["port"])
        default_method = ssd_config["encryption"]
        default_password = ssd_config["password"]
        default_plugin = ssd_config.get("plugin", "")
        default_plugin_opts = ssd_config.get("plugin_options", "")
        servers = ssd_config["servers"]
        for server in servers:
            _config = self.__get_shadowsocks_base_config()
            _config["server"] = server["server"]
            _config["server_port"] = int(server.get("port", default_port))
            _config["method"] = server.get("encryption", default_method)
            _config["password"] = server.get("password", default_password)
            _config["plugin"] = server.get("plugin", default_plugin)
            _config["plugin_opts"] = server.get("plugin_options", default_plugin_opts)
            _config["group"] = group
            _config["remarks"] = server.get("remarks", server["server"])
            if not _config["remarks"]:
                _config["remarks"] = _config["server"]
            self.__config_list.append(_config)
        logger.info("Read {} config(s).".format(len(self.__config_list)))
        return self.__config_list

    def parse_gui_config(self, filename: str):
        # In BasicParser.py
        raise AttributeError(
            "'parseGuiConfig' built-in 'BasicParser.py' with basic shadowsocks parser."
        )
