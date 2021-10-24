# -*- coding: utf-8 -*-
import datetime
from collections import Counter


def updated_resource_path(path, query):
    if query:
        path = f'{path}?{query}'
    return path


def resolve_file_name_by_uri(uri):
    # pattern = r"\/+(.*)"
    # file_name = re.findall(pattern=pattern, string=uri)[0]
    file_name = uri.split('/')[-1]
    return file_name


def calibrate_mp4_file_name(mp4_file_name):
    if mp4_file_name.strip() == '':
        return False, None

    banned_ls = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    for ch in banned_ls:
        mp4_file_name = mp4_file_name.replace(ch, '')

    if not mp4_file_name.endswith('.mp4'):
        mp4_file_name += '.mp4'

    return True, mp4_file_name


def create_mp4_file_name():
    mp4_file_name = 'm3u8_To_Mp4_{}.mp4'.format(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
    return mp4_file_name


def longest_common_subsequence(segment_absolute_urls):
    num_shortest_segment_absolute_url_length = min(len(url) for url in segment_absolute_urls)

    common_subsequence = list()
    for i in range(num_shortest_segment_absolute_url_length):
        c = Counter(segment_absolute_url[i] for segment_absolute_url in segment_absolute_urls)
        common_subsequence.append(c.most_common(1)[0][0])

    return ''.join(common_subsequence)
