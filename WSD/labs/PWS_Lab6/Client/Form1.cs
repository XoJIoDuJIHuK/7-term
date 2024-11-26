using System;
using System.Data;
using System.Linq;
using System.Windows.Forms;
using WSKNSModel;

namespace Client
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            WSKNSEntities service = new WSKNSEntities(new Uri("http://localhost:60376/Service1.svc"));

            foreach (var s in service.student.AsEnumerable())
            {
                this.listBox1.Items.Add(s.id.ToString() + " " + s.name);
            }
            foreach (var s in service.note.AsEnumerable())
            {
                this.listBox2.Items.Add(s.id.ToString() + " " + s.stud_id + " " + s.subject + " " + s.note1);
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (textBox1.Text != "")
            {
                try
                {
                    WSKNSEntities service = new WSKNSEntities(new Uri("http://localhost:60376/Service1.svc"));
                    student student = new student() { };
                    student.name = textBox1.Text;
                    service.AddTostudent(student);

                    service.SaveChanges();
                    this.listBox1.Items.Clear();
                    foreach (var s in service.student.AsEnumerable())
                    {
                        this.listBox1.Items.Add(s.id.ToString() + " " + s.name);
                    }
                }
                catch (Exception exc)
                {
                    label8.Text = exc.Message;
                }
            }
            else
            {
                label8.Text = "Ввеедите данные";
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            try
            {
                WSKNSEntities service = new WSKNSEntities(new Uri("http://localhost:60376/Service1.svc"));
				int id = this.listBox1.SelectedIndex;
				//int id = 1;
                if (id != -1)
                {
                    string item = (string)listBox1.Items[id];
                    int index = item.IndexOf(' ');
                    string result = item.Substring(0, index);
                    int idstudent = int.Parse(result);
                    var student = service.student.AsEnumerable().First(i => i.id == idstudent);
                    service.DeleteObject(student);
                    service.SaveChanges();
                    this.listBox1.Items.Clear();
                    foreach (var s in service.student.AsEnumerable())
                    {
                        this.listBox1.Items.Add(s.id.ToString() + " " + s.name);
                    }
                }
            }
            catch (Exception exc)
            {
                label5.Text = exc.Message;
            }
        }

        private void button3_Click(object sender, EventArgs e)
        {
            try
            {
                int id = this.listBox1.SelectedIndex;
                if (textBox3.Text != "" && id != 0)
                {
                    WSKNSEntities service = new WSKNSEntities(new Uri("http://localhost:60376/Service1.svc"));
                    string item = (string)listBox1.Items[id];
                    int index = item.IndexOf(' ');
                    string result = item.Substring(0, index);
                    int idstudent = int.Parse(result);
                    var student = service.student.AsEnumerable().First(i => i.id == idstudent);
                    student.name = textBox3.Text;
                    service.UpdateObject(student);
                    service.SaveChanges();
                    this.listBox1.Items.Clear();
                    foreach (var s in service.student.AsEnumerable())
                    {
                        this.listBox1.Items.Add(s.id.ToString() + " " + s.name);
                    }
                }
                else
                {
                    label9.Text = "Ввеедите данные";
                }
            }
            catch (Exception exc)
            {
                label9.Text = exc.Message;
            }
        }

        private void button6_Click(object sender, EventArgs e)
        {
            if (textBox4.Text != "")
            {
                try
                {
                    WSKNSEntities service = new WSKNSEntities(new Uri("http://localhost:60376/Service1.svc"));
                    note note = new note() { };
                    note.stud_id = (int?)Int64.Parse(textBox4.Text);
                    note.subject = textBox5.Text;
                    note.note1 = (int?)Int64.Parse(textBox6.Text);
                    service.AddTonote(note);

                    service.SaveChanges();
                    this.listBox2.Items.Clear();
                    foreach (var n in service.note.AsEnumerable())
                    {
                        this.listBox2.Items.Add(n.id.ToString() + " " + n.stud_id + " " + n.subject + " " + n.note1);
                    }
                }
                catch (Exception exc)
                {
                    label12.Text = exc.Message;
                }
            }
            else
            {
                label12.Text = "Ввеедите данные";
            }
        }

        private void button5_Click(object sender, EventArgs e)
        {
            try
            {
                WSKNSEntities service = new WSKNSEntities(new Uri("http://localhost:60376/Service1.svc"));
                int id = this.listBox2.SelectedIndex;
                if (id != -1)
                {
                    string item = (string)listBox2.Items[id];
                    int index = item.IndexOf(' ');
                    string result = item.Substring(0, index);
                    int idnote = int.Parse(result);
                    var note = service.note.AsEnumerable().First(i => i.id == idnote);
                    service.DeleteObject(note);
                    service.SaveChanges();
                    this.listBox2.Items.Clear();
                    foreach (var n in service.note.AsEnumerable())
                    {
                        this.listBox2.Items.Add(n.id.ToString() + " " + n.stud_id + " " + n.subject + " " + n.note1);
                    }
                }
            }
            catch (Exception exc)
            {
                label10.Text = exc.Message;
            }
        }

        private void button4_Click(object sender, EventArgs e)
        {
            try
            {
				int id = this.listBox2.SelectedIndex;
				//int id = 1;
                if (textBox8.Text != "" && textBox7.Text != "" && textBox2.Text != "" && id != 0)
                {
                    WSKNSEntities service = new WSKNSEntities(new Uri("http://localhost:60376/Service1.svc"));
                    string item = (string)listBox2.Items[id];
                    int index = item.IndexOf(' ');
                    string result = item.Substring(0, index);
                    int idnote = int.Parse(result);
                    var note = service.note.AsEnumerable().First(i => i.id == idnote);
                    note.stud_id = (int?)Int64.Parse(textBox8.Text);
                    note.subject = textBox7.Text;
                    note.note1 = (int?)Int64.Parse(textBox2.Text);
                    service.UpdateObject(note);
                    service.SaveChanges();
                    this.listBox2.Items.Clear();
                    foreach (var n in service.note.AsEnumerable())
                    {
                        this.listBox2.Items.Add(n.id.ToString() + " " + n.stud_id + " " + n.subject + " " + n.note1);
                    }
                }
                else
                {
                    label11.Text = "Ввеедите данные";
                }
            }
            catch (Exception exc)
            {
                label11.Text = exc.Message;
            }
        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void label7_Click(object sender, EventArgs e)
        {

        }
    }
}
