"""Local human-operated approval signer. Never exposed through MCP."""
import argparse
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from mce_web import canonical, json_file, read, sign_approval, require_windows


def main():
    require_windows()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--private-key', required=True, type=Path)
    parser.add_argument('--authorized-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--approver', required=True)
    parser.add_argument('--decision', required=True, choices=['AUTORIZO_ELABORACAO_MCE'])
    parser.add_argument('--model-reviewed', required=True, action='store_true')
    parser.add_argument('--lifetime-seconds', type=int, default=3600)
    args = parser.parse_args()
    root = args.authorized_root.resolve()
    if args.private_key.resolve().is_relative_to(root) or args.output.resolve().is_relative_to(root):
        raise ValueError('Private key and external approvals must stay outside the remote root')
    request = json_file(args.request)
    if request.get('product') != 'MCE_INDEPENDENTE' or not request.get('files'):
        raise ValueError('An exact MCE approval request is required')
    key = load_pem_private_key(read(args.private_key), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError('Ed25519 operator signing key required')
    envelope = sign_approval(request, key, args.approver, lifetime_seconds=args.lifetime_seconds)
    with args.output.open('xb') as handle:
        handle.write(canonical(envelope))
    print('SIGNED_EXACT_INPUT_APPROVAL; not engineering acceptance')


if __name__ == '__main__':
    main()
