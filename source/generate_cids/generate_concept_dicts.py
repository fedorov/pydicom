#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding required to deal with 'micro' character
"""Script for auto-generating DICOM SR context groups from FHIR JSON value set
resources.


"""

import ftplib
import json
import logging
import os
import re
from io import BytesIO
import tempfile
import glob

logger = logging.getLogger(__name__)

# Example excerpt fhir JSON for reference
"""
    "resourceType":"ValueSet",
    "id":"dicom-cid-10-InterventionalDrug",
    ...
    "name":"InterventionalDrug",
    ...
    "compose":{
        "include":[
            {
                "system":"http://snomed.info/srt",
                "concept":[
                    {
                        "code":"F-B2135",
                        "display":"Epinephrine"
                    },

"""
# The list of scheme designators is not complete.
# For full list see table 8-1 in part 3.16 chapter 8:
# http://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_8.html#table_8-1
FHIR_SYSTEM_TO_DICOM_SCHEME_DESIGNATOR = {
    'http://snomed.info/sct': 'SCT',
    'http://snomed.info/srt': 'SRT',
    'http://dicom.nema.org/resources/ontology/DCM': 'DCM',
    'http://loinc.org': 'LN',
    'http://www.radlex.org': 'RADLEX',
    'http://sig.biostr.washington.edu/projects/fm/AboutFM.html': 'FMA',
    'http://www.nlm.nih.gov/mesh/meshhome.html': 'MSH',
    'http://ncit.nci.nih.gov': 'NCIt',
    'http://unitsofmeasure.org': 'UCUM',
    'http://hl7.org/fhir/sid/ndc': 'NDC',
    'urn:iso:std:iso:11073:10101': 'MDC',
    'doi:10.1016/S0735-1097(99)00126-6': 'BARI',
    'http://www.nlm.nih.gov/research/umls': 'UMLS',
    'http://pubchem.ncbi.nlm.nih.gov': 'PUBCHEM_CID',
    'http://braininfo.rprc.washington.edu/aboutBrainInfo.aspx#NeuroNames': 'NEU',
    'http://www.itis.gov': 'ITIS_TSN',
}


def camel_case(s):
    return ''.join(word.capitalize()
                   for word in re.split('([^a-zA-Z0-9])', s)
                   if word.isalnum())

def keyword_from_meaning(name):
    """Return a camel case valid python identifier"""
    name = camel_case(name.strip())

    # Python variables must not begin with a number.
    if re.match(r'[0-9]', name):
        name = re.sub(r'^([^_]+)(_)(.*)', r'\3_\1', name)
        name = re.sub(r'^([0-9]+)(.*)', r'\2_\1', name)
    return name

