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
MNI_NS_REV_TEMPORARY_MAPPING = {v : k for k, v in MNI_NS_TEMPORARY_MAPPING.items()}
MNI_NS_PATTERN = re.compile('(' + '|'.join(MNI_NS_TEMPORARY_MAPPING.keys()) + ') *?:')
MNI_NS_REV_PATTERN = re.compile('(' + '|'.join(MNI_NS_REV_TEMPORARY_MAPPING.keys()) + '):')

def _mni_ns_to_temporary(m : re.Match) -> str:
    return MNI_NS_TEMPORARY_MAPPING.get(m.group(1), m.group(1)) + ':'
def _mni_ns_rev_to_temporary(m : re.Match) -> str:
    return MNI_NS_REV_TEMPORARY_MAPPING.get(m.group(1), m.group(1)) + ':'

def preprocess_mni(text : str) -> str:
    mni_ns_replaced = MNI_NS_PATTERN.sub(_mni_ns_to_temporary, text)
    return mni_ns_replaced
def postprocess_mni(text : str) -> str:
    mni_ns_rev_replaced = MNI_NS_REV_PATTERN.sub(_mni_ns_rev_to_temporary, text)
    return mni_ns_rev_replaced


MeiteiToBengali.set_postprocess(postprocess_mni)
MeiteiToBengali.set_preprocess(preprocess_mni)