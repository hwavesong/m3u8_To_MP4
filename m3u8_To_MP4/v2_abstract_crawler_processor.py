# -*- coding: utf-8 -*-
import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
import warnings
import zlib

from m3u8_To_MP4.helpers import path_helper
from m3u8_To_MP4.helpers import printer_helper
from m3u8_To_MP4.helpers.os_helper import get_core_count
from m3u8_To_MP4.networks.synchronous import sync_DNS

printer_helper.config_logging()


class AbstractCrawler(object):
    def __init__(self,
                 m3u8_uri,
                 file_path='./m3u8_To_MP4.mp4',
                 customized_http_header=None,
                 max_retry_times=3,
                 num_concurrent=50,
                 tmpdir=None
                 ):
        self.m3u8_uri = m3u8_uri
        self.customized_http_header = customized_http_header

        self.max_retry_times = max_retry_times
        self.num_concurrent = num_concurrent

        self.tmpdir = tmpdir

        self.file_path = file_path

    def __enter__(self):
        if self.tmpdir is None:
            self._apply_for_tmpdir()

        self.segment_path_recipe = os.path.join(self.tmpdir, "ts_recipe.txt")

        self._find_out_done_ts()

        self._legalize_file_path()
        # self._imitate_tar_file_path()

        print('\nsummary')
        print('m3u8_uri: {};\nmax_retry_times: {};\ntmp_dir: {};\nmp4_file_path: {};\n'.format(
                self.m3u8_uri, self.max_retry_times, self.tmpdir,
                self.file_path))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._freeup_tmpdir()

    def _apply_for_tmpdir(self):
        os_tmp_dir = tempfile.gettempdir()
        url_crc32_str = str(zlib.crc32(self.m3u8_uri.encode()))  # hash algorithm

        self.tmpdir = os.path.join(os_tmp_dir, 'm3u8_' + url_crc32_str)

        if not os.path.exists(self.tmpdir):
            os.mkdir(self.tmpdir)

    def _freeup_tmpdir(self):
        os_tmp_dir = tempfile.gettempdir()

        for file_symbol in os.listdir(os_tmp_dir):
            if file_symbol.startswith('m3u8_'):
                file_symbol_absolute_path = os.path.join(os_tmp_dir, file_symbol)

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

    def _legalize_file_path(self):
        parent = os.path.dirname(self.file_path)
        if not os.path.exists(parent):
            parent = os.getcwd()
            print('{} does not exists, remap to current directory.')

        name = os.path.basename(self.file_path)
        name = path_helper.calibrate_mp4_file_name(name)

        # if not is_valid:
        #     mp4_file_name = path_helper.create_mp4_file_name()
        self.file_path = os.path.join(parent, name)

        if os.path.exists(self.file_path):
            mp4_file_name = path_helper.random_name()
            self.file_path = os.path.join(parent, mp4_file_name)

    def _resolve_DNS(self):
        self.available_addr_info_pool = sync_DNS.available_addr_infos_of_url(self.m3u8_uri)
        self.best_addr_info = self.available_addr_info_pool[0]

        logging.info('Resolved available hosts:')
        for addr_info in self.available_addr_info_pool:
            logging.info('{}:{}'.format(addr_info.host, addr_info.port))

    def _create_tasks(self):
        raise NotImplementedError

    def _is_ads(self, segment_uri):
        if segment_uri.startswith(self.longest_common_subsequence):
            return True

        # if not segment_uri.endswith('.ts'):
        #     return True

        return False

    def _filter_ads_ts(self, key_segments_pairs):
        self.longest_common_subsequence = path_helper.longest_common_subsequence([segment_uri for _, segment_uri in key_segments_pairs])
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
        self.num_fetched_ts_segments = num_ts_segments - len(key_segments_pairs)

        return key_segments_pairs

    def _fetch_segments_to_local_tmpdir(self, key_segments_pairs):
        raise NotImplementedError

    def _construct_segment_path_recipe(self, key_segment_pairs):
        with open(self.segment_path_recipe, 'w', encoding='utf8') as fw:
            for _, segment in key_segment_pairs:
                file_name = path_helper.resolve_file_name_by_uri(segment)
                segment_file_path = file_name

                fw.write("file '{}'\n".format(segment_file_path))

    def _merge_to_mp4(self):
        if not self.file_path.endswith('mp4'):
            warnings.warn('{} does not end with .mp4'.format(self.file_path))

        logging.info("merging segments...")

        # copy mode
        merge_cmd = "ffmpeg " + \
                    "-y -f concat -threads {} -safe 0 ".format(get_core_count()) + \
                    "-i " + '"' + self.segment_path_recipe + '" ' + \
                    "-c copy " + \
                    '"' + self.file_path + '"'
        p = subprocess.Popen(merge_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        # change codec
        if os.path.getsize(self.file_path) < 1:
            logging.info("merged failed.")
            logging.info("change codec and re-merge segments (it may take long time.)")

            merge_cmd = "ffmpeg " + \
                        "-y -f concat -threads {} -safe 0 ".format(get_core_count()) + \
                        "-i " + '"' + self.segment_path_recipe + '" ' + \
                        '"' + self.file_path + '"'
            p = subprocess.Popen(merge_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.communicate()

    def _merge_to_ts(self):
        if not self.file_path.endswith('ts'):
            warnings.warn('{} does not end with .mp4'.format(self.file_path))

        ts_paths = list()
        with open(self.segment_path_recipe, 'r', encoding='utf8') as fr:
            for line in fr:
                line = line.strip()
                if len(line) < 1:
                    continue
                ts_paths.append(line[6:-1])

        with open(self.file_path, 'ab') as fw:
            for ts_path in ts_paths:
                with open(ts_path, 'rb') as fr:
                    fw.write(fr.read())

    def _merge_to_tar(self):
        if not self.file_path.endswith('tar'):
            warnings.warn('{} does not end with .mp4'.format(self.file_path))

        with tarfile.open(self.file_path, 'w:bz2') as targz:
            targz.add(name=self.tmpdir, arcname=os.path.basename(self.tmpdir))

    def fetch_mp4_by_m3u8_uri(self, format='ts'):

        if self.tmpdir is not None:
            os.mkdir(self.tmpdir, exist_ok=True)

        task_start_time = time.time()

        # preparation
        self._resolve_DNS()

        # resolve ts segment uris
        key_segments_pairs = self._create_tasks()
        if len(key_segments_pairs) < 1:
            raise ValueError('NO FOUND TASKS!\n Please check m3u8 url.')

        key_segments_pairs = self._filter_ads_ts(key_segments_pairs)
        self._construct_segment_path_recipe(key_segments_pairs)

        key_segments_pairs = self._filter_done_ts(key_segments_pairs)

        # download
        if len(key_segments_pairs) > 0:
            self._fetch_segments_to_local_tmpdir(key_segments_pairs)
        fetch_end_time = time.time()

        # merge
        if format == 'ts':
            self._merge_to_ts()
        elif format == 'mp4':
            self._merge_to_mp4()
        elif format == 'tar':
            self._merge_to_tar()

        task_end_time = time.time()
        printer_helper.display_speed(task_start_time, fetch_end_time, task_end_time, self.file_path)
