#!/usr/bin/env node
import { App} from 'aws-cdk-lib';
import { EmailServiceStack } from '../lib/email-service-stack';
import { readFileSync} from 'fs';

const app = new App();

const EMAIL_SOURCE_BUCKET_NAME = 'data-for-email-service';  // Replace with your bucket name
const S3_PREFIX = 'athena-output/';
const FILENAME_PATTERN = `^${S3_PREFIX}[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\.csv$`;  // Athena query ID pattern
const EMAIL_TEMPLATE_FILENAME = 'email_template.html'

const emailConfig = JSON.parse(readFileSync('email-config.json', 'utf8'));

new EmailServiceStack(app, 'EmailServiceStack', {
  emailSourceBucketName: EMAIL_SOURCE_BUCKET_NAME,
  filenamePattern: FILENAME_PATTERN,
  senderEmailAddress: emailConfig.senderEmailAddress,
  recipientEmailAddress: emailConfig.recipientEmailAddress,
  emailTemplatePath: EMAIL_TEMPLATE_FILENAME
});