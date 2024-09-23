using System.Xml.Serialization;

namespace lab3
{
    public class Student
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Phone { get; set; }

        public string ToXML()
        {
            XmlSerializer xmlSerializer = new XmlSerializer(typeof(Student));
            using (StringWriter textWriter = new StringWriter())
            {
                xmlSerializer.Serialize(textWriter, this);
                return textWriter.ToString();
            }
        }
    }

}
