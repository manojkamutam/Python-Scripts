import paramiko
import datetime
from cryptography.fernet import Fernet

# Bastion host details
BASTION_HOST = 'ec2-ip-address'
BASTION_USER = 'username'
BASTION_KEY_FILE = 'key file path'

# MySQL connection (via bastion)
MYSQL_HOST = 'database-ip'
MYSQL_DB = 'database_name'
MYSQL_QUERY = 'Your DB Query'

# === ENCRYPTED CREDS AND KEY ===
ENCRYPTION_KEY = b'enter your encryption key'  # Paste your key here
ENCRYPTED_USERNAME = b'enter encrypted username'
ENCRYPTED_PASSWORD = b'enter your encrypted password'

def decrypt_credential(token):
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(token).decode()

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{timestamp()}] {msg}")

def run_mysql_query_via_bastion():
    log("Starting SSH session...")

    try:
        # Decrypt credentials
        MYSQL_USER = decrypt_credential(ENCRYPTED_USERNAME)
        MYSQL_PASSWORD = decrypt_credential(ENCRYPTED_PASSWORD)

        # Construct MySQL command
        mysql_cmd = (
            f'mysql -h {MYSQL_HOST} -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -D {MYSQL_DB} -e "{MYSQL_QUERY}"'
        )
        log(f"MySQL command: mysql -h {MYSQL_HOST} -u ***** -p***** -D {MYSQL_DB} -e \"{MYSQL_QUERY}\"")

        # Setup SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        log(f"Connecting to bastion host {BASTION_HOST} as user {BASTION_USER}...")

        ssh.connect(BASTION_HOST, username=BASTION_USER, key_filename=BASTION_KEY_FILE)
        log("SSH connection established.")

        # Execute
        log("Executing MySQL command...")
        stdin, stdout, stderr = ssh.exec_command(mysql_cmd)
        exit_status = stdout.channel.recv_exit_status()

        out = stdout.read().decode()
        err = stderr.read().decode()

        log("Command execution completed.")
        log(f"Exit status: {exit_status}")

        if out:
            log("STDOUT:"); print(out)
        if err:
            log("STDERR:"); print(err)

        if exit_status == 0:
            log("✅ MySQL query executed successfully.")
        else:
            log("❌ MySQL query failed.")

        ssh.close()
        log("SSH connection closed.")

    except Exception as e:
        log(f"❗ Exception occurred: {e}")

if __name__ == "__main__":
    run_mysql_query_via_bastion()
