.. image:: https://img.shields.io/pypi/v/m3u8-To-MP4?style=flat-square   :alt: PyPI


m3u8-To-MP4
============

Python downloader for saving m3u8 video to local MP4 file.

QuickStart
=============


Install m3u8_To_MP4 via pip
---------------------------------------


.. code-block:: python

   1. Preparation: configure ffmpeg.
      e.g., Win10
      - `Download <https://ffmpeg.org/download.html>`_ "release full" build. It will have the largest set of libraries with greater functionality.
      - Extract the contents in the ZIP file to a folder of your choice.
      - To add FFmpeg to Win10 path. (User variables -> Path -> New and add)
      - Verify. Open the Command Prompt or PowerShell window, type ffmpeg, and press Enter.
   2. Installation: m3u8_To_MP4
      pip install m3u8_To_MP4


Download a mp4 vidoe from a m3u8 uri
---------------------------------------

To download a m3u8 video into a mp4 file, use the `download` functions:

.. code-block:: python

    import m3u8_To_MP4 as mpp

    mpp.download('http://videoserver.com/playlist.m3u8')



Resume the transfer from the point of interruption, use the `tmpdir` arguement:

.. code-block:: python

    import m3u8_To_MP4 as mpp

    mpp.download('http://videoserver.com/playlist.m3u8',tmpdir='/tmp/m3u8_xx')



Parameters to the .download() method : 
---------------------------------------------

1. Retry URL : max_retry_times=3, 
2. Specify the MP4 Directory : mp4_file_dir='./', 
3. Specify the MP4 file name : mp4_file_name='m3u8_To_Mp4.mp4'

Example : 

.. code-block:: python

    import m3u8_To_MP4 as mpp

    mpp.download('http://videoserver.com/playlist.m3u8',tmpdir='/tmp/m3u8_xx', max_retry_times=3, max_num_workers=100,
             mp4_file_dir='./', mp4_file_name='m3u8_To_Mp4.mp4', tmpdir=None)







Features
=============
#. Treat ffmpeg as a system service to achieve cross-platform.
#. Resume from interruption.
#. Use system tmp folder.
#. Concurrent requests based on the thread pool and coroutine mechanism.
#. The retry strategy is carried out collectively after the whole cycle is repeated, avoiding the problem of short retry interval.

.. _ffmpeg: http://www.ffmpeg.org/download.html