import pickle
from phe import paillier

KEY_FILE = "keys.pkl"

def generate_keys():
    public_key, private_key = paillier.generate_paillier_keypair()

    with open(KEY_FILE, "wb") as f:
        pickle.dump((public_key, private_key), f)

    print("Clés générées et sauvegardées dans", KEY_FILE)


if __name__ == "__main__":
    generate_keys()