#!/usr/bin/env node
import { App} from 'aws-cdk-lib';
import { EmailServiceStack } from '../lib/email-service-stack';
import {
  EMAIL_INTRO_TEXT,
  EMAIL_SOURCE_BUCKET_NAME,
  EMAIL_SUBJECT,
  EMAIL_TEMPLATE_PATH,
  FILENAME_PATTERN,
  RECIPIENT_EMAIL_ADDRESS,
  SENDER_EMAIL_ADDRESS
} from '../constants';

const app = new App();

new EmailServiceStack(app, 'EmailServiceStack', {
  emailSourceBucketName: EMAIL_SOURCE_BUCKET_NAME,
  filenamePattern: FILENAME_PATTERN,
  senderEmailAddress: SENDER_EMAIL_ADDRESS,
  recipientEmailAddress: RECIPIENT_EMAIL_ADDRESS,
  emailTemplatePath: EMAIL_TEMPLATE_PATH,
  emailSubject: EMAIL_SUBJECT,
  emailIntroText: EMAIL_INTRO_TEXT 
});
