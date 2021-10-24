# -*- coding: utf-8 -*-
import socket
import urllib.parse

from m3u8_To_MP4.networks.http_base import AddressInfo


def available_addr_infos_of_url(url):
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)

    # todo:: support IPv6
    addr_infos = socket.getaddrinfo(host=netloc, port=scheme, family=socket.AF_INET)

    available_addr_info_pool = list()
    for family, type, proto, canonname, sockaddr in addr_infos:
        ai = AddressInfo(host=sockaddr[0], port=sockaddr[1], family=family, proto=proto)
        available_addr_info_pool.append(ai)

    return available_addr_info_pool
