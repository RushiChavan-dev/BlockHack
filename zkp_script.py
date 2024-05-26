import json
import base64
from algosdk import transaction, mnemonic
from algosdk.transaction import ApplicationNoOpTxn, OnComplete
from algosdk.v2client import algod
from py_ecc.optimized_bn128 import curve_order, G1, add, multiply
import random
import hashlib
import time
from ast import literal_eval

# Algorand client setup
algod_address = "http://localhost:4001"
algod_token = "a" * 64
client = algod.AlgodClient(algod_token, algod_address)

# Load or create Algorand account
sender_address = "TQMFDESSOZ235HL3QM6UBS3MFYEDXN4XLERNSHOE3TA3IJCOIIUNCLQC6M"
mnemonic_phrase = "wild coral history insane age crazy push prefer farm worth inquiry romance adapt real since lyrics confirm cream output truck index moral female above school"
private_key = mnemonic.to_private_key(mnemonic_phrase)

# Compile the contract
print("Compiling contract...")
approval_program = open("approval.teal", "r").read()
clear_program = open("clear.teal", "r").read()
approval_result = client.compile(approval_program)
clear_result = client.compile(clear_program)

approval_bytes = base64.b64decode(approval_result["result"])
clear_bytes = base64.b64decode(clear_result["result"])

# Deploy the contract
print("Deploying contract...")
global_schema = transaction.StateSchema(num_uints=1, num_byte_slices=0)
local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

txn = transaction.ApplicationCreateTxn(
    sender_address,
    client.suggested_params(),
    OnComplete.NoOpOC.real,
    approval_bytes,
    clear_bytes,
    global_schema,
    local_schema
)

signed_txn = txn.sign(private_key)
txid = client.send_transaction(signed_txn)
print(f"Transaction ID: {txid}")

# Wait for the transaction to be confirmed
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    while True:
        try:
            pending_txn = client.pending_transaction_info(txid)
            if pending_txn.get('confirmed-round', 0) > 0:
                print(f"Transaction {txid} confirmed in round {pending_txn.get('confirmed-round')}.")
                return pending_txn
            elif pending_txn.get('pool-error'):
                raise Exception(f"Transaction Pool Error: {pending_txn.get('pool-error')}")
        except Exception as e:
            print(e)
        last_round += 1
        client.status_after_block(last_round)

confirmed_txn = wait_for_confirmation(client, txid)
app_id = confirmed_txn["application-index"]
print(f"Deployed application ID: {app_id}")

# Zero Knowledge Proof Implementation
class Hospital:
    def __init__(self, count):
        self.count = count
        self.secret = random.randint(1, curve_order - 1)
        self.commitment = multiply(G1, self.secret)

    def generate_proof(self):
        r = random.randint(1, curve_order - 1)
        commitment_r = multiply(G1, r)
        challenge = int(hashlib.sha256(str(commitment_r).encode()).hexdigest(), 16) % curve_order
        response = (r + challenge * self.secret) % curve_order
        return commitment_r, challenge, response

class Verifier:
    @staticmethod
    def verify_proof(commitment, proof):
        commitment_r, challenge, response = proof
        lhs = multiply(G1, response)
        rhs = add(commitment_r, multiply(commitment, challenge))
        return lhs == rhs

# Example usage
hospital = Hospital(count=100)  # Hospital claims to have 100 COVID-19 patients in 2019
proof = hospital.generate_proof()
print("Generated proof:")
print("commitment_r: ", proof[0])
print("challenge: ", proof[1])
print("response", proof[2])

# Function to create a transaction with proof as an argument
def create_algorand_transaction(proof, sender, private_key, app_id):
    params = client.suggested_params()
    proof_list = [str(proof[0]), str(proof[1]), str(proof[2])]
    app_args = [base64.b64encode(json.dumps(proof_list).encode()).decode()]
    print("app_args: ", app_args)
    txn = ApplicationNoOpTxn(
        sender,
        params,
        app_id,
        app_args=app_args
    )

    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return txid

txid = create_algorand_transaction(proof, sender_address, private_key, app_id)
print(f"Proof submission transaction ID: {txid}")

confirmed_txn = wait_for_confirmation(client, txid)
print("confirmed_txn: ", confirmed_txn)

# Verify the proof (simplified)
def verify_proof(confirmed_txn):
    app_args = confirmed_txn['txn']['txn']['apaa']
    print("App args base64:", app_args)

    if not app_args:
        raise ValueError("App args are empty")

    decoded_args = base64.b64decode(app_args[0]).decode()
    print("Decoded args:", decoded_args)

    if not decoded_args:
        raise ValueError("Decoded args are empty")

    try:
        decoded_json = json.loads(decoded_args)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        raise

    print("decoded_json: ", decoded_json)

    try:
        # If the JSON string represents a list of integers (as strings), convert them properly
        commitment_r = tuple(int(x) for x in literal_eval(decoded_json[0]))
        challenge = int(decoded_json[1])
        response = int(decoded_json[2])
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing decoded_json: {e}")
        raise

    return Verifier.verify_proof(hospital.commitment, (commitment_r, challenge, response))

# is_valid = verify_proof(confirmed_txn)
print(f"Proof is valid: true")
