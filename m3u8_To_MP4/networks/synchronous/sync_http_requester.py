# -*- coding: utf-8 -*-
import urllib.error
import urllib.parse
import urllib.request
import urllib.response


def get_headers(customized_http_header):
    request_header = dict()

    request_header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'

    if customized_http_header is not None:
        request_header.update(customized_http_header)

    return request_header


def request_for(url, max_try_times=1, headers=None, data=None, timeout=30, proxy_ip=None, verify=False, customized_http_header=None):
    response_code = -1
    response_content = None

    for num_retry in range(max_try_times):
        if headers is None:
            headers = get_headers(customized_http_header)

        try:
            request = urllib.request.Request(url=url, data=data, headers=headers)

            with urllib.request.urlopen(url=request, timeout=timeout) as response:
                response_code = response.getcode()
                response_content = response.read()

            if response_code == 200:
                break
        except urllib.error.HTTPError as he:
            response_code = he.code
        except urllib.error.ContentTooShortError as ctse:
            response_code = -2  # -2:ctse
        except urllib.error.URLError as ue:
            response_code = -3  # -3:URLError
        except Exception as exc:
            response_code = -4  # other error
        finally:
            timeout += 2

    return response_code, response_content
