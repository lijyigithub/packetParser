from abc import ABCMeta, abstractclassmethod

class Slice():
    def __init__(self, arr, a, b):
        if not isinstance(arr, list) and not isinstance(arr, Slice):
            raise ValueError('arr shoue be instance of bytes')
        if a < 0:
            raise ValueError('a should larger than 0')
        if b >= len(arr):
            raise ValueError('b should less than length of array')
        if isinstance(arr, list):
            self.arr = arr
        else:
            isinstance(arr, Slice)
            self.arr = arr.arr
        self.a = a
        self.b = b

    def __eq__(self, other):
        assert isinstance(other ,Slice)
        if self.arr != other.arr:
            return False
        if self.a != other.a:
            return False
        if self.b != other.b:
            return False

        return True

    def __ne__(self, other):
        return not self == other

    def __getitem__(self, key):
        assert isinstance(key, int)
        return self.arr[self.a + key]

    def __iter__(self):
        for i in range(self.b - self.a):
            yield self.arr[i]

    def CreateSlice(self, a, b):
        return Slice(self.arr, self.a + a, self.b + b)

CreateSlice = lambda arr, a, b:Slice(arr, a, b)

class IPacket(metaclass=ABCMeta):
    @abstractclassmethod
    @staticmethod
    def tryParse(slice):
        pass

    @abstractclassmethod
    @staticmethod
    def getPacketFromBytes(slice):
        pass

class StreamParser():
    def __init__(self, read_stream, background_thread=True, default_size=65536):
        self.read_stream = read_stream
        self.buffer = Buffer()
        self.dataframes = list()
        self.packets = list()
        self.parsers = list()
        # TODO: 添加回调函数初始化
        if background_thread:
            pass
    
    def AddParser(self, parser):
        pass


class Buffer():
    pass

def main():
    l = list(range(100))
    s = CreateSlice(l, 0, 10)
    for b in s:
        print(b)


if __name__ == '__main__':
    main()