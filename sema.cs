using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Threading;
using System.Threading.Tasks;

namespace SSRSReportGenerator
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Example list of URLs (1000 URLs)
            List<string> reportUrls = new List<string>();
            for (int i = 0; i < 1000; i++)
            {
                reportUrls.Add($"http://your-report-server/ReportServer?/YourReportFolder/YourReport{i}&rs:Command=Render&rs:Format=PDF");
            }

            // Output folder
            string outputFolder = @"C:\Reports\";

            // Create semaphore to limit concurrent tasks to 5
            using (SemaphoreSlim semaphore = new SemaphoreSlim(5))
            {
                List<Task> tasks = new List<Task>();

                foreach (string reportUrl in reportUrls)
                {
                    // Wait for semaphore slot to be available
                    await semaphore.WaitAsync();

                    // Create task for generating and saving report
                    tasks.Add(Task.Run(async () =>
                    {
                        try
                        {
                            string fileName = Path.GetFileNameWithoutExtension(reportUrl) + ".pdf";
                            string outputPath = Path.Combine(outputFolder, fileName);

                            await GenerateAndSaveReportAsync(reportUrl, outputPath);
                        }
                        finally
                        {
                            // Release semaphore slot
                            semaphore.Release();
                        }
                    }));
                }

                // Wait for all tasks to complete
                await Task.WhenAll(tasks);
            }

            Console.WriteLine("All reports generated and saved successfully.");
        }

        public static async Task GenerateAndSaveReportAsync(string reportUrl, string outputPath)
        {
            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(reportUrl);
                request.Method = "GET";
                request.Credentials = CredentialCache.DefaultCredentials;

                using (HttpWebResponse response = (HttpWebResponse)await request.GetResponseAsync())
                {
                    using (Stream responseStream = response.GetResponseStream())
                    {
                        if (responseStream != null)
                        {
                            using (FileStream fileStream = new FileStream(outputPath, FileMode.Create))
                            {
                                await responseStream.CopyToAsync(fileStream);
                            }
                        }
                    }
                }

                Console.WriteLine($"Report saved to {outputPath}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred: {ex.Message}");
            }
        }
    }
}
