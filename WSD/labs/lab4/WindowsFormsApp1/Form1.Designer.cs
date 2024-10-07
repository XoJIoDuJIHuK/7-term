namespace WindowsFormsApp1
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.button1 = new System.Windows.Forms.Button();
            this.S3 = new System.Windows.Forms.Label();
            this.S1 = new System.Windows.Forms.TextBox();
            this.K1 = new System.Windows.Forms.TextBox();
            this.F1 = new System.Windows.Forms.TextBox();
            this.S2 = new System.Windows.Forms.TextBox();
            this.K2 = new System.Windows.Forms.TextBox();
            this.F2 = new System.Windows.Forms.TextBox();
            this.K3 = new System.Windows.Forms.Label();
            this.F3 = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(156, 38);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(75, 23);
            this.button1.TabIndex = 0;
            this.button1.Text = "Sum";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click_1);
            // 
            // S3
            // 
            this.S3.AutoSize = true;
            this.S3.Location = new System.Drawing.Point(411, 131);
            this.S3.Name = "S3";
            this.S3.Size = new System.Drawing.Size(32, 13);
            this.S3.TabIndex = 1;
            this.S3.Text = "result";
            // 
            // S1
            // 
            this.S1.Location = new System.Drawing.Point(89, 124);
            this.S1.Name = "S1";
            this.S1.Size = new System.Drawing.Size(100, 20);
            this.S1.TabIndex = 2;
            // 
            // K1
            // 
            this.K1.Location = new System.Drawing.Point(89, 160);
            this.K1.Name = "K1";
            this.K1.Size = new System.Drawing.Size(100, 20);
            this.K1.TabIndex = 3;
            // 
            // F1
            // 
            this.F1.Location = new System.Drawing.Point(89, 200);
            this.F1.Name = "F1";
            this.F1.Size = new System.Drawing.Size(100, 20);
            this.F1.TabIndex = 4;
            // 
            // S2
            // 
            this.S2.Location = new System.Drawing.Point(229, 124);
            this.S2.Name = "S2";
            this.S2.Size = new System.Drawing.Size(100, 20);
            this.S2.TabIndex = 5;
            // 
            // K2
            // 
            this.K2.Location = new System.Drawing.Point(229, 160);
            this.K2.Name = "K2";
            this.K2.Size = new System.Drawing.Size(100, 20);
            this.K2.TabIndex = 6;
            // 
            // F2
            // 
            this.F2.Location = new System.Drawing.Point(229, 200);
            this.F2.Name = "F2";
            this.F2.Size = new System.Drawing.Size(100, 20);
            this.F2.TabIndex = 7;
            // 
            // K3
            // 
            this.K3.AutoSize = true;
            this.K3.Location = new System.Drawing.Point(411, 167);
            this.K3.Name = "K3";
            this.K3.Size = new System.Drawing.Size(32, 13);
            this.K3.TabIndex = 8;
            this.K3.Text = "result";
            // 
            // F3
            // 
            this.F3.AutoSize = true;
            this.F3.Location = new System.Drawing.Point(411, 207);
            this.F3.Name = "F3";
            this.F3.Size = new System.Drawing.Size(32, 13);
            this.F3.TabIndex = 9;
            this.F3.Text = "result";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 450);
            this.Controls.Add(this.F3);
            this.Controls.Add(this.K3);
            this.Controls.Add(this.F2);
            this.Controls.Add(this.K2);
            this.Controls.Add(this.S2);
            this.Controls.Add(this.F1);
            this.Controls.Add(this.K1);
            this.Controls.Add(this.S1);
            this.Controls.Add(this.S3);
            this.Controls.Add(this.button1);
            this.Name = "Form1";
            this.Text = "Form1";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Label S3;
        private System.Windows.Forms.TextBox S1;
        private System.Windows.Forms.TextBox K1;
        private System.Windows.Forms.TextBox F1;
        private System.Windows.Forms.TextBox S2;
        private System.Windows.Forms.TextBox K2;
        private System.Windows.Forms.TextBox F2;
        private System.Windows.Forms.Label K3;
        private System.Windows.Forms.Label F3;
    }
}

