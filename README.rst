.. image:: https://img.shields.io/pypi/v/m3u8-To-MP4?style=flat-square   :alt: PyPI


M3u8-To-MP4
============

Python downloader for saving m3u8 video to local MP4 file.

QuickStart
=============


Install m3u8_To_MP4 via pip
---------------------------------------


1. Preparation: configure ffmpeg. (e.g., Win10)

    * `Download <https://ffmpeg.org/download.html>`_ "release full" build. It will have the largest set of libraries with greater functionality.
    * Extract the contents in the ZIP file to a folder of your choice.
    * To add FFmpeg to Win10 path. (User variables -> Path -> New and add)
    * Verify. Open the Command Prompt or PowerShell window, type ffmpeg, and press Enter.

2. Installation: m3u8_To_MP4

    .. code-block:: python

       pip install m3u8_To_MP4



Download a mp4 vidoe from a m3u8 uri
---------------------------------------

There are two options to download a m3u8 video into a mp4 file: async and multi-threads.

Asynchronous downloader (recommend)
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
.. code-block:: python

   import m3u8_to_mp4

   if __name__ == '__main__':
       m3u8_to_mp4.async_download('http://videoserver.com/playlist.m3u8')



Multi-thread downloader
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
.. code-block:: python

   import m3u8_to_mp4

   if __name__ == '__main__':
       m3u8_to_mp4.multithread_download('http://videoserver.com/playlist.m3u8')
       # For compatibility, i reserve this api, but i do not recommend to you again.
       # m3u8_to_mp4.download('http://videoserver.com/playlist.m3u8')


Resuming
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
If you use default tmp dir, resuming the transfer from the point of interruption will be executed automatically (based on crc32 hashing).


Features
=============
#. Treat ffmpeg as a system service to achieve cross-platform.
#. If ffmpeg is not found, archiving is also supported. (v0.1.3 new features)
#. Resume from interruption. (based on crc32 temp directory path)
#. Use system tmp folder.
#. Concurrent requests based on the thread pool.
#. Concurrent requests based on efficient coroutines (v0.1.3 new features).
#. The retry strategy is carried out collectively after the whole cycle is repeated, avoiding the problem of short retry interval.


TODO
=============
* Catch exceptions during decryption. (Done)
* Align asynchronous implementation with multi-threads. (Done)
* Errors: application data after close notify.
* Extract independent asynchronous http package.
* Support IPv6.
* Compare ffmpeg/avconv/mencoder/moviepy.
* Support bilibili etc.


.. _ffmpeg: http://www.ffmpeg.org/download.html
