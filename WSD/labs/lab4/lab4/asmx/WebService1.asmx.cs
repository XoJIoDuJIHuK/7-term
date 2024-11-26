using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Script.Services;
using System.Web.Services;

namespace asmx
{
    /// <summary>
    /// Summary description for WebService1
    /// </summary>
    [WebService(Namespace = "http://TOV.com/", Description = "TOV Lab4")]
    [WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
    [System.ComponentModel.ToolboxItem(false)]
    // To allow this Web Service to be called from script, using ASP.NET AJAX, uncomment the following line. 
    // [System.Web.Script.Services.ScriptService]
    [ScriptService]
    public class WebService1 : System.Web.Services.WebService
    {

        [WebMethod(MessageName = "Add", Description = "Sum of two integer numbers")]
        public int Add(int x, int y)
        {
            return x + y;
        }

        [WebMethod(MessageName = "Concat", Description = "Concatenation of string and double values")]
        public string Concat(string s, double d)
        {
            return $"{s}{d}";
        }

        [WebMethod(MessageName = "Sum", Description = "Sum of two objects A")]
        public A Sum(A a1, A a2)
        {
            var result = new A(a1.s + a2.s, a1.k + a2.k, a1.f + a2.f);
            return result;
        }

        [ScriptMethod(ResponseFormat = ResponseFormat.Json)]
        [WebMethod()]
        public int AddS(int x, int y)
        {
            return x + y;
        }
    }

    public class A
    {
        public string s;
        public int k;
        public float f;

        public A()
        {
        }

        public A(string v1, int v2, float v3)
        {
            s = v1;
            k = v2;
            f = v3;
        }
    }
}
