using System;
using System.ServiceModel;

namespace Host
{
    class Program
    {
        static void Main(string[] args)
        {
            using (var host = new ServiceHost(typeof(WCF.Service1)))
            {
                host.Open();
                Console.WriteLine("Service ready\t{0}", host.BaseAddresses[0].AbsoluteUri);
                Console.WriteLine("Service ready\t{0}", host.BaseAddresses[1].AbsoluteUri);
                Console.WriteLine("Press Enter to stop the service...");
                Console.ReadLine();
                host.Close();
            }
        }
    }
}
