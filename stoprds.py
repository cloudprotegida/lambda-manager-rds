import boto3
import os


aws_region=os.environ['REGION']
target_tag_key=os.environ['TARGET_TAG_KEY']
target_tag_value=os.environ['TARGET_TAG_VALUE']
client=boto3.client('rds', region_name=aws_region)
response_instances=client.describe_db_instances()
response_clusters=client.describe_db_clusters()


def get_replicas():
    v_readReplica=[]
    for instance in response_instances['DBInstances']:
        readReplica=instance['ReadReplicaDBInstanceIdentifiers']
        if 0==len(readReplica):
            print('readReplica is null')
        else:
            v_readReplica.extend(readReplica)
    return v_readReplica   


def stop_db_instance():
    for instance in response_instances['DBInstances']:
        v_readReplica=get_replicas()
        if instance['DBInstanceStatus'] == 'available':
            if instance['Engine'] not in ['aurora-mysql','aurora-postgresql']:
                if instance['DBInstanceIdentifier'] not in v_readReplica and len(instance['ReadReplicaDBInstanceIdentifier']) == 0:
                    arn=instance['DBInstanceArn']
                    instance_tags=client.list_tags_for_resource(ResourceName=arn)
                    for tag in instance_tags['TagList']:
                            if tag['Key']==target_tag_key and tag['Value']==target_tag_value:
                                client.stop_db_instance(DBInstanceIdentifier=instance['DBInstanceIdentifier'])
                            else:
                                print('No tag configured')
        else: 
            print('Instance Status', instance['DBInstanceStatus'])


def stop_db_cluster():
    for instance in response_clusters['DBClusters']:
        cluster_identifier=instance['DBClusterIdentifier']
        cluarn=instance['DBClusterArn']
        if instance['Status'] == 'available':
            instance_tags=client.list_tags_for_resource(ResourceName=cluarn)
            for tag in instance_tags['TagList']:
                    if tag['Key']==target_tag_key and tag['Value']==target_tag_value:
                        client.stop_db_cluster(DBClusterIdentifier=instance['DBClusterIdentifier'])
                    else:
                        print('No tag configured')
        else: 
            print('Instance Status', instance['Status'])       

def lambda_handler(event, context):
    stop_db_instance()
    stop_db_cluster() 
