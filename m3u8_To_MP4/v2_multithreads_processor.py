# -*- coding: utf-8 -*-
import concurrent.futures
import logging
import os
import sys

from Crypto.Cipher import AES

from m3u8_To_MP4 import v2_abstract_processor
from m3u8_To_MP4.helpers import path_helper
from m3u8_To_MP4.helpers import printer_helper
from m3u8_To_MP4.networks.synchronous.sync_http_requester import request_for


def download_segment(segment_url):
    response_code, response_content = request_for(segment_url)

    return response_code, response_content


class MultiThreadsCrawler(v2_abstract_processor.AbstractCrawler):

    def _fetch_segments_to_local_tmpdir(self, key_segments_pairs):
        if len(key_segments_pairs) < 1:
            return

        progress_bar = printer_helper.ProcessBar(self.num_fetched_ts_segments, self.num_fetched_ts_segments + len(key_segments_pairs), 'segment set', 'downloading...', 'downloaded segments successfully!')

        key_url_encrypted_data_triple = list()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_concurrent) as executor:
            while len(key_segments_pairs) > 0:
                future_2_key_and_url = {executor.submit(download_segment, segment_url): (key, segment_url) for key, segment_url in key_segments_pairs}

                response_code, response_data = None, None
                for future in concurrent.futures.as_completed(future_2_key_and_url):
                    key, segment_url = future_2_key_and_url[future]
                    try:
                        response_code, response_data = future.result()
                    except Exception as exc:
                        logging.exception('{} generated an exception: {}'.format(segment_url, exc))

                    if response_code == 200:
                        key_url_encrypted_data_triple.append((key, segment_url, response_data))

                        key_segments_pairs.remove((key, segment_url))
                        progress_bar.update()

                if len(key_segments_pairs) > 0:
                    sys.stdout.write('\n')
                    logging.info('{} segments are failed to download, retry...'.format(len(key_segments_pairs)))

            logging.info('decrypt and dump segments...')
            for key, segment_url, encrypted_data in key_url_encrypted_data_triple:
                file_name = path_helper.resolve_file_name_by_uri(segment_url)
                file_path = os.path.join(self.tmpdir, file_name)

                if key is not None:
                    crypt_ls = {"AES-128": AES}
                    crypt_obj = crypt_ls[key.method]
                    cryptor = crypt_obj.new(key.value.encode(), crypt_obj.MODE_CBC)
                    encrypted_data = cryptor.decrypt(encrypted_data)

                with open(file_path, 'wb') as fin:
                    fin.write(encrypted_data)
