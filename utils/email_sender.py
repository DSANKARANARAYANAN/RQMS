import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from utils.data_manager import DataManager

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.manager_emails = os.getenv("MANAGER_EMAILS", "").split(",")
        self.data_manager = DataManager()
    
    def create_daily_report_html(self, summary):
        """Create HTML content for daily report"""
        if not summary:
            return """
            <html>
            <body>
                <h2>QRMS Daily Quality Report</h2>
                <p><strong>Date:</strong> {date}</p>
                <p>No rejection data available for yesterday.</p>
            </body>
            </html>
            """.format(date=datetime.now().strftime('%Y-%m-%d'))
        
        # Generate module table
        module_rows = ""
        for module, quantity in summary['by_module'].items():
            module_rows += f"<tr><td>{module}</td><td>{quantity}</td></tr>"
        
        # Generate type table
        type_rows = ""
        for rejection_type, quantity in summary['by_type'].items():
            type_rows += f"<tr><td>{rejection_type}</td><td>{quantity}</td></tr>"
        
        # Generate recent records table
        recent_rows = ""
        for record in summary['recent_records']:
            date_str = record['date'][:10] if isinstance(record['date'], str) else str(record['date'])[:10]
            recent_rows += f"""
            <tr>
                <td>{date_str}</td>
                <td>{record['module']}</td>
                <td>{record['rejection_type']}</td>
                <td>{record['quantity']}</td>
                <td>{record['reason'][:50]}...</td>
            </tr>
            """
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ background-color: #e7f3ff; padding: 10px; margin: 5px; border-radius: 5px; display: inline-block; }}
                .header {{ color: #1f77b4; }}
            </style>
        </head>
        <body>
            <h2 class="header">🏭 QRMS Daily Quality Rejection Report</h2>
            <p><strong>Report Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
            <p><strong>Data Period:</strong> Previous 24 hours</p>
            
            <h3>📊 Summary Metrics</h3>
            <div class="metric">
                <strong>Total Rejections:</strong> {summary['total_rejections']}
            </div>
            <div class="metric">
                <strong>Total Quantity Rejected:</strong> {summary['total_quantity']:,}
            </div>
            
            <h3>🔧 Rejections by Module</h3>
            <table>
                <tr><th>Module</th><th>Quantity Rejected</th></tr>
                {module_rows}
            </table>
            
            <h3>⚠️ Rejections by Type</h3>
            <table>
                <tr><th>Rejection Type</th><th>Quantity</th></tr>
                {type_rows}
            </table>
            
            <h3>📋 Recent Rejection Records</h3>
            <table>
                <tr><th>Date</th><th>Module</th><th>Type</th><th>Quantity</th><th>Reason</th></tr>
                {recent_rows}
            </table>
            
            <hr>
            <p><em>This is an automated report from QRMS - Quality Rejection Management System.</em></p>
        </body>
        </html>
        """
        
        return html_content
    
    def send_daily_report(self):
        """Send daily rejection report to managers"""
        try:
            if not self.email_user or not self.email_password:
                print("Email credentials not configured")
                return False, "Email credentials not configured"
            
            if not any(email.strip() for email in self.manager_emails):
                print("Manager emails not configured")
                return False, "Manager emails not configured"
            
            # Get yesterday's data
            yesterday = datetime.now() - timedelta(days=1)
            start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Get rejection summary
            summary = self.data_manager.get_rejection_summary(start_of_yesterday, end_of_yesterday)
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"QRMS Daily Quality Report - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.email_user
            msg['To'] = ", ".join([email.strip() for email in self.manager_emails if email.strip()])
            
            # Create HTML content
            html_content = self.create_daily_report_html(summary)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"Daily report sent successfully to {len([e for e in self.manager_emails if e.strip()])} recipients")
            return True, "Daily report sent successfully"
        
        except Exception as e:
            error_msg = f"Error sending daily report: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def send_test_email(self, test_email):
        """Send a test email to verify configuration"""
        try:
            if not self.email_user or not self.email_password:
                return False, "Email credentials not configured"
            
            # Create test email
            msg = MIMEMultipart()
            msg['Subject'] = "Test Email - QRMS"
            msg['From'] = self.email_user
            msg['To'] = test_email
            
            body = """
            <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a test email from QRMS - Quality Rejection Management System.</p>
                <p>If you receive this email, the email configuration is working correctly.</p>
                <p><strong>Timestamp:</strong> {timestamp}</p>
            </body>
            </html>
            """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            return True, "Test email sent successfully"
        
        except Exception as e:
            return False, f"Error sending test email: {str(e)}"
