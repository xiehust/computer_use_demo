import boto3
import os
import json
from anthropic.types.beta import (
    BetaUsage,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolUseBlock,
    BetaToolResultBlockParam)


DEFAULT_REGION = 'us-east-1'
NOVA_PRO_MODEL_ID = "us.amazon.nova-pro-v1:0"

def _convert_response_to_anthropic(response) ->BetaMessage:
    json_response = json.loads(response["body"].read())

    if "output" in json_response:
        return BetaMessage(
            id=response["ResponseMetadata"]["RequestId"],
            role="assistant",
            content=_convert_content_to_anthropic(json_response["output"]["message"]["content"]),
            model=NOVA_PRO_MODEL_ID,
            type = "message",
            stop_reason=json_response["stopReason"],
            usage=BetaUsage(
                input_tokens=json_response["usage"]["inputTokens"],
                output_tokens=json_response["usage"]["outputTokens"]
            )
        )
    else:
        raise ValueError(f"output key not exisit")
    

def _convert_content_to_anthropic(content):
    converted_content = []
    for content_block in content:
        if "text" in content_block:
            converted_content.append(
                BetaTextBlock(
                    text=content_block["text"],
                    type="text"
                )
            )
        elif "toolUse" in content_block:
            converted_content.append(
                BetaToolUseBlock(
                    id=content_block['toolUse']["toolUseId"],
                    input=content_block['toolUse']["input"],
                    name=content_block['toolUse']["name"],
                    type="tool_use"
                )
            )
        else:
            raise ValueError(f"Unknown content type: {content_block['type']}")
    return converted_content

def _convert_toolresult_content_to_nova(content) -> list:
    if isinstance(content, str):
        return [{"text":content}]
    elif isinstance(content, list):
        results = []
        for content_block in content:
            if content_block["type"] == "image":
                results.append({"image":{"format":content_block["source"]["media_type"].split('/')[1],"source":{"bytes":content_block["source"]["data"]}}})
            elif content_block["type"] == "text":
                results.append({"text":content_block["text"]}) 
        return results


def _convert_messages_to_nova(messages:list):
    new_messages = []
    for message in messages:
        contents = []
        for content_block in message["content"]:
            if content_block["type"] == "image":
                contents.append({
                    "image": {
                        "format": content_block["source"]["media_type"].split('/')[1],
                        "source": {"bytes":content_block["source"]["data"]}
                    }
                })
            elif content_block["type"] == "text":
                contents.append({
                    "text": content_block["text"]
                })
            elif content_block["type"] == "tool_use":
                contents.append({
                    "toolUse":{
                        "toolUseId": content_block["id"],
                        "name": content_block["name"],
                        "input": content_block["input"]
                    }
                })
            elif content_block["type"] == "tool_result":
                contents.append({"toolResult":{
                    "toolUseId": content_block["tool_use_id"],
                    "content":  _convert_toolresult_content_to_nova(content_block["content"]) 
                }})
        new_messages.append({
            "role": message["role"],
            "content": contents
        })
    return new_messages

class BedrockNova:
    def __init__(self, model_id=NOVA_PRO_MODEL_ID):
        self.model_id = model_id
        profile_name = os.environ.get("AWS_PROFILE", None)
        if profile_name is not None:
            session = boto3.session.Session(profile_name=profile_name,region_name=DEFAULT_REGION)
        else:
            session = boto3.session.Session(region_name=DEFAULT_REGION)
        self.bedrock_runtime = session.client(service_name = 'bedrock-runtime')

    
    def invoke(self, max_tokens:int,messages:list,system:BetaTextBlockParam,tools:list):
        converted_messages = _convert_messages_to_nova(messages)
        inf_params = {"maxTokens": max_tokens, "topP": 0.95, "temperature": 0.1}
        native_request = {
            "schemaVersion": "messages-v1",
            "messages": converted_messages,
            "system":[{"text":system['text']}],
            "inferenceConfig": inf_params,
            "toolConfig": {"tools":tools}
        }
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(native_request)
        )

        # model_response = self.bedrock_runtime.converse(
        #                     modelId=self.model_id,
        #                     messages=converted_messages,
        #                     inferenceConfig=inf_params,
        #                     toolConfig={"tools":tools},
        #                     system=system
        #                 )
        
        return _convert_response_to_anthropic(response)