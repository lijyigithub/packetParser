from packetParser import Slice, StreamParser
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



def main():
    unittest.main()

if __name__ == '__main__':
    main()