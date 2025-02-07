import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='REGION')
dynamodbTableName = 'YOUR_DYNODB_TABLE_NAME' # Your DynamoDB table name here
dynamodb = boto3.resource('dynamodb', region_name='REGION')
employeeTable = dynamodb.Table(dynamodbTableName)

def lambda_handler(event, context):
    print(event)
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
    except KeyError as e:
        print(f'Invalid event structure: {e}')
        raise

    try:
        response = index_employee_image(bucket, key)
        print(response)
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and response['FaceRecords']:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            try:
                name_parts = key.split('.')[0].split('_')
                if len(name_parts) != 2:
                    raise ValueError(f'Invalid filename format: {key}')
                firstName, lastName = name_parts
                register_employee(faceId, firstName, lastName)
            except (IndexError, ValueError) as e:
                print(f'Error parsing employee name from filename: {e}')
                raise
        return response
    
    except ClientError as e:
        print(f'AWS service error: {e}')
        raise
    except Exception as e:
        print(f'Error processing employee image {key} from bucket {bucket}: {e}')
        raise

def index_employee_image(bucket, key):
    try:
        response = rekognition.index_faces(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            },
            CollectionId='employees'
        )
        return response
    except ClientError as e:
        print(f'Rekognition indexing error: {e}')
        raise

def register_employee(faceId, firstName, lastName):
    try:
        employeeTable.put_item(
            Item={
                'rekognitionid': faceId,
                'firstName': firstName,
                'lastName': lastName
            }
        )
    except ClientError as e:
        print(f'DynamoDB error: {e}')
        raise