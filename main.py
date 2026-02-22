import os
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet

USER_DB = "users.json"
BACKUP_DIR = "backups"

current_user = None

# ---------------- User System ----------------

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password, role):
    users = load_users()

    if username in users:
        print("❌ Username already exists")
        return

    if role not in ["admin", "user"]:
        print("❌ Role must be admin or user")
        return

    salt = os.urandom(16)
    kdf = PBKDF2HMAC(hashes.SHA256(), 32, salt, 100000)
    key = base64.b64encode(kdf.derive(password.encode())).decode()

    users[username] = {
        "salt": base64.b64encode(salt).decode(),
        "key": key,
        "role": role
    }

    save_users(users)
    print("✅ Registered successfully")

def authenticate(username, password):
    users = load_users()

    if username not in users:
        return False

    salt = base64.b64decode(users[username]["salt"])
    kdf = PBKDF2HMAC(hashes.SHA256(), 32, salt, 100000)
    key = base64.b64encode(kdf.derive(password.encode())).decode()

    return key == users[username]["key"]

def get_role(username):
    return load_users().get(username, {}).get("role")

# ---------------- RSA Keys ----------------

def generate_rsa_keys():
    if get_role(current_user) != "admin":
        print("❌ Only admin can generate keys")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)

    private_key = rsa.generate_private_key(65537, 2048)
    public_key = private_key.public_key()

    with open("private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))

    with open("public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("✅ RSA keys generated")

# ---------------- Backup ----------------

def create_backup(file_path):
    if not os.path.exists("public.pem"):
        print("❌ RSA keys not found. Admin must generate first.")
        return

    if not os.path.exists(file_path):
        print("❌ File not found")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)

    with open(file_path, "rb") as f:
        data = f.read()

    aes_key = Fernet.generate_key()
    fernet = Fernet(aes_key)
    encrypted_data = fernet.encrypt(data)

    backup_name = "backup_file"

    with open(f"{BACKUP_DIR}/{backup_name}.bin", "wb") as f:
        f.write(encrypted_data)

    with open("public.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    metadata = {
        "original_file": os.path.basename(file_path),
        "encrypted_key": base64.b64encode(encrypted_key).decode()
    }

    with open(f"{BACKUP_DIR}/{backup_name}.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print("✅ Backup created")

# ---------------- List ----------------

def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print("No backups found")
        return []

    backups = [f.replace(".json", "") for f in os.listdir(BACKUP_DIR) if f.endswith(".json")]

    if not backups:
        print("No backups found")
    else:
        for i, b in enumerate(backups, 1):
            print(f"{i}. {b}")

    return backups

# ---------------- Restore ----------------

def restore_backup(backup_name, output_file):
    if get_role(current_user) != "admin":
        print("❌ Only admin can restore backups")
        return

    with open("private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), None)

    with open(f"{BACKUP_DIR}/{backup_name}.json") as f:
        metadata = json.load(f)

    encrypted_key = base64.b64decode(metadata["encrypted_key"])

    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    fernet = Fernet(aes_key)

    with open(f"{BACKUP_DIR}/{backup_name}.bin", "rb") as f:
        encrypted_data = f.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print("✅ Backup restored")

# ---------------- Menus ----------------

def admin_menu():
    while True:
        print("\nAdmin Menu")
        print("1. Generate RSA Keys")
        print("2. Create Backup")
        print("3. List Backups")
        print("4. Restore Backup")
        print("5. Logout")

        c = input("Select: ")

        if c == "1":
            generate_rsa_keys()
        elif c == "2":
            create_backup(input("File path: "))
        elif c == "3":
            list_backups()
        elif c == "4":
            backups = list_backups()
            if backups:
                idx = int(input("Select backup number: ")) - 1
                restore_backup(backups[idx], input("Output file name: "))
        elif c == "5":
            break
        else:
            print("❌ Invalid choice")

def user_menu():
    while True:
        print("\nUser Menu")
        print("1. Create Backup")
        print("2. List Backups")
        print("3. Logout")

        c = input("Select: ")

        if c == "1":
            create_backup(input("File path: "))
        elif c == "2":
            list_backups()
        elif c == "3":
            break
        else:
            print("❌ Invalid choice")

# ---------------- Main ----------------

def main():
    global current_user

    while True:
        print("\n🔐 Secure Backup System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        c = input("Select: ")

        if c == "1":
            register_user(
                input("Username: "),
                input("Password: "),
                input("Role (admin/user): ").lower()
            )

        elif c == "2":
            u = input("Username: ")
            p = input("Password: ")

            if authenticate(u, p):
                current_user = u
                print(f"✅ Logged in as {get_role(u)}")

                if get_role(u) == "admin":
                    admin_menu()
                else:
                    user_menu()
            else:
                print("❌ Login failed")

        elif c == "3":
            print("👋 Goodbye")
            break
        else:
            print("❌ Invalid choice")

