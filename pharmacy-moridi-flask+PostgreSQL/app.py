from flask import Flask, render_template, request, redirect, url_for, jsonify
from peewee import fn
from model import db, init_db, Medicine, Sale

app = Flask(__name__)


@app.before_request
def _connect():
    if db.is_closed():
        db.connect(reuse_if_open=True)


@app.teardown_appcontext
def _close(exc):
    if not db.is_closed():
        db.close()


@app.route("/")
def index():
    medicines = list(Medicine.select().order_by(Medicine.name))
    sales = list(
        Sale.select(Sale, Medicine).join(Medicine)
            .order_by(Sale.sold_at.desc()).limit(20)
    )
    return render_template("index.html", medicines=medicines, sales=sales)


@app.route("/medicines", methods=["POST"])
def add_medicine():
    name  = request.form.get("name", "").strip()
    price = request.form.get("price", type=int)
    stock = request.form.get("stock", type=int) or 0
    if name and price is not None:
        Medicine.create(name=name, price=price, stock=stock)
    return redirect(url_for("index"))


@app.route("/sell/<int:medicine_id>", methods=["POST"])
def sell(medicine_id: int):
    qty = request.form.get("qty", type=int) or 1
    with db.atomic():
        med = Medicine.get_or_none(Medicine.id == medicine_id)
        if med is None:
            return "دارو یافت نشد", 404
        if med.stock < qty:
            return f"موجودی کافی نیست (موجودی: {med.stock})", 400
        med.stock -= qty
        med.save()
        Sale.create(medicine=med, quantity=qty, total=med.price * qty)
    return redirect(url_for("index"))


@app.route("/api/medicines")
def api_medicines():
    return jsonify([
        {"id": m.id, "name": m.name, "price": m.price, "stock": m.stock}
        for m in Medicine.select()
    ])


@app.route("/api/sales")
def api_sales():
    return jsonify([
        {"medicine": s.medicine.name, "quantity": s.quantity,
         "total": s.total, "sold_at": s.sold_at.isoformat(timespec="seconds")}
        for s in Sale.select(Sale, Medicine).join(Medicine)
                     .order_by(Sale.sold_at.desc()).limit(50)
    ])


@app.route("/api/revenue")
def api_revenue():
    return jsonify({"total_revenue": Sale.select(fn.SUM(Sale.total)).scalar() or 0})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)