from _global import *
import json, re
from datetime import datetime, timedelta
from t import MeiteiToBengali, MNI_WIKILINK_PREFIX
COMMENT_FORMAT = '{timestamp} অসিদা কম্মেন্ত:  {comment}কা লোয়ননা {user} অসিনা Mteiদগি Bengদা ময়েক হন্দোকপা:  {article}([[{article}|রিভিসন]])\n{timestamp} ꯑꯁꯤꯗ ꯀꯝꯃꯦꯟꯠ:  {comment}ꯀ ꯂꯣꯏꯅꯅ {user} ꯑꯁꯤꯅ Mteiꯗꯒꯤ Bengꯗ ꯃꯌꯦꯛ ꯍꯟꯗꯣꯛꯄ:  {article}([[{article}|ꯔꯤꯚꯤꯁꯟ]])'
CONFIGURATION_PAGE = 'User:Nokib Sarkar/mayek.json'
EMERGENCY_SHUTDOWN_PAGE = 'User:Mayek_Bot/emergency_turnoff'
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
# MNI_WIKILINK_PREFIX = 'User:Mayek Bot/Test/2/'
UNREVIEWED_TEMPLATE = 'Transliterated'
UNREVIEWED_TEMPLATE_REGEX = re.compile('\{\{\s*?' + UNREVIEWED_TEMPLATE + '[^}]*?\}\}\s*', re.IGNORECASE | re.UNICODE)
UNREVIEWED_TEMPLATE_FORMAT = '{{{{Transliterated|{bengali}|{mni}|article={mni}|oldid={oldid}|reviewed=}}}}\n'
def add_new_transliterated_template(text: str, mni: str, bengali: str, oldid : int) -> str:
    replacable  =   UNREVIEWED_TEMPLATE_FORMAT.format(
        mni     =   mni,
        bengali =   f'{MNI_WIKILINK_PREFIX}{bengali}',
        oldid   =   oldid
    )
    replaced, count = UNREVIEWED_TEMPLATE_REGEX.subn(replacable, text)
    if count == 0:
        return f'{replacable}\n{text}'
    return replaced


def get_settings() -> dict:
    page_names = '|'.join([
        CONFIGURATION_PAGE,
        # EMERGENCY_SHUTDOWN_PAGE # Not needed at the moment
    ])
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": page_names,
        "rvslots": "main",
        "rvprop": "content",
        "formatversion": "2",
        "rvlimit": "1"
    }
    response    =   next(query_with_continue('mni', params))
    page        =   response['query']['pages'][0]
    content     =   page['revisions'][0]['slots']['main']['content']
    return json.loads(content)
def add_beng_template(title, beng_title, template_name="Transliterated"):
    params = {
        "action": "query",
        "format": "json",
        "prop": "templates",
        "titles": title,
        "formatversion": "2",
        "tllimit": "1",
        "tltemplates": f"Template:{template_name}"
    }
    res = BaseServer.get(lang='mni', params=params)
    if 'pages' not in res['query']:
        return False
    page = res['query']['pages'][0]
    if 'templates' in page:
        return False
    text = f'{{{{{template_name}|{beng_title}|{title}|notice=no}}}}\n'
    edit_page('mni', 
              title, 
              summary=f'Adding Bengali transliteration template for {title}',
              prependtext=text,
              recreate=False
              )
def get_recentchanges():
    settings = get_settings()
    waiting_period = settings.get('waitingPeriodInMinutes', 60)
    time_of_last_run = 0
    try:
        with open("mni_transliteration_last_run.txt", "r") as f:
            time_of_last_run = f.read()
            time_of_last_run = datetime.fromisoformat(time_of_last_run).strftime(TIMESTAMP_FORMAT)
    except:
        pass
    time_of_current_run = (datetime.now() - timedelta(hours=waiting_period)).strftime(TIMESTAMP_FORMAT)
    print(time_of_last_run, time_of_current_run)
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "generator": "recentchanges",
        "formatversion": "2",
        "rvprop": "ids|timestamp|flags|comment|user|content",
        "rvslots": "main",
        # "grcdir": "newer",
        "grcexcludeuser": "CampWiz Bot",
        "grcshow": "!bot",
        "grctype": "edit|new",
        "grctoponly": 1,
        "grclimit": "max",
        "grcfromtimestamp": time_of_current_run,
        "grctotimestamp": time_of_last_run,
        "grcnamespace" : "0" # Main namespace
    }
    try:
        response_iterator = query_with_continue('mni', params)
        for response in response_iterator:
            for page in response['query']['pages']:
                settings = get_settings() # Reload settings
                if settings.get('enabled', False) is False:
                    return
                page_title = page['title']
                page_id = page['pageid']
                page_revisions = page['revisions']
                if len(page_revisions) == 0:
                    continue
                revision = page_revisions[0]
                revision_id = revision['revid']
                revision_timestamp = revision['timestamp']
                revision_comment = revision['comment']
                revision_user = revision['user']
                revision_content = revision['slots']['main']['content']


                # Transliteration
                transliterated_page_title = MeiteiToBengali.transliterate(page_title)
                transliterated_revision_comment = MeiteiToBengali.transliterate(revision_comment)
                transliterated_revision_content = MeiteiToBengali.transliterate(revision_content)
                transliterated_revision_content = add_new_transliterated_template(transliterated_revision_content, page_title, transliterated_page_title, revision_id)
                # Comment
                comment = COMMENT_FORMAT.format(
                    article=page_title,
                    user=revision_user,
                    timestamp=revision_timestamp,
                    comment=revision_comment + " (Transliterated: " + transliterated_revision_comment + ")"
                )
                
                edit_page('mni', f"{MNI_WIKILINK_PREFIX}{transliterated_page_title}", text=transliterated_revision_content, summary=comment, recreate=False)
                add_beng_template(page_title, f"{MNI_WIKILINK_PREFIX}{transliterated_page_title}")
                delay = settings.get('editIntervalInSeconds', 10)
                print(f"Waiting for {delay} seconds")
                time.sleep(delay)
    except Exception as e:
        print(e)
    finally:
        with open("mni_transliteration_last_run.txt", "w") as f:
            f.write(datetime.now().isoformat())
        pass

if __name__ == "__main__":
    
    get_recentchanges()
    



