using System;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;

namespace JsonFormatterApp
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void FormatJson_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                string inputJson = InputTextBox.Text;
                using JsonDocument doc = JsonDocument.Parse(inputJson);
                string formattedJson = JsonSerializer.Serialize(doc.RootElement, new JsonSerializerOptions { WriteIndented = true });
                OutputTextBox.Text = formattedJson;
            }
            catch (Exception ex)
            {
                OutputTextBox.Text = "Invalid JSON: " + ex.Message;
            }
        }
    }
}
