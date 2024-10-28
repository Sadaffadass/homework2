from flask import Flask, request, send_from_directory, redirect, send_from_directory, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='44245989Sf',
            database='homework_2'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Home route
@app.route('/')
def index():
    return send_from_directory('.','index.html')

# Route to create a new purchase order
@app.route('/create', methods=['GET', 'POST'])
def create_po():
    if request.method == 'POST':
        po_num = request.form['po_num']
        req_num = request.form['req_num']
        total_amt = request.form['total_amt']

        connection = connect_to_db()
        if connection is None:
            flash("Database connection failed.")
            return redirect(url_for('index'))

        cursor = connection.cursor()
        try:
            # Insert new purchase order
            cursor.execute(
                "INSERT INTO Purchase_Orders (`PURCHASE_ORDER_NUMBER`, `REQUISITION_NUMBER`, `TOTAL_AMOUNT`) "
                "VALUES (%s, %s, %s)", (po_num, req_num, total_amt)
            )
            connection.commit()
            flash("Purchase Order created successfully.")
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('index'))

    return send_from_directory('.','create_po.html')

# Route to search for purchase orders
@app.route('/search_po', methods=['GET'])
def search_po():
    # Retrieve search parameters
    po_num = request.args.get('po_num')
    zip_code = request.args.get('zip_code')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vendor_num = request.args.get('vendor_num')
    dept_num = request.args.get('dept_num')
    min_cost = request.args.get('min_cost')
    max_cost = request.args.get('max_cost')

    # Base query
    query = """
        SELECT po.*, d.file_location
        FROM Purchase_Orders po
        LEFT JOIN Documents d ON po.purchase_order_number = d.Purchase_Order_Number
        WHERE 1=1
    """
    params = []

    # Apply filters based on available input
    if po_num:
        query += " AND po.purchase_order_number = %s"
        params.append(po_num)
    if zip_code:
        query += " AND po.zip_code = %s"
        params.append(zip_code)
    if start_date and end_date:
        query += " AND po.input_date BETWEEN %s AND %s"
        params.append(start_date)
        params.append(end_date)
    if vendor_num:
        query += " AND po.vendor_number = %s"
        params.append(vendor_num)
    if dept_num:
        query += " AND po.department_number = %s"
        params.append(dept_num)
    if min_cost:
        query += " AND po.total_amount >= %s"
        params.append(min_cost)
    if max_cost:
        query += " AND po.total_amount <= %s"
        params.append(max_cost)

    # Execute query
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    print("Current Directory:", os.getcwd())  # Print the current directory
    print("Files:", os.listdir("."))  # Print all files in the root directory
    return send_from_directory('static', 'search_po.html')

# Route to update a purchase order
@app.route('/update/<po_num>', methods=['GET', 'POST'])
def update_po(po_num):
    connection = connect_to_db()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('index'))

    cursor = connection.cursor()

    if request.method == 'POST':
        # Retrieve updated form data
        req_num = request.form['req_num']
        total_amt = request.form['total_amt']
        dept_num = request.form['dept_num']
        vendor_num = request.form['vendor_num']
        cost_center_num = request.form['cost_center_num']
        type_code = request.form['type_code']
        category_code = request.form['category_code']
        status_code = request.form['status_code']
        vouched_amt = request.form['vouched_amt']
        total_items = request.form['total_items']
        po_balance = request.form['po_balance']
        input_date = request.form['input_date']

        try:
            # Update query for the specific purchase order
            cursor.execute("""
                UPDATE Purchase_Orders
                SET REQUISITION_NUMBER = %s, TOTAL_AMOUNT = %s, DEPARTMENT_NUMBER = %s, VENDOR_NUMBER = %s,
                    COST_CENTER_NUMBER = %s, TYPE_CODE = %s, CATEGORY_CODE = %s, STATUS_CODE = %s,
                    VOUCHED_AMOUNT = %s, TOTAL_ITEMS = %s, PO_BALANCE = %s, INPUT_DATE = %s
                WHERE PURCHASE_ORDER_NUMBER = %s
            """, (req_num, total_amt, dept_num, vendor_num, cost_center_num, type_code, category_code,
                  status_code, vouched_amt, total_items, po_balance, input_date, po_num))
            connection.commit()
            flash("Purchase Order updated successfully.")
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('search_po'))

    # Fetch current order data for the update form
    cursor.execute("SELECT * FROM Purchase_Orders WHERE PURCHASE_ORDER_NUMBER = %s", (po_num,))
    order = cursor.fetchone()
    cursor.close()
    connection.close()

    if order is None:
        flash("Purchase Order not found.")
        return redirect(url_for('search_po'))

    return send_from_directory('.','update_po.html', order=order)
# Route to delete a purchase order

@app.route('/delete/<po_num>', methods=['POST'])
def delete_po(po_num):
    connection = connect_to_db()
    if connection is None:
        flash("Database connection failed.")
        return redirect(url_for('search_po'))

    cursor = connection.cursor()

    try:
        # Delete query for the specified purchase order
        cursor.execute("DELETE FROM Purchase_Orders WHERE PURCHASE_ORDER_NUMBER = %s", (po_num,))
        connection.commit()
        flash("Purchase Order deleted successfully.")
    except mysql.connector.Error as err:
        flash(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('search_po'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

