#!/usr/bin/python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Core function handler
def handler(event, context):
    logger.debug('event: {}'.format(event))
    logger.debug('context: {}'.format(context))
    return {
        "requestId": event["requestId"],
        "status": "success",
        "fragment": convert_template(event["fragment"], event["templateParameterValues"]),
    }

# Function to convert/expand the template
def convert_template(fragment, param):
    # Debug output
    logger.debug('This was the fragment: {}'.format(fragment))
    
    # Loop through each resource in the template
    resources = fragment['Resources']
    resources = fragment['Resources']
    for resource in resources:
        logger.debug('Determining if {} is a TaskDefinition'.format(resource))
        resourcejson = resources[resource]
        # If the resource is an IAM Role, expand the shorthand notation to the proper
        # CloudFormation using the function below, otherwise leave the resource as is
        if resourcejson['Type'] == 'AWS::ECS::TaskDefinition':
            logger.info('Found a task definition: {}'.format(resource))
            # Expanding Container Definition
            for container_definition in resourcejson['Properties']['ContainerDefinitions']:
                container_definition = expand_container_definition(container_definition, param)
    
    # Debug output
    logger.debug('This is the transformed fragment: {}'.format(fragment))
    # Return the converted/expanded template fragment
    return fragment

# Function to expand shorthand container definitions into proper CloudFormation
def expand_container_definition(container_definition, param):
    # Debug
    logger.info('container_definition: {}'.format(container_definition))
    logger.debug('Environment: {}'.format(container_definition['Environment']))
    container_definition['Environment'] = expand_environment(container_definition['Environment'], param)
    
    logger.debug('Secrets: {}'.format(container_definition['Secrets']))
    container_definition['Secrets'] = expand_secrets(container_definition['Secrets'], param)
    # Return the expanded proper CloudFormation 
    return container_definition

def expand_environment(environment, param):

    # TODO handle other than Ref
    ref_key = environment['Ref']
    ref_value = param[ref_key]
    if ref_value and ref_value.strip():
        return split_envs(ref_value)
    else:
        return []
def split_envs(string_input):
    res = list(
        map(lambda x: x.split('='), string_input.split(';'))
    )
    envs = []
    for i in res:
        envs.append({"Name" : i[0], "Value" : i[1]})

    return envs

def expand_secrets(secrets, param):

    # TODO handle other than Ref
    ref_key = secrets['Ref']
    ref_value = param[ref_key]

    if ref_value and ref_value.strip():
        return split_secrets_with_parameter_store(ref_value)
    else:
        return []

def split_secrets_with_parameter_store(string_input):
    res = list(
        map(lambda x: x.split('='), string_input.split(';'))
    )
    secrets = []
    for i in res:
        secrets.append({ "Name" : i[0], "ValueFrom" : {"Fn::Sub": "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/" + i[1]}})

    return secrets