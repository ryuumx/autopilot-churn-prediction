import json
import os
import logging
import boto3
# import requests

MODELENDPOINT = os.environ['MODELENDPOINT']
LOG_LEVEL = logging.INFO
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    try:
        logger.info("Start processing")
        runtime = boto3.client('runtime.sagemaker')
        
        data = event["body"]
        logger.info("Data to predict: " + str(data))
    
        response = runtime.invoke_endpoint(EndpointName=MODELENDPOINT,
                                       ContentType='text/csv',
                                       Body=data)
        
        resultString = response['Body'].read().decode()
        logger.info("ML model response: " + str(resultString))

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            results = resultString.split(',')
            answer = results[0]
            confidence = (1.0 - float(results[1])) if answer == "no" else float(results[1])

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "answer": answer,
                    "confidence": confidence
                }),
            }
        else:
            raise Exception("Inference failed. Error: " + str(resultString))
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            }),
        }
