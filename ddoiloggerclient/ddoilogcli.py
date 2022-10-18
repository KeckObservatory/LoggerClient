import argparse 
import sys
from datetime import datetime, timedelta
import requests
import os
import configparser

sDate = '2022-10-10'
eDate = '2022-10-19'
subsystem = 'MOSFIRE'
nLogs = 2

def get_logs(baseURL, subsystem=None, startDate=None, endDate=None, nLogs=None, dateFormat=None):
    url = baseURL
    if startDate:
        url += f'start_date={startDate}&'
    if endDate:
        url += f'end_date={endDate}&'
    if subsystem:
        url += f'subsystems={subsystem}&'
    if nLogs:
        url += f'n_logs={nLogs}&'
    if dateFormat:
        url += f'date_format={dateFormat}'
    return url


def get_last_n_minutes_logs(baseURL, subsystem, minutes, endDate=None):
    dateFormat = '%Y-%m-%dT%H:%M:%S'
    if not endDate:
        endDate = datetime.utcnow()
    else:
        endDate = datetime.strptime(endDate, dateFormat)
    startDate = endDate - timedelta(minutes=minutes)
    startDateStr = datetime.strftime(startDate, dateFormat)
    endDateStr = datetime.strftime(endDate, dateFormat)
    url = get_logs(baseURL, subsystem, startDateStr, endDateStr, dateFormat=dateFormat)
    resp = requests.get(url)
    print(url)
    return resp
    
def get_default_config_loc():
    config_loc = os.path.abspath(os.path.dirname(__file__))
    config_loc = os.path.join(config_loc, './configs/server_cfg.ini')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get logs from logger database")
    parser.add_arguement('--subsystem', type=str, required=False, default=None,
                         help="subsystem specific logs")
    parser.add_arguement('--startDate', type=str, required=False, default=None,
                         help="starting date to retrieve logs")
    parser.add_arguement('--endDate', type=str, required=False, default=None,
                         help="ending date to retrieve logs")
    parser.add_arguement('--nLogs', type=int, required=False, default=100,
                         help="maximum number of logs to output")
    parser.add_arguement('--minutes', type=int, required=False, default=10,
                         help="set to retrieve last n minutes of logs")
    parser.add_arguement('--dateFormat', type=str, required=False, default='%Y-%m-%dT%H:%M:%S',
                         help="how the dates are formatted (default is YYYY-mm-ddTHH:MM:SS)")

    config = get_default_config_loc()
    config_parser = configparser.ConfigParser()
    config_parser.read(config)
    config = config_parser['LOGGING_SERVER']

    url = config.get('url',  'http://localhost:5000/api/log/get_logs?')

    args = parser.parse_args()

    if args.minutes:
        resp = get_last_n_minutes_logs(url, args.subsystem, args.minutes, args.endDate)
        print(resp.json())
        sys.exit()
    else:
        resp = get_logs(baseURL, subsystem=args.subsystem, startDate=args.startDate, endDate=args.endDate, nLogs=args.nLogs, dateFormat=args.dateFormat)
        