# -*- coding: utf-8 -*-
import re
import socket
import urllib.parse

from m3u8_To_MP4.networks.http_base import AddressInfo


def available_addr_infos_of_url(url):
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)

    specific_port_pattern = re.compile(r':(\d+)')
    specific_ports = re.findall(specific_port_pattern, netloc)

    netloc = re.sub(specific_port_pattern, '', netloc)

    # todo:: support IPv6
    addr_infos = socket.getaddrinfo(host=netloc, port=scheme,
                                    family=socket.AF_INET)

    available_addr_info_pool = list()
    for family, type, proto, canonname, sockaddr in addr_infos:
        port = specific_ports[0] if len(specific_ports) > 0 else sockaddr[1]
        ai = AddressInfo(host=sockaddr[0], port=port, family=family,
                         proto=proto)
        available_addr_info_pool.append(ai)

    return available_addr_info_pool
