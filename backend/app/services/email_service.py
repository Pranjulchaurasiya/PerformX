"""
Email service — sends via SMTP using BackgroundTasks.
Falls back to console logging if SMTP not configured.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification, NotificationStatus

logger = logging.getLogger(__name__)


def _build_html_email(subject: str, body_html: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fb; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 40px auto; background: #fff; border-radius: 12px;
                      box-shadow: 0 2px 16px rgba(79,70,229,0.08); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #4f46e5, #6366f1); padding: 32px 40px; }}
        .header h1 {{ color: #fff; margin: 0; font-size: 24px; font-weight: 700; }}
        .header p {{ color: rgba(255,255,255,0.8); margin: 4px 0 0; font-size: 13px; }}
        .body {{ padding: 32px 40px; color: #374151; line-height: 1.6; }}
        .footer {{ background: #f9fafb; padding: 20px 40px; text-align: center;
                   color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb; }}
        .btn {{ display: inline-block; background: #4f46e5; color: #fff; padding: 12px 28px;
                border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 16px; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>PerformX</h1>
          <p>Goal Setting & Progress Tracking Portal</p>
        </div>
        <div class="body">
          {body_html}
        </div>
        <div class="footer">
          &copy; {datetime.now().year} PerformX. This is an automated notification.
        </div>
      </div>
    </body>
    </html>
    """


def send_email_background(
    db: Session,
    recipient_id: int,
    recipient_email: str,
    event_type: str,
    subject: str,
    body_html: str,
    deep_link: Optional[str] = None,
):
    """Send email and log to notifications table."""
    full_html = _build_html_email(subject, body_html)

    # Log to DB first
    notif = Notification(
        recipient_id=recipient_id,
        event_type=event_type,
        subject=subject,
        body=body_html,
        deep_link=deep_link,
        status=NotificationStatus.pending,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    if not settings.SMTP_USER or not settings.SMTP_PASS:
        logger.info(f"[EMAIL DEV MODE] To: {recipient_email} | Subject: {subject}")
        logger.info(f"[EMAIL BODY] {body_html[:200]}")
        notif.status = NotificationStatus.sent
        notif.sent_at = datetime.utcnow()
        db.commit()
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = recipient_email
        msg.attach(MIMEText(full_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_USER, recipient_email, msg.as_string())

        notif.status = NotificationStatus.sent
        notif.sent_at = datetime.utcnow()
        db.commit()
        logger.info(f"Email sent to {recipient_email}: {subject}")

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        notif.status = NotificationStatus.failed
        db.commit()


# ---- Event-specific helpers ----

def notify_goal_submitted(db: Session, manager_email: str, manager_id: int,
                           employee_name: str, goal_id: int):
    deep_link = f"{settings.APP_BASE_URL}/goals/{goal_id}"
    send_email_background(
        db, manager_id, manager_email, "goal_submitted",
        f"New Goal Submitted by {employee_name}",
        f"<p><strong>{employee_name}</strong> has submitted goals for your approval.</p>"
        f'<a href="{deep_link}" class="btn">Review Goals</a>',
        deep_link,
    )


def notify_goal_approved(db: Session, employee_email: str, employee_id: int, goal_id: int):
    deep_link = f"{settings.APP_BASE_URL}/goals/{goal_id}"
    send_email_background(
        db, employee_id, employee_email, "goal_approved",
        "Your Goals Have Been Approved",
        f"<p>Your goals have been <strong>approved</strong> by your manager and are now locked.</p>"
        f'<a href="{deep_link}" class="btn">View Goals</a>',
        deep_link,
    )


def notify_goal_returned(db: Session, employee_email: str, employee_id: int,
                          goal_id: int, comment: str, manager_name: str = "Your Manager",
                          cycle_deadline: Optional[str] = None):
    """
    Notify employee that their goal sheet was returned for rework.
    Deep-links to the edit page.  Includes cycle deadline if near.
    """
    edit_link = f"{settings.APP_BASE_URL}/goals/{goal_id}/edit"
    deadline_note = ""
    if cycle_deadline:
        deadline_note = (
            f"<p><strong>⚠️ Deadline Reminder:</strong> "
            f"The goal-setting window closes on <strong>{cycle_deadline}</strong>. "
            f"Please revise and resubmit before this date.</p>"
        )
    send_email_background(
        db, employee_id, employee_email, "goal_returned",
        f"Your goals need revision — {manager_name} returned your goal sheet",
        f"<p><strong>{manager_name}</strong> has returned your goal sheet for rework.</p>"
        f"<div style='background:#fef3c7;border-left:4px solid #f59e0b;padding:12px 16px;"
        f"border-radius:4px;margin:16px 0;'>"
        f"<strong>Manager's Comment:</strong><br>{comment}</div>"
        f"{deadline_note}"
        f'<a href="{edit_link}" class="btn">Revise Goals</a>',
        edit_link,
    )


def notify_goal_unlocked(db: Session, employee_email: str, employee_id: int,
                          manager_email: str, manager_id: int, goal_id: int, reason: str):
    deep_link = f"{settings.APP_BASE_URL}/goals/{goal_id}"
    for uid, email in [(employee_id, employee_email), (manager_id, manager_email)]:
        send_email_background(
            db, uid, email, "goal_unlocked",
            "A Goal Has Been Unlocked by Admin",
            f"<p>Admin has unlocked a goal for editing.</p>"
            f"<p><strong>Reason:</strong> {reason}</p>"
            f'<a href="{deep_link}" class="btn">View Goal</a>',
            deep_link,
        )


def notify_checkin_window_open(db: Session, employee_email: str, employee_id: int,
                                cycle_name: str):
    send_email_background(
        db, employee_id, employee_email, "checkin_window_open",
        f"Check-in Window Open: {cycle_name}",
        f"<p>The <strong>{cycle_name}</strong> check-in window is now open.</p>"
        f"<p>Please log your achievement updates in PerformX.</p>"
        f'<a href="{settings.APP_BASE_URL}/achievements" class="btn">Update Achievements</a>',
    )
