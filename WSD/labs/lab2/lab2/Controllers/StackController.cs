using Microsoft.AspNetCore.Mvc;

namespace lab2.Controllers
{
    public static class GlobalStack
    {
        private static List<int> stack = new();

        public static List<int> GetStack()
        {
            return stack;
        }

        public static void SetStack(List<int> newStack)
        {
            stack = newStack;
        }
    }


    [ApiController]
    [Route("api/Stack")]
    public class MyController : ControllerBase
    {
        private const string ResultKey = "result";
        private const string StackKey = "stack";
        private List<int> stack = new();

        private List<int> GetStack()
        {
            return GlobalStack.GetStack();
        }

        private void SetStack(List<int> new_stack)
        {
            GlobalStack.SetStack(new_stack);
        }

        private int GetResult()
        {
            var resultString = HttpContext.Session.GetString(ResultKey);
            return int.TryParse(resultString, out var result) ? result : 0;
        }

        private void SetResult(int result)
        {
            HttpContext.Session.SetString(ResultKey, result.ToString());
        }

        [HttpGet]
        public IActionResult Get()
        {
            var stack = GetStack();
            int clientResult = stack.Count > 0 ? GetResult() + stack[^1] : GetResult();
            return Ok(new { result = clientResult });
        }

        [Route("stack")]
        [HttpGet]
        public IActionResult GetStackAction()
        {
            var stack = GetStack();
            return Ok(new { result = stack.ToArray() });
        }

        [HttpPost]
        public IActionResult Post([FromQuery] int RESULT)
        {
            SetResult(RESULT);
            return Ok();
        }

        [HttpPut]
        public IActionResult Put([FromQuery] int ADD)
        {
            var stack = GetStack();
            stack.Add(ADD);
            SetStack(stack);
            return Ok();
        }

        [HttpDelete]
        public IActionResult Delete()
        {
            var stack = GetStack();
            if (stack.Count > 0)
            {
                stack.RemoveAt(stack.Count - 1);
                SetStack(stack);
            }
            return Ok();
        }
    }
}
