import os
import boto3
import re
import csv
from typing import List, Tuple
from datetime import datetime

s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

def parse_csv(file_content: str) -> Tuple[List[str], List[List[str]]]:
    """Parse CSV content and return headers and rows.
    
    Args:
        file_content (str): The content of the CSV file as a string.
        
    Returns:
        Tuple[List[str], List[List[str]]]: A tuple containing the list of headers and list of rows.
    
    Raises:
        ValueError: If the CSV data is empty.
    """
    csv_reader = csv.reader(file_content.splitlines())
    csv_data = list(csv_reader)

    if not csv_data:
        raise ValueError('CSV data is empty.')

    headers = csv_data[0]
    rows = csv_data[1:]

    return headers, rows

def generate_email_body(headers: List[str], rows: List[List[str]], email_template: str, subject: str, intro_text: str, timestamp: str) -> str:
    """Generate email body by replacing placeholders in the template with actual data.
    
    Args:
        headers (List[str]): The list of headers.
        rows (List[List[str]]): The list of rows.
        email_template (str): The email template with placeholders.
        subject (str): The subject of the email.
        intro_text (str): The introductory text to be included in the email.
        timestamp (str): The timestamp when the email is sent.
        
    Returns:
        str: The email body with placeholders replaced by actual data.
    """
    # Generate header row HTML
    headers_html = "".join(f"<th>{header}</th>" for header in headers)

    # Generate table rows HTML
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>"
        for row in rows
    )

    # Replace placeholders in the email template with actual data
    email_body = (email_template.replace('%HEADERS%', headers_html)
                                .replace('%ROWS%', rows_html)
                                .replace('%SUBJECT%', subject)
                                .replace('%INTRO_TEXT%', intro_text)
                                .replace('%TIMESTAMP%', timestamp)
    )
    return email_body

def send_email(subject: str, email_body: str) -> dict:
    """Send an email using AWS SES.
    
    Args:
        subject (str): The subject of the email.
        email_body (str): The body of the email in HTML format.
        
    Returns:
        Dict: The response from the SES send_email API.
    """
    return ses_client.send_email(
        Source=os.environ['SENDER_EMAIL_ADDRESS'],
        Destination={
            'ToAddresses': [
                os.environ['RECIPIENT_EMAIL_ADDRESS']
            ]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Html': {
                    'Data': email_body
                }
            }
        }
    )

def lambda_handler(event: dict, context: object) -> dict:
    """Lambda function handler for processing S3 CSV upload notifications.
    
    Args:
        event (dict): The event data from S3.
        context (object): The context in which the Lambda function is called.
        
    Returns:
        dict: A status dictionary indicating success or failure.
    """
    s3_bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']

    # Read the file pattern for triggerin email from an environment variable
    filename_pattern = re.compile(os.environ['FILENAME_PATTERN'])

    if not filename_pattern.search(s3_object_key):
        print(f'Filename {s3_object_key} does not match the expected pattern.')
        return {'status': 'Filename does not match the expected pattern.'}

    try:
        response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_object_key)
        file_content = response['Body'].read().decode('utf-8')

        # Parse CSV data
        headers, rows = parse_csv(file_content)

        # Read email template from file
        with open(os.environ['EMAIL_TEMPLATE_PATH'], 'r') as file:
            email_template = file.read()

        # Populate email template and log email body to CloudWatch
        subject = os.environ.get('EMAIL_SUBJECT', 'S3 CSV Upload Notification')
        intro_text = os.environ.get('EMAIL_INTRO_TEXT', 'Please find the attached CSV file:')
        timestamp = datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

        email_body = generate_email_body(headers, rows, email_template, subject, intro_text, timestamp)
        print(f'Email body:\n{email_body}')

        # Send email
        email_response = send_email(subject, email_body)

        return {'status': 'Success', 'response': email_response}
    except Exception as e:
        print(e)
        raise e