def download_fhir(local_dir):
    ftp_host = 'medical.nema.org'

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    logger.info('storing files in ' + local_dir)
    logger.info('log into FTP server "{}"'.format(ftp_host))
    ftp = ftplib.FTP(ftp_host, timeout=60)
    ftp.login('anonymous')

    ftp_path = 'medical/dicom/resources/valuesets/fhir/json'
    logger.info('list files in directory "{}"'.format(ftp_path))
    ftp_files = ftp.nlst(ftp_path)
    ftp_url = 'ftp://{host}/{path}'.format(host=ftp_host, path=ftp_path)

    try:
        for ftp_filepath in ftp_files:
            ftp_filename = os.path.basename(ftp_filepath)
            logger.info('retrieve file "{}"'.format(ftp_filename))
            with BytesIO() as fp:
                ftp.retrbinary('RETR {}'.format(ftp_filepath), fp.write)
                content = fp.getvalue()
            local_filename = os.path.join(local_dir, ftp_filename)
            with open(local_filename, 'wb') as f_local:
                f_local.write(content)
    finally:
        ftp.quit()    


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    local_dir = tempfile.gettempdir()
    fhir_dir = os.path.join(local_dir, "fhir")
    
    if not os.path.exists(fhir_dir) or not os.listdir(fhir_dir):
        download_fhir(fhir_dir)
    else:
        msg = "Using locally downloaded files\n"
        msg += "from directory " + fhir_dir
        logging.info(msg)
    
    ftp_files = glob.glob(os.path.join(fhir_dir, "*"))
    cid_pattern = re.compile('^dicom-cid-([0-9]+)-[a-zA-Z]+')
    
    concepts = dict()
    cid_lists = dict()
    # XXX = 0
    try:
        for ftp_filepath in ftp_files:
            ftp_filename = os.path.basename(ftp_filepath)
            logger.info('process file "{}"'.format(ftp_filename))

            with open(ftp_filepath, 'rb') as fp:
                content = fp.read()
                value_set = json.loads(content)

            cid_match = cid_pattern.search(value_set['id'])
            cid = int(cid_match.group(1)) # can take int off to store as string
            
            context_group_name = value_set['name']
            cid_concepts = {}
            for group in value_set['compose']['include']:
                system = group['system']
                try:
                    scheme_designator = FHIR_SYSTEM_TO_DICOM_SCHEME_DESIGNATOR[system]
                except KeyError:
                    raise NotImplementedError(
                        'The DICOM scheme designator for the following FHIR system '
                        'has not been specified: {}'.format(system)
                    )
                if scheme_designator not in concepts:
                    concepts[scheme_designator] = dict()
                
                for concept in group['concept']:
                    name = keyword_from_meaning(concept['display'])
                    code = concept['code'].strip()
                    display = concept['display'].strip()
                    
                    # If new name under this scheme, start dict of codes/cids that use that code
                    if name not in concepts[scheme_designator]:
                        concepts[scheme_designator][name] = {code: (display, [cid])}
                    else:
                        prior = concepts[scheme_designator][name]
                        if code in prior:
                            prior[code][1].append(cid)
                        else:
                            prior[code] = (display, [cid])

                        if prior[code][0].lower() != display.lower():
                            # Meanings can only be different by symbols, etc.
                            #    because converted to same keyword.
                            #    Nevertheless, print as info
                            msg = "'{}': Meaning '{}' in cid_{}, previously '{}' in cids {}"
                            msg = msg.format(name, display, cid,
                                             prior[code][0], prior[code][1])
                            logger.info(msg)

                    # Keep track of this cid referencing that name
                    if scheme_designator not in cid_concepts:
                        cid_concepts[scheme_designator] = []
                    cid_concepts[scheme_designator].append(name)
            cid_lists[cid] = cid_concepts
            # if XXX > 3:
                # break
            # XXX += 1
    finally:
        # If any error or KeyboardInterrupt, close up and write what we have

        from pprint import pprint
        lines = ['# Auto-generated by {}.\n'.format(os.path.basename(__file__)),
                 '# -*- coding: utf-8 -*-\n',
                 '\n',
                 '# Dict with scheme designator keys; value format is:\n',
                 '#   {keyword: {code1: (meaning, cid_list}, code2:...}\n',
                 '#\n',
                 '# Most keyword identifiers map to a single code, but not all\n',
                 '\n',
                ]
                    
        with open("_concepts_dict.py", 'w', encoding="UTF8") as f_concepts:
            f_concepts.writelines(lines)
            f_concepts.write("concepts = {}\n") # start with empty dict
            for scheme, value in concepts.items():          
                f_concepts.write("\nconcepts['{}'] = \\\n".format(scheme))
                pprint(value, f_concepts)
    
        lines = (lines[:3] + 
                 ['# Dict with cid number as keys; value format is:\n',
                  '#   {scheme designator: <list of keywords for current cid>\n',
                  '#    scheme_designator: ...}\n',
                  '\n',
                 ]
                )

        with open("_cid_dict.py", 'w', encoding="UTF8") as f_cid:
            f_cid.writelines(lines)
            f_cid.write("cid_concepts = {}\n")
            for cid, value in cid_lists.items():
                f_cid.write("\ncid_concepts[{}] = \\\n".format(cid))
                pprint(value, f_cid)
