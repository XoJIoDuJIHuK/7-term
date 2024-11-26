using lab8.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Web;
using System.Web.Http;
using System.Web.Mvc;
using HttpPostAttribute = System.Web.Http.HttpPostAttribute;

namespace lab8.Controllers
{
    [SessionState(System.Web.SessionState.SessionStateBehavior.Required)]

    public class JRServiceController : ApiController
    {
        private bool ignoreMethods = false;
        static List<string> allowedMethods = new List<string> { "GetM", "SetM", "AddM", "SubM", "MulM", "DivM", "ErrorExit" };

        [HttpPost]
        public async Task<IHttpActionResult> Process(object req)
        {
            try
            {
                List<Response> responses = new List<Response>();

                if (req is JArray dataArray)
                {
                    if (dataArray.Count == 0)
                    {
                        throw new RpcException("Make at least one request", 4);
                    }
                    if (dataArray[0] is JArray || dataArray[0] is JObject)
                    {
                        foreach (var item in dataArray)
                        {
                            Response response;
                            if (item is JObject) response = ProcessDictRequest((JObject)item);
                            //else if (item is JArray) response = ProcessArrRequest((JArray)item);
                            else throw new RpcException("Invalid request", 5);
                            responses.Add(response);
                        }
                        return Ok(responses);
                    }
                    else
                    {
                        var response = ProcessArrRequest((JArray)dataArray);
                        return Ok(response);
                    }
                }
                else
                {
                    var response = ProcessDictRequest((JContainer)req);
                    return Ok(response);
                }
            }
            catch (Exception ex)
            {
                return Ok(new Response
                {
                    Error = new RpcError
                    {
                        Code = -32700,
                        Message = "Parse error"
                    },
                    Jsonrpc = "2.0"
                });
            }
        }

