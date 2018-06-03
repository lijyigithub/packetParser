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
        Sucess,         // 解析成功
        NotComplete,    // 数据包不全
        Error,          // 数据包错误
        BadPrefix       // 错误的头部
    }

    public interface IPacket
    {
        Type PacketType { get; }
        DateTime ReceiveTime { get; }
        Slice Buffer { get; }
    }

    public struct DataFrame
    {
        public DateTime time;
        public Slice buffer;
    }

    delegate ParseResult TryParse(Slice buffer);
    delegate dynamic GetPacketFromBytes(Slice buffer);

    struct ParserFunc
    {
        public TryParse tryParse;
        public GetPacketFromBytes getPacketFromBytes;
    }

    public class StreamParser
    {
        private Stream io_stream;
        private List<ParserFunc> parsers;
        private List<IPacket> packets;
        private List<DataFrame> dataframes;
        private Buffer buffer;

        public delegate void newFrameHandler(Slice);
        public newFrameHandler OnNewFrame;
        public delegate void newPacketHandler(Slice);
        public newPacketHandler OnNewPacket;

        public StreamParser(Stream stream, bool background_thread=true, int default_size=65536)
        {
            io_stream = stream;
            buffer = new Buffer(default_size);
            dataframes = new List<DataFrame>(1024);
            packets = new List<IPacket>(1024);
            parsers = new List<ParserFunc>();
            OnNewFrame += (slice) => { };
            OnNewPacket += (slice) => { };
        }

        public void AddParser(Type packet_class)
        {
            // 检查是否实现了 IPacket 接口
            if (!packet_class.GetInterfaces().Contains<Type>(typeof(IPacket)))
                throw new ArgumentException();

            // 一个新的解析器
            ParserFunc _par = new ParserFunc();
            // 生成 TryParse 静态方法的委托
            MethodInfo mi = packet_class.GetMethod("TryParse", BindingFlags.Public | BindingFlags.Static);
            if (mi.ReturnType != typeof(ParseResult))
                throw new ArgumentException();
            _par.tryParse = Delegate.CreateDelegate(typeof(TryParse), mi) as TryParse;

            // 生成 GetPacketFromBytes 静态方法的委托
            mi = packet_class.GetMethod("GetPacketFromBytes", BindingFlags.Public | BindingFlags.Static);
            if (mi.ReturnType.IsInstanceOfType(typeof(IPacket)))
                throw new ArgumentException();
            _par.getPacketFromBytes = Delegate.CreateDelegate(typeof(GetPacketFromBytes), mi) as GetPacketFromBytes;

            // 添加到解析器列表
            parsers.Add(_par);
        }

        public void ReadAndParse()
        {
            byte[] bytes = new byte[4096] ;
            int readReadLength = io_stream.Read(bytes, 0, bytes.Length);
            buffer.Append(bytes.Take(readReadLength));

        }
    }

    public class Buffer
    {
        private int modulus = 1;
        private List<byte> buffer;
        private int read_index, write_index;
        private List<Slice> slices;
        private Slice parsed, unparsed, received;

        public Buffer(int default_size)
        {
            buffer = new List<byte>(default_size);
            read_index = 0;
            write_index = 0;
            slices = new List<Slice>(1024);
            parsed = new Slice(buffer, 0, 0);
            unparsed = new Slice(buffer, 0, 0);
            received = new Slice(buffer, 0, 0);
        }

        public int Count
        {
            get
            {
                return unparsed.Count;
            }
        }

        public int ReceivedCount
        {
            get
            {
                return received.Count;
            }
        }

        public Slice InBytes
        {
            get
            {
                return unparsed;
            }
        }

        public void Skip(int count)
        {
            lock (this)
            {
                if (count > unparsed.Count)
                    throw new ArgumentOutOfRangeException();

                read_index += count;
                parsed = new Slice(buffer, 0, read_index);
                unparsed = new Slice(buffer, read_index, write_index - read_index);
            }
        }

        public Slice CreateSlice(int offset, int count)
        {
            Slice temp;
            temp = new Slice(buffer, offset, count);
            slices.Add(temp);
            return temp;
        }

        public Slice Append(IEnumerable<byte> bytes)
        {
            lock (this)
            {
                Slice just_added;

                buffer.Concat(bytes);
                just_added = new Slice(buffer, write_index, bytes.Count());
                unparsed = new Slice(buffer, read_index, write_index - read_index);
                received = new Slice(buffer, 0, write_index);
                return just_added;
            }
        }

        public Slice All
        {
            get
            {
                return received;
            }
        }
    }
}
