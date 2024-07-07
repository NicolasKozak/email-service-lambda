export const EMAIL_SOURCE_BUCKET_NAME = "data-for-email-service";
export const FILENAME_PATTERN = "^athena-output/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}.csv$";
export const SENDER_EMAIL_ADDRESS = "example_email+my-cdk-email-service@gmail.com";
export const RECIPIENT_EMAIL_ADDRESS = "example_email+my-cdk-email-recipient@gmail.com";
export const EMAIL_TEMPLATE_PATH = "email_template.html";
export const EMAIL_SUBJECT = "My custom SES notification";
export const EMAIL_INTRO_TEXT = "Find attached the CSV data from S3:";

  