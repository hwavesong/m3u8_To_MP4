import unittest
import hashlib
import m3u8_To_MP4 

testURI = "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8 "
mp4Path = "./data/test.mp4"
mp4MD5 = "ee39e2f004949d7e94ea40fb93b88465"

def getMD5(filePath):
    with open(filePath, 'rb') as f:
        data = f.read()
        MD5 = hashlib.md5(data).hexdigest()
    return MD5

class TestDownloadFunction(unittest.TestCase):

    def test_download(self):
        m3u8_To_MP4.multithread_download(testURI, file_path=mp4Path, max_num_workers=40, max_retry_times=5)
        self.assertEqual(mp4MD5, getMD5(mp4Path))

if __name__ == '__main__':
    unittest.main()