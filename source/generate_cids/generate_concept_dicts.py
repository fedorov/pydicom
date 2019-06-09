#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding required to deal with 'micro' character
"""Script for auto-generating DICOM SR context groups from FHIR JSON value set
resources.


"""

from io import BytesIO
import json
import ftplib
import glob
import logging
import os
import re
import sys
import tempfile
from xml.etree import ElementTree as ET

if sys.version_info[0] < 3:
    import urllib as urllib_request
else:
    import urllib.request as urllib_request

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
                "system":"http://snomed.info/sct",
                "concept":[
                    {
                        "code":"387362001",
                        "display":"Epinephrine"
                    },

"""
# The list of scheme designators is not complete.
# For full list see table 8-1 in part 3.16 chapter 8:
# http://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_8.html#table_8-1
FHIR_SYSTEM_TO_DICOM_SCHEME_DESIGNATOR = {
    'http://snomed.info/sct': 'SCT',
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

leave_alone = ['mm', 'cm', 'km', 'um',
               'ms',  #  'us'?-doesn't seem to be there
               'ml',
               'mg', 'kg',
               ]  # ... probably need others


def camel_case(s):
    return ''.join(word.capitalize() if word != word.upper()
                   and word not in leave_alone
                   else word
                   for word in re.split(r"\W", s, flags=re.UNICODE)
                   if word.isalnum()
                   )


def keyword_from_meaning(name):
    """Return a camel case valid python identifier"""
    # Try to adhere to keyword scheme in DICOM (CP850)

    # singular/plural alternative forms are made plural
    #     e.g., “Physician(s) of Record” becomes “PhysiciansOfRecord”
    name = name.replace("(s)", "s")

    # “Patient’s Name” -> “PatientName”
    # “Operators’ Name” -> “OperatorsName”
    name = name.replace("’s ", " ")
    name = name.replace("'s ", " ")
    name = name.replace("s’ ", "s ")
    name = name.replace("s' ", "s ")

    # Mathematical symbols
    name = name.replace("%", " Percent ")
    name = name.replace(">", " Greater Than ")
    name = name.replace("=", " Equals ")
    name = name.replace("<", " Lesser Than ")

    name = re.sub(r'([0-9]+)\.([0-9]+)', '\\1 Point \\2', name)
    name = re.sub(r'\s([0-9.]+)-([0-9.]+)\s', ' \\1 To \\2 ', name)

    name = re.sub(r'([0-9]+)day', '\\1 Day', name)
    name = re.sub(r'([0-9]+)y', '\\1 Years', name)

    name = camel_case(name.strip())

    # Python variables must not begin with a number.
    if re.match(r'[0-9]', name):
        name = "_" + name

    return name


def download_fhir_value_sets(local_dir):
    ftp_host = 'medical.nema.org'

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    logger.info('storing files in ' + local_dir)
    logger.info('log into FTP server "{}"'.format(ftp_host))
    ftp = ftplib.FTP(ftp_host, timeout=60)
    ftp.login('anonymous')

    ftp_path = 'medical/dicom/resources/valuesets/fhir/json'
    logger.info('list files in directory "{}"'.format(ftp_path))
    fhir_value_set_files = ftp.nlst(ftp_path)
    ftp_url = 'ftp://{host}/{path}'.format(host=ftp_host, path=ftp_path)

    try:
        for ftp_filepath in fhir_value_set_files:
            ftp_filename = os.path.basename(ftp_filepath)
            logger.info('retrieve value set file "{}"'.format(ftp_filename))
            with BytesIO() as fp:
                ftp.retrbinary('RETR {}'.format(ftp_filepath), fp.write)
                content = fp.getvalue()
            local_filename = os.path.join(local_dir, ftp_filename)
            with open(local_filename, 'wb') as f_local:
                f_local.write(content)
    finally:
        ftp.quit()


def _parse_html(content):
    # from lxml import html
    # doc = html.document_fromstring(content)
    return ET.fromstring(content, parser=ET.XMLParser(encoding='utf-8'))


def _download_html(url):
    response = urllib_request.urlopen(url)
    return response.read()


def _get_text(element):
    text = "".join(element.itertext())
    return text.strip()


def get_table_o1():
    url = 'http://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_O.html#table_O-1'
    root = _parse_html(_download_html(url))
    namespaces = {'w3': root.tag.split('}')[0].strip('{')}
    body = root.find('w3:body', namespaces=namespaces)
    table = body.findall('.//w3:tbody', namespaces=namespaces)[0]
    rows = table.findall('./w3:tr', namespaces=namespaces)
    return [
        (
            _get_text(row[0].findall('.//w3:a', namespaces=namespaces)[-1]),
            _get_text(row[1].findall('.//w3:p', namespaces=namespaces)[0]),
            _get_text(row[2].findall('.//w3:p', namespaces=namespaces)[0]),
        )
        for row in rows
    ]


def get_table_d1():
    url = 'http://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_D.html#table_D-1'
    root = _parse_html(_download_html(url))
    namespaces = {'w3': root.tag.split('}')[0].strip('{')}
    body = root.find('w3:body', namespaces=namespaces)
    table = body.findall('.//w3:tbody', namespaces=namespaces)[0]
    rows = table.findall('./w3:tr', namespaces=namespaces)
    return [
        (
             _get_text(row[0].findall('.//w3:p', namespaces=namespaces)[0]),
             _get_text(row[1].findall('.//w3:p', namespaces=namespaces)[0])
        )
        for row in rows
    ]


def write_concepts(concepts, cid_concepts, cid_lists, name_for_cid):
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
        f_cid.write("name_for_cid = {}\n")
        f_cid.write("cid_concepts = {}\n")
        for cid, value in cid_lists.items():
            f_cid.write("\nname_for_cid[{}] = '{}'\n".format(
                         cid, name_for_cid[cid]))
            f_cid.write("cid_concepts[{}] = \\\n".format(cid))
            pprint(value, f_cid)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    local_dir = tempfile.gettempdir()
    fhir_dir = os.path.join(local_dir, "fhir")

    if not os.path.exists(fhir_dir) or not os.listdir(fhir_dir):
        download_fhir_value_sets(fhir_dir)
    else:
        msg = "Using locally downloaded files\n"
        msg += "from directory " + fhir_dir
        logging.info(msg)

    fhir_value_set_files = glob.glob(os.path.join(fhir_dir, "*"))
    cid_pattern = re.compile('^dicom-cid-([0-9]+)-[a-zA-Z]+')

    concepts = dict()
    cid_lists = dict()
    name_for_cid = dict()

    # XXX = 0
    try:
        for ftp_filepath in fhir_value_set_files:
            ftp_filename = os.path.basename(ftp_filepath)
            logger.info('process file "{}"'.format(ftp_filename))

            with open(ftp_filepath, 'rb') as fp:
                content = fp.read()
                value_set = json.loads(content)

            cid_match = cid_pattern.search(value_set['id'])
            cid = int(cid_match.group(1)) # can take int off to store as string

            name_for_cid[cid] = value_set['name']
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
                    if name in cid_concepts[scheme_designator]:
                      msg = "'{}': Meaning '{}' in cid_{} is duplicated!"
                      msg = msg.format(name, concept['display'], cid)
                      logger.warning(msg)
                    cid_concepts[scheme_designator].append(name)
            cid_lists[cid] = cid_concepts
            # if XXX > 3:
                # break
            # XXX += 1


        scheme_designator = 'SCT'
        snomed_codes = get_table_o1()
        for code, srt_code, meaning in snomed_codes:
            name = keyword_from_meaning(meaning)
            if name not in concepts[scheme_designator]:
                concepts[scheme_designator][name] = {code: (meaning, [])}
            else:
                prior = concepts[scheme_designator][name]
                if code not in prior:
                    prior[code] = (meaning, [])

        scheme_designator = 'DCM'
        dicom_codes = get_table_d1()
        for code, meaning in dicom_codes:
            name = keyword_from_meaning(meaning)
            if name not in concepts[scheme_designator]:
                concepts[scheme_designator][name] = {code: (meaning, [])}
            else:
                prior = concepts[scheme_designator][name]
                if code not in prior:
                    prior[code] = (meaning, [])

    finally:
        # If any error or KeyboardInterrupt, close up and write what we have

        write_concepts(concepts, cid_concepts, cid_lists, name_for_cid)
