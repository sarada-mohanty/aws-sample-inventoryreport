import boto3
import datetime
import time
from pprint import pprint
import csv
from io import StringIO

today = datetime.datetime.now()
date_time = today.strftime("%d-%m-%Y")
month = today.strftime("%m")
year = today.strftime("%Y")
day = today.strftime("%d")
s3path = year+'/'+month+'/'+day

def lambda_handler(event, context):
    
    ssm = boto3.client('ssm',region_name='us-east-1')

    ssm_res = ssm.get_parameters(Names=['Inventory-Engine-Accounts'], WithDecryption=True)
    x = ssm_res.get('Parameters')
    aws_accountnumbers = x[0]['Value']
    

    a = aws_accountnumbers.replace('\n','')
    acct_list = a.split(',')
    #pprint(b)
    
    
    #acct_list=event["Account_List"]   
    print(acct_list)
    ec2_serv = boto3.client('ec2')
    print("\nFetching all available regions...hold on !!")
    all_regions = ec2_serv.describe_regions().get('Regions')
    #print(all_regions)
    region_list = []
    for a in all_regions:
        b = a.get('RegionName')
        region_list.append(b)
    print("\nThese are the available region to scan \n")
    print(region_list)
    header_csv = ['S_No','AccountID','InstanceName','InstanceID','InstanceType','CurrentStatus','PrivateIP','PublicIP','VPCID','Region','LaunchTime']
    with open("/tmp/ec2_inventory.csv", "w") as f:
        #fo = open("/tmp/ec2_inventory.csv","w")
        f = StringIO()
        csv_w = csv.writer(f)
        csv_w.writerow(header_csv)
    
    #acct_list=event["Account_List"]   
    S_No = 1
    #acct_list = []
    for acct_id in acct_list:
        print('\n Scanning Inventory for account: '+acct_id)
        sts_connection = boto3.client('sts')
        acct_b = sts_connection.assume_role(RoleArn="arn:aws:iam::"+acct_id+":role/Inventory-IAM-Execution-Role",RoleSessionName="cross_acct_lambda")
    
        ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
        SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
        SESSION_TOKEN = acct_b['Credentials']['SessionToken']
    
        print("\nNow Scanning for all ec2 instances in above regions...hold on !!")    
        for region in region_list:
            ec2 = boto3.resource('ec2',region_name=region,aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN)
            #print("\nNow Scanning for all ec2 instances in above regions...hold on !!")
            for each_in in ec2.instances.all():
                #pprint(dir(each_in))
                ins_id = each_in.instance_id
                ins_type = each_in.instance_type
                launch_time = each_in.launch_time
                for tag in each_in.tags:
                    if tag['Key'] == 'Name':
                        ins_tag = tag['Value']
                ins1_state = each_in.state
                ins_state = ins1_state.get('Name')
                #pprint(ins_state)
                pvt_ip = each_in.private_ip_address
                pub_ip = each_in.public_ip_address
                vpcid = each_in.vpc_id
                print("\nWriting instance "+ins_tag+" data in to CSV file...")
                csv_w.writerow([S_No,acct_id,ins_tag,ins_id,ins_type,ins_state,pvt_ip,pub_ip,vpcid,region,launch_time])
                S_No = S_No+1
        #time.sleep(3)
        print("\nCSV is ready now uploading to S3...")
        s3client = boto3.client('s3',region_name='us-east-1')
        s3client.put_object(Bucket='mys3bucket',ContentType='application/vnd.ms-excel', Body=f.getvalue(),Key= (s3path+'/'+'EC2_Inventory_'+date_time+'.csv'))
    f.close()
    print("\nCongratulations CSV is uploaded to S3 successfully...Enjoy :)")

