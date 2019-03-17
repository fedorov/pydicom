#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding required to deal with 'micro' character
"""Script for auto-generating DICOM SR context groups from FHIR JSON value set
resources."""
import ftplib
import json
import logging
import os
import re
from io import BytesIO

logger = logging.getLogger(__name__)

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

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    ftp_host = 'medical.nema.org'
    logger.info('log into FTP server "{}"'.format(ftp_host))
    ftp = ftplib.FTP(ftp_host, timeout=60)
    ftp.login('anonymous')

    ftp_path = 'medical/dicom/resources/valuesets/fhir/json'
    logger.info('list files in directory "{}"'.format(ftp_path))
    ftp_files = ftp.nlst(ftp_path)
    ftp_url = 'ftp://{host}/{path}'.format(host=ftp_host, path=ftp_path)

    cid_pattern = re.compile('^dicom-cid-([0-9]+)-[a-zA-Z]+')
    for ftp_filepath in ftp_files:
        src_code_lines = []
        ftp_filename = os.path.basename(ftp_filepath)
        logger.info('retrieve file "{}"'.format(ftp_filename))
        with BytesIO() as fp:
            ftp.retrbinary('RETR {}'.format(ftp_filepath), fp.write)
            content = fp.getvalue()
            value_set = json.loads(content)

        cid_match = cid_pattern.search(value_set['id'])
        cid = cid_match.group(1)
        context_group_name = value_set['name']
        logger.info('create source code for context group CID {}'.format(cid))
        docstring_lines = [
            '"""CID {} {}'.format(cid, context_group_name),
            'auto-generated by {}.'.format(os.path.basename(__file__)),
            '"""',
        ]
        src_code_lines.extend(docstring_lines)
        import_lines = [
            'from pydicom.sr.value_types import CodedConcept',
        ]
        src_code_lines.extend(import_lines)
        # Two empty lines between import statements and rest of the code.
        # The second empty line will be added below.
        src_code_lines.append('')

        keys = set()
        for group in value_set['compose']['include']:
            system = group['system']
            try:
                scheme_designator = FHIR_SYSTEM_TO_DICOM_SCHEME_DESIGNATOR[system]
            except KeyError:
                raise NotImplementedError(
                    'The DICOM scheme designator for the following FHIR system '
                    'has not been specified: {}'.format(system)
                )
            for concept in group['concept']:
                name = concept['display'].strip().upper()
                name = name.replace(' ', '_')
                name = re.sub(r'[-]', '', name)
                name = re.sub(r'[^a-zA-Z0-9]', '_', name)
                name = re.sub(r'(_+?)\1+', r'\1', name)
                # Python variables must not begin with a number.
                if re.match(r'[0-9]', name):
                    name = re.sub(r'^([^_]+)(_)(.*)', r'\3_\1', name)
                    name = re.sub(r'^([0-9]+)(.*)', r'\2_\1', name)
                if name in keys:
                    logger.warning(
                        'repeated context group item "{}"'.format(name)
                    )
                    continue
                keys.add(name)
                concept_lines = [
                    '',  # One empty line between items
                    '{} = CodedConcept('.format(name),
                    '    value="{}",'.format(concept['code']),
                    '    meaning="{}",'.format(concept['display']),
                    '    scheme_designator="{}"'.format(scheme_designator),
                    ')',
                ]
                src_code_lines.extend(concept_lines)
        # Two empty lines after each class definition
        src_code_lines.extend(['', ''])

        src_code = '\n'.join(src_code_lines)

        src_directory = os.path.dirname(__file__)
        src_filepath = os.path.join(
            src_directory,
            '..',
            '..',
            'pydicom',
            'sr',
            'context_groups',
            'cid_{}.py'.format(cid)
        )
        logger.info('write source code file "{}"'.format(src_filepath))

        with open(src_filepath, 'w') as fp:
            fp.write(src_code)

    ftp.quit()

