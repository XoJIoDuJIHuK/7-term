using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;

namespace lab3.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ErrorController : ControllerBase
    {
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public IActionResult GetError(int id)
        {
            switch (id)
            {
                case 0: return Ok(new { Detail = "Error not found by id" });
                case 1: return Ok(new { Detail = "User not found by id" });
                case 2: return Ok(new { Detail = "User ID mismatch" });
                case 3: return Ok(new { Detail = "User ID taken" });
                default:
                {
                    return BadRequest(new { HATEOS = 0 });
                }
            }
        }
    }
}