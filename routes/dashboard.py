from flask import Blueprint, render_template
from models.mobil_model import MobilModel

dashboard_bp = Blueprint('dashboard_bp', __name__)


@dashboard_bp.route("/")
def dashboard():
    mobil_model = MobilModel()
    jumlah = mobil_model.count_mobil()
    total = mobil_model.total_harga()
    rata_tahun = mobil_model.rata_rata_tahun()
    chart_data = mobil_model.get_jumlah_mobil_per_tahun()

    tahun = [str(row[0]) for row in chart_data]
    jumlah_chart = [row[1] for row in chart_data]

    return render_template("dashboard.html",
                           jumlah_mobil=jumlah,
                           total_harga=total,
                           rata_tahun=rata_tahun,
                           tahun_chart=tahun,
                           jumlah_chart=jumlah_chart)
