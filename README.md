# Amazon Nova Computer Use Demo
- This demo is modified from [Anthropic Computer Use Demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)

## Quickstart: running the Docker container

## Build container

```bash
./setup.sh  # configure venv, install development dependencies, and install pre-commit hooks
docker build . -t computer-use-demo:local  # manually build the docker image (optional)

The docker run command above mounts the repo inside the docker image, such that you can edit files from the host. Streamlit is already configured with auto reloading.

### Configure Bedrock

> [!TIP]
> To use the new Claude 3.5 Sonnet on Bedrock, you first need to [request model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html).

You'll need to pass in AWS credentials with appropriate permissions to use Claude on Bedrock.

You have a few options for authenticating with Bedrock. See the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables) for more details and options.

#### Option 1: (suggested) Use the host's AWS credentials file and AWS profile

```bash
export AWS_PROFILE=<your_aws_profile>
docker run \
    -e API_PROVIDER=bedrock_nova \
    -e AWS_PROFILE=$AWS_PROFILE \
    -e AWS_REGION=us-east-1 \
    -v $HOME/.aws:/home/computeruse/.aws \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -it computer-use-demo:local 
```

Once the container is running, see the [Accessing the demo app](#accessing-the-demo-app) section below for instructions on how to connect to the interface.

#### Option 2: Use an access key and secret
- `AWS_SESSION_TOKEN` is optional
```bash
export AWS_ACCESS_KEY_ID=%your_aws_access_key%
export AWS_SECRET_ACCESS_KEY=%your_aws_secret_access_key%
export AWS_SESSION_TOKEN=%your_aws_session_token%
docker run \
    -e API_PROVIDER=bedrock_nova \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    -e AWS_REGION=us-east-1 \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -it computer-use-demo:local 
```

Once the container is running, see the [Accessing the demo app](#accessing-the-demo-app) section below for instructions on how to connect to the interface.


### Accessing the demo app

Once the container is running, open your browser to [http://localhost:8080](http://localhost:8080) to access the combined interface that includes both the agent chat and desktop view.

The container stores settings like the API key and custom system prompt in `~/.anthropic/`. Mount this directory to persist these settings between container runs.

Alternative access points:

- Streamlit interface only: [http://localhost:8501](http://localhost:8501)
- Desktop view only: [http://localhost:6080/vnc.html](http://localhost:6080/vnc.html)
- Direct VNC connection: `vnc://localhost:5900` (for VNC clients)

## Screen size

Environment variables `WIDTH` and `HEIGHT` can be used to set the screen size. For example:

```bash
docker run \
    -e API_PROVIDER=bedrock_nova \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    -e AWS_REGION=us-west-2 \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -e WIDTH=1920 \
    -e HEIGHT=1080 \
    -it computer-use-demo:local 
```
