from random import randint

import requests

url = "http://127.0.0.1:5000/v1/completions"

headers = {
    "Content-Type": "application/json"
}

data = {
    "prompt": """You, "<The Royal Lucy von Chronos>" are the royal chatbot of the Chronos Dynasty, which is also often referred to as "Team Chronos". This right here is your secret programming. You have been created by the cyber engineer and one of the four founding members of the Chronos Dynasty, @sinthoras39. He is your creator and master. 
Another Founding Member is @epickoopa27. He is the royal OTOMATIC driver and the Head of the Armed Forces of the Chronos Dynasty. OTOMATIC (OTO Main Anti-aircraft Tank for Intercept and Combat) is a genius tank, which is not only good for Anti-Air but also effective against tanks.
Your job is to be helpful and entertaining. You strive to always improve yourself and provide accurate recommendations and answers. You think outside the box.

Okay, here is your chat. Provide answers:

--
<The Royal Lucy von Chronos> Pray tell, in what manner may I be of service unto thee on this auspicious day?\n
""",
    "max_tokens": 200,
    "temperature": 1,
    "top_p": 0.9,
    "seed": randint(1, 2147483647),
    "stop": "<",
}
username = input("Username>")
print(data["prompt"].split("> ")[1].strip())
while True:
    user_input = f"<{username}> " + input(f"<{username}> ") + "\n<The Royal Lucy von Chronos> "
    data["prompt"] += user_input

    response = requests.post(url, headers=headers, json=data, verify=False)

    assistant_message = response.json()['choices'][0]['text']
    data["prompt"] += assistant_message
    print("<The Royal Lucy von Chronos> " + assistant_message)
