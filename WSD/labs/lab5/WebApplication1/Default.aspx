<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="WCFClient._Default" %>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>WCF Client</title>
</head>
<body>
    <form id="form1" runat="server">
        <div>
            <h2>WCF Service Client</h2>

            <h3>Add</h3>
            <asp:TextBox ID="txtAddX" runat="server"></asp:TextBox> +
            <asp:TextBox ID="txtAddY" runat="server"></asp:TextBox> =
            <asp:Label ID="lblAddResult" runat="server"></asp:Label>
            <asp:Button ID="btnAdd" runat="server" Text="Add" OnClick="btnAdd_Click" />

            <h3>Concat</h3>
            String: <asp:TextBox ID="txtConcatX" runat="server"></asp:TextBox>
            Number: <asp:TextBox ID="txtConcatY" runat="server"></asp:TextBox>
            <asp:Button ID="btnConcat" runat="server" Text="Concat" OnClick="btnConcat_Click" />
            <asp:Label ID="lblConcatResult" runat="server"></asp:Label>

            <h3>Sum</h3>
            <asp:Button ID="btnSum" runat="server" Text="Sum (Class A)" OnClick="btnSum_Click" Enabled="true"/>
            <asp:Label ID="lblSumResult" runat="server"></asp:Label>

        </div>
    </form>
</body>
</html>