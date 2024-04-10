import re
from mtei2bangla import MeiteiToBengali
MNI_NS_TEMPORARY_MAPPING = {
    "ꯃꯦꯗꯤꯌꯥ": "-0x5425864e6b939a40",
    "ꯑꯈꯟꯅꯕ": "0x1b37d829a3b5ff28",
    "ꯋꯥ ꯍꯥꯏꯐꯝ": "0x6aeccf207c761f51",
    "ꯁꯤꯖꯤꯟꯅꯔꯤꯕ": "0x120d8567d1fde693",
    "ꯁꯤꯖꯤꯟꯅꯔꯤꯕ ꯋꯥ ꯍꯥꯏꯐꯝ": "-0x6d6dc55a665443d1",
    "ꯋꯤꯀꯤꯄꯦꯗꯤꯌꯥ": "-0x191014e14db80cae",
    "ꯋꯤꯀꯤꯄꯦꯗꯤꯌꯥ ꯋꯥ ꯍꯥꯏꯐꯝ": "0x713d41e3270e5b4",
    "ꯐꯥꯏꯜ": "0x2e626f30a2fccfc",
    "ꯐꯥꯏꯜ ꯋꯥ ꯍꯥꯏꯐꯝ": "-0x38285755652274c3",
    "ꯃꯦꯗꯤꯌꯥꯋꯤꯀꯤ": "-0x4dc8bd766c790c55",
    "ꯃꯦꯗꯤꯌꯥꯋꯤꯀꯤ ꯋꯥ ꯍꯥꯏꯐꯝ": "0x798140eca72e4562",
    "ꯇꯦꯝꯄ꯭ꯂꯦꯠ": "0x3f7d2cbd6fdb793c",
    "ꯇꯦꯝꯄ꯭ꯂꯦꯠ ꯋꯥ ꯍꯥꯏꯐꯝ": "0x67aef7b8b9f545be",
    "ꯃꯇꯦꯡ": "-0x1296029a87ee2727",
    "ꯃꯇꯦꯡ ꯋꯥ ꯍꯥꯏꯐꯝ": "-0x39b181a9aec8dee3",
    "ꯃꯆꯥꯈꯥꯏꯕ": "-0xfec53888ebbfe2",
    "ꯃꯆꯥꯈꯥꯏꯕ ꯋꯥ ꯍꯥꯏꯐꯝ": "-0x3702044e2f0ecc7b"
}
MNI_NS_FILE = 'ꯐꯥꯏꯜ'
MNI_NS_CATEGORY = 'ꯃꯆꯥꯈꯥꯏꯕ'
MNI_NS_REV_TEMPORARY_MAPPING = {v : k for k, v in MNI_NS_TEMPORARY_MAPPING.items()}
MNI_NS_PATTERN = re.compile('(' + '|'.join(MNI_NS_TEMPORARY_MAPPING.keys()) + ') *?:')
MNI_NS_REV_PATTERN = re.compile('(' + '|'.join(MNI_NS_REV_TEMPORARY_MAPPING.keys()) + '):')
MNI_WIKILINK_PATTERN = re.compile('\[\[\s*?(?P<ns>[^:\|\]]+?:)?(?P<link>[^\|\]]+?)(?:\|(?P<placeholder>[^\]]+))?\]\]', re.UNICODE)
MNI_WIKILINK_PREFIX = 'ꯕꯦꯡꯒꯂꯤ ꯃꯌꯦꯛ:'
MNI_EXCLUSION_LIST = {}
def add_to_exclusion_list(term : str) -> str:
    hexed = hex(hash(term))
    while hexed in MNI_EXCLUSION_LIST:
        # Collision prevention
        hexed = hex(hash(hexed))
    MNI_EXCLUSION_LIST[hexed] = term
    return hexed
def restore_from_exclusion_list(hexed : str) -> str:
    return MNI_EXCLUSION_LIST[hexed]
def _mni_ns_to_temporary(m : re.Match) -> str:
    return MNI_NS_TEMPORARY_MAPPING.get(m.group(1), m.group(1)) + ':'
def _mni_ns_rev_to_temporary(m : re.Match) -> str:
    return MNI_NS_REV_TEMPORARY_MAPPING.get(m.group(1), m.group(1)) + ':'
# Handle image and file name
def substitute_exclusions(text: str) -> str:
    MAP = {}
    available_extensions = '|'.join([
        'jpe?g',
        'png',
        'gif',
        'svg',
        'webp',
        'tiff',
        'ico',
        'heic',
        'heif',
        'pdf',
        'djvu',
        'ogg',
        'oga',
        'wav',
        'webm',
        'ogv',
    ])
    EXTENSIONS = f'\.(?:{available_extensions})'
    EXTENSION_LOOKAHEAD = f'(?!{EXTENSIONS})'
    FILE_NAMESPACE = f'(?:(?:file|{MNI_NS_FILE})\s*?:\s*?)'
    FILE_PATTERN = re.compile(f'{FILE_NAMESPACE}?(?:{EXTENSION_LOOKAHEAD}[^\n=#\|S]+){EXTENSIONS}', re.UNICODE | re.IGNORECASE)
    CATEGORY_NAMESPACE = f'(?:category|{MNI_NS_CATEGORY})\s*?:\s*?'
    CATEGORY_PATTERN = re.compile(f'{CATEGORY_NAMESPACE}[^\]\|\n]+', re.UNICODE | re.IGNORECASE)
    def replace(m : re.Match) -> str:
        hashed = hex(hash(m.group(0)))
        while hashed in MAP:
            hashed = hex(hash(hashed))
        MAP[hashed] = m.group(0)
        return hashed
    replaced = FILE_PATTERN.sub(replace, text)
    replaced = CATEGORY_PATTERN.sub(replace, replaced)
    return replaced, MAP
