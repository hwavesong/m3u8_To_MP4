# -*- coding: utf-8 -*-
import urllib.request
import urllib.response


def get_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    return headers


def request_for(url, max_try_times=1, headers=None, data=None, timeout=30,
                proxy_ip=None, verify=False):
    is_successful = False
    response_content = None

    for num_retry in range(max_try_times):
        if headers is None:
            headers = get_headers()

        try:
            if data == None:
                request = urllib.request.Request(url=url, headers=headers,
                                                 method='get')
            else:
                request = urllib.request.Request(url=url, data=data,
                                                 headers=headers,
                                                 method='post')

            with urllib.request.urlopen(url=request,
                                        timeout=timeout) as response:
                response_content = response.read()

            is_successful = True
            break

        except Exception as exc:
            # logging.exception(exc)
            timeout += 2
        finally:
            pass
            # response.close()

    return is_successful, response_content
