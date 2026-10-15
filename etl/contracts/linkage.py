"""REDCap issues participant IDs; NDS separately registers and consents after source export.

This module never creates participant IDs or registers/consents a person.
Internal database revision UUIDs are unrelated to participant numbering.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RedcapParticipantKey:
    project: str
    source_id: str
    issuer: str = 'REDCap'

    def __post_init__(self):
        if (type(self.project) is not str or not self.project or
                type(self.source_id) is not str or not self.source_id or self.issuer != 'REDCap'):
            raise ValueError('Explicit REDCap project and issued string identifier required')

    @classmethod
    def from_record(cls, project, record, contract):
        linkage = contract['participant_linkage']
        if linkage['id_issuer'] != 'REDCap':
            raise ValueError('Unverified participant identifier issuer')
        field = linkage['source_record_id_field']
        if contract['fields'][0]['name'] != field:
            raise ValueError('Source record ID field differs from verified dictionary')
        return cls(project, record.get(field))
