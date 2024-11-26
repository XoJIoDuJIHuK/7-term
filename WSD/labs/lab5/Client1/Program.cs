using System;

namespace Client1
{
    class Program
    {
        static void Main(string[] args)
        {
            ServiceReference1.Service1Client service1Client = new ServiceReference1.Service1Client();

            var sumResult = service1Client.Sum(
                new WCF.A { s = "hel", k = 1, f = 0.5f },
                new WCF.A { s = "lo", k = 2, f = 1.5f }
                );

            Console.WriteLine($"======  SUM  ======");
            Console.WriteLine($"\ns = {sumResult.s}\nf = {sumResult.f}\nk = {sumResult.k}\n\n");
            Console.WriteLine($"======  ADD  =======");
            Console.WriteLine($"\n{sumResult.k} + 10 = " + service1Client.Add(sumResult.k, 10) + "\n\n");
            Console.WriteLine($"=====  CONCAT  =====");
            Console.WriteLine($"\n{sumResult.s} + {sumResult.f} = " + service1Client.Concat(sumResult.s, sumResult.f) + "\n\n");

            service1Client.Close();

            Console.ReadKey();
        }
    }
}
