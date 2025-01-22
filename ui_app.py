import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from datetime import datetime
import sys


class LogAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Analyzer")
        self.root.geometry("300x200")

        # Admin email configuration
        self.admin_email = "jaykumar636904@gmail.com"
        self.sender_email = "jaykumar636904@gmail.com"  # Same as admin email
        self.sender_password = "kzud zblj tpod xqhb"  # Replace with your Gmail App Password

        # Center the content
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(expand=True)

        # Run button
        self.run_button = ttk.Button(
            main_frame,
            text="Run Analysis",
            command=self.run_analysis,
            style="Large.TButton"
        )
        self.run_button.pack(pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=10)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=5)

        # Configure style for larger button
        style = ttk.Style()
        style.configure("Large.TButton", padding=10, font=("Arial", 12))

    def run_analysis(self):
        self.progress.start()
        self.status_var.set("Running analysis...")
        self.run_button.state(['disabled'])

        try:
            # Determine script location
            if getattr(sys, 'frozen', False):  # If running as .exe
                current_dir = sys._MEIPASS
            else:  # If running as a script
                current_dir = os.path.dirname(os.path.abspath(__file__))

            main_script = os.path.join(current_dir, 'main.py')

            # Ensure proper Python executable path
            result = subprocess.run(
                [sys.executable, main_script],
                capture_output=True,
                text=True,
                check=True
            )

            # Debugging output
            print("Output:", result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)

            # Verify output files
            output_dir = os.path.join(current_dir, 'analysis_results')
            exported_logons = os.path.join(output_dir, 'exported_logons.csv')
            exported_logoffs = os.path.join(output_dir, 'exported_logoffs.csv')

            if not os.path.exists(exported_logons) or not os.path.exists(exported_logoffs):
                raise FileNotFoundError("Expected output files are missing.")

            # Send email with attachments
            self.send_email([exported_logons, exported_logoffs])

            messagebox.showinfo("Success", "Analysis completed and email sent!")
        except subprocess.CalledProcessError as e:
            error_msg = f"Error running analysis:\n{e.stderr if e.stderr else str(e)}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            print(str(e))
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("Ready")
            self.run_button.state(['!disabled'])

    def send_email(self, attachments):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.admin_email
        msg['Subject'] = f"Log Analysis Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = "Please find attached the log analysis results."
        msg.attach(MIMEText(body, 'plain'))

        for file in attachments:
            if os.path.exists(file):
                with open(file, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype="csv")
                    attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
                    msg.attach(attachment)

        try:
            # Connect to Gmail's SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            # Send email
            server.send_message(msg)
            server.quit()

            # Archive files
            archive_dir = "archived_results"
            os.makedirs(archive_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            for file in attachments:
                if os.path.exists(file):
                    os.rename(file, os.path.join(archive_dir, f"{timestamp}_{os.path.basename(file)}"))

        except Exception as e:
            print(f"Error sending email: {e}")
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")


def main():
    root = tk.Tk()
    app = LogAnalyzerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
