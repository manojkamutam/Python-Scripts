import paramiko
import os
import datetime

# === CONFIGURATION ===
EC2_HOST = "Enter-IP-here"
EC2_USER = "username"
EC2_KEY_FILE = "path of key file"
LOCAL_JAR_FILE = "your_jar_name.jar"
JAVA_PACKAGE_NAME = "your_application name" #This can be anything you can give
REMOTE_DIR = "/home/ubuntu/jar-deployment"
REMOTE_BACKUP_DIR = f"{REMOTE_DIR}/backup"
REMOTE_JAR_NAME = "remote_jar_name.jar"
REMOTE_JAR_PATH = f"{REMOTE_DIR}/{REMOTE_JAR_NAME}"
REMOTE_LOG_FILE = f"{REMOTE_DIR}/{JAVA_PACKAGE_NAME}.out"

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{timestamp()}] {msg}")

def ssh_exec(ssh, command, stop_on_error=True):
    log(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode()
    error = stderr.read().decode()
    if output:
        log("STDOUT:\n" + output)
    if error:
        log("STDERR:\n" + error)
    if stop_on_error and exit_status != 0:
        raise RuntimeError(f"Command failed: {command}\nError: {error}")
    return output, error

def deploy_jar():
    log("📡 Connecting to EC2 instance...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(EC2_HOST, username=EC2_USER, key_filename=EC2_KEY_FILE)

    sftp = ssh.open_sftp()

    log("📁 Creating necessary directories...")
    ssh_exec(ssh, f"mkdir -p {REMOTE_DIR} {REMOTE_BACKUP_DIR}")

    log("🔍 Finding and killing existing JAR process...")
    kill_cmd = f"""ps -ef | grep {REMOTE_JAR_NAME} | grep -v grep | awk '{{print $2}}' | xargs -r kill -9"""
    ssh_exec(ssh, kill_cmd)

    log("🗃️ Backing up existing JAR file if exists...")
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = f"{REMOTE_BACKUP_DIR}/{REMOTE_JAR_NAME}.{timestamp_str}"
    ssh_exec(ssh, f"if [ -f {REMOTE_JAR_PATH} ]; then mv {REMOTE_JAR_PATH} {backup_path}; fi")

    log("📤 Uploading new JAR file...")
    sftp.put(LOCAL_JAR_FILE, f"{REMOTE_DIR}/temp-upload.jar")

    log("🚚 Renaming uploaded JAR to my-java.jar...")
    ssh_exec(ssh, f"sudo mv {REMOTE_DIR}/temp-upload.jar {REMOTE_JAR_PATH}")

    log("🚀 Deploying new JAR file using nohup...")
    deploy_cmd = f"sudo nohup java -jar {REMOTE_JAR_PATH} >> {REMOTE_LOG_FILE} 2>&1 &"
    ssh_exec(ssh, deploy_cmd)

    log("⏱️ Waiting 5 seconds for process to spin up...")
    import time
    time.sleep(5)

    log("✅ Verifying process is running...")
    ssh_exec(ssh, f"sudo ps -ef | grep {REMOTE_JAR_NAME} | grep -v grep")

    log("🔎 Checking listening ports using netstat...")
    ssh_exec(ssh, "sudo netstat -tuln | grep LISTEN")
    ssh_exec(ssh, "sleep 10")

    log("📄 Fetching last 200 lines from log to find active Spring profile or config...")
    output, _ = ssh_exec(ssh, f"sudo tail -n 200 {REMOTE_LOG_FILE}")
    for line in output.splitlines():
        if "property" in line.lower() or "profile" in line.lower():
            print(f"[FOUND] {line}")

    log("✅ Deployment complete.")
    sftp.close()
    ssh.close()

if __name__ == "__main__":
    deploy_jar()
