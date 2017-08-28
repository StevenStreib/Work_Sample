import troposphere.ec2 as ec2
import troposphere.sns as sns
from troposphere import Join, Output, Ref, Tags, Template

# Create template object. This will be added to throughout the script
template = Template()

# Set Description and add to template
description = "Service VPC - used for services"
template.add_description(description)

# Set Metadata and add to template
metadata = {
    "Build": "development",
    "DependsOn": [],
    "Environment": "ApiDev",
    "Revision": "develop",
    "StackName": "ApiDev-Dev-VPC",
    "StackType": "InfrastructureResource",
    "TemplateBucket": "cfn-apidev",
    "TemplateName": "VPC",
    "TemplatePath": "ApiDev/Dev/VPC"
}
template.add_metadata(metadata)

# Create Parameters and add to template


# Populate Outputs and add to template
outputs = [
    Output("BastionSG", Value=Ref("BastionSG")),
    Output("CloudWatchAlarmTopic", Value=Ref("CloudWatchAlarmTopic")),
    Output("InternetGateway", Value=Ref("InternetGateway")),
    Output("NatEmergencyTopicARN", Value=Ref("NatEmergencyTopic")),
    Output("VPCID", Value=Ref("VPC")),
    Output("VPCName", Value=Ref("AWS::StackName")),
    Output("VpcNetworkAcl", Value=Ref("VpcNetworkAcl"))
]
template.add_output(outputs)

# Declare Tags Dictionary to be used throughout resource declaration
resource_tags = {
    "Environment": "ApiDev",
    "Name": "",
    "Owner": "Foo industries",
    "Service": "ServiceVPC",
    "VPC": "Dev"
}

# Add Security Group for Bastion Hosts
resource_tags.update({"Name": "ApiDev-Dev-VPC-Bastion-SG"})
BastionSGProperties = {
    "GroupDescription": "Used for source/dest rules",
    "Tags": Tags(resource_tags),
    "VpcId": Ref("VPC")
}
BastionSG = ec2.SecurityGroup(
    "BastionSG",
    GroupDescription=BastionSGProperties.get("GroupDescription"),
    Tags=BastionSGProperties.get("Tags"),
    VpcId=BastionSGProperties.get("VpcId")
)
template.add_resource(BastionSG)

# Add CloudWatch Alarm Topic from SNS
CloudWatchAlarmTopic = sns.Topic(
    "CloudWatchAlarmTopic",
    TopicName="ApiDev-Dev-CloudWatchAlarms"
)
template.add_resource(CloudWatchAlarmTopic)

# Add DHCP Options
resource_tags.update({"Name": "ApiDev-Dev-DhcpOptions"})
DhcpOptions = ec2.DHCPOptions(
    "DhcpOptions",
    DomainName=Join("", (Ref("AWS::Region"), ".compute.internal")),
    DomainNameServers=["AmazonProvidedDNS"],
    Tags=Tags(resource_tags)
)
template.add_resource(DhcpOptions)

# Add Internet Gateway
resource_tags.update({"Name": "ApiDev-Dev-InternetGateway"})
InternetGateway = ec2.InternetGateway(
    "InternetGateway",
    Tags=Tags(resource_tags)
)
template.add_resource(InternetGateway)

# Add NAT Emergency SNS Topic
NatEmergencyTopic = sns.Topic(
    "NatEmergencyTopic",
    TopicName="ApiDev-Dev-NatEmergencyTopic"
)
template.add_resource(NatEmergencyTopic)

# Add VPC
resource_tags.update({"Name": "ApiDev-Dev-ServiceVPC"})
VPC = ec2.VPC(
    "VPC",
    CidrBlock="10.0.0.0/16",
    EnableDnsHostnames="true",
    EnableDnsSupport="true",
    InstanceTenancy="default",
    Tags=Tags(resource_tags)
)
template.add_resource(VPC)

# Add DHCP Options Set Association
VpcDhcpOptionsAssociation = ec2.VPCDHCPOptionsAssociation(
    "VpcDhcpOptionsAssociation",
    DhcpOptionsId=Ref("DhcpOptions"),
    VpcId=Ref("VPC")
)
template.add_resource(VpcDhcpOptionsAssociation)

# Attach Internet Gateway to VPC
VpcGatewayAttachment = ec2.VPCGatewayAttachment(
    "VpcGatewayAttachment",
    InternetGatewayId=Ref("InternetGateway"),
    VpcId=Ref("VPC")
)
template.add_resource(VpcGatewayAttachment)

# Add VPC Network ACL
resource_tags.update({"Name": "ApiDev-Dev-NetworkAcl"})
VpcNetworkAcl = ec2.NetworkAcl(
    "VpcNetworkAcl",
    Tags=Tags(resource_tags),
    VpcId=Ref("VPC")
)
template.add_resource(VpcNetworkAcl)

# Add ACL rule for inbound public traffic over port 443
VpcNetworkAclInboundRulePublic443 = ec2.NetworkAclEntry(
    "VpcNetworkAclInboundRulePublic443",
    CidrBlock="0.0.0.0/0",
    Egress="false",
    NetworkAclId=Ref("VpcNetworkAcl"),
    PortRange=ec2.PortRange(
        From="443",
        To="443"
    ),
    Protocol="6",
    RuleAction="allow",
    RuleNumber=20001
)
template.add_resource(VpcNetworkAclInboundRulePublic443)

# Add ACL rule for inbound public traffic over port 80
VpcNetworkAclInboundRulePublic80 = ec2.NetworkAclEntry(
    "VpcNetworkAclInboundRulePublic80",
    CidrBlock="0.0.0.0/0",
    Egress="false",
    NetworkAclId=Ref("VpcNetworkAcl"),
    PortRange=ec2.PortRange(
        From="80",
        To="80"
    ),
    Protocol="6",
    RuleAction="allow",
    RuleNumber=20000
)
template.add_resource(VpcNetworkAclInboundRulePublic80)

# Add ACL rule for outbound traffic
VpcNetworkAclOutboundRule = ec2.NetworkAclEntry(
    "VpcNetworkAclOutboundRule",
    CidrBlock="0.0.0.0/0",
    Egress="true",
    NetworkAclId=Ref("VpcNetworkAcl"),
    Protocol="-1",
    RuleAction="allow",
    RuleNumber=30000
)
template.add_resource(VpcNetworkAclOutboundRule)

# Add ACL rule for SSH access from localhost
VpcNetworkAclSsh = ec2.NetworkAclEntry(
    "VpcNetworkAclSsh",
    CidrBlock="127.0.0.1/32",
    Egress="false",
    NetworkAclId=Ref("VpcNetworkAcl"),
    PortRange=ec2.PortRange(
        From="22",
        To="22"
    ),
    Protocol="6",
    RuleAction="allow",
    RuleNumber=10000
)
template.add_resource(VpcNetworkAclSsh)

# Print Template to file
file = open("worksample_generated.cfn.template", "w")
file.truncate()
file.write(template.to_json())
file.close()
