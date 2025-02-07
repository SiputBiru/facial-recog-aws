import boto3
import json
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition', region_name='ap-southeast-2')
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table('DYNMODBTABLE')
bucketName = 'VISITOR_BUCKET'

def lambda_handler(event, context):
    print(event)
    try:
        body = json.loads(event['body'])
        objectKey = body['objectKey']
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        return buildResponse(400, {'Message': 'Missing or invalid objectKey parameter'})

    try:
        response = rekognition_client.search_faces_by_image(
            CollectionId='employees',
            Image={
                'S3Object': {
                    'Bucket': bucketName,
                    'Name': objectKey
                }
            }
        )
    except ClientError as e:
        print(f'Rekognition error: {e}')
        return buildResponse(500, {'Message': 'Face detection failed'})

    for match in response['FaceMatches']:
        confidence = match['Similarity']
            
        try:
            face = table.get_item(
                Key={
                    'rekognitionid': match['Face']['FaceId']
                }
            )
        except ClientError as e:
            print(f'DynamoDB error: {e}')
            return buildResponse(500, {'Message': 'Database query failed'})

        if 'Item' in face:
            return buildResponse(200, {
                'Message': 'Success',
                'firstName': face['Item']['firstName'],
                'lastName': face['Item']['lastName'],
                'confidence': confidence
            })

    return buildResponse(404, {'Message': 'Person not found'})

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response
