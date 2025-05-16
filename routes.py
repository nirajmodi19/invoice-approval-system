from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from excel_manager import validate_user, get_user, get_invoices_for_role, add_invoice, update_invoice_status, add_approval_record, get_approval_logs
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change to a strong secret in prod

UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user(username, password):
            user = get_user(username)
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Placeholder for dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    role = session['role']

    if request.method == 'POST':
        # Handle raising invoice (only for Manager)
        if role == 'Manager':
            description = request.form.get('description')
            amount = request.form.get('amount')
            file = request.files.get('file')
            file_path = None
            if file and file.filename:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
            if description and amount:
                add_invoice(description, amount, username, file_path)
                flash('Invoice raised successfully!', 'success')
            else:
                flash('Description and Amount are required!', 'danger')

        # Handle approving/rejecting invoices (Accounts or CEO)
        if role in ['Accounts', 'CEO']:
            invoice_id = int(request.form.get('invoice_id'))
            action = request.form.get('action')
            if action == 'approve':
                status = 'Approved by Accounts' if role == 'Accounts' else 'Approved by CEO'
            else:
                status = f'Rejected by {role}'

            update_invoice_status(invoice_id, status, role)
            add_approval_record(invoice_id, role, status)
            flash(f'Invoice {invoice_id} has been {status.lower()}!', 'success')

    # Fetch invoices based on role
    invoices = get_invoices_for_role(role, username)

    for invoice in invoices:
        invoice['logs'] = get_approval_logs(invoice['id'])

    return render_template('dashboard.html', role=role, invoices=invoices)

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
