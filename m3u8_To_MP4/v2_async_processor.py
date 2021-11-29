# -*- coding: utf-8 -*-
from m3u8_To_MP4 import v2_abstract_task_processor
from m3u8_To_MP4.networks.asynchronous import async_producer_consumer


class AsynchronousFileCrawler(v2_abstract_task_processor.AbstractFileCrawler):

    def _fetch_segments_to_local_tmpdir(self, key_segments_pairs):
        async_producer_consumer.factory_pipeline(self.num_fetched_ts_segments, key_segments_pairs, self.available_addr_info_pool, self.num_concurrent, self.tmpdir)



class AsynchronousUriCrawler(v2_abstract_task_processor.AbstractUriCrawler):

    def _fetch_segments_to_local_tmpdir(self, key_segments_pairs):
        async_producer_consumer.factory_pipeline(self.num_fetched_ts_segments, key_segments_pairs, self.available_addr_info_pool, self.num_concurrent, self.tmpdir)
