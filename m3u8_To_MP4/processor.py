# -*- coding: utf-8 -*-
import collections
import concurrent.futures
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time

import m3u8
from Crypto.Cipher import AES

from m3u8_To_MP4 import utils
from m3u8_To_MP4.weber import request_for


def download_segment(segment_url):
    response_code, response_content = request_for(segment_url)

    return response_code, response_content


EncryptedKey = collections.namedtuple(typename='EncryptedKey',
                                      field_names=['method', 'value', 'iv'])


class Crawler(object):
    def __init__(self, m3u8_uri, max_retry_times=3, max_num_workers=100,
                 mp4_file_dir='./', mp4_file_name='m3u8_To_Mp4.mp4',
                 tmpdir=None):
        self.m3u8_uri = m3u8_uri

        self.max_retry_times = max_retry_times

        self.max_num_workers = max_num_workers

        self.tmpdir = tmpdir
        self.fetched_file_names = list()

        self.mp4_file_dir = mp4_file_dir
        self.mp4_file_name = mp4_file_name
        self.mp4_file_path = None

    def __enter__(self):
        if self.tmpdir is None:
            self._apply_for_tmpdir()

        self.fetched_file_names = os.listdir(self.tmpdir)

        self._legalize_valid_mp4_file_path()

        print('\nsummary:')
        print(
            'm3u8_uri: {};\nmax_retry_times: {};\nmax_num_workers: {};\ntmp_dir: {};\nmp4_file_path: {}\n'.format(
                self.m3u8_uri, self.max_retry_times, self.max_num_workers,
                self.tmpdir, self.mp4_file_path))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._freeup_tmpdir()

    def _apply_for_tmpdir(self):
        self.tmpdir = tempfile.mkdtemp(prefix='m3u8_')

    def _freeup_tmpdir(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def _legalize_valid_mp4_file_path(self):
        is_valid, mp4_file_name = utils.calibrate_mp4_file_name(
            self.mp4_file_name)
        if not is_valid:
            mp4_file_name = utils.create_mp4_file_name()

        mp4_file_path = os.path.join(self.mp4_file_dir, mp4_file_name)
        if os.path.exists(mp4_file_path):
            mp4_file_name = utils.create_mp4_file_name()
            mp4_file_path = os.path.join(self.mp4_file_dir, mp4_file_name)

        self.mp4_file_path = mp4_file_path

    def _get_m3u8_obj_by_uri(self, m3u8_uri):
        try:
            m3u8_obj = m3u8.load(uri=m3u8_uri)
        except Exception as exc:
            logging.exception(
                'failed to load m3u8 file,reason is {}'.format(exc))
            raise Exception('FAILED TO LOAD M3U8 FILE!')

        return m3u8_obj

    def _get_m3u8_obj_with_best_bandwitdth(self, m3u8_uri):
        m3u8_obj = self._get_m3u8_obj_by_uri(m3u8_uri)

        if m3u8_obj.is_variant:
            best_bandwidth = -1
            best_bandwidth_m3u8_uri = None
            for playlist in m3u8_obj.playlists:
                if playlist.stream_info.bandwidth > best_bandwidth:
                    best_bandwidth = playlist.stream_info.bandwidth
                    best_bandwidth_m3u8_uri = playlist.absolute_uri

            logging.info(
                "choose the best bandwidth, which is {}".format(best_bandwidth))
            logging.info("m3u8 uri is {}".format(best_bandwidth_m3u8_uri))

            m3u8_obj = self._get_m3u8_obj_by_uri(best_bandwidth_m3u8_uri)

        return m3u8_obj

    def _is_fetched(self, segment_uri):
        file_name = utils.resolve_file_name_by_uri(segment_uri)

        if file_name in self.fetched_file_names:
            return True

        return False

    def _construct_key_segment_pairs_by_m3u8(self, m3u8_obj):
        key_segments_pairs = list()
        for key in m3u8_obj.keys:
            if key:
                response_code, encryped_value = request_for(key.absolute_uri,
                                                            max_try_times=self.max_retry_times)
                if response_code!=200:
                    raise Exception('DOWNLOAD KEY FAILED, URI IS {}'.format(
                        key.absolute_uri))

                _encrypted_key = EncryptedKey(method=key.method,
                                              value=encryped_value, iv=key.iv)

                key_segments = m3u8_obj.segments.by_key(key)
                segments_by_key = [segment.absolute_uri for segment in
                                   key_segments if
                                   not self._is_fetched(segment.absolute_uri)]

                key_segments_pairs.append((_encrypted_key, segments_by_key))

        if len(key_segments_pairs) == 0:
            _encrypted_key = None

            key_segments = m3u8_obj.segments
            segments_by_key = [segment.absolute_uri for segment in
                               key_segments if
                               not self._is_fetched(segment.absolute_uri)]

            key_segments_pairs.append((_encrypted_key, segments_by_key))

        return key_segments_pairs

    def _fetch_segments_to_local_tmpdir(self, num_segments,
                                        key_segments_pairs):
        if len(self.fetched_file_names) >= num_segments:
            return

        progress_bar = utils.ProcessBar(len(self.fetched_file_names),
                                        num_segments, 'segment set',
                                        'downloading...',
                                        'downloaded segments successfully!')

        for encrypted_key, segments_by_key in key_segments_pairs:
            segment_url_to_encrypted_content = list()

            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.max_num_workers) as executor:
                while len(segments_by_key) > 0:
                    future_2_segment_uri = {executor.submit(download_segment,
                                                            segment_url): segment_url
                                            for segment_url in segments_by_key}

                    for future in concurrent.futures.as_completed(
                            future_2_segment_uri):
                        segment_uri = future_2_segment_uri[future]
                        try:
                            response_code, response_content = future.result()
                        except Exception as exc:
                            logging.exception(
                                '{} generated an exception: {}'.format(
                                    segment_uri, exc))

                        if response_code==200:
                            segment_url_to_encrypted_content.append(
                                (segment_uri, response_content))

                            segments_by_key.remove(segment_uri)
                            progress_bar.update()

                    if len(segments_by_key) > 0:
                        sys.stdout.write('\n')
                        logging.info(
                            '{} segments are failed to download, retry...'.format(
                                len(segments_by_key)))

            logging.info('decrypt and dump segments...')
            for segment_url, encrypted_content in segment_url_to_encrypted_content:
                file_name = utils.resolve_file_name_by_uri(segment_url)
                file_path = os.path.join(self.tmpdir, file_name)

                if encrypted_key is not None:
                    crypt_ls = {"AES-128": AES}
                    crypt_obj = crypt_ls[encrypted_key.method]
                    cryptor = crypt_obj.new(encrypted_key.value,
                                            crypt_obj.MODE_CBC)
                    encrypted_content = cryptor.decrypt(encrypted_content)

                with open(file_path, 'wb') as fin:
                    fin.write(encrypted_content)

    def _merge_tmpdir_segments_to_mp4_by_ffmpeg(self, m3u8_obj):
        order_segment_list_file_path = os.path.join(self.tmpdir, "ts_ls.txt")
        with open(order_segment_list_file_path, 'w', encoding='utf8') as fin:
            for segment in m3u8_obj.segments:
                file_name = utils.resolve_file_name_by_uri(segment.uri)
                segment_file_path = os.path.join(self.tmpdir, file_name)

                fin.write("file '{}'\n".format(segment_file_path))

        merge_cmd = "ffmpeg -y -f concat -safe 0 -i " + '"' + order_segment_list_file_path + '"' + " -c copy " \
                    + '"' + self.mp4_file_path + '"'

        p = subprocess.Popen(merge_cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("merging segments...")
        p.communicate()

    def fetch_mp4_by_m3u8_uri(self):
        m3u8_obj = self._get_m3u8_obj_with_best_bandwitdth(self.m3u8_uri)

        key_segments_pairs = self._construct_key_segment_pairs_by_m3u8(
            m3u8_obj)

        start_time = time.time()
        self._fetch_segments_to_local_tmpdir(len(m3u8_obj.segments),
                                             key_segments_pairs)
        fetch_end_time = time.time()

        self._merge_tmpdir_segments_to_mp4_by_ffmpeg(m3u8_obj)
        task_end_time = time.time()

        if len(self.fetched_file_names) < len(m3u8_obj.segments):
            utils.display_speed(start_time, fetch_end_time, task_end_time,
                                self.mp4_file_path)
