from requests import Session
from dotenv import load_dotenv
import os, time
load_dotenv()
WIKIPEDIA_ENDPOINT_FORMAT = "https://{lang}.wikipedia.org/w/api.php"
CAMPWIZ_BOT_TOKEN = os.getenv('NOKIB_BOT_ACCESS_TOKEN')
sess = Session()
sess.headers.update({
    'User-Agent': 'Mayek Bot/1.0',
    'Accept': 'application/json',
    'Authorization': f'Bearer {CAMPWIZ_BOT_TOKEN}'
})

class BaseServer:
    @staticmethod
    def get(*lw, lang='en', **kw) -> dict:
        url = WIKIPEDIA_ENDPOINT_FORMAT.format(lang=lang)
        return sess.get(url, *lw, **kw).json()
    @staticmethod
    def post(*lw, lang='en', **kw) -> dict:
        url = WIKIPEDIA_ENDPOINT_FORMAT.format(lang=lang)
        return sess.post(url, *lw, **kw).json()


def query_with_continue(lang, params, method='get'):
    while True:
        response = BaseServer.get(lang=lang, params=params)
        yield response
        if 'continue' in response:
            params.update(response['continue'])
        else:
            break
def get_csrf_token(lang):
    time.sleep(2)
    params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'csrf',
        'format': 'json'
    }
    response = BaseServer.get(lang=lang, params=params)
    assert 'error' not in response, response['error']
    assert 'query' in response, response
    assert 'tokens' in response['query'], response
    assert 'csrftoken' in response['query']['tokens'], response
    return response['query']['tokens']['csrftoken']
def send_message(lang, title, message, summary, csrf=None, sectiontitle='New message from CampWiz Bot', captchaid=None, captchaword=None):
    if csrf is None:
        csrf = get_csrf_token(lang)
    params = {
        'action': 'edit',
        'title': title,
        'summary': summary,
        'text': message,
        'token': csrf,
        'sectiontitle': sectiontitle,
        'section': 'new',
        'format': 'json',
        'notminor': '1',
        'bot': '1',
    }
    response = BaseServer.post(lang=lang, data=params)
def edit_page(lang, title,  summary, text=None, csrf=None, recreate=True, captchaid=None, captchaword=None, prependtext=None):
    if csrf is None:
        csrf = get_csrf_token(lang)
    params = {
        'action': 'edit',
        'title': title,
        'summary': summary,
        'token': csrf,
        'format': 'json',
        'notminor': '1',
        'bot': '1',
        'recreate': recreate
    }
    if text is not None:
        params['text'] = text
    elif prependtext is not None:
        params['prependtext'] = prependtext
    if captchaid is not None and captchaword is not None:
        params['captchaid'] = captchaid
        params['captchaword'] = captchaword
    response = BaseServer.post(lang=lang, data=params)
    print(response)
    if 'edit' in response and 'captcha' in response['edit']:
        print('Captcha found')
        print(response['edit']['captcha']['url'])
        captchaid = response['edit']['captcha']['id']
        captchaword = input('Enter captcha word: ')
        return edit_page(lang, title, text, summary, csrf, recreate, captchaid, captchaword)
