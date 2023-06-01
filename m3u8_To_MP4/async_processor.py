# -*- coding: utf-8 -*-
import collections
import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
import zlib

import m3u8

from m3u8_To_MP4.helpers import path_helper
from m3u8_To_MP4.helpers import printer_helper
from m3u8_To_MP4.networks.asynchronous import async_producer_consumer
from m3u8_To_MP4.networks.synchronous import sync_DNS
from m3u8_To_MP4.networks.synchronous import sync_http

printer_helper.config_logging()

EncryptedKey = collections.namedtuple(typename='EncryptedKey',
                                      field_names=['method', 'value', 'iv'])


class Crawler(object):
    def __init__(self, m3u8_uri, max_retry_times=3, num_concurrent=50,
                 mp4_file_dir=None, mp4_file_name='m3u8-To-Mp4.mp4',
                 tmpdir=None,
                 proxy=None):
        self.m3u8_uri = m3u8_uri

        self.max_retry_times = max_retry_times
        self.num_concurrent = num_concurrent

        self.tmpdir = tmpdir
        self.proxy = proxy
        self.mp4_file_dir = mp4_file_dir
        self.mp4_file_name = mp4_file_name

        self.use_ffmpeg = True

    def __enter__(self):
        if self.tmpdir is None:
            self._apply_for_tmpdir()

        self.segment_path_recipe = os.path.join(self.tmpdir, "ts_recipe.txt")

        self._find_out_done_ts()

        self._legalize_mp4_file_path()
        self._imitate_tar_file_path()

        print('\nsummary')
        print(
            'm3u8_uri: {};\nmax_retry_times: {};\ntmp_dir: {};\nmp4_file_path: {};\n'.format(
                self.m3u8_uri, self.max_retry_times, self.tmpdir,
                self.mp4_file_path))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._freeup_tmpdir()

    def _apply_for_tmpdir(self):
        os_tmp_dir = tempfile.gettempdir()
        url_crc32_str = str(
            zlib.crc32(self.m3u8_uri.encode()))  # hash algorithm

        self.tmpdir = os.path.join(os_tmp_dir, 'm3u8_' + url_crc32_str)

        if not os.path.exists(self.tmpdir):
            os.mkdir(self.tmpdir)

    def _freeup_tmpdir(self):
        os_tmp_dir = tempfile.gettempdir()

        for file_symbol in os.listdir(os_tmp_dir):
            if file_symbol.startswith('m3u8_'):
                file_symbol_absolute_path = os.path.join(os_tmp_dir,
                                                         file_symbol)

                if os.path.isdir(file_symbol_absolute_path):
                    shutil.rmtree(file_symbol_absolute_path)

    def _find_out_done_ts(self):
        file_names_in_tmpdir = os.listdir(self.tmpdir)

        full_ts_file_names = list()
        for file_name in reversed(file_names_in_tmpdir):
            if file_name == 'ts_recipe.txt':
                continue

            absolute_file_path = os.path.join(self.tmpdir, file_name)
            if os.path.getsize(absolute_file_path) > 0:
                full_ts_file_names.append(file_name)

        self.fetched_file_names = full_ts_file_names

    def _legalize_mp4_file_path(self):
        if self.mp4_file_dir is None:
            self.mp4_file_dir = os.getcwd()

        is_valid, mp4_file_name = path_helper.calibrate_mp4_file_name(
            self.mp4_file_name)
        if not is_valid:
            mp4_file_name = path_helper.create_mp4_file_name()

        mp4_file_path = os.path.join(self.mp4_file_dir, mp4_file_name)

        if os.path.exists(mp4_file_path):
            mp4_file_name = path_helper.create_mp4_file_name()
            mp4_file_path = os.path.join(self.mp4_file_dir, mp4_file_name)

        self.mp4_file_path = mp4_file_path

    def _imitate_tar_file_path(self):
        self.tar_file_path = self.mp4_file_path[:-4] + '.tar.bz2'

    def _resolve_DNS(self):
        self.available_addr_info_pool = sync_DNS.available_addr_infos_of_url(
            self.m3u8_uri)
        self.best_addr_info = self.available_addr_info_pool[0]

        logging.info('Resolved available hosts:')
        for addr_info in self.available_addr_info_pool:
            logging.info('{}:{}'.format(addr_info.host, addr_info.port))

    def _request_m3u8_obj_from_url(self):
        try:
            response_code, m3u8_bytes = sync_http.retrieve_resource_from_url(
                self.best_addr_info, self.m3u8_uri)
            if response_code != 200:
                raise Exception(
                    'DOWNLOAD KEY FAILED, URI IS {}'.format(self.m3u8_uri))

            m3u8_str = m3u8_bytes.decode()
            m3u8_obj = m3u8.loads(content=m3u8_str, uri=self.m3u8_uri)
        except Exception as exc:
            logging.exception(
                'Failed to load m3u8 file,reason is {}'.format(exc))
            raise Exception('FAILED TO LOAD M3U8 FILE!')

        return m3u8_obj

    def _get_m3u8_obj_with_best_bandwitdth(self):
        m3u8_obj = self._request_m3u8_obj_from_url()

        if m3u8_obj.is_variant:

            best_bandwidth = -1
            best_bandwidth_m3u8_uri = None

            for playlist in m3u8_obj.playlists:
                if playlist.stream_info.bandwidth > best_bandwidth:
                    best_bandwidth = playlist.stream_info.bandwidth
                    best_bandwidth_m3u8_uri = playlist.absolute_uri

            logging.info("Choose the best bandwidth, which is {}".format(
                best_bandwidth))
            logging.info("Best m3u8 uri is {}".format(best_bandwidth_m3u8_uri))

            self.m3u8_uri = best_bandwidth_m3u8_uri

            m3u8_obj = self._request_m3u8_obj_from_url()

        return m3u8_obj

    def _construct_key_segment_pairs_by_m3u8(self, m3u8_obj):
        key_segments_pairs = list()
        for key in m3u8_obj.keys:
            if key:
                if key.method.lower() == 'none':
                    continue

                response_code, encryped_value = sync_http.retrieve_resource_from_url(
                    self.best_addr_info, key.absolute_uri)

                if response_code != 200:
                    raise Exception('DOWNLOAD KEY FAILED, URI IS {}'.format(
                        key.absolute_uri))

                encryped_value = encryped_value.decode()
                _encrypted_key = EncryptedKey(method=key.method,
                                              value=encryped_value, iv=key.iv)

                key_segments = m3u8_obj.segments.by_key(key)
                segments_by_key = [(_encrypted_key, segment.absolute_uri) for
                                   segment in key_segments]

                key_segments_pairs.extend(segments_by_key)

        if len(key_segments_pairs) == 0:
            _encrypted_key = None

            key_segments = m3u8_obj.segments
            segments_by_key = [(_encrypted_key, segment.absolute_uri) for
                               segment in key_segments]

            key_segments_pairs.extend(segments_by_key)

        return key_segments_pairs

    def _is_ads(self, segment_uri):
        if segment_uri.startswith(self.longest_common_subsequence):
            return True

        if not segment_uri.endswith('.ts'):
            return True

        return False

    def _filter_ads_ts(self, key_segments_pairs):
        self.longest_common_subsequence = path_helper.longest_common_subsequence(
                [segment_uri for _, segment_uri in key_segments_pairs])
        key_segments_pairs = [(_encrypted_key, segment_uri) for
                              _encrypted_key, segment_uri in key_segments_pairs
                              if not self._is_ads(segment_uri)]

        return key_segments_pairs

    def _is_fetched(self, segment_uri):
        file_name = path_helper.resolve_file_name_by_uri(segment_uri)

        if file_name in self.fetched_file_names:
            return True

        return False

    def _filter_done_ts(self, key_segments_pairs):
        num_ts_segments = len(key_segments_pairs)
        key_segments_pairs = [(_encrypted_key, segment_uri) for
                              _encrypted_key, segment_uri in key_segments_pairs
                              if not self._is_fetched(segment_uri)]
        self.num_fetched_ts_segments = num_ts_segments - len(
            key_segments_pairs)

        return key_segments_pairs

    def _fetch_segments_to_local_tmpdir(self, key_segments_pairs):
        async_producer_consumer.factory_pipeline(self.num_fetched_ts_segments,
                                                 key_segments_pairs,
                                                 self.available_addr_info_pool,
                                                 self.num_concurrent,
                                                 self.tmpdir,
                                                 self.proxy)

    def _construct_segment_path_recipe(self, key_segment_pairs):
        with open(self.segment_path_recipe, 'w', encoding='utf8') as fw:
            for _, segment in key_segment_pairs:
                file_name = path_helper.resolve_file_name_by_uri(segment)
                segment_file_path = os.path.join(self.tmpdir, file_name)

                fw.write("file '{}'\n".format(segment_file_path))

    def _merge_to_mp4_by_ffmpeg(self):
        merge_cmd = "ffmpeg -y -f concat -safe 0 -i " + '"' + self.segment_path_recipe + '"' + " -c copy " + '"' + self.mp4_file_path + '"'
        p = subprocess.Popen(merge_cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        logging.info("merging segments...")

        p.communicate()

    def _merge_to_mp4_by_os(self):
        raise NotImplementedError

    def _merge_to_tar_by_os(self):
        with tarfile.open(self.tar_file_path, 'w:bz2') as targz:
            targz.add(name=self.tmpdir, arcname=os.path.basename(self.tmpdir))

    def fetch_mp4_by_m3u8_uri(self, as_mp4):
        task_start_time = time.time()

        # preparation
        self._resolve_DNS()

        # resolve ts segment uris
        m3u8_obj = self._get_m3u8_obj_with_best_bandwitdth()

        key_segments_pairs = self._construct_key_segment_pairs_by_m3u8(
            m3u8_obj)

        key_segments_pairs = self._filter_ads_ts(key_segments_pairs)
        self._construct_segment_path_recipe(key_segments_pairs)

        key_segments_pairs = self._filter_done_ts(key_segments_pairs)

        # download
        if len(key_segments_pairs) > 0:
            self._fetch_segments_to_local_tmpdir(key_segments_pairs)
        fetch_end_time = time.time()

        if as_mp4:
            self._merge_to_mp4_by_ffmpeg()

            task_end_time = time.time()
            printer_helper.display_speed(task_start_time, fetch_end_time,
                                         task_end_time, self.mp4_file_path)
        else:
            self._merge_to_tar_by_os()

            task_end_time = time.time()
            printer_helper.display_speed(task_start_time, fetch_end_time,
                                         task_end_time, self.tar_file_path)
