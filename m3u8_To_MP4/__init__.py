# -*- coding: utf-8 -*-

"""
m3u8ToMP4
~~~~~~~~~~~~

Basic usage:

import m3u8_to_mp4
m3u8_to_mp4.download("https://xxx.com/xxx/index.m3u8")


"""

# verify ffmpeg
import subprocess

test_has_ffmpeg_cmd = "ffmpeg -version"

proc = subprocess.Popen(test_has_ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
outs, errs = proc.communicate()
output_text = outs.decode('utf8')

import logging
from m3u8_To_MP4.helpers import printer_helper

printer_helper.config_logging()

if 'version' not in output_text:
    logging.warning('NOT FOUND FFMPEG!')
    logging.info('Compressing into tar.bz2 is only supported')

# define API
import m3u8_To_MP4.async_processor
from m3u8_To_MP4.async_processor import Crawler as AsyncCrawler
from m3u8_To_MP4.sync_processor import Crawler as SyncCrawler

__all__ = (
    "SyncCrawler",
    "async_download",
    "AsyncCrawler",
    "multithread_download",
    "download"
)


def async_download(m3u8_uri, max_retry_times=3, num_concurrent=50, mp4_file_dir=None, mp4_file_name='m3u8_To_Mp4.mp4', tmpdir=None):
    '''
    Download mp4 video from given m3u uri.

    :param m3u8_uri: m3u8 uri
    :param max_retry_times: max retry times
    :param max_concurrent: concurrency
    :param mp4_file_dir: folder path where mp4 file is stored
    :param mp4_file_name: a mp4 file name with suffix ".mp4"
    :return:
    '''

    with m3u8_To_MP4.async_processor.Crawler(m3u8_uri, max_retry_times, num_concurrent, mp4_file_dir, mp4_file_name, tmpdir) as crawler:
        crawler.fetch_mp4_by_m3u8_uri(True)


def multithread_download(m3u8_uri, max_retry_times=3, max_num_workers=100, mp4_file_dir='./', mp4_file_name='m3u8_To_Mp4.mp4', tmpdir=None):
    '''
    Download mp4 video from given m3u uri.

    :param m3u8_uri: m3u8 uri
    :param max_retry_times: max retry times
    :param max_num_workers: number of download threads
    :param mp4_file_dir: folder path where mp4 file is stored
    :param mp4_file_name: a mp4 file name with suffix ".mp4"
    :return:
    '''
    with m3u8_To_MP4.sync_processor.Crawler(m3u8_uri, max_retry_times, max_num_workers, mp4_file_dir, mp4_file_name, tmpdir) as crawler:
        crawler.fetch_mp4_by_m3u8_uri()

import warnings

def download(m3u8_uri, max_retry_times=3, max_num_workers=100, mp4_file_dir='./', mp4_file_name='m3u8_To_Mp4.mp4', tmpdir=None):
    '''
    Download mp4 video from given m3u uri.
    
    :param m3u8_uri: m3u8 uri
    :param max_retry_times: max retry times
    :param max_num_workers: number of download threads
    :param mp4_file_dir: folder path where mp4 file is stored
    :param mp4_file_name: a mp4 file name with suffix ".mp4"
    :return:
    '''
    warnings.warn('download function is deprecated, and please use multithread_download.',DeprecationWarning)

    multithread_download(m3u8_uri, max_retry_times, max_num_workers, mp4_file_dir, mp4_file_name, tmpdir)
