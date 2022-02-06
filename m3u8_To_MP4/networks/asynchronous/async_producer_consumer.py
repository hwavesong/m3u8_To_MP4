# -*- coding: utf-8 -*-
import asyncio
import itertools
import logging
import os
import platform
# import random
import urllib.parse
import urllib.parse
from collections import Counter
from multiprocessing import JoinableQueue, Process

from Crypto.Cipher import AES

from m3u8_To_MP4.helpers import path_helper
from m3u8_To_MP4.helpers import printer_helper
from m3u8_To_MP4.networks import http_base
from m3u8_To_MP4.networks.asynchronous import async_http


async def ts_request(concurrent_condition, ssl_context, addr_info, _encrypted_key, segment_uri):
    async with concurrent_condition:
        response_header_state, response_content_bytes = await async_http.retrieve_resource_from_url(addr_info, segment_uri, ssl_context, limit=256 * 1024)
    return addr_info, segment_uri, response_header_state, _encrypted_key, response_content_bytes


async def ts_producer_scheduler(key_segment_pairs, addr_infos, ts_queue, num_concurrent, addr_quantity_statistics):
    exec_event_loop = asyncio.get_event_loop()

    # concurrent_condition = asyncio.Semaphore(value=50, loop=exec_event_loop)# Python 3.10 does not recommend
    concurrent_condition = asyncio.Semaphore(value=num_concurrent)

    scheme, domain_name_with_suffix, path, query, fragment = urllib.parse.urlsplit(key_segment_pairs[0][1])
    default_ssl_context = http_base.ssl_under_scheme(scheme)

    task_params = list()
    for (_encrypted_key, segment_uri), addr_info in zip(key_segment_pairs, itertools.cycle(addr_infos)):
        task_params.append((concurrent_condition, default_ssl_context, addr_info, _encrypted_key, segment_uri))

    awaitable_tasks = list()
    for params in task_params:
        awaitable_task = exec_event_loop.create_task(ts_request(*params))
        awaitable_tasks.append(awaitable_task)

    incompleted_tasks = list()
    for task in asyncio.as_completed(awaitable_tasks):
        addr_info, segment_uri, response_header_state, encrypted_key, encrypted_content_bytes = await task

        if response_header_state['response_code'] == 200:
            file_name = path_helper.resolve_file_name_by_uri(segment_uri)
            ts_queue.put((encrypted_key, encrypted_content_bytes, file_name))

        else:
            incompleted_tasks.append((encrypted_key, segment_uri))
            addr_quantity_statistics.update([addr_info.host])

    return incompleted_tasks, addr_quantity_statistics


def producer_process(key_segment_uris, addr_infos, ts_queue, num_concurrent):
    incompleted_tasks = key_segment_uris

    num_efficient_addr_info = int(len(addr_infos) * 0.5)
    num_efficient_addr_info = 1 if num_efficient_addr_info < 1 else num_efficient_addr_info

    addr_quantity_statistics = Counter({addr_info.host: 0 for addr_info in addr_infos})

    # solve error in windows: event loop is closed
    if platform.system().lower() == 'windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    while len(incompleted_tasks) > 0:
        incompleted_tasks, addr_quantity_statistics = asyncio.run(ts_producer_scheduler(incompleted_tasks, addr_infos, ts_queue, num_concurrent, addr_quantity_statistics))

        efficient_hosts = [host for host, _ in addr_quantity_statistics.most_common()]
        efficient_hosts = efficient_hosts[-num_efficient_addr_info:]
        addr_infos = [addr_info for addr_info in addr_infos if addr_info.host in efficient_hosts]
        # random.shuffle(addr_infos)

        if len(incompleted_tasks) > 0:
            print()
            logging.info('{} requests failed, retry ...'.format(len(incompleted_tasks)))


def consumer_process(ts_queue, tmpdir, progress_bar):
    while True:
        encrypted_key, encrypted_content, file_name = ts_queue.get()

        if encrypted_key is not None:
            crypt_ls = {"AES-128": AES}
            crypt_obj = crypt_ls[encrypted_key.method]
            cryptor = crypt_obj.new(encrypted_key.value.encode(), crypt_obj.MODE_CBC)
            encrypted_content = cryptor.decrypt(encrypted_content)

        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, 'wb') as fin:
            fin.write(encrypted_content)

        ts_queue.task_done()

        progress_bar.update()


def factory_pipeline(num_fetched_ts_segments, key_segments_pairs, available_addr_info_pool, num_concurrent, tmpdir):
    num_ts_segments = len(key_segments_pairs)
    progress_bar = printer_helper.ProcessBar(num_fetched_ts_segments, num_ts_segments + num_fetched_ts_segments, 'segment set', 'downloading...', 'downloaded segments successfully!')

    # schedule tasks
    ts_queue = JoinableQueue()

    ts_producer = Process(target=producer_process, args=(key_segments_pairs, available_addr_info_pool, ts_queue, num_concurrent))
    ts_consumer = Process(target=consumer_process, args=(ts_queue, tmpdir, progress_bar))

    ts_producer.start()
    
    ts_consumer.daemon = True
    ts_consumer.start()

    ts_producer.join()
