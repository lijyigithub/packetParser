using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Reflection;

namespace PacketParser
{
    public enum ParseResult
    {
        Sucess,
        NotComplete,
        Error,
        BadPrefix
    }

    public interface IPacket
    {
        Type packetType { get; }
        DateTime receiveTime { get; }
        Slice<byte> buffer { get; }
    }

    public struct DataFrame
    {
        public DateTime time;
        public Slice<byte> buffer;
    }

    delegate ParseResult _tryParse(Slice<byte> buffer);
    delegate dynamic _getPacketFromBytes(Slice<byte> buffer);

    struct _ParserFunc
    {
        public _tryParse tryParse;
        public _getPacketFromBytes getPacketFromBytes;
    }

    public class StreamParser
    {
        private Stream io_stream;
        private List<_ParserFunc> parsers;
        private List<IPacket> packets;
        private List<DataFrame> dataframes;
        private Buffer buffer;

        public delegate void newFrameHandler();
        public newFrameHandler OnNewFrame;
        public delegate void newPacketHandler();
        public newPacketHandler OnNewPacket;

        public StreamParser(Stream stream)
        {
            io_stream = stream;
            buffer = new Buffer();
            dataframes = new List<DataFrame>(1024);
            packets = new List<IPacket>(1024);
            parsers = new List<_ParserFunc>();
            OnNewFrame += () => { };
            OnNewPacket += () => { };
        }

        public void addParser(Type packet_class)
        {
            if (!packet_class.GetInterfaces().Contains<Type>(typeof(IPacket)))
                throw new ArgumentException();
            _ParserFunc _par = new _ParserFunc();
            MethodInfo mi = packet_class.GetMethod("tryParse", BindingFlags.Public | BindingFlags.Static);
            if (mi.ReturnType != typeof(ParseResult))
                throw new ArgumentException();
            _par.tryParse = Delegate.CreateDelegate(typeof(_tryParse), mi) as _tryParse;
            mi = packet_class.GetMethod("getPacketFromBytes", BindingFlags.Public | BindingFlags.Static);
            if (mi.ReturnType.IsInstanceOfType(typeof(IPacket)))
                throw new ArgumentException();
            _par.getPacketFromBytes = Delegate.CreateDelegate(typeof(_getPacketFromBytes), mi) as _getPacketFromBytes;

            parsers.Add(_par);
        }
    }

    public class Buffer
    {
        private int _buffer_size = 1024 * 1024;
        private int _modulus = 1;
        private byte[] _buffer;
        private int _read_index, _write_index;
        private List<Slice<byte>> _slices;
        private Slice<byte> _parsed, _unparsed, _received;

        public Buffer()
        {
            _buffer = new byte[_buffer_size * _modulus];
            _read_index = 0;
            _write_index = 0;
            _slices = new List<Slice<byte>>(1024);
            _parsed = new Slice<byte>(ref _buffer, 0, 0);
            _unparsed = new Slice<byte>(ref _buffer, 0, 0);
            _received = new Slice<byte>(ref _buffer, 0, 0);
        }

        public int Count
        {
            get
            {
                return _unparsed.Count;
            }
        }

        public int receivedCount
        {
            get
            {
                return _received.Count;
            }
        }

        public Slice<byte> InBytes
        {
            get
            {
                return _unparsed;
            }
        }

        public void Skip(int count)
        {
            lock (this)
            {
                Console.WriteLine("Skipped: " + count.ToString());
                if (count > _unparsed.Count)
                    throw new ArgumentOutOfRangeException();

                _read_index += count;
                _parsed = new Slice<byte>(ref _buffer, 0, _read_index);
                _unparsed = new Slice<byte>(ref _buffer, _read_index, _write_index - _read_index);
            }
        }

        public Slice<byte> createSlice(int offset, int count)
        {
            Slice<byte> temp;
            temp = new Slice<byte>(ref _buffer, offset, count);
            _slices.Add(temp);
            return temp;
        }

        public void disposeSlice(Slice<byte> slice)
        {
            if (!_slices.Contains(slice))
                throw new ArgumentOutOfRangeException();
            _slices.Remove(slice);
        }

        public Slice<byte> append(byte[] bytes)
        {
            lock (this)
            {
                Slice<byte> just_added;

                if (bytes.Length + _write_index > _buffer.Length)
                {
                    // 空间不够的话，直接翻倍
                    _modulus *= 2;
                    byte[] temp = new byte[_buffer_size * _modulus];
                    _buffer.CopyTo(temp, 0);
                    _buffer = temp;
                }

                bytes.CopyTo(_buffer, _write_index);
                just_added = new Slice<byte>(ref _buffer, _write_index, bytes.Length);
                _write_index += bytes.Length;
                _unparsed = new Slice<byte>(ref _buffer, _read_index, _write_index - _read_index);
                _received = new Slice<byte>(ref _buffer, 0, _write_index);
                return just_added;
            }
        }

        public Slice<byte> All
        {
            get
            {
                return _received;
            }
        }
    }
}
