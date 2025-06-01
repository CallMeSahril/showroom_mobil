from datetime import datetime
import pdfkit
from flask import request, redirect, url_for, flash
from flask import Blueprint, render_template
from controllers.mobil_controller import MobilController

mobil_bp = Blueprint('mobil', __name__)
controller = MobilController()


@mobil_bp.route("/mobil")
def index():
    model = request.args.get("model")
    tahun = request.args.get("tahun")
    kondisi = request.args.get("kondisi")
    merek = request.args.get("merek")
    data = controller.list_mobil_filtered(model, tahun, kondisi, merek)

    return render_template("mobil/list.html", data=data)


@mobil_bp.route("/mobil/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "POST":
        form = request.form
        controller.tambah_mobil(form)
        flash("Data mobil berhasil ditambahkan", "success")
        return redirect(url_for("mobil.index"))
    return render_template("mobil/form.html")


@mobil_bp.route("/mobil/export/pdf")
def export_pdf():
    from flask import make_response
    from models.mobil_model import MobilModel

    model = MobilModel()
    data = model.get_all()
    tanggal = datetime.now().strftime('%d-%m-%Y')

    html = render_template("mobil/pdf_template.html",
                           data=data, tanggal=tanggal)

    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pdf = pdfkit.from_string(html, False, configuration=config)
    response = make_response(pdf)
    response.headers["Content-Disposition"] = "attachment; filename=laporan_mobil.pdf"
    response.headers["Content-Type"] = "application/pdf"
    return response


@mobil_bp.route("/mobil/perhitungan/wp", methods=["GET"])
def perhitungan_wp():
    from models.mobil_model import MobilModel
    from datetime import datetime

    model = MobilModel()
    data = model.get_all()
    skenario_id = request.args.get("skenario_id", 1, type=int)

    # Ambil daftar semua skenario untuk dropdown
    skenario_list = model.get_all_skenario()
    skenario = model.get_skenario_by_id(skenario_id)

    if not skenario:
        flash("Skenario tidak ditemukan", "danger")
        return redirect(url_for("mobil.index"))

    bobot_wp = {
        "harga": skenario[2],
        "tahun": skenario[3],
        "km": skenario[4],
        "bbm": skenario[5],
        "kondisi": skenario[6],
        "pajak": skenario[7],
    }

    jenis_kriteria = {
        "harga": "cost",
        "tahun": "benefit",
        "km": "cost",
        "bbm": "benefit",
        "kondisi": "benefit",
        "pajak": "cost"
    }

    total_bobot = sum(bobot_wp.values())
    for k in bobot_wp:
        bobot_wp[k] = bobot_wp[k] / total_bobot

    alternatif = []
    transmisi_mapping = {"Manual": 0, "Automatic": 1}

    for m in data:
        print("DATA:", m)

        nilai = {
            "kode": m[0],
            "merek": m[1],
            "model": m[2],
            "harga": float(m[6]),
            "tahun": float(m[5]),
            "km": float(m[7]),
            "bbm": float(m[9]),
            'kondisi': float(0.1),
            # "kondisi": float(m[10]),
            "pajak": float(m[11])
        }

        S = 1
        for k, w in bobot_wp.items():
            val = nilai[k]
            S *= val ** (-w) if jenis_kriteria[k] == "cost" else val ** w

        nilai["skor"] = round(S, 6)
        alternatif.append(nilai)

    total_skor = sum(a["skor"] for a in alternatif)
    for a in alternatif:
        a["nilai"] = round(a["skor"] / total_skor, 6)

    alternatif.sort(key=lambda x: x["nilai"], reverse=True)

    return render_template("mobil/perhitungan/wp.html",
                           alternatif=alternatif,
                           skenario_list=skenario_list,
                           skenario_aktif=skenario)
