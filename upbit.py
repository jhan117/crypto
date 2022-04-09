from ast import literal_eval
import logging
import time
import requests


# Set logging level to DEBUG
logging.basicConfig(
    format='[%(levelname)s => %(filename)s:%(lineno)d][%(asctime)s]\n%(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.DEBUG
)


'''
- Name : get_env_var
- Desc : Read token and keys
- Input
    Key : key of env.txt
- Output
    Value : value of key
'''


def get_env_var(key):
    try:
        path = './env/env.txt'

        f = open(path, 'r')
        line = f.readline()
        f.close()

        env_dict = literal_eval(line)
        logging.debug("env var info: " + str(env_dict))

        return env_dict[key]

    except Exception:
        raise


'''
- Name : send_request
- Desc : Handle request
- Input
    reqMethod: method of request (ex: get, post, put, delete)
    reqUrl: the url of the request
    reqHeader: headers to send to the specified url
    reqParam: parameters to send to the specified url
- Output
    response: response to the HTTP request
'''


def send_request(reqMethod, reqUrl, reqParam, reqHeader):
    try:
        # time to wait for the number of requests available (second)
        REQ_WAIT_TIME = 0.3

        while True:
            # request
            response = requests.request(
                reqMethod, reqUrl, params=reqParam, headers=reqHeader)

            # get the number of remaining requests
            if 'Remaining-Req' in response.headers:
                req_remaining = response.headers['Remaining-Req']
                remaining_sec = req_remaining.split(';')[2].split('=')[1]
            else:
                logging.error('Error in headers received from the Request')
                logging.error('Check headers ->', response.headers)
                break

            # for error prevention
            if int(remaining_sec) < 3:
                logging.debug('Caution! The left requests:', remaining_sec)
                time.sleep(REQ_WAIT_TIME)

            # response
            if response.status_code == 200:
                break
            elif response.status_code == 429:
                logging.error('Too many requests!')
                time.sleep(REQ_WAIT_TIME)
            else:
                logging.error('response error:', str(response.status_code))
                logging.error('Check response ->', response)
                break
            logging.info('Re-request...')

        return response

    except Exception:
        raise
