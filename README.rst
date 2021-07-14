.. image:: https://img.shields.io/pypi/v/m3u8-To-MP4?style=flat-square   :alt: PyPI


m3u8-To-MP4
============

Python downloader for saving m3u8 video to local MP4 file.

QuickStart
=============


Install m3u8_To_MP4 by pip
---------------------------------------

Configure ffmpeg_.

.. code-block:: python

   pip install m3u8_To_MP4


Download a mp4 vidoe from a m3u8 uri
---------------------------------------

To download a m3u8 video into a mp4 file, use the `download` functions:

.. code-block:: python

    import m3u8_to_mp4

    m3u8_to_mp4.download('http://videoserver.com/playlist.m3u8')



Resume the transfer from the point of interruption, use the `tmpdir` arguement:

.. code-block:: python

    import m3u8_to_mp4

    m3u8_to_mp4.download('http://videoserver.com/playlist.m3u8',tmpdir='/tmp/m3u8_xx')




Features
=============
#. Treat ffmpeg as a system service to achieve cross-platform.
#. Resume from interruption.
#. Use system tmp folder.
#. Concurrent requests based on the thread pool.
#. The retry strategy is carried out collectively after the whole cycle is repeated, avoiding the problem of short retry interval.

.. _ffmpeg: http://www.ffmpeg.org/download.html