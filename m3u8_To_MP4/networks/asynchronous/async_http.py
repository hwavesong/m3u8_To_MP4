# -*- coding: utf-8 -*-
import asyncio
import logging
import urllib.error
import urllib.parse
import urllib.request
import urllib.response

from m3u8_To_MP4.helpers import path_helper
from m3u8_To_MP4.networks import http_base


def http_get_header(domain_name, port, resource_path_at_server, is_keep_alive):
    http_get_resource = http_base.statement_of_http_get_resource_str(resource_path_at_server)
    http_connect_address = http_base.statement_of_http_connect_address_str(domain_name, port)
    user_agent = http_base.random_user_agent_str()
    http_connection = http_base.statement_of_http_connection_str(is_keep_alive)

    # x_forward_for=random_x_forward_for()
    # cookie=random_cookie()

    request_header = '\r\n'.join((http_get_resource, http_connect_address, user_agent, http_connection)) + '\r\n\r\n'

    return request_header.encode()


async def handler_of_connection(address_info, default_ssl_context, limit=256 * 1024):
    loop = asyncio.get_event_loop()

    host = address_info.host
    port = address_info.port
    family = address_info.family
    proto = address_info.proto

    reader = asyncio.StreamReader(limit=limit, loop=loop)
    protocol = asyncio.StreamReaderProtocol(reader, loop=loop)

    transport, protocol = await loop.create_connection(lambda: protocol, host, port, ssl=default_ssl_context, family=family, proto=proto)

    writer = asyncio.StreamWriter(transport, protocol, reader, loop)

    return reader, writer


async def retrieve_resource_from_handler(reader, writer, request_header):
    writer.write(data=request_header)
    await writer.drain()

    byted_response_header = await reader.readuntil(separator=b'\r\n\r\n')
    response_header = byted_response_header.decode()
    http_header_state = http_base.formatted_http_header(response_header)

    content_length = -1
    if 'content_length' in http_header_state:
        content_length = int(http_header_state['content_length'])
    byted_response_content = await reader.read(n=content_length)

    return http_header_state, byted_response_content


async def retrieve_resource_from_url(address_info, url, ssl_context_, is_keep_alive=False, max_retry_times=5, limit=2 ** 10):
    port = address_info.port
    scheme, domain_name_with_suffix, path, query, fragment = urllib.parse.urlsplit(url)
    resource_path = path_helper.updated_resource_path(path, query)

    reader, writer = None, None
    response_header_state, byted_response_content = {'response_code': -1}, None

    num_retry = 0
    while num_retry < max_retry_times:
        try:
            request_header = http_get_header(domain_name_with_suffix, port, resource_path, is_keep_alive)
            reader, writer = await asyncio.wait_for(handler_of_connection(address_info, ssl_context_, limit), 3)

            response_header_state, byted_response_content = await asyncio.wait_for(retrieve_resource_from_handler(reader, writer, request_header), timeout=8)

        except asyncio.TimeoutError as te:
            logging.debug('request timeout: {}'.format(url))

        except Exception as exc:
            logging.debug('request failed: {}, and caused reason is {}'.format(url, str(exc)))

        try:
            if not is_keep_alive:
                if writer is not None:
                    writer.close()
                    await writer.wait_closed()

                # if reader is not None:
                #     reader.feed_eof()
                # assert reader.at_eof()
        except Exception as exc:
            logging.debug('request failed: {}, and caused reason is {}'.format(url, str(exc)))

        if response_header_state['response_code'] == 200:
            return response_header_state, byted_response_content

        num_retry += 1

    else:
        return response_header_state, None
