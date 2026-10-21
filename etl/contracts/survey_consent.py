"""User-requested consent extension; proposed metadata, never deployed evidence.

The original source dictionary remains unchanged. The first source identifier
stays first; one survey-consent question is inserted before respondent content.
"""
import csv
import io
from .v31 import DICTIONARY_HEADERS, NAME, FORM, TYPE, CHOICES, BRANCH

CONSENT_FIELD = 'survey_consent'


def extend(dictionary):
    if dictionary[0][NAME] != 'study_id' or any(r[NAME] == CONSENT_FIELD for r in dictionary):
        raise ValueError('Source identifier/consent extension needs review')
    consent = {header:'' for header in DICTIONARY_HEADERS}
    consent.update({NAME:CONSENT_FIELD, FORM:dictionary[0][FORM], TYPE:'radio',
                    'Field Label':'I consent to take part in this NEPS survey.',
                    CHOICES:'1, Yes, I consent | 0, No, I do not consent', 'Required Field?':'y'})
    identifier=dict(dictionary[0])
    identifier['Section Header']='Survey identification and consent'
    identifier['Field Label']='REDCap survey record ID'
    identifier['Field Note']='REDCap-issued survey record identifier.'
    rows=[identifier,consent]
    for original in dictionary[1:]:
        row=dict(original)
        # No NDS call is involved in display: source consent alone controls it.
        old=row[BRANCH]
        row[BRANCH]="[survey_consent] = '1'" + (f' and ({old})' if old else '')
        rows.append(row)
    return rows


def write_csv(rows,path):
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=DICTIONARY_HEADERS)
        writer.writeheader();writer.writerows(rows)
