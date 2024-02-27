from _global import *
import json
from datetime import datetime, timedelta
from t import MeiteiToBengali
COMMENT_FORMAT = '{timestamp} অসিদা কম্মেন্ত:  {comment}কা লোয়ননা {user} অসিনা Mteiদগি Bengদা ময়েক হন্দোকপা:  {article}([[User:CampWiz Bot/Test/{article}|রিভিসন]])\n{timestamp} ꯑꯁꯤꯗ ꯀꯝꯃꯦꯟꯠ:  {comment}ꯀ ꯂꯣꯏꯅꯅ {user} ꯑꯁꯤꯅ Mteiꯗꯒꯤ Bengꯗ ꯃꯌꯦꯛ ꯍꯟꯗꯣꯛꯄ:  {article}([[User:CampWiz Bot/Test/{article}|ꯔꯤꯚꯤꯁꯟ]])'
CONFIGURATION_PAGE = 'User:Nokib Sarkar/mayek.json'
EMERGENCY_SHUTDOWN_PAGE = 'User:Mayek_Bot/emergency_turnoff'
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

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
    response = next(query_with_continue('mni', params))
    page = response['query']['pages'][0]
    content = page['revisions'][0]['slots']['main']['content']
    return json.loads(content)
def get_recentchanges():
    settings = get_settings()
    waiting_period = settings.get('waitingPeriodInMinutes', 60)
    time_of_last_run = 0
    try:
        with open("mni_transliteration_last_run.txt", "r") as f:
            time_of_last_run = int(f.read())
            time_of_last_run = datetime.fromtimestamp(time_of_last_run).strftime(TIMESTAMP_FORMAT)
    except:
        pass
    time_of_current_run = (datetime.now() - timedelta(minutes=waiting_period)).strftime(TIMESTAMP_FORMAT)
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "generator": "recentchanges",
        "formatversion": "2",
        "rvprop": "ids|timestamp|flags|comment|user|content",
        "rvslots": "main",
        "grcdir": "newer",
        "grcexcludeuser": "CampWiz Bot",
        "grcshow": "!bot",
        "grctype": "edit|new",
        "grctoponly": 1,
        "grclimit": "max",
        "grcfromtimestamp": time_of_last_run,
        "grctotimestamp": time_of_current_run,
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
                
                # Commen`t
                comment = COMMENT_FORMAT.format(
                    article=page_title,
                    user=revision_user,
                    timestamp=revision_timestamp,
                    comment=revision_comment + "(Transliterated: " + transliterated_revision_comment + ")"
                )
                
                edit_page('mni', f"User:Mayek Bot/Test/Bangla/{transliterated_page_title}", transliterated_revision_content, comment, recreate=False)
                delay = settings.get('editIntervalInSeconds', 10)
                print(f"Waiting for {delay} seconds")
                time.sleep(delay)
    except Exception as e:
        print(e)
    finally:
        with open("mni_transliteration_last_run.txt", "w") as f:
            f.write(str(int(datetime.now().timestamp())))
        pass
if __name__ == "__main__":
    get_recentchanges()
    print(get_settings())
    pass
    



