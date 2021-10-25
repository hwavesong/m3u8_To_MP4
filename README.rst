.. image:: https://img.shields.io/pypi/v/m3u8-To-MP4?style=flat-square   :alt: PyPI


m3u8-To-MP4
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

To download a m3u8 video into a mp4 file, use the `download` functions:

.. code-block:: python

   import m3u8_to_mp4

   if __name__ == '__main__':
   
       m3u8_to_mp4.download('http://videoserver.com/playlist.m3u8')



Resume the transfer from the point of interruption, use the `tmpdir` arguement:

.. code-block:: python

   import m3u8_to_mp4

   if __name__ == '__main__':

       m3u8_to_mp4.download('http://videoserver.com/playlist.m3u8',tmpdir='/tmp/m3u8_xx')




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
* Align asynchronous implementation with multi-threads.
* Errors: application data after close notify.
* Extract independent asynchronous http package.
* Support IPv6.

.. _ffmpeg: http://www.ffmpeg.org/download.html