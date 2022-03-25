# AWS Resources Inventory Report in CSV
Objective: To get all desired AWS resources (in this case EC2 instances) details as inventory report in CSV format. This setup will scan single or multiple AWS accounts and will fetch all EC2 running with custom tags and will store the output in S3 in csv format.

Steps:
Create in master/central account:
1. Create a S3 bucket and give a unique bucket name 
2. Create Lambda master IAM role for Lambda with full EC2, S3 and SSM parameter store permission (Restric to specific permissions in case of actual production setup)
3. Create a SSM parameter store and add desired AWS account numbers as shown below:
![image](https://user-images.githubusercontent.com/90566922/157006956-e6ba233e-c0d4-4a6e-8b06-c990ebf9b732.png)
4. Create a Lambda function and paste the complete EC2-Inventory-CrossAccount-Lambda - Ver-2.py code. Attach above created IAM role and set timeout to 5 minutes.
5. Replace <your_parameter_store_name> in line 19 of the Lambda script with actual SSM parameter name created above.
5. Replace <your_bucket_name>

This script will scan single or multiple AWS accounts and will fetch all EC2 running with custom tags and will store the output in S3 in csv format.
