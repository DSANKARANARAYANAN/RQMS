import schedule
import time
import threading
from utils.email_sender import EmailSender
import os

class ReportScheduler:
    def __init__(self):
        self.email_sender = EmailSender()
        self.is_running = False
        self.schedule_time = os.getenv("DAILY_REPORT_TIME", "08:00")  # Default to 8:00 AM
    
    def send_daily_report_job(self):
        """Job function to send daily report"""
        try:
            print("Running scheduled daily report...")
            success, message = self.email_sender.send_daily_report()
            if success:
                print("Scheduled daily report completed successfully")
            else:
                print(f"Scheduled daily report failed: {message}")
        except Exception as e:
            print(f"Error in scheduled daily report: {str(e)}")
    
    def setup_schedule(self):
        """Setup the daily schedule"""
        # Clear any existing schedules
        schedule.clear()
        
        # Schedule daily report
        schedule.every().day.at(self.schedule_time).do(self.send_daily_report_job)
        print(f"Daily report scheduled for {self.schedule_time}")
    
    def run_scheduler(self):
        """Run the scheduler in a loop"""
        self.is_running = True
        self.setup_schedule()
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def start(self):
        """Start the scheduler in a background thread"""
        if not self.is_running:
            scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            scheduler_thread.start()
            print("Report scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        print("Report scheduler stopped")

# Global scheduler instance
_scheduler = None

def start_scheduler():
    """Start the global scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = ReportScheduler()
        _scheduler.start()
    return _scheduler

def get_scheduler():
    """Get the global scheduler instance"""
    global _scheduler
    return _scheduler

def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
