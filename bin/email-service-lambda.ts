#!/usr/bin/env node
import { App} from 'aws-cdk-lib';
import { EmailServiceStack } from '../lib/email-service-stack';
import { readFileSync} from 'fs';

const app = new App();

const emailConfig = JSON.parse(readFileSync('email-config.json', 'utf8'));

new EmailServiceStack(app, 'EmailServiceStack', {
  emailSourceBucketName: emailConfig.emailSourceBucketName,
  filenamePattern: emailConfig.filenamePattern,
  senderEmailAddress: emailConfig.senderEmailAddress,
  recipientEmailAddress: emailConfig.recipientEmailAddress,
  emailTemplatePath: emailConfig.emailTemplatePath
});