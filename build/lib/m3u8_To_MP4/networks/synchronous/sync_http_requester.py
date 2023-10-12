# -*- coding: utf-8 -*-
import requests
import time

def get_headers(customized_http_header):
    request_header = dict()

    request_header[
        'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'

    if customized_http_header is not None:
        request_header.update(customized_http_header)

    return request_header

def request_for(url, max_try_times=1, headers=None, data=None, timeout=30, customized_http_header=None, proxy=None):
    response_code = -1
    response_content = None
    proxies = None

    # Configure requests to use the proxy
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }

    for num_retry in range(max_try_times):
        if headers is None:
            headers = get_headers(customized_http_header)

        try:
            if proxy:
                response = requests.get(url, headers=headers, data=data, timeout=timeout, proxies=proxies)
            else:
                response = requests.get(url, headers=headers, data=data, timeout=timeout)

            response_code = response.status_code
            response_content = response.content

            if response_code == 200:
                break
        except requests.exceptions.HTTPError as he:
            response_code = he.response.status_code
        except requests.exceptions.Timeout as to:
            response_code = -2  # -2: timeout
        except requests.exceptions.RequestException as re:
            response_code = -3  # -3: RequestException
        except Exception as exc:
            response_code = -4  # other error
        finally:
            timeout += 2
            time.sleep(2)  # add sleep before the next retry attempt

    return response_code, response_content
