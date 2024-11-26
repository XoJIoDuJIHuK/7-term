using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml;
using System.Xml.Linq;

namespace Client
{
    public partial class WCFSyndicationClient : Form
    {
        public WCFSyndicationClient()
        {
            InitializeComponent();
        }

        private void ATOM_Click(object sender, EventArgs e)
        {
            richTextBox1.Text = "";
            label2.Text = "";

            if (textBox1.Text != "")
            {
                XmlDocument xmlDoc = new XmlDocument();
                xmlDoc.Load(@"http://localhost:8734/SyndicationService/feed/" + textBox1.Text + "?format=atom");
                XmlElement root = xmlDoc.DocumentElement;

                XmlNamespaceManager nsmgr = new XmlNamespaceManager(xmlDoc.NameTable);
                nsmgr.AddNamespace("atom", "http://www.w3.org/2005/Atom");

                XmlNodeList entryNodes = root.SelectNodes("//atom:entry", nsmgr);

                StringBuilder atomContent = new StringBuilder();

                atomContent.Append("ATOM\n\n");

                foreach (XmlNode atomEntry in entryNodes)
                {
                    XmlNode titleNode = atomEntry.SelectSingleNode("atom:title", nsmgr);
                    string title = titleNode != null ? titleNode.InnerText : "";

                    XmlNode contentNode = atomEntry.SelectSingleNode("atom:content", nsmgr);
                    string description = contentNode != null ? contentNode.InnerText : "";

                    atomContent.Append("Subject: " + title + "\nDescription: " + description + "\n\n");
                }

                richTextBox1.Text = atomContent.ToString();
            }
            else label2.Text = "Заполните поле student id";
        }

        private void RSS_Click(object sender, EventArgs e)
        {
            richTextBox1.Text = "";
            label2.Text = "";

            if (textBox1.Text != "")
            {
                XmlDocument rssXmlDoc = new XmlDocument();

                rssXmlDoc.Load(@"http://localhost:8734/SyndicationService/feed/" + textBox1.Text + "?format=rss");

                XmlNodeList rssNodes = rssXmlDoc.SelectNodes("rss/channel/item");

                StringBuilder rssContent = new StringBuilder();

                rssContent.Append("RSS\n");

                foreach (XmlNode rssNode in rssNodes)
                {
                    XmlNode rssSubNode = rssNode.SelectSingleNode("title");
                    string title = rssSubNode != null ? rssSubNode.InnerText : "";

                    rssSubNode = rssNode.SelectSingleNode("description");
                    string description = rssSubNode != null ? rssSubNode.InnerText : "";

                    rssContent.Append("Subject: " + title + "\nDescription: " + description + "\n\n");
                }
                richTextBox1.Text = rssContent.ToString();
            }
            else label2.Text = "Заполните поле student id";
        }

        private void button1_Click(object sender, EventArgs e)
        {
            richTextBox1.Text = "";
            label2.Text = "";

            if (textBox1.Text != "")
            {
                string url = @"http://localhost:8734/SyndicationService/feed/" + textBox1.Text + "?format=json";
                using (var webClient = new WebClient())
                {
                    try
                    {
                        string xmlData = webClient.DownloadString(url);

                        XmlDocument xmlDoc = new XmlDocument();
                        xmlDoc.LoadXml(xmlData);

                        XmlNamespaceManager nsmgr = new XmlNamespaceManager(xmlDoc.NameTable);
                        nsmgr.AddNamespace("z", "http://schemas.microsoft.com/2003/10/Serialization/");

                        XmlNode jsonNode = xmlDoc.SelectSingleNode("//z:anyType", nsmgr);

                        string jsonData = jsonNode.InnerText;

                        JObject rssJson = JObject.Parse(jsonData);
                        JArray rssArray = (JArray)rssJson["value"];

                        StringBuilder rssContent = new StringBuilder();
                        rssContent.Append("------ JSON ------\n\n");

                        foreach (JToken rssItem in rssArray)
                        {
                            string title = rssItem["subject"]?.ToString() ?? "";
                            string description = rssItem["note1"]?.ToString() ?? "";

                            rssContent.Append("Subject: " + title + "\nNote: " + description + "\n\n");
                        }

                        richTextBox1.Text = rssContent.ToString();
                    }
                    catch (Exception ex)
                    {
                        richTextBox1.Text = "Ошибка: " + ex.Message;
                    }
                }
            }
            else label2.Text = "Заполните поле student id";
        }
    }
}