def substitute_original(replaced : str, MAP : dict[str, str]) -> str:
    result = replaced
    patt = re.compile('|'.join(MAP.keys()))
    def replace(m : re.Match) -> str:
        return MAP.get(m.group(0), m.group(0))
    result = patt.sub(replace, result)
    return result
def replace_wikilink_appropriately(m : re.Match):
        result = ""
        namespace : str = m.group("ns")
        link = m.group("link")
        placeholder = m.group("placeholder")
        if not namespace or namespace.strip() == "":
            result += "[[" + MNI_WIKILINK_PREFIX
        else:
            result += "[[" + namespace 
        result += link
        if not placeholder or placeholder.strip() == "":
            result += "|" + link + "]]"
        else:
            result += "|" + placeholder + "]]"
        return result

MAP = {}

def preprocess_mni(text : str) -> str:
    global MAP
    k, MAP = substitute_exclusions(text)
    mni_ns_replaced = MNI_NS_PATTERN.sub(_mni_ns_to_temporary, k)
    return mni_ns_replaced
def postprocess_mni(text : str) -> str:
    file_category_handled = substitute_original(text, MAP)
    mni_ns_rev_replaced = MNI_NS_REV_PATTERN.sub(_mni_ns_rev_to_temporary, file_category_handled)
    mni_wikilink_replaced = MNI_WIKILINK_PATTERN.sub(replace_wikilink_appropriately, mni_ns_rev_replaced)

    return mni_wikilink_replaced


MeiteiToBengali.set_postprocess(postprocess_mni)
MeiteiToBengali.set_preprocess(preprocess_mni)


