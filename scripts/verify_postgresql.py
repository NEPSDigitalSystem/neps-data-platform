"""Run the full suite against a new local synthetic PostgreSQL container."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from uuid import uuid4
import xml.etree.ElementTree as ET


IMAGE = 'postgres@sha256:74935e72241653ca55e0414067e6d8763aceb8a810eb51b452253ec3dcfc4336'
REPO = Path(__file__).resolve().parents[1]


def verify(output, network=None):
    output.mkdir(parents=True, exist_ok=False)
    container = 'neps-de03-synthetic-' + uuid4().hex[:12]
    commands = []
    started = False

    def docker(*args):
        command = ['docker', *args]
        commands.append(command)
        return subprocess.run(command, check=True, capture_output=True, text=True)

    try:
        if network:
            if not network.startswith('neps-de03-synthetic-network-'):
                raise ValueError('Only a dedicated synthetic network is allowed')
            details = json.loads(docker('network', 'inspect', network).stdout)[0]
            if details['Internal'] is not True or details.get('Labels', {}).get('neps.task') != 'DE03':
                raise ValueError('The synthetic network must be internal and labelled DE03')
        transport = ['--network', network] if network else ['--publish', '127.0.0.1::5432']
        docker('run', '--detach', '--rm', '--name', container,
               '--label', 'neps.task=DE03', *transport,
               '--tmpfs', '/var/lib/postgresql:rw',
               '--env', 'POSTGRES_HOST_AUTH_METHOD=trust',
               '--env', 'POSTGRES_DB=neps_de03_seed', IMAGE)
        started = True
        for attempt in range(60):
            ready = subprocess.run(['docker', 'exec', container, 'pg_isready', '-h', '127.0.0.1',
                '-U', 'postgres', '-d', 'neps_de03_seed'], capture_output=True)
            if ready.returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('Disposable PostgreSQL did not become ready')
        if network:
            host, port = container, '5432'
        else:
            ports = json.loads(docker('inspect', '--format', '{{json .NetworkSettings.Ports}}', container).stdout)
            binding = ports['5432/tcp'][0]
            assert binding['HostIp'] == '127.0.0.1'
            host, port = '127.0.0.1', binding['HostPort']
        version = docker('exec', container, 'psql', '-h', '127.0.0.1', '-U', 'postgres', '-d', 'neps_de03_seed',
                         '-Atc', 'SELECT version()').stdout.strip()
        with tempfile.TemporaryDirectory(prefix='neps-synthetic-url-') as directory:
            url_file = Path(directory) / 'database-url'
            url_file.write_text('postgresql://postgres@' + host + ':' + port + '/neps_de03_seed')
            url_file.chmod(0o600)
            env = {'PATH': os.environ['PATH'], 'LANG': 'C.UTF-8',
                'PYTHONDONTWRITEBYTECODE': '1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
                'NEPS_DE03_PG_URL_FILE': str(url_file),
                'NEPS_DE03_APPROVED': 'synthetic-disposable',
                'NEPS_DE03_CONTAINER': container,
                'NEPS_DE03_RECOVERY_EVIDENCE': str(output / 'recovery.json')}
            if network:
                env['NEPS_DE03_NETWORK'] = network
            command = [sys.executable, '-m', 'pytest', 'tests', '-q', '--tb=short',
                       '--junitxml=' + str(output / 'junit.xml')]
            start = time.monotonic()
            result = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True)
            (output / 'tests.log').write_text(result.stdout + result.stderr)
            suites = ET.parse(output / 'junit.xml').getroot().findall('testsuite')
            skipped = sum(int(s.attrib['skipped']) for s in suites)
            record = {'command': command, 'cwd': str(REPO), 'environment': env,
                'exit_code': result.returncode, 'seconds': time.monotonic() - start,
                'python': sys.version, 'postgresql': version, 'image': IMAGE,
                'suites': [s.attrib for s in suites], 'docker_commands': commands,
                'DBA_acceptance': 'TBD', 'RPO': 'TBD', 'RTO': 'TBD'}
            (output / 'run.json').write_text(json.dumps(record, indent=2) + '\n')
            print(result.stdout, end='')
            print(result.stderr, end='', file=sys.stderr)
            if result.returncode:
                return result.returncode
            if skipped:
                raise RuntimeError('Full PostgreSQL verification must not skip tests')
            if not (output / 'recovery.json').is_file():
                raise RuntimeError('Full verification did not produce recovery evidence')
            return 0
    except subprocess.CalledProcessError as error:
        (output / 'setup-error.json').write_text(json.dumps({
            'command': error.cmd, 'exit_code': error.returncode,
            'stdout': error.stdout, 'stderr': error.stderr}, indent=2) + '\n')
        raise
    finally:
        if started:
            # Only remove the uniquely named container created by this invocation.
            docker('rm', '--force', '--volumes', container)
        (output / 'container-cleanup.json').write_text(json.dumps({
            'container': container, 'removed': started, 'commands': commands}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', required=True, type=Path)
    parser.add_argument('--network', help='Existing labelled internal synthetic network for container tests')
    args = parser.parse_args()
    raise SystemExit(verify(args.evidence_dir.resolve(), args.network))
