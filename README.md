# Env Secret Builder CloudFormation Macro

The `Env Secret Builder` macro provides capability for developers to add a list of environment variables and secrets as parameters of cloudformation.

See below for instructions to install and use the macro and for a full description of the macro's features.

This macro is public available in Serverless Application Repository with name: `ECSTaskDefinitionEnvSecretBuilder`

## How to install and use the ShortHand macro in your AWS account

### Deploying

1. You will need an S3 bucket to store the CloudFormation artifacts:
    * If you don't have one already, create one with `aws s3 mb s3://<bucket name>`

2. Package the Macro CloudFormation template. The provided template uses [the AWS Serverless Application Model](https://aws.amazon.com/about-aws/whats-new/2016/11/introducing-the-aws-serverless-application-model/) so must be transformed before you can deploy it.

    ```shell
    aws cloudformation package \
        --template-file macro.template \
        --s3-bucket <your bucket name here> \
        --output-template-file EnvSecretBuilderCFnMacro.packaged.template
    ```

4. Deploy the packaged CloudFormation template to a CloudFormation stack:

    ```shell
    aws cloudformation deploy \
        --stack-name EnvSecretBuilderCFnMacro \
        --template-file EnvSecretBuilderCFnMacro.packaged.template \
        --capabilities CAPABILITY_IAM 
    ```

5. To test out the macro's capabilities, try launching the provided example template:

    ```shell
    aws cloudformation deploy \
        --stack-name EnvSecretBuilder-macro-example \
        --template-file example.template \
        --parameter-overrides ExecutionRoleArn=<your execution role arn> TaskRoleArn=<your task role arn> Image=<you docker image here> Envs=<yours envs here like 'A=1;B=2'> Secrets=<yours parameter store here like'SECRET1=/RDE/Tests/DB/password;SECRET2=/RDE/Tests/DB/username'>\
        --capabilities CAPABILITY_IAM 
    ```

### Usage

To make use of the macro, add `Transform: EnvSecretBuilder` to the top level of your CloudFormation template.

Then specify a list of environment variables and secrets using Parameters:

this macro will transform this template with `Envs='A=1;B=2'` and `Secrets='SECRET1=username;SECRET2=password'`:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: EnvSecretBuilder
Parameters:
  Envs:
    Type: String
    Description: Environment variables  
    Default: 'A=1;B=2'
  Secrets:
    Type: String
    Description: Secrets
    Default: 'SECRET1=username;SECRET2=password'
Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family:                ecs-task-definition-example
      RequiresCompatibilities:
        - EC2
      ContainerDefinitions:
        - Name:              ecs-container-definition-example
          Image:             <Your docker image>
          Environment:       !Ref Envs
          Secrets:           !Ref Secrets
```

into this template:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: EnvSecretBuilder
Parameters:
  Envs:
    Type: String
    Description: Environment variables  
    Default: 'A=1;B=2'
  Secrets:
    Type: String
    Description: Secrets
    Default: 'SECRET1=username;SECRET2=password'
Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family:                ecs-task-definition-example
      RequiresCompatibilities:
        - EC2
      ContainerDefinitions:
        - Name:              ecs-container-definition-example
          Image:             <Your docker image>
          Environment:
            - Name: A
              Value: 1
            - Name: B
              Value: 2
          Secrets:
            - Name: SECRET1
              ValueFrom: !Sub arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/username
            - Name: SECRET2
              ValueFrom: !Sub arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/password
```

## Author

[Martin Wang](www.linkedin.com/in/martin-wang-a980159b)
Cloud Solutions Architect
