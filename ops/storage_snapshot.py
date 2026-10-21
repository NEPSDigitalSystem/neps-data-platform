"""Read-only recovery digest. Never accepts a credential URL on the command line."""
import argparse
import json
from pathlib import Path
from sqlalchemy import create_engine
from etl.load.db import database_url
from etl.repository.integrity import storage_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url-file', type=Path, required=True)
    parser.add_argument('--schema', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    engine = create_engine(database_url(args.url_file.read_text().strip()),
                           hide_parameters=True, echo=False)
    try:
        result = storage_snapshot(engine, args.schema)
        # Do not overwrite earlier evidence accidentally.
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2); stream.write('\n')
    finally:
        engine.dispose()


if __name__ == '__main__':
    main()
