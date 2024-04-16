from requests import Session
from dotenv import load_dotenv
import os
load_dotenv()

api_url = 'https://mni.wikipedia.org/w/api.php'
source_file_name = 'Gadget-mayek-bot.js'
source_text = open(source_file_name, 'r').read()
target_page = 'User:Nokib Sarkar/Gadget-mayek-bot.js'
params = {
    'action': 'query',
    'format': 'json',
    'meta': 'tokens',
    'type': 'csrf'
}
sess = Session()
sess.headers.update({
    'Authorization': f'Bearer {os.getenv("NOKIB_SARKAR_ACCESS_TOKEN")}',
})
csrf_esp = sess.get(api_url, params=params).json()
if 'error' in csrf_esp:
    print(csrf_esp)
    exit()

csrf_token = csrf_esp['query']['tokens']['csrftoken']
print("CSRF Token Fetched", csrf_token)
print("Uploading", source_file_name, "to", target_page)
params = {
    'action': 'edit',
    'format': 'json',
    'title': target_page,
    'text': source_text,
    'token': csrf_token
}
edit_response = sess.post(api_url, data=params).json()
if 'error' in edit_response:
    print(edit_response)
    exit()
print("Uploaded Successfully")
