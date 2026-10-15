"""Independent source receipt, followed by separately retryable NDS processing.

REDCap collection/completion has no NDS callback. Receipt runs without NDS
registration, NDS ID or NDS consent. A separate consumer resolves later NDS
registration/consent/purpose permissions; unavailable processing leaves raw
source revisions and their queue entries intact.
"""
from sqlalchemy import select
from etl.intake.v31 import RecordIdentity as SourceIdentity
from etl.repository.v31 import RecordIdentity, AccessDenied, validated
from etl.extract.production_client import metadata_to_dictionary, RedcapMetadataDrift
from etl.contracts.v31 import metadata_drift
from etl.scoring.v31 import Scorer


def serialise(result):
    return {'algorithm_version':result.algorithm_version, 'contract_sha256':result.contract_sha256,
            'source_sha256':result.source_sha256, 'provisional':result.provisional,
            'scores':{name:{'value':None if score.value is None else
                           {'numerator':score.value.numerator,'denominator':score.value.denominator},
                           'issues':[{'field':i.field,'state':i.state} for i in score.issues]}
                      for name,score in result.scores.items()}}


class Workflow:
    """Full-project reconciliation into durable source intake only."""
    def __init__(self,client,intake,*,project,context_provider=None):
        if client.project_id != project or intake.project != project:
            raise PermissionError('Source project differs from configured intake')
        self.client,self.intake,self.project,self.context_provider=client,intake,project,context_provider

    def sync(self,*,source_version,actor='source-collector',since=None,full=True):
        if self.context_provider is None:
            raise PermissionError('Verified source event/repeat configuration required')
        # Full source reconciliation avoids losing corrected/late offline uploads.
        # dateRangeBegin is not assumed to be a reliable modification watermark.
        snapshot=self.client.export_source_snapshot()
        prepared=[]
        for record in snapshot.records:
            event,instrument,instance=self.context_provider(record)
            identity=SourceIdentity(self.project,record[snapshot.record_id_field],event,instrument,instance)
            prepared.append((identity,record))
        for identity,record in prepared:
            self.intake.receive(identity,record,source_version,actor,
                                record_id_field=snapshot.record_id_field,metadata_snapshot=snapshot.metadata)
        reconciliation=self.intake.reconcile([identity for identity,record in prepared],actor,
                                             full_export_succeeded=True)
        return {'received':len(prepared),'full_reconciliation':True,
                'metadata_sha256':snapshot.metadata_sha256,'contract_drift':snapshot.contract_drift,
                'reconciliation':reconciliation}


class DownstreamProcessor:
    """Optional later NDS stage. Never a dependency of source export/receipt."""
    def __init__(self,intake,repository,links,*,applicability_provider=None,accepted_metadata=None,
                 approved_metadata_versions=None):
        self.intake,self.repository,self.links=intake,repository,links
        self.applicability_provider=applicability_provider
        self.accepted_metadata=accepted_metadata or [f['dictionary_metadata'] for f in repository.contract['fields']]
        # Explicit reviewed versions allow old/new receipts to coexist. Adding
        # a version never overwrites source history or changes scoring rules.
        self.approved_metadata_versions=approved_metadata_versions or {}
        self.scorer=Scorer(repository.contract)

    def process(self,*,actor='nds-processor',limit=100):
        if type(limit) is not int or not 1<=limit<=10000:
            raise ValueError('Bounded processing batch required')
        processed,deferred=0,0
        for _ in range(limit):
            claim=self.intake.claim(actor)
            if claim is None:break
            try:
                mapping=self.links.resolve(claim.identity.project,claim.identity.source_id)
                if mapping is None:
                    self.intake.fail(claim.source_revision_id,claim.claim_token,actor,'mapping_pending',retry_delay=60)
                    deferred+=1;continue
                try:
                    source_metadata=None if claim.metadata_snapshot is None else metadata_to_dictionary(claim.metadata_snapshot)
                except RedcapMetadataDrift:
                    self.intake.fail(claim.source_revision_id,claim.claim_token,actor,'processing_restricted',retry_delay=60)
                    deferred+=1;continue
                reviewed=self.approved_metadata_versions.get(claim.metadata_hash)
                expected=self.accepted_metadata if reviewed is None else reviewed['metadata']
                policy_version='local-reviewed-metadata' if reviewed is None else reviewed['version']
                if type(policy_version) is not str or not policy_version or source_metadata is None or metadata_drift(expected,source_metadata):
                    self.intake.fail(claim.source_revision_id,claim.claim_token,actor,'processing_restricted',retry_delay=60)
                    deferred+=1;continue
                i=claim.identity
                identity=RecordIdentity(i.project,i.source_id,i.event,i.instrument,i.instance)
                sid=self.repository.ingest(identity,claim.payload,claim.source_version,actor,
                                           nds_participant_id=mapping['nds_id'],source_metadata=source_metadata,
                                           intake_revision_id=claim.source_revision_id)
                with self.repository.engine.connect() as c:
                    layer=c.execute(select(validated).where(validated.c.source_id==sid)).mappings().one()
                reasons={name:('not_applicable' if state=='inapplicable' else 'invalid')
                         for name,state in layer['issues'].items() if name in self.scorer.codes}
                applicable=False if self.applicability_provider is None else self.applicability_provider(identity)
                if type(applicable) is not bool:
                    raise PermissionError('Unverified applicability decision')
                result=self.scorer.score(layer['values'],missingness=reasons,epi_applicable=applicable,
                    source_context={'source_id':sid,'intake_revision':claim.source_revision_id,
                                    'source_version':claim.source_version,'nds_id':mapping['nds_id'],
                                    'metadata_policy_version':policy_version})
                stored_result=serialise(result)
                stored_result['intake_revision_id']=claim.source_revision_id
                stored_result['source_metadata_sha256']=claim.metadata_hash
                stored_result['nds_participant_id']=mapping['nds_id']
                stored_result['mapping_version']=mapping['mapping_version']
                stored_result['metadata_policy_version']=policy_version
                self.repository.store_derived(sid,result.algorithm_version+':'+result.source_sha256,stored_result,actor)
                self.intake.ack(claim.source_revision_id,claim.claim_token,actor)
                processed+=1
            except PermissionError:
                self.intake.fail(claim.source_revision_id,claim.claim_token,actor,'processing_restricted',retry_delay=60)
                deferred+=1
            except Exception:
                # Keep sensitive upstream errors out of queue, responses and logs.
                self.intake.fail(claim.source_revision_id,claim.claim_token,actor,'nds_unavailable',retry_delay=60)
                deferred+=1
        return {'processed':processed,'deferred':deferred}
