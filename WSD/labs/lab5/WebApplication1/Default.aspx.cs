using System;
using System.ServiceModel;
using System.Web.UI;
using System.Web.UI.WebControls;
using WebApplication1.ServiceReference1;

namespace WCFClient
{
    public partial class _Default : Page
    {
        protected void Page_Load(object sender, EventArgs e)
        {

        }

        protected void btnAdd_Click(object sender, EventArgs e)
        {
            try
            {
                int x = int.Parse(txtAddX.Text);
                int y = int.Parse(txtAddY.Text);
                using (var client = new Service1Client("BasicHttpBinding_IService1"))
                {
                    lblAddResult.Text = client.Add(x, y).ToString();
                }
            }
            catch (Exception ex)
            {
                lblAddResult.Text = "Error: " + ex.Message;
            }
        }

        protected void btnConcat_Click(object sender, EventArgs e)
        {
            try
            {
                string x = txtConcatX.Text;
                double y;
                if (double.TryParse(txtConcatY.Text, out y))
                {
                    using (var client = new Service1Client("BasicHttpBinding_IService1"))
                    {
                        lblConcatResult.Text = client.Concat(x, y);
                    }
                }
                else
                {
                    lblConcatResult.Text = "Error: Invalid number";
                }
            }
            catch (Exception ex)
            {
                lblConcatResult.Text = "Error: " + ex.Message;
            }
        }

        protected void btnSum_Click(object sender, EventArgs e)
        {
            using (var client = new Service1Client("BasicHttpBinding_IService1"))
            {
                try
                {
                    var sumResult = client.Sum(
                    new A { s = "hel", k = 1, f = 0.5f },
                    new A { s = "lo", k = 2, f = 1.5f }
                    );
                    lblSumResult.Text = $"{sumResult.s} {sumResult.k} {sumResult.f}";
                }
                catch (Exception ex)
                {
                    lblSumResult.Text = "Error: " + ex.Message;
                }
            }
        }
    }
}
