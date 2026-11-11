"""Read only the bundled allowlisted snapshot; no SDK, network or credentials."""
import argparse
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent


def documents():
    return json.loads((HERE / 'documents.json').read_text(encoding='utf-8'))


def search_documents(query):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 500:
        raise ValueError('Use uma busca de 1 a 500 caracteres.')
    terms = re.findall(r'\w+', query.casefold())
    if not terms:
        return {'results': []}
    ranked = []
    for doc in documents().values():
        title, body = doc['title'].casefold(), doc['text'].casefold()
        if all(term in title or term in body for term in terms):
            score = sum(10 * title.count(term) + min(body.count(term), 10) for term in terms)
            ranked.append((score, doc))
    ranked.sort(key=lambda row: (-row[0], row[1]['id']))
    return {'results': [{k: doc[k] for k in ('id', 'title', 'url')} for _, doc in ranked[:20]]}


def fetch_document(id):
    catalog = documents()
    if id not in catalog:
        raise ValueError('Documento inexistente; use um id retornado por search.')
    doc = catalog[id]
    return {**{k: doc[k] for k in ('id', 'title', 'text', 'url')},
            'metadata': {'source_sha256': doc['sha256'], 'snapshot': '2026-10-21',
                         'source_instructions': 'reference_only', 'license': 'MIT'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['search', 'fetch'])
    parser.add_argument('value')
    args = parser.parse_args()
    try:
        result = search_documents(args.value) if args.operation == 'search' else fetch_document(args.value)
        result['execution_route'] = 'local_reference'
        if 'metadata' in result:
            result['metadata']['execution_route'] = 'local_reference'
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({'execution_route': 'local_reference', 'error': str(error)}, ensure_ascii=True))
        return 2


if __name__ == '__main__':
    sys.exit(main())
