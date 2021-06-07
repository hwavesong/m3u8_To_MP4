# -*- coding: utf-8 -*-

"""
m3u8ToMP4
~~~~~~~~~~~~

Basic usage:

import m3u8_to_mp4
m3u8_to_mp4.download("https://xxx.com/xxx/index.m3u8")
    
"""
import subprocess

test_has_ffmpeg_cmd = "ffmpeg -version"

proc = subprocess.Popen(test_has_ffmpeg_cmd, shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
outs, errs = proc.communicate()
output_text = outs.decode('utf8')

if 'version' not in output_text:
    raise Exception('NOT FOUND FFMPEG!')

import logging

logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s',
                    level=logging.INFO)

import m3u8_To_MP4.processor
from m3u8_To_MP4.processor import Crawler

__all__ = (
    "Crawler",
    "download"
)


def download(m3u8_uri, max_retry_times=3, max_num_workers=100,
             mp4_file_dir='./', mp4_file_name='m3u8_To_Mp4.mp4', tmpdir=None):
    '''
    Download mp4 video from given m3u uri.

    :param m3u8_uri: m3u8 uri
    :param max_retry_times: max retry times
    :param max_num_workers: number of download threads
    :param mp4_file_dir: folder path where mp4 file is stored
    :param mp4_file_name: a mp4 file name with suffix ".mp4"
    :return:
    '''
    with m3u8_To_MP4.processor.Crawler(m3u8_uri, max_retry_times,
                                       max_num_workers, mp4_file_dir,
                                       mp4_file_name, tmpdir) as crawler:
        crawler.fetch_mp4_by_m3u8_uri()
