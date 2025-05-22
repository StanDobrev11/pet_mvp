from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import translation
from django.conf import settings
from celery import shared_task


class EmailService:
    """Service for handling email operations using Brevo"""
    @staticmethod
    def send_email(subject, to_email, html_content, from_email=None, cc=None):
        """
        Send an email immediately  
        Args:
            subject (str): Email subject
            to_email (str or list): Recipient email address(es)
            cc (str or list, optional): CC email address(es)
            html_content (str): HTML content of the email
            from_email (str, optional): Sender email address. Defaults to settings.DEFAULT_FROM_EMAIL.
        Returns:
            bool: True if email was sent successfully
        """
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
        plain_text = strip_tags(html_content)
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=from_email,
            cc=[] if cc is None else [cc] if isinstance(cc, str) else cc,
            to=[to_email] if isinstance(to_email, str) else to_email
        )
        email.attach_alternative(html_content, "text/html")
        return email.send() > 0

    @staticmethod
    def send_template_email(subject, to_email, template_name, context, from_email=None, cc=None):
        """
        Send an email using a template        
        Args:
            subject (str): Email subject
            to_email (str or list): Recipient email address(es)
            cc (str or list, optional): CC email address(es)
            template_name (str): Name of the template to use
            context (dict): Context data for the template
            from_email (str, optional): Sender email address. Defaults to settings.DEFAULT_FROM_EMAIL.            
        Returns:
            bool: True if email was sent successfully
        """
        lang = context.get('lang', 'en')
        with translation.override(lang):
            html_content = render_to_string(template_name, context)
        return EmailService.send_email(subject, to_email, html_content, from_email, cc)

    @staticmethod
    @shared_task
    def send_email_async(subject, to_email, html_content, from_email=None):
        """
        Send an email asynchronously using Celery

        Args:
            subject (str): Email subject
            to_email (str or list): Recipient email address(es)
            html_content (str): HTML content of the email
            from_email (str, optional): Sender email address. Defaults to settings.DEFAULT_FROM_EMAIL.

        Returns:
            bool: True if email was sent successfully
        """
        return EmailService.send_email(subject, to_email, html_content, from_email)

    @staticmethod
    @shared_task
    def send_template_email_async(subject, to_email, template_name, context, from_email=None, cc=None):
        """
        Send a templated email asynchronously using Celery

        Args:
            subject (str): Email subject
            to_email (str or list): Recipient email address(es)
            cc (str, list, optional): CC email address(es)
            template_name (str): Name of the template to use
            context (dict): Context data for the template
            from_email (str, optional): Sender email address. Defaults to settings.DEFAULT_FROM_EMAIL.

        Returns:
            bool: True if email was sent successfully
        """
        return EmailService.send_template_email(subject, to_email, template_name, context, from_email, cc)
