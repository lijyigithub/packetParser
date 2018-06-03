using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace PacketParser
{
    public static class ExtensionHolder
    {
        public static Slice CreateSlice(this List<byte> t, int a, int b)
        {
            return new Slice(t, a, b - a);
        }
    }

    public class Slice: List<byte>
    {
        private List<byte> targetlist;
        private int a;
        private int b;

        public Slice(List<byte> array, int a, int b)
        {
            targetlist = array ?? throw new NullReferenceException();
            if (a < 0)
                throw new IndexOutOfRangeException();
            if (b >= array.Count)
                throw new IndexOutOfRangeException();
            this.a = a;
            this.b = b;
        }

        public new byte this[int index]
        {
            get
            {
                return targetlist[a + index];
            }
            set
            {
                targetlist[a + index] = value;
            }
        }

        public void Reloc(int a, int b)
        {
            this.a = a;
            this.b = b;
        }

        public new int Count
        {
            get
            {
                return b-a;
            }
        }
    }
}