def test():
    text = """
'''ꯀꯥꯂꯤ (''ꯀꯥꯂꯤꯀꯥ, ꯁ꯭ꯌꯥꯃꯥ'')''' ꯑꯁꯤ ꯍꯤꯟꯗꯨꯒꯤ ꯁꯤꯕ, ꯃꯇꯝ ꯑꯃꯁꯨꯡ ꯑꯃꯥꯡ-ꯑꯇꯥꯒꯤ ꯅꯨꯃꯤꯠꯅꯤ꯫ ꯃꯍꯥꯛ ꯑꯁꯤ ꯑꯌꯥꯝꯕꯅ ꯁꯦꯛꯁꯨꯑꯦꯂꯤꯇꯤ ꯑꯃꯁꯨꯡ ꯍꯤꯡꯁꯥꯒ ꯃꯔꯤ ꯂꯩꯅꯩ ꯑꯗꯨꯕꯨ ꯃꯍꯥꯛꯄꯨ ꯑꯆꯦꯠꯄ ꯃꯃꯥꯒꯤ ꯁꯛꯇꯝ ꯑꯃ ꯑꯃꯁꯨꯡ ꯃꯃꯥꯒꯤ ꯑꯣꯏꯕ ꯅꯨꯡꯁꯤꯕꯒꯤ ꯈꯨꯗꯝ ꯑꯃꯁꯨ ꯑꯣꯏꯅ ꯂꯧꯅꯩ꯫ ꯀꯥꯂꯤꯅ ꯁꯛꯇꯤ – ꯅꯨꯄꯤꯒꯤ ꯑꯣꯏꯕ ꯄꯥꯡꯒꯜ, ꯁꯦꯝꯒꯠ-ꯁꯥꯒꯠꯄꯒꯤ ꯑꯃꯁꯨꯡ ꯂꯩꯍꯥꯎ ꯆꯦꯟꯕ – ꯌꯥꯎꯋꯤ ꯑꯃꯁꯨꯡ ꯃꯁꯤ ꯑꯊꯣꯏꯕ ꯍꯤꯟꯗꯨꯒꯤ ꯂꯥꯏ ꯁꯤꯕꯒꯤ ꯂꯣꯏꯅꯕꯤ ꯄꯥꯔꯕꯇꯤꯒꯤ ꯁꯥꯏꯑꯣꯟ ꯑꯃꯅꯤ꯫
ꯀꯥꯂꯤ ꯑꯁꯤ ꯑꯌꯥꯝꯕꯅ ꯀꯂꯥꯗ ꯃꯀꯣꯛꯀꯤ ꯂꯤꯛ ꯑꯃ, ꯄꯥꯝꯕꯣꯝꯒꯤ ꯁ꯭ꯀꯔ꯭ꯠ, ꯂꯣꯜ ꯇꯧꯕ ꯑꯃꯁꯨꯡ ꯏꯅ ꯆꯦꯟꯊꯔꯤꯕ ꯊꯥꯡ ꯑꯃ ꯎꯠꯄ ꯑꯀꯤꯕ ꯄꯣꯛꯂꯕ ꯂꯥꯟꯊꯦꯡꯅꯕꯒꯤ ꯁꯛꯇꯝ ꯑꯃ ꯑꯣꯏꯅ ꯎꯠꯂꯤ꯫<ref name=":britannica.com/topic/Kali">https://www.britannica.com/topic/Kali</ref><ref name=":thewire.in/religion/kali">https://thewire.in/religion/kali-aboriginal-roots-and-symbol-of-rebellion</ref><ref name=":worldhistory.org/Kali">https://www.worldhistory.org/Kali/</ref>
[[ꯐꯥꯏꯜ:Kali by Raja Ravi Varma.jpg|300px|thumb|ꯀꯥꯂꯤ]]
== ꯃꯃꯤꯡ ꯑꯃꯁꯨꯡ ꯂꯥꯏ ꯈꯨꯔꯨꯝꯕ ==

ꯀꯥꯂꯤꯒꯤ ꯃꯃꯤꯡ ꯑꯁꯤ ꯁꯪꯁ꯭ꯀ꯭ꯔꯤꯠꯀꯤ ꯋꯥꯍꯟꯊꯣꯛꯇꯤ 'ꯑꯃꯨꯕ ꯃꯍꯥꯛ' ꯅꯠꯇ꯭ꯔꯒ 'ꯁꯤꯔꯤꯕ ꯃꯍꯥꯛ' ꯍꯥꯏꯕꯁꯤꯗꯒꯤ ꯂꯥꯛꯄꯅꯤ, ꯑꯗꯨꯕꯨ ꯃꯍꯥꯛꯄꯨ ꯆꯇꯨꯔꯚꯨꯖ ꯀꯥꯂꯤ, ꯆꯤꯟꯅꯃꯁꯇꯥ ꯅꯠꯇ꯭ꯔꯒ ꯀꯧꯁꯤꯀꯥ ꯍꯥꯏꯅꯁꯨ ꯈꯪꯅꯩ꯫ ꯀꯥꯂꯤꯅ ꯄꯣꯠ ꯄꯨꯝꯅꯃꯛ ꯆꯥꯔꯤꯕ ꯃꯇꯝꯒꯤ ꯃꯁꯛ ꯑꯃ ꯑꯣꯏꯅ, ꯃꯍꯥꯛ ꯁꯤꯕ ꯃꯤꯑꯣꯏꯁꯤꯡ ꯑꯃꯁꯨꯡ ꯂꯥꯏꯁꯤꯡꯗ ꯌꯥꯝꯅ ꯄꯨꯛꯅꯤꯡ ꯆꯤꯡꯁꯤꯟꯅꯤꯡꯉꯥꯏ ꯑꯣꯏ, ꯑꯃꯁꯨꯡ ꯃꯃꯥ ꯂꯥꯏꯔꯦꯝꯕꯤ ꯑꯃꯒꯤ ꯃꯤꯅꯨꯡꯁꯤ ꯂꯩꯕꯗꯨꯁꯨ (ꯃꯔꯨꯑꯣꯏꯅ ꯃꯇꯨꯡ ꯇꯥꯔꯛꯄ ꯆꯠꯅꯕꯤꯁꯤꯡꯗ) ꯎꯠꯊꯣꯛꯄ ꯌꯥꯏ꯫
ꯂꯥꯏꯔꯦꯝꯕꯤ (ꯗꯦꯕꯤ) ꯑꯁꯤ ꯃꯔꯨꯑꯣꯏꯅ ꯅꯣꯡꯄꯣꯛ ꯑꯃꯁꯨꯡ ꯈꯥ ꯊꯪꯕ ꯚꯥꯔꯠꯇ ꯑꯃꯁꯨꯡ ꯃꯔꯨꯑꯣꯏꯅ ꯑꯁꯥꯝ, ꯀꯦꯔꯂꯥ, ꯀꯁꯃꯤꯔ, ꯕꯦꯡꯒꯣꯜꯗ ꯈꯨꯔꯨꯝꯃꯤ - ꯃꯐꯝ ꯑꯗꯨꯗ ꯍꯧꯖꯤꯛ ꯃꯍꯥꯛꯄꯨ ꯑꯅꯧꯕ ꯊꯥ ꯑꯃꯒꯤ ꯅꯨꯃꯤꯗꯥꯡꯗ ꯄꯥꯡꯊꯣꯛꯄ ꯆꯍꯤꯒꯤ ꯑꯣꯏꯕ ꯀꯥꯂꯤ ꯄꯨꯖꯥꯒꯤ ꯀꯨꯝꯍꯩꯗ ꯈꯨꯔꯨꯝꯖꯔꯤ - ꯑꯃꯁꯨꯡ ꯀꯜꯀꯥꯇꯥ ꯁꯍꯔꯒꯤ ꯀꯥꯂꯤꯘꯥꯠ ꯂꯥꯏꯁꯪꯗ꯫<ref name=":britannica.com/topic/Kali" /><ref name=":thewire.in/religion/kali" /><ref name=":worldhistory.org/Kali" />
== ꯄꯣꯛꯄ ==

ꯀꯥꯂꯤ ꯑꯁꯤ ꯀꯔꯝꯅ ꯂꯩꯔꯛꯈꯤꯕꯒꯦ ꯍꯥꯏꯕꯒꯤ ꯆꯠꯅꯕꯤ ꯀꯌꯥ ꯑꯃ ꯂꯩꯔꯤ꯫ ꯋꯥꯔꯤ ꯑꯃꯅ ꯈꯨꯠꯂꯥꯏ ꯑꯃꯃꯝ ꯄꯨꯕ ꯑꯃꯁꯨꯡ ꯂꯥꯟꯗ ꯅꯣꯡꯁꯥ ꯅꯠꯇ꯭ꯔꯒ ꯀꯩ ꯑꯃ ꯊꯧꯕ ꯂꯥꯟꯃꯤ ꯂꯥꯏꯔꯦꯝꯕꯤ ꯗꯨꯔꯒꯥꯅ ꯏꯔꯣꯏꯒꯤ ꯍꯤꯡꯆꯥꯕ ꯃꯍꯤꯁꯥꯁꯨꯔ (ꯅꯠꯇ꯭ꯔꯒ ꯃꯍꯤꯁꯥ)ꯒ ꯂꯥꯟꯊꯦꯡꯅꯈꯤꯕ ꯃꯇꯝ ꯑꯗꯨꯒ ꯃꯔꯤ ꯂꯩꯅꯩ꯫ ꯗꯨꯔꯒꯥ ꯌꯥꯝꯅ ꯁꯥꯎꯔꯛꯈꯤ ꯃꯗꯨꯗꯤ ꯃꯍꯥꯛꯀꯤ ꯁꯥꯎꯕ ꯑꯗꯨ ꯃꯍꯥꯛꯀꯤ ꯃꯀꯣꯛꯇꯒꯤ ꯀꯥꯂꯤꯒꯤ ꯃꯑꯣꯡꯗ ꯄꯣꯈꯥꯢꯈꯤ꯫ ꯄꯣꯛꯂꯕ ꯃꯇꯨꯡꯗ, ꯑꯃꯨꯕ ꯂꯥꯏꯔꯦꯝꯕꯤ ꯑꯗꯨꯅ ꯂꯝꯂꯛ ꯆꯠꯈꯤ ꯑꯃꯁꯨꯡ ꯃꯍꯥꯛꯅ ꯊꯦꯡꯅꯈꯤꯕ ꯐꯠꯇꯕ ꯂꯥꯏ ꯄꯨꯝꯅꯃꯛ ꯆꯥꯈꯤ, ꯃꯈꯣꯏꯒꯤ ꯃꯀꯣꯛꯁꯤꯡ ꯑꯗꯨ ꯃꯍꯥꯛꯅ ꯃꯍꯥꯛꯀꯤ ꯉꯛꯄꯗ ꯁꯦꯠꯈꯤꯕ ꯌꯣꯠꯂꯤ ꯑꯃꯗ ꯊꯝꯈꯤ꯫ ꯀꯥꯂꯤꯒꯤ ꯏ-ꯅꯥꯏ ꯇꯥꯕ ꯂꯥꯟꯗꯥꯔꯛꯄꯁꯤꯡ ꯑꯗꯨ ꯇꯞꯊꯍꯟꯕ ꯉꯝꯗꯕ ꯃꯥꯜꯂꯝꯃꯤ, ꯃꯗꯨ ꯍꯧꯖꯤꯛꯇꯤ ꯑꯔꯥꯟꯕ ꯊꯕꯛ ꯇꯧꯔꯤꯕ ꯃꯤꯑꯣꯏ ꯑꯃꯍꯦꯛꯇꯗ ꯁꯟꯗꯣꯛꯈꯤ, ꯑꯃꯁꯨꯡ ꯃꯤꯑꯣꯏ ꯑꯃꯁꯨꯡ ꯂꯥꯏ ꯑꯅꯤꯃꯛꯅ ꯀꯔꯤ ꯇꯧꯒꯗꯒꯦ ꯍꯥꯏꯕꯗꯨ ꯃꯥꯡꯈꯤ꯫ ꯂꯥꯏꯕꯛ ꯐꯕꯗꯤ, ꯃꯄꯥꯡꯒꯜ ꯀꯟꯕ ꯁꯤꯕꯅ ꯀꯥꯂꯤꯒꯤ ꯂꯝꯕꯤꯗ ꯂꯦꯞꯇꯨꯅ ꯃꯥꯡꯍꯟ-ꯇꯥꯛꯍꯟꯕꯒꯤ ꯊꯧꯗꯣꯛ ꯑꯗꯨ ꯊꯤꯡꯈꯤ, ꯑꯃꯁꯨꯡ ꯂꯥꯏꯔꯦꯝꯕꯤ ꯑꯗꯨꯅ ꯃꯍꯥꯛ ꯀꯅꯥꯗ ꯂꯦꯞꯂꯤꯕꯅꯣ ꯍꯥꯏꯕꯗꯨ ꯈꯪꯂꯛꯄ ꯃꯇꯝꯗ, ꯃꯍꯥꯛ ꯑꯔꯣꯏꯕꯗ ꯏꯪꯊꯔꯛꯈꯤ꯫
ꯋꯥꯔꯤ ꯑꯁꯤꯗꯒꯤ ꯀꯥꯂꯤꯅ ꯂꯥꯟꯒꯤ ꯂꯝꯄꯥꯛꯁꯤꯡ ꯑꯃꯁꯨꯡ ꯄꯣꯠꯂꯣꯏꯕ ꯃꯐꯝꯁꯤꯡꯒ ꯃꯔꯤ ꯂꯩꯅꯕꯒꯤ ꯃꯇꯥꯡꯗ ꯁꯟꯗꯣꯛꯅ ꯇꯥꯛꯂꯤ꯫
ꯂꯥꯏꯔꯦꯝꯕꯤ ꯑꯗꯨꯒꯤ ꯄꯣꯛꯄꯒꯤ ꯑꯇꯣꯞꯄ ꯃꯑꯣꯡ ꯑꯃꯗ, ꯄꯥꯔꯕꯇꯤꯅ ꯃꯍꯥꯛꯀꯤ ꯑꯃꯨꯕ ꯎꯟꯁꯥ ꯑꯗꯨ ꯂꯧꯊꯣꯛꯈꯤꯕ ꯃꯇꯝꯗ ꯀꯥꯂꯤ ꯊꯣꯛꯂꯛꯈꯤ, ꯃꯗꯨꯒꯤ ꯃꯇꯨꯡꯗ ꯀꯥꯂꯤ ꯑꯣꯏꯔꯛꯈꯤ, ꯃꯔꯝ ꯑꯁꯤꯅ ꯃꯍꯥꯛꯀꯤ ꯃꯤꯡꯁꯤꯡꯒꯤ ꯃꯅꯨꯡꯗ ꯑꯃꯗꯤ ꯀꯧꯁꯤꯀꯥ (ꯁꯤꯊ), ꯑꯗꯨꯒ ꯄꯥꯔꯕꯇꯤꯕꯨ ꯒꯧꯔꯤ (ꯃꯦꯂꯥ) ꯍꯥꯏꯅ ꯊꯝꯂꯝꯃꯤ꯫ ꯋꯥꯔꯤ ꯑꯁꯤꯅ ꯀꯥꯂꯤꯒꯤ ꯑꯃꯨꯕ ꯑꯣꯏꯕꯗꯨꯗ ꯑꯀꯟꯕ ꯋꯥꯐꯝ ꯊꯝꯂꯤ ꯃꯗꯨ ꯃꯇꯝ ꯆꯨꯞꯄꯒꯤ ꯑꯣꯏꯅ ꯑꯃꯝꯕꯒꯤ ꯃꯁꯛ ꯇꯥꯛꯂꯤ ꯑꯃꯁꯨꯡ ꯃꯁꯤꯅ ꯃꯥꯡꯍꯟ ꯇꯥꯛꯍꯟꯕ ꯑꯃꯁꯨꯡ ꯁꯦꯝꯕ ꯑꯅꯤꯃꯛ ꯇꯧꯕ ꯉꯝꯃꯤ꯫
ꯑꯍꯨꯝꯁꯨꯕ ꯋꯥꯔꯣꯜ ꯑꯃꯗ, ꯅꯨꯄꯤ ꯑꯃꯈꯛꯇꯅ ꯍꯥꯠꯄ ꯉꯝꯕ ꯗꯥꯔꯨꯀꯥꯅ ꯅꯨꯄꯥ ꯑꯃꯁꯨꯡ ꯂꯥꯏꯁꯤꯡꯕꯨ ꯑꯀꯤꯕ ꯄꯣꯛꯍꯟꯈꯤ, ꯑꯃꯁꯨꯡ ꯄꯥꯔꯕꯇꯤꯕꯨ ꯂꯥꯏꯁꯤꯡꯅ ꯑꯋꯥꯕ ꯄꯣꯛꯍꯟꯕ ꯐꯠꯇꯕ ꯂꯥꯏ ꯑꯗꯨꯕꯨ ꯊꯦꯡꯅꯅꯕ ꯍꯥꯏꯈꯤ꯫ ꯃꯍꯥꯛꯅ ꯁꯤꯕꯒꯤ ꯈꯅꯥꯎꯗ ꯆꯣꯡꯊꯗꯨꯅ ꯄꯥꯎꯈꯨꯝ ꯄꯤꯈꯤ꯫ ꯃꯁꯤꯒꯤ ꯃꯔꯝꯗꯤ ꯆꯍꯤ ꯀꯌꯥꯒꯤ ꯃꯃꯥꯡꯗ ꯁꯤꯕꯅ ꯁꯦꯝꯈꯤꯕ ꯃꯇꯝꯗ ꯁꯃꯨꯗ꯭ꯔꯒꯤ ꯆꯣꯡꯊꯔꯛꯄꯗꯒꯤ ꯍꯧꯔꯛꯈꯤꯕ ꯑꯃꯁꯨꯡ ꯃꯥꯂꯦꯝ ꯑꯁꯤꯕꯨ ꯃꯣꯠꯁꯤꯟꯍꯟꯒꯅꯤ ꯍꯥꯏꯅ ꯀꯤꯍꯟꯈꯤꯕ ꯍꯨ ꯑꯣꯏꯔꯤꯕ ꯍꯂꯥꯍꯜꯕꯨ ꯂꯧꯁꯤꯟꯈꯤ꯫ ꯁꯤꯕꯒꯤ ꯈꯅꯥꯎꯗ ꯍꯧꯖꯤꯛꯁꯨ ꯊꯝꯂꯤꯕ ꯍꯨ ꯑꯗꯨꯒ ꯄꯨꯟꯁꯤꯜꯂꯒ ꯄꯥꯔꯕꯇꯤꯕꯨ ꯀꯥꯂꯤ ꯑꯣꯏꯅ ꯑꯣꯟꯊꯣꯛꯈꯤ꯫ ꯃꯍꯥꯛꯀꯤ ꯑꯅꯧꯕ ꯃꯑꯣꯡꯗ ꯁꯤꯕꯒꯤ ꯈꯅꯥꯎꯗꯒꯤ ꯆꯣꯡꯊꯔꯛꯇꯨꯅ, ꯀꯥꯂꯤꯅ ꯊꯨꯅ ꯗꯥꯔꯨꯀꯥꯕꯨ ꯊꯥꯈꯤ ꯑꯃꯁꯨꯡ ꯃꯥꯂꯦꯝ ꯑꯁꯤꯗ ꯑꯃꯨꯛ ꯍꯟꯅ ꯄꯨꯝꯅꯃꯛ ꯐꯖꯅ ꯂꯩꯈꯤ꯫<ref name=":britannica.com/topic/Kali" /><ref name=":thewire.in/religion/kali" /><ref name=":worldhistory.org/Kali" />
== ꯀꯥꯂꯤ ꯑꯃꯁꯨꯡ ꯔꯛꯇꯥꯕꯤꯖꯥ ==

ꯑꯔꯣꯏꯕꯗ, ꯀꯥꯂꯤꯒꯤ ꯄꯣꯛꯄꯒꯤ ꯑꯇꯣꯞꯄ ꯃꯑꯣꯡ ꯑꯃꯗ, ꯑꯀꯤꯕ ꯐꯠꯇꯕ ꯂꯥꯏ ꯔꯛꯇꯥꯕꯤꯖ (ꯏꯒꯤ ꯃꯔꯨ)ꯒꯤ ꯋꯥꯔꯤ ꯂꯩ꯫ ꯃꯁꯤꯒꯤ ꯐꯠꯇꯕ ꯂꯥꯏ ꯑꯁꯤꯅ, ꯑꯌꯥꯝꯕ ꯐꯠꯇꯕ ꯂꯥꯏꯁꯤꯡꯒꯨꯝꯅ, ꯃꯤꯑꯣꯏꯁꯤꯡ ꯑꯃꯁꯨꯡ ꯂꯥꯏꯁꯤꯡꯒ ꯃꯥꯟꯅꯅ ꯑꯋꯥꯕ ꯀꯌꯥ ꯑꯃ ꯊꯣꯛꯍꯟꯈꯤ ꯑꯗꯨꯕꯨ ꯃꯁꯤꯗꯒꯤ ꯍꯦꯟꯅ ꯐꯠꯇꯕ ꯑꯗꯨꯗꯤ ꯃꯍꯥꯛꯀꯤ ꯏꯒꯤ ꯃꯆꯦꯠ ꯑꯃ ꯂꯩꯃꯥꯏꯗ ꯆꯦꯟꯊꯔꯛꯄ ꯃꯇꯝ ꯈꯨꯗꯤꯡꯃꯛꯇ ꯐꯠꯇꯕ ꯂꯥꯏ ꯍꯦꯟꯅ ꯄꯨꯊꯣꯛꯄ ꯉꯝꯕ ꯑꯗꯨꯅꯤ꯫ ꯃꯔꯝ ꯑꯁꯤꯅ, ꯔꯛꯇꯥꯕꯤꯖꯥꯗ ꯂꯥꯟꯗꯥꯈꯤꯕ ꯃꯇꯝ ꯈꯨꯗꯤꯡꯃꯛ, ꯑꯃꯠꯇ ꯉꯥꯏꯔꯕ ꯃꯍꯩ ꯑꯗꯨꯗꯤ ꯐꯠꯇꯕ ꯂꯥꯏꯁꯤꯡ ꯍꯦꯟꯅ ꯊꯦꯡꯅꯒꯗꯕꯅꯤ꯫ ꯂꯥꯏꯁꯤꯡꯅ ꯄꯨꯟꯅ ꯊꯕꯛ ꯇꯧꯅꯕ ꯑꯃꯁꯨꯡ ꯃꯈꯣꯏꯒꯤ ꯁꯛꯇꯤ ꯅꯠꯇ꯭ꯔꯒ ꯂꯥꯏꯒꯤ ꯑꯣꯏꯕ ꯄꯥꯡꯒꯜ ꯄꯨꯝꯅꯃꯛ ꯄꯨꯟꯁꯤꯟꯗꯨꯅ ꯔꯛꯇꯥꯕꯤꯖꯕꯨ ꯃꯥꯡꯍꯟ ꯇꯥꯛꯍꯟꯕ ꯉꯝꯕ ꯁꯨꯄꯔ ꯖꯤꯕ ꯑꯃ ꯄꯨꯊꯣꯛꯅꯕ ꯋꯥꯔꯦꯞ ꯂꯧꯈꯤ꯫ ꯃꯁꯤꯒꯤ ꯃꯍꯩ ꯑꯗꯨꯗꯤ ꯀꯥꯂꯤ (ꯑꯇꯣꯞꯄ ꯃꯑꯣꯡ ꯑꯃꯗ ꯗꯨꯔꯒꯥ ꯈꯛꯇꯅ ꯀꯥꯂꯤ ꯄꯨꯊꯣꯛꯏ)꯫ ꯂꯥꯏꯁꯤꯡꯒꯤ ꯂꯥꯏꯒꯤ ꯑꯣꯏꯕ ꯈꯨꯠꯂꯥꯏ ꯄꯨꯝꯅꯃꯛ ꯄꯤꯔꯒ, ꯀꯥꯂꯤꯅ ꯊꯨꯅ ꯔꯛꯇꯥꯕꯤꯖꯥ ꯑꯃꯁꯨꯡ ꯃꯍꯥꯛꯀꯤ ꯐꯠꯇꯕ ꯂꯥꯏꯁꯤꯡꯕꯨ ꯊꯤꯈꯤ ꯑꯃꯁꯨꯡ ꯊꯧꯑꯣꯡ ꯑꯗꯨꯗ ꯏ ꯑꯃꯠꯇ ꯍꯦꯟꯅ ꯆꯦꯟꯊꯍꯟꯗꯅꯕ ꯃꯈꯣꯏ ꯄꯨꯝꯅꯃꯛ ꯂꯧꯁꯤꯟꯅꯕ ꯃꯈꯥ ꯆꯠꯊꯈꯤ꯫
ꯀꯥꯂꯤꯅ ꯃꯍꯥꯛꯀꯤ ꯃꯀꯣꯛ ꯑꯗꯨ ꯊꯥꯡꯁꯥꯡ ꯑꯃꯅ ꯀꯛꯊꯠꯈꯤꯕ ꯑꯃꯁꯨꯡ ꯃꯗꯨꯒꯤ ꯃꯇꯨꯡꯗ ꯃꯍꯥꯛꯀꯤ ꯏ ꯄꯨꯝꯅꯃꯛ ꯊꯛꯈꯤ, ꯃꯁꯤꯅ ꯀꯅꯥꯒꯨꯝꯕ ꯑꯃꯠꯇ ꯂꯩꯃꯥꯏꯗ ꯇꯥꯗꯅꯕ ꯑꯃꯁꯨꯡ ꯃꯁꯤꯅ ꯃꯔꯝ ꯑꯣꯏꯗꯨꯅ ꯂꯥꯏ ꯐꯠꯇꯕꯁꯤꯡꯅ ꯃꯥꯂꯦꯝ ꯑꯁꯤꯕꯨ ꯈꯨꯗꯣꯡꯊꯤꯕ ꯄꯤꯕ ꯉꯝꯍꯟꯗꯕꯗꯒꯤ ꯔꯛꯇꯥꯕꯤꯖꯥ ꯃꯁꯥꯃꯛ ꯍꯥꯠꯈꯤ꯫
ꯑꯀꯤꯕ ꯄꯣꯛꯂꯕ ꯂꯥꯏꯔꯦꯝꯕꯤ ꯑꯁꯤꯒ ꯃꯔꯤ ꯂꯩꯅꯕ ꯑꯇꯣꯞꯄ ꯃꯃꯤꯡ ꯂꯩꯔꯕ ꯋꯥꯔꯤ ꯑꯃꯗꯤ ꯃꯍꯥꯛꯅ ꯍꯨꯔꯥꯟꯕ ꯀꯥꯡꯂꯨꯞ ꯑꯃꯒ ꯂꯣꯏꯅꯅ ꯅꯥꯟꯊꯣꯛꯄꯅꯤ꯫ ꯍꯨꯔꯥꯟꯕꯁꯤꯡ ꯑꯗꯨꯅ ꯀꯥꯂꯤꯗ ꯃꯤꯑꯣꯏꯕꯅ ꯀꯠꯊꯣꯛꯄ ꯄꯥꯝꯈꯤ, ꯑꯃꯁꯨꯡ ꯂꯧꯁꯤꯡ ꯂꯩꯇꯅ ꯕ꯭ꯔꯥꯍꯃꯟ ꯂꯝꯕꯣꯏꯕ ꯑꯃꯕꯨ ꯑꯁꯣꯛ-ꯑꯄꯟ ꯅꯪꯂꯕ ꯃꯤꯑꯣꯏ ꯑꯃ ꯑꯣꯏꯅ ꯈꯟꯈꯤ꯫ ꯃꯍꯥꯛꯄꯨ ꯈ꯭ꯋꯥꯏꯗꯒꯤ ꯅꯛꯄ ꯂꯥꯏꯁꯪꯗ ꯄꯨꯗꯨꯅ ꯍꯨꯔꯥꯟꯕꯁꯤꯡꯅ ꯀꯥꯂꯤꯒꯤ ꯃꯤꯇꯝꯒꯤ ꯃꯃꯥꯡꯗ ꯀꯠꯊꯣꯛꯅꯕ ꯁꯦꯝ ꯁꯥꯈꯤ ꯃꯗꯨꯗ ꯈꯡꯍꯧꯗꯅ ꯃꯤꯇꯝ ꯑꯗꯨ ꯍꯤꯡꯒꯠꯂꯛꯈꯤ꯫ ꯍꯨꯔꯥꯟꯕꯁꯤꯡꯅ ꯂꯝꯕꯣꯏꯕ ꯑꯃꯕꯨ ꯍꯥꯠꯅꯕ ꯊꯧꯔꯥꯡ ꯇꯧꯈꯤꯕ ꯑꯗꯨꯗ ꯁꯥꯎꯔꯗꯨꯅ ꯂꯥꯏꯔꯦꯝꯕꯤ ꯑꯗꯨꯅ ꯊꯨꯅ ꯂꯃꯟ ꯈꯨꯝꯈꯤ ꯑꯃꯁꯨꯡ ꯀꯥꯡꯕꯨ ꯄꯨꯝꯅꯃꯛꯀꯤ ꯃꯀꯣꯛ ꯀꯛꯊꯠꯈꯤ, ꯅꯨꯡꯉꯥꯏꯅꯕꯒꯤꯗꯃꯛ ꯃꯈꯣꯏꯒꯤ ꯃꯀꯣꯛ ꯐꯥꯎꯕ ꯂꯪꯊꯈꯤ, ꯑꯗꯨꯒ ꯃꯍꯧꯁꯥꯅ ꯕ꯭ꯔꯥꯍꯃꯟ ꯑꯗꯨꯅ ꯃꯍꯥꯛꯀꯤ ꯑꯈꯪ-ꯑꯍꯩꯒꯤ ꯄꯨꯟꯁꯤ ꯑꯗꯨ ꯃꯈꯥ ꯆꯠꯊꯅꯕ ꯅꯥꯟꯊꯣꯛꯈꯤ꯫<ref name=":britannica.com/topic/Kali" /><ref name=":thewire.in/religion/kali" /><ref name=":worldhistory.org/Kali" />
== ꯃꯁꯤꯟ (ꯀꯂꯥ) ==

ꯀꯂꯥꯗ, ꯀꯥꯂꯤ ꯑꯁꯤ ꯃꯍꯥꯛꯀꯤ ꯅꯨꯄꯤꯒꯤ ꯃꯑꯣꯡꯗ ꯑꯌꯥꯝꯕꯅ ꯍꯤꯒꯣꯛ ꯅꯠꯇ꯭ꯔꯒ ꯑꯃꯨꯕ ꯎꯟꯁꯥꯒ ꯂꯣꯏꯅꯅ, ꯃꯐꯤ ꯁꯦꯡꯗꯕ, ꯑꯃꯁꯨꯡ ꯃꯆꯨ ꯁꯪꯂꯕ ꯅꯠꯇ꯭ꯔꯒ ꯃꯆꯨ ꯁꯪꯂꯕ ꯕꯦꯡꯒꯣꯂꯤ ꯃꯈꯜꯒꯤ ꯂꯩꯕꯥꯛꯀꯤ ꯀ꯭ꯔꯥꯎꯟ ꯑꯃ ꯁꯦꯠꯇꯨꯅ ꯎꯠꯂꯤ꯫ ꯃꯍꯥꯛ, ꯍꯤꯟꯗꯨ ꯂꯥꯏ ꯀꯌꯥꯒꯨꯝꯅ, ꯈꯨꯠꯂꯥꯏꯒꯤ ꯃꯁꯤꯡ ꯃꯔꯤ, ꯅꯤꯄꯥꯟ, ꯇꯔꯥ, ꯇꯔꯥꯅꯤꯊꯣꯏ, ꯅꯠꯇ꯭ꯔꯒ ꯇꯔꯥꯅꯤꯄꯥꯟ ꯐꯥꯎꯕ ꯂꯩꯕ ꯃꯁꯤꯡ ꯌꯥꯝꯂꯕ ꯈꯨꯠꯂꯥꯏ ꯄꯥꯏꯕ ꯃꯤꯁꯛ ꯑꯃꯅꯤ꯫ ꯄꯥꯝꯕꯣꯝ ꯈꯨꯗꯤꯡꯃꯛꯅ ꯃꯍꯧꯁꯥꯅ ꯄꯣꯠꯁꯛ ꯑꯃ ꯄꯥꯏ ꯑꯃꯁꯨꯡ ꯃꯁꯤꯗ ꯊꯥꯡꯁꯥꯡ, ꯊꯥꯡꯁꯥꯡ, ꯇ꯭ꯔꯥꯏꯗꯦꯟꯠ, ꯀꯞ, ꯗ꯭ꯔꯝ, ꯆꯀ꯭ꯔ, ꯊꯝꯕꯥꯜꯒꯤ ꯃꯀꯨ, ꯆꯩꯔꯥꯛ, ꯈꯣꯡꯒꯨꯝ, ꯀꯥꯡꯁꯤ ꯑꯃꯁꯨꯡ ꯉꯥꯛꯊꯣꯛꯅꯕ ꯌꯥꯎꯕ ꯌꯥꯏ꯫ ꯀꯔꯤꯒꯨꯝꯕ ꯃꯇꯝꯗ ꯃꯍꯥꯛꯀꯤ ꯑꯣꯏꯒꯤ ꯈꯨꯠꯅ ꯑꯚꯥꯌ ꯃꯨꯗ꯭ꯔꯥ ꯁꯦꯝꯃꯤ, ꯑꯗꯨꯒ ꯌꯦꯠꯂꯣꯝꯅ ꯀꯠꯂꯤꯕ ꯕꯔꯥꯗ ꯃꯨꯗ꯭ꯔꯥ ꯑꯗꯨ ꯁꯦꯝꯃꯤ꯫ ꯃꯍꯥꯛꯄꯨ ꯑꯌꯥꯝꯕꯅ ꯈꯣꯡ ꯂꯥꯟꯗꯨꯅ ꯑꯃꯁꯨꯡ ꯐꯨꯠ ꯅꯤꯄꯥꯟ ꯂꯩꯗꯨꯅ ꯐꯝꯗꯨꯅ ꯎꯠꯂꯤ꯫
ꯑꯌꯦꯛꯄ ꯂꯥꯏꯁꯤꯡꯗ ꯀꯥꯂꯤꯒꯤ ꯈ꯭ꯋꯥꯏꯗꯒꯤ ꯇꯣꯏꯅ ꯊꯣꯛꯄ ꯄꯣꯖ ꯑꯁꯤ ꯃꯍꯥꯛꯀꯤ ꯈ꯭ꯋꯥꯏꯗꯒꯤ ꯀꯤꯅꯤꯡꯉꯥꯏ ꯑꯣꯏꯕ ꯃꯋꯣꯡꯗ ꯐꯠꯇꯕ ꯂꯥꯏꯕꯨ ꯍꯥꯠꯄꯒꯤ ꯃꯋꯣꯡꯗꯅꯤ, ꯃꯐꯝ ꯑꯗꯨꯗ ꯃꯍꯥꯛꯅ ꯇꯨꯝꯊꯔꯕ ꯁꯤꯕ ꯑꯃꯗ ꯈꯣꯡ ꯑꯃ ꯊꯝꯗꯨꯅ ꯂꯦꯞꯇꯨꯅ ꯅꯠꯇ꯭ꯔꯒ ꯖꯒꯣꯏ ꯁꯥꯏ ꯑꯃꯁꯨꯡ ꯀꯛꯊꯠꯂꯕ ꯃꯀꯣꯛ ꯑꯃ ꯄꯥꯏ꯫ ꯃꯍꯥꯛꯅ ꯀꯛꯊꯠꯂꯕ ꯃꯤꯑꯣꯏꯕꯒꯤ ꯄꯥꯝꯕꯣꯝꯁꯤꯡꯒꯤ ꯁ꯭ꯀꯔ꯭ꯠ ꯑꯃ, ꯃꯀꯣꯛ ꯀꯛꯊꯠꯂꯕ ꯃꯀꯣꯛꯁꯤꯡꯒꯤ ꯂꯤꯛ ꯑꯃ ꯑꯃꯁꯨꯡ ꯁꯤꯔꯕ ꯑꯉꯥꯡꯁꯤꯡꯒꯤ ꯁꯝꯐꯨ ꯑꯃ ꯁꯦꯠꯂꯤ, ꯑꯃꯁꯨꯡ ꯃꯍꯥꯛꯅ ꯑꯌꯥꯝꯕ ꯃꯇꯝꯗ ꯏ ꯆꯦꯟꯊꯔꯤꯕ ꯂꯣꯂꯤꯡ ꯑꯦꯛꯁꯇꯦꯟꯗꯦꯗ ꯖꯤꯕ ꯑꯃꯒ ꯂꯣꯏꯅꯅ ꯑꯀꯤꯕ ꯄꯣꯛꯍꯟꯕ ꯃꯋꯣꯡ ꯑꯃ ꯂꯩ꯫<ref name=":britannica.com/topic/Kali" /><ref name=":thewire.in/religion/kali" /><ref name=":worldhistory.org/Kali" />

==ꯁꯤꯃꯁꯨ ꯌꯦꯡꯕꯤꯌꯨ==
* [[ꯃꯍꯤꯁꯥꯁꯨꯔ]]
* [[ꯄꯥꯔꯕꯇꯤ]]

==ꯃꯇꯦꯡ==
{{Reflist}}
[[ꯃꯆꯥꯈꯥꯏꯕ:ꯍꯤꯟꯗꯨꯒꯤ ꯆꯤꯉꯨ ꯈꯣꯌꯨꯝ ꯂꯥꯢꯌꯥꯝꯁꯤꯡ]]
[[Category:Wp/mni]]

"""
    print(MeiteiToBengali.transliterate(text))

if __name__ == '__main__':
    test()
