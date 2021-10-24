# -*- coding: utf-8 -*-
import urllib.error
import urllib.parse
import urllib.request
import urllib.response

from m3u8_To_MP4.helpers import path_helper
from m3u8_To_MP4.networks import http_base


def http_get_header(domain_name, port, resource_path_at_server, is_keep_alive):
    # http_get_resource = http_base.statement_of_http_get_resource(resource_path_at_server)
    # http_connect_address = http_base.statement_of_http_connect_address(domain_name, port)
    user_agent = http_base.random_user_agent()
    # http_connection = http_base.statement_of_http_connection(is_keep_alive)

    # x_forward_for=random_x_forward_for()
    # cookie=random_cookie()

    request_header = {
        'User-Agent': user_agent
    }

    return request_header


def retrieve_resource_from_url(address_info, url, is_keep_alive=False, max_retry_times=5, timeout=30):
    port = address_info.port
    scheme, domain_name_with_suffix, path, query, fragment = urllib.parse.urlsplit(url)

    resource_path = path_helper.updated_resource_path(path, query)

    response_code = -1
    response_content = None

    for num_retry in range(max_retry_times):
        headers = http_get_header(domain_name_with_suffix, port, resource_path, is_keep_alive)

        try:
            request = urllib.request.Request(url=url, headers=headers)

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
