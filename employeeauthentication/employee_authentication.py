import boto3
import json
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='ap-southeast-2')
dynamodbTableName = 'rekog-employee'
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
employeeTable = dynamodb.Table(dynamodbTableName)
bucketName = 'rekog-visitor-pics'

def lambda_handler(event, context):
    print(event)
    try:
        objectKey = event['queryStringParameters']['objectKey']
    except (KeyError, TypeError) as e:
        return buildResponse(400, {'Message': 'Missing or invalid objectKey parameter'})

    try:
        image_bytes = s3.get_object(Bucket=bucketName, Key=objectKey)['Body'].read()
    except ClientError as e:
        print(f'Error retrieving image: {e}')
        return buildResponse(404, {'Message': 'Image not found'})

    try:
        response = rekognition.search_faces_by_image(
            CollectionId='employees',
            Image={'Bytes': image_bytes}
        )
    except ClientError as e:
        print(f'Rekognition error: {e}')
        return buildResponse(500, {'Message': 'Face detection failed'})

    for match in response['FaceMatches']:
        confidence = match['Similarity']
            
        try:
            face = employeeTable.get_item(
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