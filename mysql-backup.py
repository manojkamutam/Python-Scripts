import os
import subprocess
import shutil
import datetime
import glob

# MySQL credentials
DB_HOST = "localhost"
DB_USER = "your_user"
DB_PASSWORD = "your_password"
BACKUP_DIR = "/path/to/backup"

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def get_database_list():
    """Fetch list of all databases except system databases."""
    cmd = f"mysql -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} -e 'SHOW DATABASES;'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    databases = result.stdout.split("\n")[1:]
    return [db for db in databases if db.strip() and db not in ("information_schema", "performance_schema", "mysql", "sys")]

def backup_database(db_name):
    """Take a backup of a given database including routines."""
    backup_file = os.path.join(BACKUP_DIR, f"{db_name}.sql")
    cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} -R {db_name} > {backup_file}"
    subprocess.run(cmd, shell=True)
    return backup_file

def zip_backups():
    """Compress all backups into a zip file named with the current date."""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    zip_filename = os.path.join(BACKUP_DIR, f"backup_{date_str}.zip")
    shutil.make_archive(zip_filename.replace(".zip", ""), 'zip', BACKUP_DIR)
    # Remove individual .sql files after zipping
    for sql_file in glob.glob(os.path.join(BACKUP_DIR, "*.sql")):
        os.remove(sql_file)

def clean_old_backups():
    """Remove backup zip files older than 15 days."""
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=15)
    for file in glob.glob(os.path.join(BACKUP_DIR, "backup_*.zip")):
        file_date_str = file.split("backup_")[-1].split(".zip")[0]
        try:
            file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d")
            if file_date < cutoff_date:
                os.remove(file)
        except ValueError:
            continue

def main():
    databases = get_database_list()
    print("Databases to backup:", databases)
    for db in databases:
        print(f"Backing up: {db}")
        backup_database(db)
    zip_backups()
    clean_old_backups()
    print("Backup process completed!")

if __name__ == "__main__":
    main()
