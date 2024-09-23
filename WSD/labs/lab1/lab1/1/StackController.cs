using Microsoft.AspNetCore.Mvc;

namespace lab1.Controllers
{
    [ApiController]
    [Route("api/Stack")]
    public class MyController : ControllerBase
    {
        private static int result = 0;
        private static Stack<int> stack = new Stack<int>();

        [HttpGet]
        public IActionResult Get()
        {
            int client_result = stack.Count > 0 ? result + stack.Peek() : result;
            return Ok(new { result = client_result });
        }

        [Route("stack")]
        [HttpGet]
        public IActionResult GetStack()
        {
            return Ok(new { result = stack.ToArray()});
        }

        [HttpPost]
        public IActionResult Post([FromQuery] int RESULT)
        {
            result = RESULT;
            return Ok();
        }

        [HttpPut]
        public IActionResult Put([FromQuery] int ADD)
        {
            stack.Push(ADD);
            return Ok();
        }

        [HttpDelete]
        public IActionResult Delete()
        {
            if (stack.Count > 0)
            {
                stack.Pop();
            }
            return Ok();
        }
    }
}
