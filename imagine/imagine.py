import json
import uuid
from urllib import request

from imagine.scanlist import nsfw_keywords

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())


def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = request.Request("http://127.0.0.1:8188/prompt", data=data)
    response = json.loads(request.urlopen(req).read())
    """
    prompt_id = response['prompt_id']
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data
    print("generated!")"""

def check_image (filename, prompt = None):
    for i in nsfw_keywords:
        if ","+i in prompt or " "+i in prompt or i in prompt:
            print(i)
            return False
    return True

def test():
    print(check_image("C:\\Library\\workspaces\\stable-diffusion\\webui\\ComfyUI\\output\\ComfyUI_00010_.png"))