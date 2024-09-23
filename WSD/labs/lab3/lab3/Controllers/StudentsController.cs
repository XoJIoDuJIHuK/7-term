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

        public StudentsController(StudentContext context)
        {
            _context = context;
        }

        // GET: api/students
        [HttpGet]
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
            [FromQuery] bool xml = false
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
                    Phone = selectedColumns.Contains("PHONE") ? s.Phone : null
                }).ToListAsync();
                return Ok(result);
            }

            var students = await query.ToListAsync();
            if (xml)
            {
                XmlSerializer xmlSerializer = new XmlSerializer(typeof(List<Student>));
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

        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> GetStudent(
            int id,
            [FromQuery] bool xml = false
        )
        {
            var student = await _context.Students.FindAsync(id);
            if (student == null)
            {
                return BadRequest(new { HATEOS = 1 });
            }
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(),
                    StatusCode = 200
                };
            }

            return Ok(student);
        }

        // POST: api/students
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> CreateStudent(
            Student student,
            [FromQuery] bool xml = false
        )
        {
            if (await _context.Students.FindAsync(student.Id) != null)
            {
                return BadRequest(new { HATEOS = 3});
            }
            _context.Students.Add(student);
            await _context.SaveChangesAsync();
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(),
                    StatusCode = 200
                };
            }
            return CreatedAtAction(nameof(GetStudent), new { id = student.Id }, student);
        }

        // PUT: api/students/5
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> UpdateStudent(
            int id,
            Student student,
            [FromQuery] bool xml = false
        )
        {
            if (id != student.Id)
            {
                return BadRequest(new { HATEOS = 2 });
            }

            _context.Entry(student).State = EntityState.Modified;
            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!_context.Students.Any(e => e.Id == id))
                    return BadRequest(new { HATEOS = 1 });
                throw;
            }
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(),
                    StatusCode = 200
                };
            }

            return Ok(student);
        }

        // DELETE: api/students/5
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> DeleteStudent(
            int id,
            [FromQuery] bool xml = false
        )
        {
            var student = await _context.Students.FindAsync(id);
            if (student == null)
            {
                return BadRequest(new { HATEOS = 1 });
            }

            _context.Students.Remove(student);
            await _context.SaveChangesAsync();
            if (xml)
            {
                return new ContentResult{
                    ContentType = "application/xml",
                    Content = student.ToXML(),
                    StatusCode = 200
                };
            }
            return Ok();
        }
    }

}
