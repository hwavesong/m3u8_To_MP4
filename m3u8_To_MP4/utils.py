# -*- coding: utf-8 -*-
import datetime
import logging
import os
import re
import sys


class ProcessBar:
    def __init__(self, progress, max_iter, prefix='Progress',
                 suffix='complete',
                 completed_suffix='completed', bar_length=50):
        self.progress = progress
        self.max_iter = max_iter

        self.bar_length = bar_length

        self.prefix = prefix
        self.suffix = suffix

        self.completed_suffix = completed_suffix

    def display(self):
        progress_rate = self.progress / self.max_iter

        percent = 100 * progress_rate

        filled_length = round(self.bar_length * progress_rate)
        bar = '#' * filled_length + '-' * (self.bar_length - filled_length)

        sys.stdout.write(
            '\r{}: |{}| {:.1f}% {}'.format(self.prefix, bar, percent,
                                           self.suffix))

        if self.progress == self.max_iter:
            sys.stdout.write(
                '\r{}: |{}| {:.1f}% {}'.format(self.prefix, bar, percent,
                                               self.completed_suffix))
            sys.stdout.write('\n')

        sys.stdout.flush()

    def update(self):
        self.progress += 1

        self.display()


def resolve_file_name_by_uri(uri):
    pattern = r".*\/(.*)"
    file_name = re.findall(pattern=pattern, string=uri)[0]
    return file_name


def display_speed(start_time, fetch_end_time, task_end_time,
                  target_mp4_file_path):
    download_time = fetch_end_time - start_time
    total_time = task_end_time - start_time

    download_speed = os.path.getsize(
        target_mp4_file_path) / download_time / 1024

    logging.info(
        "download successfully！ take {:.2f}s,  average download speed is {:.2f}KB/s".format(
            total_time, download_speed))


def calibrate_mp4_file_name(mp4_file_name):
    if mp4_file_name.strip() == '':
        return False, None

    banned_ls = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    for ch in banned_ls:
        mp4_file_name = mp4_file_name.replace(ch, '')

    return True, mp4_file_name


def create_mp4_file_name():
    mp4_file_name = 'm3u8_To_Mp4_{}.mp4'.format(
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return mp4_file_name
