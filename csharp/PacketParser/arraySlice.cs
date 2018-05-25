using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace PacketParser
{
    public static class Extension<T>
    {
        public static Slice<T> createSlice(this T[] t, int a, int b)
        {
            return new Slice<T>(ref t, a, b - a);
        }
    }

    public class Slice<T>
    {
        private T[] _as;
        private int _offset;
        private int _count;

        public Slice(ref T[] array, int Offset, int Count)
        {
            if (array == null)
                throw new NullReferenceException();
            this._as = array;
            if (_offset < 0)
                throw new IndexOutOfRangeException();
            if (_offset + Count >= array.Length)
                throw new IndexOutOfRangeException();
            this._offset = Offset;
            this._count = Count;
        }

        public T this[int index]
        {
            get
            {
                return _as[_offset + index];
            }
            set
            {
                _as[_offset + index] = value;
            }
        }

        public void reloc(int a, int b)
        {
            this._offset = a;
            this._count = b - a;
        }

        public int Count
        {
            get
            {
                return this._as.Length;
            }
        }
    }
}
