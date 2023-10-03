# -*- coding: utf-8 -*-
import logging
import os
import sys


def config_logging():
    str_format = '%(asctime)s | %(levelname)s | %(message)s'
    logging.basicConfig(format=str_format, level=logging.INFO)


class ProcessBar:
    def __init__(self, progress, max_iter, prefix='Progress',
                 suffix='downloading', completed_suffix='completed',
                 bar_length=50, tracker=None):
        self.progress = progress
        self.max_iter = max_iter

        self.bar_length = bar_length

        self.prefix = prefix
        self.suffix = suffix

        self.completed_suffix = completed_suffix
        self.tracker = tracker

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
        if self.tracker:
            self.tracker(self.progress)
        self.display()


def display_speed(start_time, fetch_end_time, task_end_time, target_mp4_file_path):
    download_time = fetch_end_time - start_time
    total_time = task_end_time - start_time

    if download_time < 0.01:
        download_speed = os.path.getsize(target_mp4_file_path) / 1024
    else:
        download_speed = os.path.getsize( target_mp4_file_path) / download_time / 1024

    logging.info( "download successfully！ take {:.2f}s,  average download speed is {:.2f}KB/s".format( total_time, download_speed))
