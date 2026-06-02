from flask import Flask, render_template, request, redirect, send_file
import io

app = Flask(__name__)

history = []
last_result = []

# FORMAT FUNCTION (REMOVE .00)
def format_money(x):
    if x == int(x):
        return int(x)
    return round(x, 2)


@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "acc_admin" and request.form['password'] == "2639":
            return redirect('/main')
        else:
            return "Invalid Login"
    return render_template('login.html')


@app.route('/main')
def main():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    global last_result

    names = request.form.getlist('names')
    amounts = list(map(float, request.form.getlist('amounts')))

    total = sum(amounts)
    share = total / len(names)

    expenses = dict(zip(names, amounts))

    debtors = []
    creditors = []

    for person in names:
        balance = expenses[person] - share
        if balance < 0:
            debtors.append([person, abs(balance)])
        else:
            creditors.append([person, balance])

    transactions = []

    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        d_name, d_amt = debtors[i]
        c_name, c_amt = creditors[j]

        pay = min(d_amt, c_amt)

        transactions.append(
            f"💸 {d_name.capitalize()} → ₹{format_money(pay)} → {c_name.capitalize()}"
        )

        debtors[i][1] -= pay
        creditors[j][1] -= pay

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    last_result = transactions

    history.append({
        "total": format_money(total),
        "share": format_money(share),
        "transactions": transactions
    })

    return render_template('result.html',
                           total=format_money(total),
                           share=format_money(share),
                           transactions=transactions,
                           history=history)


@app.route('/download')
def download():
    content = "\n".join(last_result)
    return send_file(
        io.BytesIO(content.encode()),
        as_attachment=True,
        download_name="report.txt",
        mimetype='text/plain'
    )


if __name__ == '__main__':
    app.run(debug=True)