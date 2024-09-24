using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Xml.Serialization;

namespace lab3.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class StudentsController : ControllerBase
    {
        private readonly StudentContext _context;
        private readonly string baseURI;
        private readonly string errorURI;

        public StudentsController(StudentContext context)
        {
            _context = context;
            baseURI = "http://localhost:5242/api/Students/";
            errorURI = "http://localhost:5242/api/Error/";
        }

        private IActionResult GetErrorResponse(int code, bool xml)
        {
            if (xml)
            {
                return BadRequest($"<ErrorURI>{errorURI}{code}</ErrorURI>");
            }
            else
            {
                return BadRequest(new { ErrorURI = $"{errorURI}{code}" });
            }
        }

        // GET: api/students
        [HttpGet(".{format}/")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> GetStudents(
            [FromQuery] int? limit,
            [FromQuery] int? offset,
            [FromQuery] string? sort,
            [FromQuery] int? minid,
            [FromQuery] int? maxid,
            [FromQuery] string? like,
            [FromQuery] string? globalike,
            [FromQuery] string? columns,
            string format = "json"
        )
        {
            var query = _context.Students.AsQueryable();

            // Фильтрация по minid и maxid
            if (minid.HasValue)
                query = query.Where(s => s.Id >= minid.Value);
            if (maxid.HasValue)
                query = query.Where(s => s.Id <= maxid.Value);

            // Фильтрация по полю NAME
            if (!string.IsNullOrEmpty(like))
                query = query.Where(s => s.Name.Contains(like));

            // Глобальный фильтр
            if (!string.IsNullOrEmpty(globalike))
                query = query.Where(s => (s.Id.ToString() + s.Name + s.Phone).Contains(globalike));

            // Сортировка
            if (!string.IsNullOrEmpty(sort) && sort.ToLower() == "name")
                query = query.OrderBy(s => s.Name);
            else
                query = query.OrderBy(s => s.Id);

            if (offset.HasValue)
                query = query.Skip(offset.Value);

            if (limit.HasValue)
                query = query.Take(limit.Value);

            // Выбор столбцов
            if (!string.IsNullOrEmpty(columns))
            {
                var selectedColumns = columns.Split(",").Select(c => c.Trim().ToUpper()).ToArray();
                var result = await query.Select(s => new
                {
                    Id = selectedColumns.Contains("ID") ? s.Id : (int?)null,
                    Name = selectedColumns.Contains("NAME") ? s.Name : null,
                    Phone = selectedColumns.Contains("PHONE") ? s.Phone : null,
                    CreateURI = baseURI
                }).ToListAsync();
                return Ok(result);
            }

            var students = (await query.ToListAsync()).Select(e => new StudentHATEOS(e, baseURI))
            .ToList();
            if (format == "xml")
            {
                XmlSerializer xmlSerializer = new XmlSerializer(typeof(List<StudentHATEOS>));
                using (StringWriter textWriter = new StringWriter())
                {
                    xmlSerializer.Serialize(textWriter, students);
                    string xmlStudents = textWriter.ToString();
                    return new ContentResult{
                        ContentType = "application/xml",
                        Content = xmlStudents,
                        StatusCode = 200
                    };
                }
            }
            return Ok(students);
        }

        [HttpGet(".{format}/{id}/")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> GetStudent(
            int id,
            string format = "json"
        )
        {
            bool xml = format == "xml";
            var student = await _context.Students.FindAsync(id);
            if (student == null)
            {
                return GetErrorResponse(1, xml);
            }
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(baseURI),
                    StatusCode = 200
                };
            }

            return Ok(new StudentHATEOS(student, baseURI));
        }

        // POST: api/students
        [HttpPost(".{format}/")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> CreateStudent(
            Student student,
            string format = "json"
        )
        {
            bool xml = format == "xml";
            if (await _context.Students.FindAsync(student.Id) != null)
            {
                return GetErrorResponse(3, xml);
            }
            _context.Students.Add(student);
            await _context.SaveChangesAsync();
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(baseURI),
                    StatusCode = 200
                };
            }
            return Ok(new StudentHATEOS(student, baseURI));
        }

        // PUT: api/students/5
        [HttpPut(".{format}/{id}/")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> UpdateStudent(
            int id,
            Student student,
            string format = "json"
        )
        {
            bool xml = format == "xml";
            if (id != student.Id)
            {
                return GetErrorResponse(2, xml);
            }

            _context.Entry(student).State = EntityState.Modified;
            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!_context.Students.Any(e => e.Id == id))
                    return GetErrorResponse(1, xml);
                throw;
            }
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(baseURI),
                    StatusCode = 200
                };
            }

            return Ok(new StudentHATEOS(student, baseURI));
        }

        // DELETE: api/students/5
        [HttpDelete(".{format}/{id}/")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> DeleteStudent(
            int id,
            string format = "json"
        )
        {
            bool xml = format == "xml";
            var student = await _context.Students.FindAsync(id);
            if (student == null)
            {
                return GetErrorResponse(1, xml);
            }

            _context.Students.Remove(student);
            await _context.SaveChangesAsync();
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(baseURI),
                    StatusCode = 200
                };
            }
            return Ok();
        }
    }

}
