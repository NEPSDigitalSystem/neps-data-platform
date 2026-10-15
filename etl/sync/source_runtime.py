"""Configured API collector using existing engine/secrets/scheduler entry point.

Configuration grants source service access only; no NDS registry or consent
query participates. SOURCE_INTAKE_ENABLED is operator configuration, not proof
of ethics, country-transfer or live API approval. Configure actual source/DAG
and destination permissions before enabling an authorised environment.
"""
import hashlib
from etl.extract.production_client import ProductionRedcapClient
from etl.intake.v31 import Intake
from etl.load.db import create_db_engine
from etl.sync.v31_workflow import Workflow


class SourceServiceGrant:
    def __init__(self,settings):
        if (not settings.source_intake_enabled or settings.redcap_mock_enabled or
                not settings.redcap_api_token or not settings.source_destination or
                not settings.source_service_identity or settings.source_event_mode=='unverified'):
            raise PermissionError('Source service configuration is incomplete')
        self.settings=settings
        self.fingerprint=hashlib.sha256(settings.redcap_api_token.encode()).hexdigest()

    def export(self,scope):
        return (scope.project_id==self.settings.redcap_project_id and
                scope.environment==self.settings.app_env and scope.api_endpoint==self.settings.redcap_api_url and
                scope.service_identity_fingerprint==self.fingerprint and scope.operation in ('metadata','record'))

    def authorises(self,scope):
        return (scope.project==self.settings.redcap_project_id and
                scope.destination==self.settings.source_destination and
                scope.service_identity==self.settings.source_service_identity and
                scope.actor=='source-collector' and scope.action in ('receive','reconcile'))

    def context(self,row):
        if self.settings.source_event_mode=='auto':
            event=row.get('redcap_event_name','')
            if type(event) is not str:
                raise ValueError('Native source event metadata requires review')
        elif self.settings.source_event_mode=='longitudinal':
            event=row.get('redcap_event_name')
            if type(event) is not str or not event:
                raise ValueError('Source longitudinal event is missing')
        else:
            event=row.get('redcap_event_name','')
            if event!='':raise ValueError('Classic source unexpectedly contains longitudinal event')
        instrument=row.get('redcap_repeat_instrument','')
        instance=row.get('redcap_repeat_instance','')
        # Keep source values intact; only the explicit identity component is canonical.
        if type(instrument) is not str or type(instance) not in (str,int) or isinstance(instance,bool):
            raise ValueError('Source repeat metadata requires review')
        return event,instrument,str(instance)


def build_collector(settings,*,engine=None,session=None):
    grant=SourceServiceGrant(settings)
    engine=create_db_engine(settings) if engine is None else engine
    client=ProductionRedcapClient(settings,authorisation_provider=grant.export,session=session)
    intake=Intake(engine,project=settings.redcap_project_id,destination=settings.source_destination,
                  service_identity=settings.source_service_identity,policy=grant)
    return Workflow(client,intake,project=settings.redcap_project_id,context_provider=grant.context)
