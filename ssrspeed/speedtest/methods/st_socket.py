import copy
import logging
import socket
import threading
import time
from typing import Optional

import socks

from ssrspeed.config import ssrconfig
from ssrspeed.utils import ip_loc
from ssrspeed.utils.rules import DownloadRuleMatch

logger = logging.getLogger("Sub")
MAX_THREAD = ssrconfig["fileDownload"]["maxWorkers"]
DEFAULT_SOCKET = socket.socket
MAX_FILE_SIZE = 100 * 1024 * 1024
BUFFER = ssrconfig["fileDownload"]["buffer"]
EXIT_FLAG = False
LOCAL_PORT = 1080
LOCK = threading.Lock()
TOTAL_RECEIVED = 0
MAX_TIME = 0
SPEED_TEST = ssrconfig["speed"]
STSPEED_TEST = ssrconfig["StSpeed"]


def set_proxy_port(port: int):
    global LOCAL_PORT
    LOCAL_PORT = port


def restore_socket():
    socket.socket = DEFAULT_SOCKET


def speed_test_thread(link: str) -> Optional[int]:
    global TOTAL_RECEIVED, MAX_TIME
    logger.debug("Thread {} started.".format(threading.current_thread().ident))
    link = link.replace("https://", "").replace("http://", "")
    host = link[: link.find("/")]
    request_uri = link[link.find("/") :]
    logger.debug("\nLink: %s\nHost: %s\nRequestUri: %s" % (link, host, request_uri))
    # print(link, MAX_FILE_SIZE)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(12)
        try:
            s.connect((host, 80))
            logger.debug("Connected to %s" % host)
        except:
            logger.error("Connect to %s error." % host)
            LOCK.acquire()
            TOTAL_RECEIVED += 0
            LOCK.release()
            return None
        s.send(
            b"GET %b HTTP/1.1\r\nHost: %b\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            b"(KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36\r\n\r\n "
            % (request_uri.encode("utf-8"), host.encode("utf-8"))
        )
        logger.debug("Request sent.")
        start_time = time.time()
        received = 0
        while True:
            try:
                xx = s.recv(BUFFER)
            except socket.timeout:
                logger.error("Receive data timeout.")
                break
            except ConnectionResetError:
                logger.warning("Remote host closed connection.")
                break
            lxx = len(xx)
            # 	received += len(xx)
            received += lxx
            # 	TR = 0
            LOCK.acquire()
            TOTAL_RECEIVED += lxx
            # 	TR = TOTAL_RECEIVED
            LOCK.release()
            # 	logger.debug(TR)
            if received >= MAX_FILE_SIZE or EXIT_FLAG:
                break
        end_time = time.time()
        delta_time = end_time - start_time
        if delta_time >= 12:
            delta_time = 11
        s.close()
        logger.debug(
            "Thread {} done,time : {}".format(
                threading.current_thread().ident, delta_time
            )
        )
        LOCK.acquire()
        # 	TOTAL_RECEIVED += received
        MAX_TIME = max(MAX_TIME, delta_time)
        LOCK.release()
    except:
        logger.exception("")
        return 0


def speed_test_socket(port: int) -> tuple:
    if not SPEED_TEST:
        return 0, 0, [], 0

    global EXIT_FLAG, LOCAL_PORT, MAX_TIME, TOTAL_RECEIVED, MAX_FILE_SIZE
    LOCAL_PORT = port

    dlrm = DownloadRuleMatch()
    res = dlrm.get_url(ip_loc())

    MAX_FILE_SIZE = res[1] * 1024 * 1024
    MAX_TIME = 0
    TOTAL_RECEIVED = 0
    EXIT_FLAG = False
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", LOCAL_PORT)
    socket.socket = socks.socksocket

    if STSPEED_TEST:
        for i in range(0, 1):
            nmsl = threading.Thread(target=speed_test_thread, args=(res[0],))
            nmsl.start()

        max_speed_list = []
        max_speed = 0
        current_speed = 0
        old_received = 0
        delta_received = 0
        for i in range(1, 11):
            time.sleep(0.5)
            LOCK.acquire()
            delta_received = TOTAL_RECEIVED - old_received
            old_received = TOTAL_RECEIVED
            LOCK.release()
            current_speed = delta_received / 0.5
            max_speed_list.append(current_speed)
            print(
                "\r["
                + "=" * i
                + "> [%d%%/100%%] [%.2f MB/s]"
                % (int(i * 10), current_speed / 1024 / 1024),
                end="",
            )
            if EXIT_FLAG:
                break
        print(
            "\r["
            + "=" * i
            + "] [100%%/100%%] [%.2f MB/s]" % (current_speed / 1024 / 1024)
        )
        EXIT_FLAG = True
        for i in range(0, 10):
            time.sleep(0.1)
            if MAX_TIME != 0:
                break
        if MAX_TIME == 0:
            logger.error("Socket Test Error !")
            return 0, 0, [], 0

        raw_speed_list = copy.deepcopy(max_speed_list)
        max_speed_list.sort()
        if len(max_speed_list) > 12:
            msum = 0
            for i in range(12, len(max_speed_list) - 2):
                msum += max_speed_list[i]
            max_speed = msum / (len(max_speed_list) - 2 - 12)
        else:
            max_speed = current_speed
        logger.info(
            "SingleThread: Fetched {:.2f} KB in {:.2f} s.".format(
                TOTAL_RECEIVED / 1024, MAX_TIME
            )
        )

        avg_st_speed = TOTAL_RECEIVED / MAX_TIME

        MAX_TIME = 0
        TOTAL_RECEIVED = 0
        EXIT_FLAG = False

    for i in range(0, MAX_THREAD):
        nmsl = threading.Thread(target=speed_test_thread, args=(res[0],))
        nmsl.start()

    max_speed_list = []
    max_speed = 0
    current_speed = 0
    old_received = 0
    delta_received = 0
    for i in range(1, 11):
        time.sleep(0.5)
        LOCK.acquire()
        delta_received = TOTAL_RECEIVED - old_received
        old_received = TOTAL_RECEIVED
        LOCK.release()
        current_speed = delta_received / 0.5
        max_speed_list.append(current_speed)
        print(
            "\r["
            + "=" * i
            + "> [%d%%/100%%] [%.2f MB/s]" % (int(i * 10), current_speed / 1024 / 1024),
            end="",
        )
        if EXIT_FLAG:
            break
    print(
        "\r[" + "=" * i + "] [100%%/100%%] [%.2f MB/s]" % (current_speed / 1024 / 1024)
    )
    EXIT_FLAG = True
    for i in range(0, 10):
        time.sleep(0.1)
        if MAX_TIME != 0:
            break
    if MAX_TIME == 0:
        logger.error("Socket Test Error !")
        return 0, 0, [], 0

    restore_socket()
    raw_speed_list = copy.deepcopy(max_speed_list)
    max_speed_list.sort()
    if len(max_speed_list) > 7:
        msum = 0
        for i in range(7, len(max_speed_list) - 2):
            msum += max_speed_list[i]
        max_speed = msum / (len(max_speed_list) - 2 - 7)
    else:
        max_speed = current_speed
    logger.info(
        "MultiThread: Fetched {:.2f} KB in {:.2f} s.".format(
            TOTAL_RECEIVED / 1024, MAX_TIME
        )
    )
    avg_speed = TOTAL_RECEIVED / MAX_TIME

    if not STSPEED_TEST:
        avg_st_speed = avg_speed
        avg_speed = max_speed

    return avg_st_speed, avg_speed, raw_speed_list, TOTAL_RECEIVED
