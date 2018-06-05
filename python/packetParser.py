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
        if isinstance(key, int):
            return self.arr[self.a + key]
        elif isinstance(key, slice):
            if key.step is not None and key.step != 1:
                raise ValueError('Step should be 1')
            start = 0
            end = 0
            if key.start is None:
                start = self.a
            else:
                if key.start >=0:
                    start = self.a + key.start
                else:
                    start = self.b + key.start
            
            if key.stop is None:
                end = self.b
            else:
                if key.stop >= 0:
                    end = self.a + key.stop
                else:
                    end = self.b + key.stop
            
            return Slice(self.arr, start, end)

    def __iter__(self):
        for i in range(self.a, self.b):
            yield self.arr[i]

    def __len__(self):
        return self.b - self.a

    def Reloc(self, a, b):
        self.a = a
        self.b = b

    def CreateSlice(self, a, b):
        return Slice(self.arr, self.a + a, self.a + b)


class StreamParser():
    def __init__(self, read_stream, background_thread=True, default_size=65536):
        r_stream = None
        import random
        import string
        type_name = 'ReadObject_' + ''.join([random.choice(string.ascii_letters) for _ in range(32)])
        if hasattr(read_stream, 'recv'):
            # socket
            r_stream = type(type_name, (object,), dict(read=read_stream.recv))
        elif hasattr(read_stream, 'read'):
            # file or serial
            r_stream = type(type_name, (object,), dict(read=read_stream.read))
        else:
            raise ValueError('read_stream shoud be instance of file, socket, serial or object has method like .read(size).')
        self.read_stream = r_stream
        self.buffer = Buffer(default_size)
        self.dataframes = list()
        self.packets = list()
        self.parsers = list()
        self.OnNewDataFrame = list()
        self.OnNewPacket = list()
        if background_thread:
            import threading
            self.thread = threading.Thread(target=self.RunForever)
            self.thread.setDaemon(True)
            self.thread.run()
    
    def AddParser(self, parser):
        pass

    def ReadAndParse(self):
        buf = None
        try:
            buf = self.read_stream.read(4096)
        except TimeoutError:
            pass

        self.buffer.Append(buf)



class Buffer():
    pass
