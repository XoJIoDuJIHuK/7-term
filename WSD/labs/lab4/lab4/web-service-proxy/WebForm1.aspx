<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="WebForm1.aspx.cs" Inherits="web_service_proxy.WebForm1" %>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title></title>
</head>
<body>
    <form id="form1" runat="server">
        <div>
            <asp:Label runat="server">Enter two numbers</asp:Label> <br />
            <asp:TextBox runat="server" ID="x" />
            <asp:TextBox runat="server" ID="y" />    
            <asp:Button runat="server" ID="sum" OnClick="SumClick" Text="Sum" />
        </div>
        <br />
        <div>
            <asp:Label runat="server">Result</asp:Label>
            <asp:TextBox runat="server" ID="result" />
        </div>
    </form>
</body>
</html>
