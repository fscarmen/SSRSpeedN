import json
import logging
import os
import shutil
import time

from ssrspeed.paths import KEY_PATH

logger = logging.getLogger("Sub")

RESULTS_DIR = KEY_PATH["results"]
TEMPLATES_DIR = KEY_PATH["templates"]


class ExporterWps(object):
    def __init__(self, result: dict):
        now_time = []
        for item in result:
            item["geoIP"]["inbound"]["address"] = "*.*.*.*"
            item["geoIP"]["outbound"]["address"] = "*.*.*.*"
            now_time.append(item)
        self.__results: list = now_time

    def export(self):
        now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        fileloc = RESULTS_DIR + now_time
        res = "var res = " + json.dumps(
            self.__results, sort_keys=True, indent=4, separators=(",", ":")
        )
        if os.path.exists(fileloc):
            shutil.rmtree(fileloc)
        shutil.copytree(TEMPLATES_DIR, fileloc)
        filename = os.path.join(fileloc, "results.js")
        with open(filename, "w+", encoding="utf-8") as f:
            f.writelines(res)
        index_filename = os.path.join(fileloc, "index.html")
        index = ""
        with open(index_filename, "r", encoding="utf-8") as f:
            read = f.readlines()
        for r in read:
            index += r
        index = index.replace(r"{{ $generatedTime }}", now_time)
        with open(index_filename, "w+", encoding="utf-8") as f:
            f.writelines(index)
        logger.info("Web page simulation result exported as %s." % fileloc)
