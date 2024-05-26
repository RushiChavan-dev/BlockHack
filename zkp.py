
import pandas as pd
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

# Load the CSV file with the correct delimiter
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, delimiter=',')
        return df
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: The file could not be parsed.")
        return None

# Print column names and count the number of diabetes patients
def count_diabetes_patients(df):
    if df is not None:
        print("Column names:", df.columns)
        diabetes_patients = df[df['Outcome'] == 'Yes']
        return diabetes_patients.shape[0]
    else:
        return 0

# Generate a Zero-Knowledge Proof
def generate_proof(count):
    secret = get_random_bytes(16)  # Generate a random secret
    data_to_hash = f'{count}{secret.hex()}'.encode('utf-8')
    hash_obj = SHA256.new(data_to_hash)
    proof = hash_obj.hexdigest()
    return proof, secret

# Verify the Zero-Knowledge Proof
def verify_proof(count, proof, secret):
    data_to_hash = f'{count}{secret}'.encode('utf-8')
    hash_obj = SHA256.new(data_to_hash)
    generated_proof = hash_obj.hexdigest()
    return generated_proof == proof

# Main function to execute the ZKP process
def main(file_path):
    df = load_data(file_path)
    if df is not None:
        diabetes_count = count_diabetes_patients(df)
        proof, secret = generate_proof(diabetes_count)
        print(f'Number of diabetes patients: {diabetes_count}')
        print(f'Proof: {proof}')
        print(f'Secret: {secret.hex()}')

        # Verification step
        is_valid = verify_proof(diabetes_count, proof, secret.hex())
        print(f'Is the proof valid? {is_valid}')
    else:
        print("No data to process.")

# Example usage
file_path = 'diabetes.csv'
main(file_path)
