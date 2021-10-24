# -*- coding: utf-8 -*-
import collections
import random
import ssl

AddressInfo = collections.namedtuple(typename='AddressInfo', field_names=['host', 'port', 'family', 'proto'])


def statement_of_http_get_resource(resource_path_at_server):
    return f'{resource_path_at_server}'


def statement_of_http_get_resource_str(resource_path_at_server):
    return f'GET {statement_of_http_get_resource(resource_path_at_server)} HTTP/1.1'


def statement_of_http_connect_address(domain_name, port):
    return f'{domain_name}:{port}'


def statement_of_http_connect_address_str(domain_name, port):
    return f'Host: {statement_of_http_connect_address(domain_name,port)}'


def random_user_agent():
    user_agent_pool = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    ]
    return random.choice(user_agent_pool)


def random_user_agent_str():
    return 'User-Agent: ' + random_user_agent()


def statement_of_http_connection(is_keep_alive):
    state = 'Keep-alive' if is_keep_alive else 'close'
    return state


def statement_of_http_connection_str(is_keep_alive):
    return 'Connection: ' + statement_of_http_connection(is_keep_alive)


# optional
def random_x_forward_for():
    num_ips = random.randint(2, 5)

    ip_segments = list()
    while len(ip_segments) < 4 * num_ips:
        ip_segments.append(str(random.randint(0, 256)))

    ips = list()
    for ip_index in range(num_ips):
        ips.append('.'.join(ip_segments[ip_index * 4:(ip_index + 1) * 4]))
    return ','.join(ips)


def random_x_forward_for_str():
    return 'X-Forwarded-For ' + random_x_forward_for()


# optional
def random_cookie():
    return 'Cookie: ' + ''


# ssl
def ssl_context():
    _ssl_context = ssl.create_default_context()

    _ssl_context.check_hostname = False

    _ssl_context.verify_mode = ssl.CERT_NONE

    return _ssl_context


def ssl_under_scheme(scheme):
    if scheme == 'https':
        return ssl_context()
    elif scheme == 'http':
        return False
    else:
        raise ValueError('{} is not supported now.'.format(scheme))


def formatted_http_header(http_header_str):
    http_header_state = dict()

    http_header_lines = http_header_str.strip().split('\n')

    response_fragments = http_header_lines[0].strip().split()

    response_code = response_fragments[1]
    response_description = ' '.join(response_fragments[2:])

    http_header_state['response_code'] = int(response_code)
    http_header_state['response_description'] = response_description

    for line in http_header_lines[1:]:
        line = line.strip()
        i = line.find(':')
        if i == -1:
            continue

        key = line[:i]
        value = line[i + 1:]

        http_header_state[key.lower()] = value

    return http_header_state
