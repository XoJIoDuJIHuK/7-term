using System.Xml.Serialization;

namespace lab3
{
    public class Student
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Phone { get; set; }

        public string ToXML(string baseURI)
        {
            XmlSerializer xmlSerializer = new XmlSerializer(typeof(StudentHATEOS));
            using (StringWriter textWriter = new StringWriter())
            {
                xmlSerializer.Serialize(textWriter, new StudentHATEOS(this, baseURI));
                return textWriter.ToString();
            }
        }
    }

    public class StudentHATEOS : Student
    {
        public string GetURI {get; set;}
        public string UpdateURI {get; set;}
        public string DeleteURI {get; set;}

        public StudentHATEOS(Student s, string baseURI)
        {
            Id = s.Id;
            Name = s.Name;
            Phone = s.Phone;
            GetURI = UpdateURI = DeleteURI = $"{baseURI}{s.Id}";
        }
        public StudentHATEOS()
        {
            Id = 1337;
            Name = Phone = GetURI = UpdateURI = DeleteURI = "undefined";
        }
    }
}
