import logging

import yaml

from ssrspeed.paths import KEY_PATH

logger = logging.getLogger("Sub")


class ParserV2RayClash(object):
    def __init__(self):
        self.__clash_vmess_configs: list = []
        self.__decoded_configs: list = []

    @staticmethod
    def __clash_config_convert(clash_cfg: dict) -> dict:
        server = clash_cfg["server"]
        remarks = clash_cfg.get("name", server)
        remarks = remarks if remarks else server
        group = "N/A"
        port = int(clash_cfg["port"])
        uuid = clash_cfg["uuid"]
        aid = int(clash_cfg["alterId"])
        security = clash_cfg.get("cipher", "auto")
        tls = "tls" if (clash_cfg.get("tls", False)) else ""  # TLS
        allow_insecure = True if (clash_cfg.get("skip-cert-verify", False)) else False
        net = clash_cfg.get("network", "tcp")  # ws, tcp
        _type = clash_cfg.get("type", "none")  # Obfs type
        ws_header = clash_cfg.get("ws-headers", {})
        host = ws_header.get(
            "Host", ""
        )  # http host, web socket host, h2 host, quic encrypt method
        headers = {}
        for header in ws_header.keys():
            if header != "Host":
                headers[header] = ws_header[header]
        tls_host = host
        path = clash_cfg.get(
            "ws-path", ""
        )  # Websocket path, http path, quic encrypt key
        logger.debug(
            "Server : {}, Port : {}, tls-host : {}, Path : {}, Type : {}, UUID : {}, AlterId : {}, Network : {}, "
            "Host : {}, TLS : {}, Remarks : {}, group={}".format(
                server,
                port,
                tls_host,
                path,
                _type,
                uuid,
                aid,
                net,
                host,
                tls,
                remarks,
                group,
            )
        )
        return {
            "remarks": remarks,
            "group": group,
            "server": server,
            "server_port": port,
            "id": uuid,
            "alterId": aid,
            "security": security,
            "type": _type,
            "path": path,
            "allowInsecure": allow_insecure,
            "network": net,
            "headers": headers,
            "tls-host": tls_host,
            "host": host,
            "tls": tls,
        }

    def __parse_config(self, clash_cfg: dict):
        for cfg in clash_cfg["Proxy"]:
            if cfg.get("type", "N/A").lower() == "vmess":
                self.__clash_vmess_configs.append(cfg)
            else:
                pass
        # 	logger.info("Config {}, type {} not support.".format(
        # 		cfg["name"],
        # 		cfg["type"]
        # 		)
        # 	)
        # 	logger.debug("Read {} configs.".format(
        # 		len(self.__clashVmessConfigs)
        # 		)
        # 	)
        for cfg in self.__clash_vmess_configs:
            self.__decoded_configs.append(self.__clash_config_convert(cfg))

    def parse_subs_config(self, config) -> list:
        try:
            clash_cfg = yaml.load(config, Loader=yaml.FullLoader)
        except:
            logger.exception("Not Clash config.")
            return []
        self.__parse_config(clash_cfg)
        return self.__decoded_configs

    def parse_gui_config(self, filename: str) -> list:
        with open(filename, "r+", encoding="utf-8") as f:
            try:
                clash_cfg = yaml.load(f, Loader=yaml.FullLoader)
            except:
                logger.exception("Not Clash config.")
                return []
        self.__parse_config(clash_cfg)
        return self.__decoded_configs


if __name__ == "__main__":
    cvp = ParserV2RayClash()
    cvp.parse_gui_config(KEY_PATH["tmp"] + "config.example.yml")
