import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSender:
    """Utility class for sending emails"""
    
    def __init__(
        self, 
        smtp_server=None, 
        smtp_port=None, 
        username=None, 
        password=None,
        use_tls=True
    ):
        """Initialize email sender with SMTP configuration
        
        Args:
            smtp_server: SMTP server address (default from env EMAIL_SMTP_SERVER)
            smtp_port: SMTP port (default from env EMAIL_SMTP_PORT)
            username: SMTP username/email (default from env EMAIL_USERNAME)
            password: SMTP password (default from env EMAIL_PASSWORD)
            use_tls: Whether to use TLS encryption (default True)
        """
        self.smtp_server = smtp_server or os.getenv('EMAIL_SMTP_SERVER')
        self.smtp_port = smtp_port or int(os.getenv('EMAIL_SMTP_PORT', 587))
        self.username = username or os.getenv('EMAIL_USERNAME')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        self.use_tls = use_tls
        
        # Validate required settings
        if not all([self.smtp_server, self.smtp_port, self.username, self.password]):
            logger.warning("Email configuration incomplete. Some settings are missing.")

    def send_email(self, to_email, subject, body_text, body_html=None, attachments=None, cc=None, bcc=None):
        """Send an email
        
        Args:
            to_email: Recipient email or list of emails
            subject: Email subject
            body_text: Plain text email body
            body_html: HTML email body (optional)
            attachments: List of file paths to attach (optional)
            cc: CC recipient(s) (optional)
            bcc: BCC recipient(s) (optional)
            
        Returns:
            Boolean indicating success or failure
        """
        if not all([self.smtp_server, self.smtp_port, self.username, self.password]):
            logger.error("Email configuration incomplete. Cannot send email.")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            
            # Handle recipients
            if isinstance(to_email, list):
                msg['To'] = ', '.join(to_email)
            else:
                msg['To'] = to_email
                
            # Add CC if provided
            if cc:
                if isinstance(cc, list):
                    msg['Cc'] = ', '.join(cc)
                else:
                    msg['Cc'] = cc
                    
            # Add BCC if provided
            if bcc:
                if isinstance(bcc, list):
                    msg['Bcc'] = ', '.join(bcc)
                else:
                    msg['Bcc'] = bcc
            
            # Add text part
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
            
            # Add HTML part if provided
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)
                
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as file:
                            part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                            msg.attach(part)
                    except Exception as e:
                        logger.error(f"Error attaching file {file_path}: {str(e)}")
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.username, self.password)
                
                # Get all recipients
                all_recipients = []
                if isinstance(to_email, list):
                    all_recipients.extend(to_email)
                else:
                    all_recipients.append(to_email)
                    
                if cc:
                    if isinstance(cc, list):
                        all_recipients.extend(cc)
                    else:
                        all_recipients.append(cc)
                        
                if bcc:
                    if isinstance(bcc, list):
                        all_recipients.extend(bcc)
                    else:
                        all_recipients.append(bcc)
                
                server.sendmail(self.username, all_recipients, msg.as_string())
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_feedback_notification(self, feedback_data):
        """Send a notification email about received feedback
        
        Args:
            feedback_data: Dictionary containing feedback information
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Get recipient from environment variable
            feedback_recipient = os.getenv('FEEDBACK_EMAIL_RECIPIENT')
            if not feedback_recipient:
                logger.error("FEEDBACK_EMAIL_RECIPIENT not set in environment variables")
                return False
            
            # Format the feedback
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            subject = f"Portfolio Feedback: {feedback_data.get('category', 'General')} [{feedback_data.get('sentiment', 'neutral')}]"
            
            text_body = f"""
New Feedback Received at {timestamp}

Category: {feedback_data.get('category', 'Not specified')}
Sentiment: {feedback_data.get('sentiment', 'neutral')}
Priority: {feedback_data.get('priority', 1)}/5

Message:
{feedback_data.get('message', 'No message content')}

Rating: {feedback_data.get('rating', 'Not provided')}
            """
            
            html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 15px; border-bottom: 3px solid #6a82fb; }}
        .content {{ padding: 20px 0; }}
        .footer {{ font-size: 12px; color: #777; margin-top: 30px; }}
        .priority {{ display: inline-block; padding: 3px 6px; border-radius: 3px; }}
        .priority-1 {{ background-color: #e9ecef; }}
        .priority-2 {{ background-color: #e2f0d9; }}
        .priority-3 {{ background-color: #fff2cc; }}
        .priority-4 {{ background-color: #fce5cd; }}
        .priority-5 {{ background-color: #f8cecc; }}
        .sentiment-positive {{ color: #2e7d32; }}
        .sentiment-neutral {{ color: #757575; }}
        .sentiment-negative {{ color: #c62828; }}
        .message-box {{ background-color: #f1f3f4; padding: 15px; border-left: 3px solid #6a82fb; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>New Portfolio Feedback</h2>
            <p>Received at {timestamp}</p>
        </div>
        <div class="content">
            <p><strong>Category:</strong> {feedback_data.get('category', 'Not specified')}</p>
            <p>
                <strong>Sentiment:</strong> 
                <span class="sentiment-{feedback_data.get('sentiment', 'neutral')}">
                    {feedback_data.get('sentiment', 'neutral')}
                </span>
            </p>
            <p>
                <strong>Priority:</strong> 
                <span class="priority priority-{feedback_data.get('priority', 1)}">
                    {feedback_data.get('priority', 1)}/5
                </span>
            </p>
            <p><strong>Rating:</strong> {feedback_data.get('rating', 'Not provided')}</p>
            
            <h3>Message:</h3>
            <div class="message-box">
                {feedback_data.get('message', 'No message content').replace("\\n", "<br>")}
            </div>
        </div>
        <div class="footer">
            <p>This is an automated notification from your Portfolio AI Assistant</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Send the email
            return self.send_email(
                to_email=feedback_recipient,
                subject=subject,
                body_text=text_body,
                body_html=html_body
            )
            
        except Exception as e:
            logger.error(f"Error sending feedback notification: {str(e)}")
            return False 