# 🧰 DevOps & Automation Scripts

A collection of Python scripts to simplify cloud operations, ECS task management, database automation, frontend deployment, and secure resource handling. Each script serves a specific purpose in streamlining DevOps workflows.

---

## 📦 Scripts Overview

### 1. `cred_encrypt.py`
🔐 **Purpose**: Encrypt and decrypt credentials securely.

- Supports secure storage of sensitive information (like DB passwords or API keys).
- Can be integrated with other scripts for encrypted credential access.

### 2. `delete_data_from_table.py`
🧹 **Purpose**: Delete all records from a specified table in a MySQL database via a Flask REST API.

- Exposes a secure `/delete` endpoint.
- Requires an API key for authentication.
- Supports JSON requests to specify the target table.

### 3. `ecs_tasks_update.py`
⚙️ **Purpose**: Update the desired task count of an ECS service.

- Uses `boto3` to interact with ECS.
- Logs changes and verifies task count after update.
- CLI usage with flags: `--cluster`, `--service`, `--count`.

### 4. `fe_deployment_S3_cloud_front.py`
🌐 **Purpose**: Automate frontend deployment to S3 + CloudFront.

- Uploads frontend assets to an S3 bucket.
- Invalidates the CloudFront cache to reflect new changes instantly.
- Useful for SPA/static site deployments.

### 5. `jar_deployment_ec2.py`
🚀 **Purpose**: Deploy `.jar` files to EC2 instances.

- Connects to EC2 via SSH.
- Transfers the JAR file.
- Starts or restarts the Java application on the instance.

### 6. `mysql-backup.py`
💾 **Purpose**: Backup MySQL databases.

- Dumps the full database to a `.sql` file.
- Can be scheduled via cron or triggered manually.
- Supports local or remote DB backups.

### 7. `mysql_query_exec_bastion_secure.py`
🔐 **Purpose**: Execute secure MySQL queries through a bastion host.

- SSH tunneling to route queries through a secure bastion.
- Useful for environments where DBs are in private subnets.
- Prevents direct DB exposure over the internet.

---
