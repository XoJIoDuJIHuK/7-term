using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace lab8.Models
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

}