import boto3
import os

TAG_KEY = os.environ.get('TAG_KEY')
DRY_RUN = os.environ.get('DRY_RUN', False)


def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    response = ec2.describe_addresses(Filters=[
        {'Name': 'tag-key', 'Values': [TAG_KEY]}])
    associated_instances = []  # An array of instances with EIPs attached
    for address in response.get('Addresses', []):
        instance_id = address.get('InstanceId')
        if instance_id:
            associated_instances.append(instance_id)
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
            for resource in tag_response.get('Tags', []):
                instance_id = resource.get('ResourceId')
                allocation_id = address.get('AllocationId')
                if (instance_id not in associated_instances
                        and resource.get('ResourceType')
                        in ('instance', 'network-interface')):
                    assoc_response = ec2.associate_address(
                            AllocationId=allocation_id,
                            InstanceId=instance_id,
                            DryRun=DRY_RUN)
                    assocation_id = assoc_response.get('AssociationId')
                    print ("%s given to %s (%s)" % (address.get('PublicIp'),
                           instance_id, assocation_id))
                    break
