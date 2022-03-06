# -*- coding: utf-8 -*-
import asyncio
import socket
import urllib.parse

from m3u8_To_MP4.networks.http_base import AddressInfo


async def available_addr_infos_of_url(url):
    loop = asyncio.get_event_loop()

    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)

    # todo:: support IPv6
    addr_infos = await loop.getaddrinfo(host=netloc, port=scheme,
                                        family=socket.AF_INET)

    available_addr_info_pool = list()
    for family, type, proto, canonname, sockaddr in addr_infos:
        ai = AddressInfo(host=sockaddr[0], port=sockaddr[1], family=family,
                         proto=proto)
        available_addr_info_pool.append(ai)

    return available_addr_info_pool
