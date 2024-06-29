import os
import boto3
import re
import csv

s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

def lambda_handler(event, context):
    s3_bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']

    # Read the file pattern from an environment variable
    filename_pattern = re.compile(os.environ['FILENAME_PATTERN'])

    if not filename_pattern.search(s3_object_key):
        print(f'Filename {s3_object_key} does not match the expected pattern.')
        return {'status': 'Filename does not match the expected pattern.'}

    try:
        response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_object_key)
        file_content = response['Body'].read().decode('utf-8')

         # Parse CSV data
        csv_reader = csv.reader(file_content.splitlines())
        csv_data = list(csv_reader)

        # Log CSV data to Cloudwatch    
        print(f'CSV data:\n{csv_data}')

        # Read email template from file
        with open(os.environ['EMAIL_TEMPLATE_PATH'], 'r') as file:
            email_template = file.read()

        # Generate table rows
        rows_html = ""
        for row in csv_data:
            rows_html += "<tr>"
            for col in row:
                rows_html += f"<td>{col}</td>"
            rows_html += "</tr>"

        # Replace %ROWS% placeholder in email template with actual rows
        email_body = email_template.replace('%ROWS%', rows_html)
        
        # Log email body for debugging
        print(f'Email body:\n{email_body}')
        
        email_response = ses_client.send_email(
            Source= os.environ['SENDER_EMAIL_ADDRESS'],
            Destination={
                'ToAddresses': [
                    os.environ['RECIPIENT_EMAIL_ADDRESS']
                ]
            },
            Message={
                'Subject': {
                    'Data': 'S3 Upload Notification'
                },
                'Body': {
                    'Html': {
                        'Data': email_body
                    }
                }
            }
        )

        return {'status': 'Success', 'response': email_response}
    except Exception as e:
        print(e)
        raise e
