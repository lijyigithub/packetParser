using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using PacketParser;

namespace Test
{
    class Program
    {
        static void Main(string[] args)
        {
            byte[] temp = new byte[1024];
            for (int i = 0; i < 1024; i++)
            {
                temp[i] = (byte)i;
            }
            var s = temp.createSlice(0, 10);
            for (int i = 0; i < 10; i++)
            {
                Console.Write(s[i]);
                Console.Write(' ');
            }
            Console.WriteLine();
            temp = new byte[1024];
            s.UpdateRef(ref temp);
            for (int i = 0; i < 1024; i++)
            {
                temp[i] = (byte)(2 * i);
            }
            for (int i = 0; i < 10; i++)
            {
                Console.Write(s[i]);
                Console.Write(' ');
            }
            Console.WriteLine();

            Console.ReadKey();
        }
    }
}
