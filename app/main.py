from fastapi import FastAPI
from pydantic import BaseModel
from web3 import Web3
import hashlib
import json
import os
from dotenv import load_dotenv

# ------------------------
# Load Environment
# ------------------------
load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# ------------------------
# Connect to Blockchain
# ------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)

# Replace this ABI with your contract ABI
ABI = [
    {
        "inputs": [{"internalType": "string","name": "hashValue","type": "string"}],
        "name": "storeHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# ------------------------
# FastAPI Setup
# ------------------------
app = FastAPI()


class PredictionInput(BaseModel):
    crop: str
    state: str
    temperature: float
    rainfall: float


# ------------------------
# Hash Function
# ------------------------
def generate_hash(data: dict) -> str:
    json_string = json.dumps(data, sort_keys=True)
    encoded = json_string.encode()
    hash_object = hashlib.sha256(encoded)
    return hash_object.hexdigest()


# ------------------------
# Store Hash On Blockchain
# ------------------------
def store_hash_on_chain(hash_value: str):
    nonce = w3.eth.get_transaction_count(account.address)

    txn = contract.functions.storeHash(hash_value).build_transaction({
        "chainId": 11155111,  # Sepolia testnet
        "gas": 200000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "nonce": nonce
    })

    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return w3.to_hex(tx_hash)


# ------------------------
# Prediction Endpoint
# ------------------------
@app.post("/predict")
def predict(data: PredictionInput):

    # Dummy model logic (replace later)
    predicted_price = 3000 + data.temperature * 5 - data.rainfall * 2

    prediction_output = {
        "crop": data.crop,
        "state": data.state,
        "predicted_price": predicted_price
    }

    # Generate hash
    hash_value = generate_hash(prediction_output)

    # Store on blockchain
    tx_hash = store_hash_on_chain(hash_value)

    return {
        "prediction": prediction_output,
        "hash": hash_value,
        "transaction_hash": tx_hash
    }
