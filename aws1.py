import boto3
ec2 = boto3.resource('ec2')

vpc = ec2.create_vpc(CidrBlock='172.17.0.0/16')

vpc.create_tags(Tags=[{"Key": "Name", "Value": "devops"}])

vpc.wait_until_available()

ec2Client = boto3.client('ec2')
ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsSupport = { 'Value': True } )
ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsHostnames = { 'Value': True } )

internetgateway = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=internetgateway.id)

routetable = vpc.create_route_table()
route = routetable.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internetgateway.id)

subnet = ec2.create_subnet(CidrBlock='172.17.1.0/24', VpcId=vpc.id)
routetable.associate_with_subnet(SubnetId=subnet.id)

securitygroup = ec2.create_security_group(GroupName='devops', Description='SSH AND HTTP', VpcId=vpc.id)
securitygroup.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
securitygroup.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=80, ToPort=80)

outfile = open('devops_lab.pem', 'w')

key_pair = ec2.create_key_pair(KeyName='devops_lab')

KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)

instances = ec2.create_instances(
 ImageId='ami-0b24a34cb636c19ec',
 InstanceType='t2.micro',
 MaxCount=1,
 MinCount=1,
 NetworkInterfaces=[{
 'SubnetId': subnet.id,
 'DeviceIndex': 0,
 'AssociatePublicIpAddress': True,
 'Groups': [securitygroup.group_id]
 }],
 KeyName='ec2-keypair')
