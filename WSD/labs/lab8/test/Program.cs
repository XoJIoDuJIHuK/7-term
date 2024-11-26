using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Threading.Tasks;
using System.Linq;

namespace test
{
    public class Request
    {
        public int? Id { get; set; }
        public string Method { get; set; }
        public Params Params { get; set; } = new Params();
        public string Jsonrpc { get; set; }
    }

    public class Request2
    {
        public int? Id { get; set; }
        public string Method { get; set; }
        public string[] Params { get; set; }
        public string Jsonrpc { get; set; }
    }

    public class Response
    {
        public int? Id { get; set; }
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public object Result { get; set; } = null;
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public RpcError Error { get; set; } = null;
        public string Jsonrpc { get; set; }
    }
    public class RpcException : Exception
    {
        public int Code { get; set; }

        public RpcException(string message, int code) : base(message)
        {
            Code = code;
        }
    }
    public class RpcError
    {
        public int Code { get; set; }
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public string Message { get; set; }
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public object Data { get; set; }
    }

    public class Params
    {
        public string K { get; set; } = null;
        public int? X { get; set; } = null;

    }

    internal class Program
    {
        static string validSingleDictRequest = "{\"id\":1,\"jsonrpc\": \"2.0\",\"params\": {\"k\": 1,\"x\": 20},\"method\": \"SetM\"}";
        static string invalidSingleDictRequest = "{\"id\":1, \"jsonrpc\": \"2.0\", \"params\": {\"k\": 1,\"x\": 20}}";
        static string validSingleArrRequest = "[1, \"2.0\",[1, 20],\"SetM\"]";

        static List<string> allowedMethods = new List<string> { "GetM", "SetM", "AddM", "SubM", "MulM", "DivM", "ErrorExit" };

        public static void Main()
        {
            ProcessRequest(validSingleDictRequest);
        }

        private static void ProcessRequest(object req)
        {
            // remove in webapp
            object jsonObject = JContainer.Parse(req.ToString());

            List<Request> responses = new List<Request>();

            if (jsonObject is JArray dataArray)
            {
                if (dataArray.Count == 0)
                {
                    throw new RpcException("Make at least one request", 4);
                }
                if (dataArray[0] is JObject)
                {
                    foreach (var item in dataArray)
                    {
                        Request response;
                        if (item is JObject) response = ProcessDictRequest((JObject)item);
                        else if (item is JArray) response = ProcessArrRequest((JArray)item);
                        else throw new RpcException("Invalid request", 5);
                        responses.Add(response);
                    }
                    Console.WriteLine(responses);
                }
                else
                {
                    var response = ProcessArrRequest((JArray)dataArray);
                    Console.WriteLine(response);
                }
            }
            else
            {
                var response = ProcessDictRequest((JContainer)jsonObject);
                Console.WriteLine(response);
            }
        }

        //private Response RPCOperationProcess(Request req)
        //{

        //}


        private static Response ProcessArrRequest(JArray jsonObject)
        {
            try
            {
                if (jsonObject.Count != 4) throw new RpcException("Invalid array request", 7);
                var idProperty = jsonObject[0];
                if (idProperty is null) throw new RpcException("ID must not be null", 1);
                if (!int.TryParse(idProperty.ToString(), out int requestId)) throw new RpcException("ID must be a number", 2);

                var jsonrpcProperty = jsonObject[1];
                if (jsonrpcProperty is null || jsonrpcProperty.ToString() != "2.0") throw new RpcException("Invalid protocol", 3);

                var paramsProperty = jsonObject[2];
                if (!(paramsProperty is JArray)) throw new RpcException("Params must be stored in array", 8);
                var paramsArray = (JArray)paramsProperty;
                if (paramsArray.Count != 2) throw new RpcException("There must be exactly 2 params", 9);

                var k = paramsArray[0];
                if (k is null || string.IsNullOrEmpty(k.ToString())) throw new RpcException("K must be a non-empty string", 10);

                var x = paramsArray[1];
                if (x is null || x.Type != JTokenType.Integer) throw new RpcException("X must be an integer", 11);


                var methodProperty = jsonObject[3];
                if (methodProperty is null || methodProperty.Type != JTokenType.String || !allowedMethods.Contains(methodProperty.ToString())) throw new RpcException("Invalid method", 12);

                return new Response()
                {
                    Id = int.Parse(idProperty.ToString()),
                    Method = methodProperty.ToString(),
                    Params = new Params()
                    {
                        K = k.ToString(),
                        X = int.Parse(x.ToString())
                    },
                    Jsonrpc = jsonrpcProperty.ToString(),
                };
            }
            catch (RpcException ex)
            {
                return new Response
                {
                    Id = null,
                    Error = new RpcError
                    {
                        Code = ex.Code,
                        Message = ex.Message
                    },
                    Jsonrpc = "2.0"
                };
            }
        }

        private static Request ProcessDictRequest(JContainer jsonObject)
        {
            var idProperty = jsonObject["id"];
            if (idProperty is null) throw new RpcException("ID must not be null", 1);
            if (!int.TryParse(idProperty.ToString(), out int requestId)) throw new RpcException("ID must be a number", 2);

            var jsonrpcProperty = jsonObject["jsonrpc"];
            if (jsonrpcProperty is null || jsonrpcProperty.ToString() != "2.0") throw new RpcException("Invalid protocol", 3);

            var paramsProperty = jsonObject["params"];
            //var paramsObject = (JObject)paramsProperty;
            if (paramsProperty is null || paramsProperty.Type != JTokenType.Object) throw new RpcException("Params must be stored in dictionary", 8);
            
            var k = paramsProperty["k"];
            if (k is null || string.IsNullOrEmpty(k.ToString())) throw new RpcException("K must be a non-empty string", 10);

            var x = paramsProperty["x"];
            if (x is null || x.Type != JTokenType.Integer) throw new RpcException("X must be an integer", 11);


            var methodProperty = jsonObject["method"];
            if (methodProperty is null || methodProperty.Type != JTokenType.String || !allowedMethods.Contains(methodProperty.ToString())) throw new RpcException("Invalid method", 12);

            return new Request()
            {
                Id = int.Parse(idProperty.ToString()),
                Method = methodProperty.ToString(),
                Params = new Params()
                {
                    K = k.ToString(),
                    X = int.Parse(x.ToString())
                },
                Jsonrpc = jsonrpcProperty.ToString(),
            };
        }
    }
}
