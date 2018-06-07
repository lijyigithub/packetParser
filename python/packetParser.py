import time

class Slice():
    def __init__(self, arr, a, b):
        if not isinstance(arr, list) and not isinstance(arr, Slice):
            raise ValueError('arr shoue be instance of bytes')
        if a < 0:
            raise ValueError('a should larger than 0')
        if b > len(arr):
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

class ParseResult:
    Sucess = 0
    NotComplete = 1
    BadSuffix = 2
    Error = 3

class StreamParser():
    def __init__(self, read_stream, background_thread=True, default_size=65536, packet_queue=None):
        r_stream = None
        self.queue = None
        if packet_queue is not None:
            import queue
            assert isinstance(packet_queue, queue.Queue)
            self.queue = packet_queue
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
        self.mutex = None
        if background_thread:
            import threading
            self.thread = threading.Thread(target=self.RunForever)
            self.thread.setDaemon(True)
            self.notstop = True
            self.mutex = threading.Lock()
            self.thread.run()
    
    def AddParser(self, parser):
        assert hasattr(parser, 'tryParse')
        assert hasattr(parser.tryParse, '__call__')
        assert hasattr(parser, 'getPacketFromBytes')
        assert hasattr(parser.getPacketFromBytes, '__call__')
        self.mutex and self.mutex.acquire()
        try:
            self.parsers.append(parser)
        finally:
            self.mutex and self.mutex.release()

    def ReadAndParse(self):
        buf = None
        try:
            buf = self.read_stream.read(4096)
        except TimeoutError:
            pass

        self.mutex and self.mutex.acquire()
        try:
            df = self.buffer.Append(buf)
            self.dataframes.append(df)
            for cb in self.OnNewDataFrame:
                cb(df)

            while len(self.buffer.InBytes) > 0:
                parse_result = [par.tryParse(self.buffer.InBytes) for par in self.parsers]
                if ParseResult.Sucess in parse_result:
                    index = parse_result.index(ParseResult.Sucess)
                    packet = self.parsers[index].getPacketFromBytes(self.buffer.InBytes)
                    self.packets.append(packet)
                    if self.queue is not None:
                        self.queue.put(packet)
                    for cb in self.OnNewPacket:
                        cb(packet)
                    self.buffer.Skip(len(packet.buffer))
                elif all([r != ParseResult.NotComplete for r in parse_result]):
                    self.buffer.Skip(1)
                else:
                    break
        finally:
            self.mutex and self.mutex.release()

    def RunForever(self):
        while self.notstop:
            self.ReadAndParse()

    def Stop(self):
        self.mutex and self.mutex.acquire()
        self.notstop = False
        self.mutex.release()

class Buffer():
    def __init__(self, size):
        # 预分配空间
        self.buffer = [None] * size
        self.out_index = 0
        self.length = 0
        self.inbytes = Slice(self.buffer, 0, 0)

    def __len__(self):
        return self.length

    @property
    def InBytes(self):
        return self.inbytes

    def Append(self, buf):
        if isinstance(buf, bytes):
            buf = list(buf)
        assert isinstance(buf, list)
        start = self.out_index
        stop = self.out_index + len(buf)
        if stop > len(self.buffer):
            stop = None
        self.buffer[start:stop] = buf
        self.length = start + len(buf)
        self.inbytes.Reloc(start, self.length)
        return Slice(self.buffer, start, self.length)

    def Skip(self, n):
        assert isinstance(n, int)
        assert self.out_index + n <= self.length
        self.out_index += n
        self.inbytes.Reloc(self.out_index, self.length)

    def CreateSlice(self, a, b):
        assert a >= 0
        assert b > a
        assert b <= self.length
        return Slice(self.buffer, a, b)
