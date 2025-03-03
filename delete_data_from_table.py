from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "your_user",
    "password": "your_password",
    "database": "your_database"
}

def delete_table_data(table_name):
    """Deletes all data from the specified table."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"All data from table '{table_name}' deleted successfully."}
    except Exception as e:
        return {"error": str(e)}

@app.route("/delete", methods=["POST"])
def delete_data():
    """API endpoint to delete all data from a table."""
    data = request.get_json()
    table_name = data.get("table_name")
    if not table_name:
        return jsonify({"error": "Missing table_name parameter."}), 400
    response = delete_table_data(table_name)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
