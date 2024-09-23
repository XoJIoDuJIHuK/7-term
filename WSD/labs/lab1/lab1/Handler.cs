//using System;
//using System.Collections.Generic;
//using System.Web;
//using System.Web.SessionState;

//namespace PWS_Lab1
//{
//    public class MyHandler : IHttpHandler, IRequiresSessionState
//    {
//        private int _result;

//        public bool IsReusable => true;

//        public void ProcessRequest(HttpContext context)
//        {
//            var req = context.Request;
//            var res = context.Response;

//            var session = HttpContext.Current.Session;
//            var stack = session["Stack"] as Stack<int>;
//            Console.WriteLine(session.SessionID);

//            if (stack is null)
//            {
//                session["Stack"] = new Stack<int>();
//                stack = session["Stack"] as Stack<int>;
//            }


//            switch (req.HttpMethod)
//            {
//                case "GET":
//                    var result = (stack.Count > 0) ? (_result + stack.Peek()) : _result;
//                    res.ContentType = "application/json";
//                    res.Write("{\"result\": " + result + "}");
//                    break;

//                case "POST":
//                    if (!int.TryParse(req.QueryString["result"], out int resultParameter))
//                    {
//                        SendResponse(res, 400, "[ERROR] Enter integer parameter.");
//                        break;
//                    }
//                    _result = resultParameter;
//                    break;

//                case "PUT":
//                    if (!int.TryParse(req.QueryString["add"], out int addParameter))
//                    {
//                        SendResponse(res, 400, "[ERROR] Enter integer parameter.");
//                        break;
//                    }
//                    stack.Push(addParameter);
//                    break;

//                case "DELETE":
//                    if (stack.Count <= 0)
//                    {
//                        SendResponse(res, 400, "[ERROR] Stack is empty.");
//                        break;
//                    }
//                    stack.Pop();
//                    break;

//                default:
//                    SendResponse(res, 405, "[ERROR] Method Not Allowed.");
//                    break;
//            }
//        }

//        private void SendResponse(HttpResponse res, int code, string message)
//        {
//            res.StatusCode = code;
//            res.Write(message);
//        }
//    }
//}