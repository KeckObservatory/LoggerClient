import configparser
import pdb
import json
import zmq
import sys
import os
import pytest
import sys
sys.path.append('../LoggerClient')
from Logger import Logger
import yaml


subsystem='MOSFIRE'
config=None
author="ttucker"
progid="2022B"
semid="1234"
loggername = 'DDOI'
rs = 'test log' 

url = "tcp://localhost:5570"
config_parser = configparser.ConfigParser()

config_loc = os.path.join(os.getcwd(), 'logger_cfg.yaml')
with open(config_loc, 'r') as f:
    config = yaml.safe_load(f)

@pytest.mark.client
def test_logger_client():

    logger = Logger(url, subsystem=subsystem, author=author, progid=progid, semid=semid, loggername=loggername)
    alive = logger.server_interface._check_cfg_url_alive()
    assert alive, 'heartbeat failing'

    logSchema = [*config[loggername]['LOG_SCHEMA_BASE'],
                *config[loggername]['LOG_SCHEMA'] ]
    msg = 'test msg'
    ack = logger.send_log(message=msg, logSchema=logSchema, test=True)
    resp = ack.get('resp', 400)
    msg = ack.get('msg', None)
    assert resp == 200, 'message not sent'
    assert 'log submitted to database' in msg, 'message not added to database'

@pytest.mark.client
def test_request_logs():

    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect(url)
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    nLogs = 10
    reqParams = {'nLogs': nLogs, 'loggername': loggername }
    msg = {'msg_type': 'request_logs', 'body': reqParams}
    socket.send_string(json.dumps(msg)) #  zeromq method is faster

    sockets = dict(poll.poll(1000))
    resp = json.loads(socket.recv()) if socket in sockets else {}
    assert resp.get('resp', False) == 200, f"logs not recieved: {resp.get('msg', 'no msg found')}"
    logs = resp.get('msg')
    assert len(logs) == nLogs, f'logs not returned, nLogs {nLogs}!={len(logs)}'



if __name__ == '__main__':
    testCmd = 'python -m pytest -m client'
    os.system(testCmd)
