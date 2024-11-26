using System;

namespace Client2
{
    class Program
    {
        static void Main(string[] args)
        {
            ServiceReference1.Service1Client client = new ServiceReference1.Service1Client("NetTcpEndpoint"); // Use the name of the endpoint

            try
            {
                var sumResult = client.Sum(
                new WCF.A { s = "hel", k = 1, f = 0.5f },
                new WCF.A { s = "lo", k = 2, f = 1.5f }
                );

                Console.WriteLine($"======  SUM  ======");
                Console.WriteLine($"\ns = {sumResult.s}\nf = {sumResult.f}\nk = {sumResult.k}\n\n");
                Console.WriteLine($"======  ADD  =======");
                Console.WriteLine($"\n{sumResult.k} + 10 = " + client.Add(sumResult.k, 10) + "\n\n");
                Console.WriteLine($"=====  CONCAT  =====");
                Console.WriteLine($"\n{sumResult.s} + {sumResult.f} = " + client.Concat(sumResult.s, sumResult.f) + "\n\n");

                client.Close();

                Console.ReadKey();
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error: " + ex.Message);
                client.Abort();
            }
        }
    }
}
