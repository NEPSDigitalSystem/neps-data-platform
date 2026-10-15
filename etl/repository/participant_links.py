"""Explicit post-export links to IDs issued by the existing NDS registry.

No participant or consent is created here. The authoriser must verify an actual
NDS registration/ID and actor permission before binding an external source ID.
"""
from sqlalchemy import Column, MetaData, String, Table, insert, select

metadata=MetaData()
links=Table('nds_v31_participant_links',metadata,
            Column('project',String,primary_key=True),Column('source_id',String,primary_key=True),
            Column('nds_id',String,nullable=False),Column('mapping_version',String,nullable=False))


class ParticipantLinks:
    def __init__(self,engine,*,authoriser=None):
        self.engine,self.authoriser=engine,authoriser

    def bind(self,project,source_id,nds_id,mapping_version,actor):
        if any(type(x) is not str or not x for x in (project,source_id,nds_id,mapping_version,actor)):
            raise ValueError('Explicit source and separate NDS identifiers required')
        if nds_id==source_id:
            raise ValueError('NDS identifier must be separate from source record ID')
        if self.authoriser is None:
            raise PermissionError('Authorised NDS registration adapter required')
        try:
            allowed=self.authoriser(project,source_id,nds_id,actor)
        except Exception:
            raise PermissionError('NDS registration verification unavailable') from None
        if allowed is not True:
            raise PermissionError('NDS registration binding not authorised')
        with self.engine.begin() as c:
            old=c.execute(select(links).where(links.c.project==project,links.c.source_id==source_id)).mappings().first()
            if old:
                if old['nds_id']!=nds_id or old['mapping_version']!=mapping_version:
                    raise ValueError('Existing ID binding requires separately reviewed correction')
                return dict(old)
            row=dict(project=project,source_id=source_id,nds_id=nds_id,mapping_version=mapping_version)
            c.execute(insert(links).values(**row));return row

    def resolve(self,project,source_id):
        with self.engine.connect() as c:
            row=c.execute(select(links).where(links.c.project==project,links.c.source_id==source_id)).mappings().first()
            return None if row is None else dict(row)