        private Response ProcessArrRequest(JArray jsonObject)
        {
            // INCORRECT, DO NOT USE
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

                var kProperty = paramsArray[0];
                if (kProperty is null || string.IsNullOrEmpty(kProperty.ToString())) throw new RpcException("K must be a non-empty string", 10);

                var xProperty = paramsArray[1];
                if (xProperty is null || !int.TryParse(xProperty.ToString(), out int x)) throw new RpcException("X must be an integer", 11);


                var methodProperty = jsonObject[3];
                if (methodProperty is null || methodProperty.Type != JTokenType.String || !allowedMethods.Contains(methodProperty.ToString())) throw new RpcException("Invalid method", 12);

                return RPCOperationProcess(new Request()
                {
                    Id = int.Parse(idProperty.ToString()),
                    Method = methodProperty.ToString(),
                    Params = new Params()
                    {
                        K = kProperty.ToString(),
                        X = int.Parse(x.ToString())
                    },
                    Jsonrpc = jsonrpcProperty.ToString(),
                });
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

        private Response ProcessDictRequest(JContainer jsonObject)
        {
            try
            {
                var idProperty = jsonObject["id"];
                if (idProperty is null) throw new RpcException("ID must not be null", 1);
                if (!int.TryParse(idProperty.ToString(), out int requestId)) throw new RpcException("ID must be a number", 2);

                var jsonrpcProperty = jsonObject["jsonrpc"];
                if (jsonrpcProperty is null || jsonrpcProperty.ToString() != "2.0") throw new RpcException("Invalid protocol", 3);

                var paramsProperty = jsonObject["params"];
                JToken kProperty = null;
                JToken xProperty = null;
                if (paramsProperty is null) throw new RpcException("Params must not be null", 8);
                if (paramsProperty.Type == JTokenType.Object)
                {
                    kProperty = paramsProperty["k"];
                    xProperty = paramsProperty["x"];
                }
                else if (paramsProperty.Type == JTokenType.Array)
                {
                    var arr = (JArray)paramsProperty;
                    if (arr.Count != 2) throw new RpcException("Invalid params count", 13);
                    kProperty = arr[0];
                    xProperty = arr[1];
                }
                else
                {
                    throw new RpcException($"Unknown type {paramsProperty.Type}", 9);
                }
                if (kProperty is null || string.IsNullOrEmpty(kProperty.ToString())) throw new RpcException("K must be a non-empty string", 10);
                if (xProperty is null || !int.TryParse(xProperty.ToString(), out int x)) throw new RpcException("X must be an integer", 11);


                var methodProperty = jsonObject["method"];
                if (methodProperty is null || methodProperty.Type != JTokenType.String || !allowedMethods.Contains(methodProperty.ToString())) throw new RpcException("Invalid method", 12);

                return RPCOperationProcess(new Request()
                {
                    Id = int.Parse(idProperty.ToString()),
                    Method = methodProperty.ToString(),
                    Params = new Params()
                    {
                        K = kProperty.ToString(),
                        X = int.Parse(x.ToString())
                    },
                    Jsonrpc = jsonrpcProperty.ToString(),
                });
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

        private Response RPCOperationProcess(Request req)
        {
            try
            {
                int tempValue = 0;
                ValidRequst(req);

                if (ignoreMethods)
                    return null;

                Response response = new Response
                {
                    Id = req.Id,
                    Jsonrpc = "2.0"
                };

                try
                {
                    switch (req.Method)
                    {
                        case "SetM":
                            if (req.Params == null || string.IsNullOrEmpty(req.Params.K) || req.Params.X == null)
                                throw new RpcException("Invalid params", -32602);

                            HttpContext.Current.Session[req.Params.K] = req.Params.X;
                            response.Result = GetValue(req.Params.K);
                            break;

                        case "GetM":
                            if (req.Params == null || string.IsNullOrEmpty(req.Params.K))
                                throw new RpcException("Invalid params", -32602);

                            response.Result = GetValue(req.Params.K);
                            break;

                        case "AddM":
                            if (req.Params == null || string.IsNullOrEmpty(req.Params.K) || req.Params.X == null)
                                throw new RpcException("Invalid params", -32602);

                            tempValue = GetValue(req.Params.K);
                            tempValue += req.Params.X ?? 0;
                            HttpContext.Current.Session[req.Params.K] = tempValue;
                            response.Result = GetValue(req.Params.K);
                            break;
                        case "SubM":
                            if (req.Params == null || string.IsNullOrEmpty(req.Params.K) || req.Params.X == null)
                                throw new RpcException("Invalid params", -32602);

                            tempValue = GetValue(req.Params.K);
                            tempValue -= req.Params.X ?? 0;
                            HttpContext.Current.Session[req.Params.K] = tempValue;
                            response.Result = GetValue(req.Params.K);
                            break;

                        case "MulM":
                            if (req.Params == null || string.IsNullOrEmpty(req.Params.K) || req.Params.X == null)
                                throw new RpcException("Invalid params", -32602);

                            tempValue = GetValue(req.Params.K);
                            tempValue *= req.Params.X ?? 0;
                            HttpContext.Current.Session[req.Params.K] = tempValue;
                            response.Result = GetValue(req.Params.K);
                            break;

                        case "DivM":
                            if (req.Params == null || string.IsNullOrEmpty(req.Params.K) || req.Params.X == null)
                                throw new RpcException("Invalid params", -32602);

                            tempValue = GetValue(req.Params.K);
                            tempValue /= req.Params.X ?? 0;
                            HttpContext.Current.Session[req.Params.K] = tempValue;
                            response.Result = GetValue(req.Params.K);
                            break;

                        case "ErrorExit":
                            ignoreMethods = true;
                            HttpContext.Current.Session.Clear();
                            break;

                        default:
                            throw new RpcException("Uknown method", -32601);
                    }
                    if (response.Result == null)
                        response.Result = "";
                }
                catch (RpcException ex)
                {
                    response.Error = new RpcError
                    {
                        Code = ex.Code,
                        Message = ex.Message,
                    };
                }

                return response;

            }
            catch (RpcException ex)
            {
                return new Response
                {
                    Id = req == null ? null : req.Id,
                    Error = new RpcError
                    {
                        Code = ex.Code,
                        Message = ex.Message
                    },
                    Jsonrpc = "2.0"
                };
            }
            catch (Exception ex)
            {
                return new Response
                {
                    Id = req == null ? null : req.Id,
                    Error = new RpcError
                    {
                        Code = -32603,
                        Message = "Internal error"
                    },
                    Jsonrpc = "2.0"
                };
            }
        }

        private void ValidRequst(Request req)
        {
            if (req == null)
                throw new RpcException("Parse error", -32700);
            if (req.Jsonrpc != "2.0")
                throw new RpcException("Invalid request", -32600);
            if (string.IsNullOrEmpty(req.Method))
                throw new RpcException("Method not found", -32601);
        }

        private int GetValue(string key)
        {
            var data = HttpContext.Current.Session[key];
            if (data == null)
                return 0;

            if (int.TryParse(data.ToString(), out var value))
                return value;

            return 0;
        }
    }
}