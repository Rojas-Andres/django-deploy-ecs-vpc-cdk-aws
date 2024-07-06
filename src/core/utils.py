"""
File that contains utility functions for the project.
"""
import os

import boto3
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def send_email(
    subject, html_content, to_send_email, cc_send_email=None, bcc_send_email=None, reply_to_email=None, headers=None
):  # pylint: disable=too-many-arguments
    """
    Sends a transactional email using the Sendinblue/Brevo API.

    Args:
        subject (str): The subject of the email.
        html_content (str): The HTML content of the email.
        to_send_email (str or list): The recipient email address(es).
        cc_send_email (str or list, optional): The CC email address(es). Defaults to None.
        bcc_send_email (str or list, optional): The BCC email address(es). Defaults to None.
        reply_to_email (str, optional): The reply-to email address. Defaults to None.
        headers (dict, optional): The email headers. Defaults to None.

    Returns:
        str: Message if the email is sent successfully.
        str: Error message if an exception occurs.
    """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = os.environ.get("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    sender = {"name": os.environ.get("SENDER_NAME"), "email": os.environ.get("SENDER_EMAIL")}

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to_send_email,
        bcc=bcc_send_email,
        cc=cc_send_email,
        reply_to=reply_to_email,
        headers=headers,
        html_content=html_content,
        sender=sender,
        subject=subject,
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
        return "Email sent successfully."
    except ApiException as e:
        return f"Exception when calling SMTPApi->send_transac_email: {e}\n"


def send_sms(phone_number, message):
    """
    Sends an SMS message to the specified phone number using Amazon SNS and AWS credentials.

    Args:
        phone_number (str): The phone number to which the SMS message will be sent.
        message (str): The message to be sent in the SMS.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the execution of the function.
    """
    try:
        sns_client = boto3.client(
            "sns",
        )
        response = sns_client.publish(PhoneNumber=phone_number, Message=message)

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print("SMS sent successfully.")
            return "SMS sent successfully."
        print("SMS not sent.")
        return "SMS not sent."
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"
