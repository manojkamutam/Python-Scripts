import boto3
import time
import logging

# Configure logging
logging.basicConfig(filename="ecs_update.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize ECS client
ecs_client = boto3.client("ecs", region_name="us-east-1")  # Change region accordingly

def get_current_task_count(cluster_name, service_name):
    """Fetch the current desired count of tasks for a service."""
    try:
        response = ecs_client.describe_services(cluster=cluster_name, services=[service_name])
        tasks_count = response['services'][0]['desiredCount']
        logging.info(f"Current task count for {service_name}: {tasks_count}")
        return tasks_count
    except Exception as e:
        logging.error(f"Failed to fetch task count: {e}")
        return None

def update_task_count(cluster_name, service_name, new_count):
    """Update the task count of a service."""
    try:
        ecs_client.update_service(cluster=cluster_name, service=service_name, desiredCount=new_count)
        logging.info(f"Updated task count for {service_name} to {new_count}")
    except Exception as e:
        logging.error(f"Failed to update task count: {e}")

def main(cluster_name, service_name, new_count):
    """Main function to update and verify task count."""
    print("Fetching current task count...")
    current_count = get_current_task_count(cluster_name, service_name)
    if current_count is None:
        print("Failed to fetch current task count. Exiting.")
        return
    
    print(f"Updating task count to {new_count}...")
    update_task_count(cluster_name, service_name, new_count)
    
    print("Waiting for 2 minutes before verifying...")
    time.sleep(120)
    
    print("Fetching updated task count...")
    updated_count = get_current_task_count(cluster_name, service_name)
    print(f"Updated Task Count: {updated_count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update ECS Task Count")
    parser.add_argument("--cluster", required=True, help="ECS Cluster Name")
    parser.add_argument("--service", required=True, help="ECS Service Name")
    parser.add_argument("--count", type=int, required=True, help="New Task Count")
    
    args = parser.parse_args()
    main(args.cluster, args.service, args.count)
