"""Independent configured source collector safety tests; no live activation."""
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from sqlalchemy import create_engine,inspect
from etl.sync.source_runtime import SourceServiceGrant,build_collector
from etl.config import Settings
from etl.extract.production_client import ProductionRedcapClient
from test_v31_source_runtime import config
from test_v31_connector import Session

def test_runtime_construction_never_migrates_or_requests_remote_data():
 engine=create_engine('sqlite:///:memory:');transport=Session()
 collector=build_collector(config(),engine=engine,session=transport)
 assert collector.project=='source-only-project'
 assert inspect(engine).get_table_names()==[]
 assert transport.calls==[]

def test_configured_grant_rejects_wrong_project_environment_endpoint_and_identity():
 cfg=config();grant=SourceServiceGrant(cfg)
 client=ProductionRedcapClient(cfg,session=Session())
 scope=client._scope('metadata')
 assert grant.export(scope) is True
 for change in [{'project_id':'other-project'},{'environment':'other-env'},{'api_endpoint':'https://other.invalid/'},{'service_identity_fingerprint':'0'*64},{'operation':'import'}]:
  assert grant.export(replace(scope,**change)) is False


def test_settings_start_disabled_and_event_mode_unverified():
 defaults=Settings(_env_file=None,SOURCE_INTAKE_ENABLED=False,SOURCE_EVENT_MODE='unverified')
 assert defaults.source_intake_enabled is False and defaults.source_event_mode=='unverified'
 with pytest.raises(PermissionError):SourceServiceGrant(defaults)

def test_cli_source_failure_reports_only_sanitised_code(capsys):
 import etl.main as main
 marker='SYNTHETIC-TOKEN-RECORD-UNSAFE-ERROR'
 with patch.object(main,'get_settings',return_value=config()),patch('etl.sync.source_runtime.build_collector',side_effect=RuntimeError(marker)):
  assert main.cmd_collect_source(SimpleNamespace())==1
 captured=capsys.readouterr()
 assert marker not in captured.out+captured.err
