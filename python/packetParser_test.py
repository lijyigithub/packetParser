import time
from packetParser import Slice, StreamParser, Buffer, ParseResult
import unittest

class TestSlice(unittest.TestCase):
    """Test Slice"""

    def test_basic(self):
        l = list(bytes(range(100)))
        s = Slice(l, 0, 10)
        s_ = Slice(l, 0, 10)
        self.assertEqual(id(s.arr), id(l))
        self.assertEqual(s.arr, l)
        self.assertEqual(s, s_)
        s_ = s[:-1]
        self.assertNotEqual(s, s_)
        self.assertEqual(s.a, 0)
        self.assertEqual(s.b, 10)
        self.assertEqual(len(s), 10)

    def test_value(self):
        l = list(range(100))
        s = Slice(l, 0, 10)
        self.assertEqual(list(s), list(range(10)))
        s.Reloc(10, 20)
        self.assertEqual(s.a, 10)
        self.assertEqual(s.b, 20)
        self.assertEqual(list(s), list(range(10, 20)))
        for i in range(10):
            self.assertEqual(s[i], i+10)

    def test_subslice(self):
        l = list(range(100))
        s = Slice(l, 0, 10)
        s1 = s[1:3]
        self.assertEqual(s1.arr, l)
        self.assertEqual(s1.a, 1)
        self.assertEqual(s1.b, 3)
        s2 = s[:3]
        self.assertEqual(s2.arr, l)
        self.assertEqual(s2.a, 0)
        self.assertEqual(s2.b, 3)
        s3 = s[2:]
        self.assertEqual(s3.arr, l)
        self.assertEqual(s3.a, 2)
        self.assertEqual(s3.b, 10)
        s4 = s[:]
        self.assertEqual(s4.arr, l)
        self.assertEqual(s4.a, 0)
        self.assertEqual(s4.b, 10)
        s = Slice(l, 10, 20)
        s5 = s[-2:-1]
        self.assertEqual(s5.arr, l)
        self.assertEqual(s5.a, 18)
        self.assertEqual(s5.b, 19)

    def test_buffer_basic(self):
        buf = Buffer(4096)
        self.assertEqual(buf.length, 0)
        self.assertIsInstance(buf.buffer, list)
        self.assertSequenceEqual(buf.buffer, [None]*4096)
        buf.Append(bytes(list(range(10))))
        self.assertEqual(buf.length, 10)
        self.assertEqual(len(buf), 10)
        self.assertListEqual(list(buf.InBytes), list(range(10)))
        buf.Skip(1)
        self.assertEqual(len(buf), 10)
        self.assertEqual(len(buf.InBytes), 9)
        self.assertListEqual(list(buf.InBytes), list(range(1, 10)))
        buf.Skip(9)
        self.assertEqual(len(buf), 10)
        self.assertEqual(len(buf.InBytes), 0)
        self.assertListEqual(list(buf.InBytes), list())
        buf.Append([1]*4086)
        buf.Skip(4086)
        self.assertEqual(len(buf.InBytes), 0)
        buf.Append(bytes(range(0,20,2)))
        self.assertEqual(len(buf.InBytes), 10)
        self.assertListEqual(list(buf.InBytes), list(range(0, 20, 2)))

    def test_streamparser(self):
        def read(size):
            return bytes(list(range(10)))
        read_obj = type('test_object', (object,), dict(read=read))
        import queue
        q = queue.Queue(maxsize=200)
        s = StreamParser(read_obj, background_thread=False, packet_queue=q)
        class Packet0to9:
            def __init__(self, buf):
                self.ReceiveTime = time.time()
                self.buffer = buf[:10]
            @staticmethod
            def tryParse(buf):
                if len(buf) < 10:
                    return ParseResult.NotComplete
                elif list(buf) == list(range(10)):
                    return ParseResult.Sucess
                else:
                    return ParseResult.Error

            @classmethod
            def getPacketFromBytes(cls, buf):
                return cls(buf)

        s.AddParser(Packet0to9)
        number = 0
        def printdf(s):
            nonlocal number
            self.assertIsInstance(s, Slice)
            number += 1
        def printpkt(p):
            nonlocal number
            self.assertIsInstance(p, Packet0to9)
            self.assertListEqual(list(p.buffer), list(range(10)))
            number += 1
        s.OnNewDataFrame.append(printdf)
        s.OnNewPacket.append(printpkt)
        for _ in range(50):
            s.ReadAndParse()
        self.assertEqual(number, 100)
        self.assertEqual(q.qsize(), 50)



def main():
    unittest.main()

if __name__ == '__main__':
    main()