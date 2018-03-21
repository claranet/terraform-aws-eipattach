import boto3
import os

TAG_KEY = os.environ.get('TAG_KEY')
DISABLE_SOURCE_DEST = False
if os.environ.get('DISABLE_SOURCE_DEST', 'false') != 'false':
    DISABLE_SOURCE_DEST = True


def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    response = ec2.describe_addresses(Filters=[
        {'Name': 'tag-key', 'Values': [TAG_KEY]}])
    associated_instances = []  # An array of instances with EIPs attached
    for address in response.get('Addresses', []):
        resource_id = address.get('InstanceId')
        eni_id = address.get('NetworkInterfaceId')
        if resource_id:
            associated_instances.append(resource_id)
        if eni_id:
            associated_instances.append(eni_id)
    # Loop through again looking for unattached EIPs and attach them
    for address in response.get('Addresses', []):
        if not address.get('AssociationId'):
            tag_value = ""
            for tag_pair in address.get('Tags', []):
                if tag_pair.get('Key') == TAG_KEY:
                    tag_value = tag_pair.get('Value')
            tag_response = ec2.describe_tags(Filters=[{
                    'Name': 'tag:' + TAG_KEY,
                    'Values': [tag_value],
                     }])
            public_ip = address.get('PublicIp')
            for resource in tag_response.get('Tags', []):
                resource_id = resource.get('ResourceId')  # Could be an ENI ID
                allocation_id = address.get('AllocationId')
                resource_type = resource.get('ResourceType')
                if (resource_id not in associated_instances
                        and resource_type in
                        ('instance', 'network-interface')):
                    assoc_response = {}
                    if resource_type == 'instance':
                        try:
                            assoc_response = ec2.associate_address(
                                    AllocationId=allocation_id,
                                    InstanceId=resource_id)
                            if DISABLE_SOURCE_DEST:
                                print("Disabling source/dest check for ",
                                      resource_id)
                                ec2.modify_instance_attribute(
                                        SourceDestCheck={'Value': False},
                                        InstanceId=resource_id)
                        except:
                            print("Error associating %s with %s" %
                                  public_ip, resource_id)
                    if resource_type == 'network-interface':
                        try:
                            assoc_response = ec2.associate_address(
                                    AllocationId=allocation_id,
                                    NetworkInterfaceId=resource_id)
                        except:
                            print("Error associating %s with %s" %
                                  public_ip, resource_id)
                    assocation_id = assoc_response.get('AssociationId')
                    if assocation_id:
                        print ("%s given to %s (%s)" % (public_ip,
                               resource_id, assocation_id))
                        break
