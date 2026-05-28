using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            string launcherDir = AppDomain.CurrentDomain.BaseDirectory;
            string appDir = Path.Combine(launcherDir, "AppFiles");
            string appExe = Path.Combine(appDir, "ForzaMusicOverlayApp.exe");

            if (!File.Exists(appExe))
            {
                MessageBox.Show(
                    "找不到 AppFiles\\ForzaMusicOverlayApp.exe，請重新解壓縮完整 release 套件。\n\nAppFiles\\ForzaMusicOverlayApp.exe was not found. Please extract the full release package again.",
                    "Forza Music",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
                return 1;
            }

            Process.Start(new ProcessStartInfo
            {
                FileName = appExe,
                Arguments = string.Join(" ", args.Select(QuoteArgument)),
                WorkingDirectory = appDir,
                UseShellExecute = false
            });

            return 0;
        }
        catch (Exception ex)
        {
            MessageBox.Show(ex.Message, "Forza Music", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    private static string QuoteArgument(string value)
    {
        if (string.IsNullOrEmpty(value))
        {
            return "\"\"";
        }

        if (value.IndexOfAny(new[] { ' ', '\t', '"' }) < 0)
        {
            return value;
        }

        return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
    }
}
