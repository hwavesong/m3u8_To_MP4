# -*- coding: utf-8 -*-
import collections
import logging
import os.path

import m3u8

from m3u8_To_MP4.networks.synchronous import sync_http
from m3u8_To_MP4.v2_abstract_crawler_processor import AbstractCrawler

EncryptedKey = collections.namedtuple(typename='EncryptedKey',
                                      field_names=['method', 'value', 'iv'])


class M3u8FileIsVariantException(Exception):
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason


class M3u8PlaylistIsNoneException(Exception):
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason


class AbstractFileCrawler(AbstractCrawler):
    def __init__(self, m3u8_uri, m3u8_file_path, customized_http_header=None,
                 max_retry_times=3, num_concurrent=50, mp4_file_dir=None,
                 mp4_file_name='m3u8-To-Mp4.mp4', tmpdir=None):
        file_path=os.path.join(mp4_file_dir,mp4_file_name)
        super(AbstractFileCrawler, self).__init__(m3u8_uri,
                                                  file_path,
                                                  customized_http_header,
                                                  max_retry_times,
                                                  num_concurrent,
                                                  tmpdir)
        self.m3u8_file_path = m3u8_file_path

    def _read_m3u8_file(self):
        m3u8_str = ''
        with open(self.m3u8_file_path, 'r', encoding='utf8') as fin:
            m3u8_str = fin.read().strip()
        return m3u8_str

    def _construct_key_segment_pairs_by_m3u8(self, m3u8_obj):
        key_segments_pairs = list()
        for key in m3u8_obj.keys:
            if key:
                if key.method.lower() == 'none':
                    continue

                response_code, encryped_value = sync_http.retrieve_resource_from_url(
                    self.best_addr_info, key.absolute_uri,
                    customized_http_header=self.customized_http_header)

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

        if len(key_segments_pairs) == 0:
            raise M3u8PlaylistIsNoneException(name=self.m3u8_file_path,
                                              reason='M3u8 playlist is null!')

        return key_segments_pairs

    def _create_tasks(self):
        m3u8_str = self._read_m3u8_file()

        m3u8_obj = m3u8.loads(content=m3u8_str, uri=self.m3u8_uri)
        if m3u8_obj.is_variant:
            raise M3u8FileIsVariantException(self.m3u8_file_path,
                                             'M3u8 file is variant, and i do not support retrieve m3u8 in current mode!')

        logging.info("Read m3u8 file from {}".format(self.m3u8_file_path))

        key_segments_pairs = self._construct_key_segment_pairs_by_m3u8(
            m3u8_obj)

        return key_segments_pairs


class AbstractUriCrawler(AbstractCrawler):
    def _request_m3u8_obj_from_url(self):
        try:
            response_code, m3u8_bytes = sync_http.retrieve_resource_from_url(
                self.best_addr_info, self.m3u8_uri,
                customized_http_header=self.customized_http_header)
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
                    self.best_addr_info, key.absolute_uri,
                    customized_http_header=self.customized_http_header)

                if response_code != 200:
                    raise Exception('DOWNLOAD KEY FAILED, URI IS {}'.format(
                        key.absolute_uri))

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

    def _create_tasks(self):
        # resolve ts segment uris
        m3u8_obj = self._get_m3u8_obj_with_best_bandwitdth()

        key_segments_pairs = self._construct_key_segment_pairs_by_m3u8(
            m3u8_obj)

        return key_segments_pairs
