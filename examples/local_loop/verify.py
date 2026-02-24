import json
import hashlib

ARTIFACT_LOG = "artifacts\\gatekeeper.ndjson"

def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

with open(ARTIFACT_LOG, "r") as f:
    lines = [l.strip() for l in f if l.strip()]

prev_hash = "sha256:" + "0" * 64
all_valid = True

for line in lines:
    record = json.loads(line)
    idx = record["idx"]

    # recompute this_hash
    check = {**record, "chain": {"prev_hash": record["chain"]["prev_hash"], "this_hash": ""}}
    computed = sha256(json.dumps(check, sort_keys=True).encode())

    chain_ok = record["chain"]["prev_hash"] == prev_hash
    hash_ok = record["chain"]["this_hash"] == computed

    print(f"record {idx}: prev_hash={'OK' if chain_ok else 'FAIL'} | this_hash={'OK' if hash_ok else 'FAIL'}")

    if not chain_ok or not hash_ok:
        all_valid = False

    prev_hash = record["chain"]["this_hash"]

print(f"\nchain valid: {all_valid}")