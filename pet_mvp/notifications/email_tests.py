"""
Test file for sending emails with MailHog

Usage:
    python manage.py shell
    from pet_mvp.common.email_tests import send_test_email
    send_test_email('recipient@example.com')
"""
from django.core.mail import send_mail
from django.conf import settings
from pet_mvp.notifications.email_service import EmailService


def send_test_email(recipient_email):
    """
    Send a test email using Django's send_mail function
    
    This will use the configured EMAIL_BACKEND in settings.py
    For development with MailHog, this will send to the MailHog SMTP server
    
    Args:
        recipient_email (str): Recipient email address
        
    Returns:
        bool: True if email was sent successfully
    """
    subject = 'Test Email from Django'
    message = 'This is a test email sent from Django using MailHog.'
    from_email = settings.DEFAULT_FROM_EMAIL
    
    return send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[recipient_email],
        fail_silently=False,
    )


def send_test_template_email(recipient_email):
    """
    Send a test template email using the EmailService
    
    This demonstrates using the EmailService with MailHog
    
    Args:
        recipient_email (str): Recipient email address
        
    Returns:
        bool: True if email was sent successfully
    """
    subject = 'Test Template Email from Django'
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { padding: 20px; }
            .header { background-color: #4CAF50; color: white; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Test Email</h1>
            </div>
            <p>This is a test email sent from Django using MailHog.</p>
            <p>The email service is working correctly!</p>
        </div>
    </body>
    </html>
    '''
    
    return EmailService.send_email(
        subject=subject,
        to_email=recipient_email,
        html_content=html_content,
    )


def send_test_async_email(recipient_email):
    """
    Send a test async email using the EmailService and Celery
    
    This demonstrates using the async email service with MailHog
    
    Args:
        recipient_email (str): Recipient email address
        
    Returns:
        AsyncResult: Celery task result
    """
    subject = 'Test Async Email from Django'
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { padding: 20px; }
            .header { background-color: #4682B4; color: white; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Test Async Email</h1>
            </div>
            <p>This is a test async email sent from Django using MailHog and Celery.</p>
            <p>The async email service is working correctly!</p>
        </div>
    </body>
    </html>
    '''
    
    return EmailService.send_email_async.delay(
        subject=subject,
        to_email=recipient_email,
        html_content=html_content,
    )
