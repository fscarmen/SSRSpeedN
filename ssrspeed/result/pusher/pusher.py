import logging

import requests

from ssrspeed.config import ssrconfig
from ssrspeed.paths import KEY_PATH

logger = logging.getLogger("Sub")

UPLOAD_RESULT = ssrconfig["uploadResult"]
TEST_PNG = KEY_PATH["tmp"] + "test.png"


def push2server(filename: str) -> dict:
    result = {"status": -1, "code": -1}
    try:
        logger.info("Pushing %s to server." % filename)
        files = {"file": open(filename, "rb")}
        param = {"token": UPLOAD_RESULT["apiToken"], "remark": UPLOAD_RESULT["remark"]}
        rep = requests.post(
            UPLOAD_RESULT["server"], files=files, data=param, timeout=10
        )
        result["status"] = rep.status_code
        if rep.status_code == 200:
            if rep.text == "ok":
                result["code"] = 0
        return result
    except requests.exceptions.Timeout:
        logger.error("Connect to server timeout.")
        return result
    except:
        logger.exception("Pushing result to server error.")
        return result


if __name__ == "__main__":
    print(push2server(TEST_PNG))
