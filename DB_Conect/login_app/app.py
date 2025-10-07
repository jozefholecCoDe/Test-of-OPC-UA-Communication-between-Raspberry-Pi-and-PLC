from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "my-awesome-secret"

#@app.route('/')
#def home():
    #return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ''

    if request.method == 'POST':    
        Name = request.form['username']
        Password = request.form['password']

        try:
            db = mysql.connector.connect(
                host="localhost",
                user="SafeControl",
                password="SafeControl2523",
                database="skuska"
            )
            if db.is_connected():
                print("✅ Connected to MySQL on login.")

            cursor = db.cursor()
            query = "SELECT COUNT(*) FROM users WHERE Name=%s AND Password=%s"
            cursor.execute(query, (Name, Password))
            result = cursor.fetchone()
            print("Username:", Name)
            print("Password:", Password)
            print("Query result:", result)

            if result and result[0] == 1:
                # ✅ Get role BEFORE closing cursor
                cursor.execute("SELECT Role FROM users WHERE Name = %s", (Name,))
                role = cursor.fetchone()[0]

                session['username'] = Name
                session['role'] = role

                cursor.close()
                db.close()
                print("🔌 MySQL connection closed.")

                if role == 1:
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('welcome'))
            else:
                message = "❌ Invalid credentials."

            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            print("❌ Database error:", err)
            message = "❌ Database connection failed."

    return render_template('login.html', message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role')  # 🆕 get role from form

        try:
            db = mysql.connector.connect(
                host="localhost",
                user="SafeControl",
                password="SafeControl2523",
                database="skuska"
            )

            cursor = db.cursor()
            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE Name = %s", (username,))
            result = cursor.fetchone()

            if result[0] > 0:
                message = "❌ Username already exists."
            else:
                # Insert user with role
                cursor.execute(
                    "INSERT INTO users (Name, Password, Role) VALUES (%s, %s, %s)",
                    (username, password, role)
                )
                db.commit()
                message = "✅ Account created. You can now log in!"
                cursor.close()
                db.close()
                #return render_template('login.html', message=message)

        except mysql.connector.Error as err:
            print("❌ Database error:", err)
            message = "❌ Registration failed."

    return render_template('register.html', message=message)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session or session.get('role') != 1:
        return redirect(url_for('login'))

    db = mysql.connector.connect(
        host="localhost",
        user="SafeControl",
        password="SafeControl2523",
        database="skuska"
    )
    cursor = db.cursor(dictionary=True)

    # Get all users
    cursor.execute("SELECT Name, Role FROM users")
    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin.html", users=users)

@app.route('/admin/register', methods=['POST'])
def admin_register():
    if 'username' not in session or session.get('role') != 1:
        return redirect(url_for('login'))

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    db = mysql.connector.connect(
        host="localhost",
        user="SafeControl",
        password="SafeControl2523",
        database="skuska"
    )
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (Name, Password, Role) VALUES (%s, %s, %s)", (username, password, role))
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin'))

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    if 'username' not in session or session.get('role') != 1:
        return redirect(url_for('login'))

    user_to_delete = request.form['username']
    if user_to_delete != session['username']:  # prevent deleting yourself
        db = mysql.connector.connect(
            host="localhost",
            user="SafeControl",
            password="SafeControl2523",
            database="skuska"
        )
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE Name = %s", (user_to_delete,))
        db.commit()
        cursor.close()
        db.close()

    return redirect(url_for('admin'))

    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/welcome')
def welcome():

    # Check if logged-in user is an Admin
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="SafeControl",
            password="SafeControl2523",
            database="skuska"
        )

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT Role FROM users WHERE Name = %s", (session['username'],))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        print("❌ Error:", err)
        return "❌ Failed to load admin panel"
    
    return render_template('welcome.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
