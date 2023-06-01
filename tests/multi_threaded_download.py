import unittest
import hashlib
import m3u8_To_MP4 

def getMD5(filePath):
    with open(filePath, 'rb') as f:
        data = f.read()
        MD5 = hashlib.md5(data).hexdigest()
    return MD5

class TestDownloadFunction(unittest.TestCase):

    def test_multithread_download(self):
        testURI = "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8"
        mp4Path = "./data/test_multithread_download.mp4"
        mp4MD5 = "ee39e2f004949d7e94ea40fb93b88465"
        m3u8_To_MP4.multithread_download(testURI, file_path=mp4Path, max_num_workers=60,
                                         max_retry_times=5)
        self.assertEqual(mp4MD5, getMD5(mp4Path))

    def test_multithread_proxy_download(self):
        testURI = "https://stream.us-central1-b.swagit.com/on-demand/_definst_/mp4:vault01/dentontx/b90ebdf3-69a0-4c06-9fba-1c41c2c4d949.mp4/playlist.m3u8"
        mp4Path = "./data/test_multithread_proxy_download.mp4"
        mp4MD5 = "2ffd46cbb1da38e1518ea9ed09b03948"
        m3u8_To_MP4.multithread_download(testURI, file_path=mp4Path, max_num_workers=60,
                                         max_retry_times=5, proxy="http://coxswain-proxy-nginx.coxswain.svc.sandbox.internal:8080")
        self.assertEqual(mp4MD5, getMD5(mp4Path))

if __name__ == '__main__':
    unittest.main()