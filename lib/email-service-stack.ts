import { Stack, StackProps } from 'aws-cdk-lib';
import { LambdaDestination } from 'aws-cdk-lib/aws-s3-notifications';
import { PolicyStatement } from 'aws-cdk-lib/aws-iam';
import { Function, Code, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Bucket, EventType } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

interface EmailServiceStackProps extends StackProps {
  readonly emailSourceBucketName: string;
  readonly filenamePattern: string;
  readonly senderEmailAddress: string;
  readonly recipientEmailAddress: string;
  readonly emailTemplatePath: string;
}

export class EmailServiceStack extends Stack {
    constructor(scope: Construct, id: string, props: EmailServiceStackProps) {
        super(scope, id, props);

        // Reference the existing S3 bucket with the data to be mailed
        const emailSourceBucket = Bucket.fromBucketName(this, 'EmailSourceBucket', props.emailSourceBucketName);

        // Create the Lambda function for sending the email
        const emailServiceLambda = new Function(this, 'EmailServiceLambda', {
            functionName: 'EmailServiceLambda',
            runtime: Runtime.PYTHON_3_9,
            handler: 'send_email.lambda_handler',
            code: Code.fromAsset('lambda'),
            environment: {
                TARGET_S3_BUCKET_NAME: props.emailSourceBucketName,
                FILENAME_PATTERN: props.filenamePattern,
                SENDER_EMAIL_ADDRESS: props.senderEmailAddress,
                RECIPIENT_EMAIL_ADDRESS: props.recipientEmailAddress,
                EMAIL_TEMPLATE_PATH: props.emailTemplatePath
            },
        });

        // Grant S3 read permissions to the Lambda function
        emailSourceBucket.grantRead(emailServiceLambda);

        // Grant SES send email permissions to the Lambda function
        emailServiceLambda.addToRolePolicy(new PolicyStatement({
            actions: ['ses:SendEmail', 'ses:SendRawEmail'],
            resources: ['*']
        }));

        // Add S3 event notification to trigger the Lambda function
        emailSourceBucket.addEventNotification(EventType.OBJECT_CREATED, new LambdaDestination(emailServiceLambda));
    }
}
