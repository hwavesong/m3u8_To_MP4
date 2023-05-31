# -*- coding: utf-8 -*-
import urllib.parse
import requests
import time

from m3u8_To_MP4.helpers import path_helper
from m3u8_To_MP4.networks import http_base


def http_get_header(domain_name, port, resource_path_at_server, is_keep_alive,
                    customized_http_header):
    request_header = dict()

    user_agent = http_base.random_user_agent()
    request_header['User-Agent'] = user_agent

    if customized_http_header is not None:
        request_header.update(customized_http_header)

    return request_header

def retrieve_resource_from_url(address_info, url, is_keep_alive=False,
                               max_retry_times=5, timeout=30,
                               customized_http_header=None, proxy=None):

    # Extract necessary information
    port = address_info.port
    scheme, domain_name_with_suffix, path, query, fragment = urllib.parse.urlsplit(url)
    resource_path = path_helper.updated_resource_path(path, query)

    # Initialize response variables
    response_code = -1
    response_content = None
    proxies = {}
    
    # Configure requests to use the proxy
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy,
        }

    # Retry loop
    for num_retry in range(max_retry_times):
        headers = http_get_header(domain_name_with_suffix, port, resource_path,
                                  is_keep_alive, customized_http_header)
        try:
            # Make request and get response
            if proxy:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            else:
                response = requests.get(url, headers=headers, timeout=timeout)

            response_code = response.status_code
            response_content = response.content

            # Break loop if response is successful
            if response_code == 200:
                break

        # Handle various exceptions
        except requests.exceptions.HTTPError as he:
            response_code = he.response.status_code
        except requests.exceptions.ConnectionError:
            response_code = -3  # URLError
        except Exception as exc:
            response_code = -4  # other error
        finally:
            # Increment timeout for next retry
            timeout += 2
            # Sleep before the next retry
            time.sleep(2)

    return response_code, response_content