# -*- coding: utf-8 -*-
import datetime
import random
from collections import Counter

WINDOWS_BANNED_CHARACTERS = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']


def updated_resource_path(path, query):
    if query:
        path = f'{path}?{query}'
    return path


def resolve_file_name_by_uri(uri):
    # pattern = r"\/+(.*)"
    # file_name = re.findall(pattern=pattern, string=uri)[0]
    name = uri.split('/')[-1]
    return calibrate_name(name)


def calibrate_mp4_file_name(mp4_file_name):
    mp4_file_name = calibrate_name(mp4_file_name)

    return mp4_file_name


def random_5_char():
    random_digits = [str(random.randint(0, 10)) for _ in range(5)]
    return ''.join(random_digits)


def random_name():
    dt_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    return 'm3u8_To_MP4' + dt_str + random_5_char()+'.mp4'


def calibrate_name(name):
    if len(name.strip()) == 0:
        return random_name()

    for ch in WINDOWS_BANNED_CHARACTERS:
        name = name.replace(ch, '')
    return name


# def create_mp4_file_name():
#     mp4_file_name = 'm3u8_To_Mp4_{}.mp4'.format(
#         datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
#     return mp4_file_name


def longest_common_subsequence(segment_absolute_urls):
    num_shortest_segment_absolute_url_length = min(
            len(url) for url in segment_absolute_urls)

    common_subsequence = list()
    for i in range(num_shortest_segment_absolute_url_length):
        c = Counter(segment_absolute_url[i] for segment_absolute_url in
                    segment_absolute_urls)
        common_subsequence.append(c.most_common(1)[0][0])

    return ''.join(common_subsequence)
