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

    model = MobilModel()
    skenario_id = request.args.get("skenario_id", 1, type=int)
    merek = request.args.get("merek", "")  # ✅ tambahkan ini

    # Ambil daftar semua skenario untuk dropdown
    skenario_list = model.get_all_skenario()
    skenario = model.get_skenario_by_id(skenario_id)

    if not skenario:
        flash("Skenario tidak ditemukan", "danger")
        return redirect(url_for("mobil.index"))

    # Buat bobot dari hasil DB
    bobot_wp = {
        "harga": skenario[2],
        "tahun": skenario[3],
        "km": skenario[4],
        "bbm": skenario[5],
        "kondisi": skenario[6],
        "pajak": skenario[7],
    }

    # Normalisasi bobot
    total_bobot = sum(bobot_wp.values())
    for k in bobot_wp:
        bobot_wp[k] = bobot_wp[k] / total_bobot

    hasil = model.proses_wp(bobot_wp, merek_filter=merek)

    return render_template("mobil/perhitungan/wp.html",
                           alternatif=hasil,
                           skenario_list=skenario_list,
                           skenario_aktif=skenario,
                           merek=merek)  # ✅ agar form merek tetap tampil


@mobil_bp.route("/mobil/perhitungan/wp/pdf")
def export_wp_pdf():
    from flask import make_response
    from models.mobil_model import MobilModel

    skenario_id = request.args.get("skenario_id", 1, type=int)
    merek = request.args.get("merek", "")

    model = MobilModel()
    skenario = model.get_skenario_by_id(skenario_id)
    skenario_list = model.get_all_skenario()

    if not skenario:
        flash("Skenario tidak ditemukan", "danger")
        return redirect(url_for("mobil.index"))

    # Hitung bobot
    bobot_wp = {
        "harga": skenario[2],
        "tahun": skenario[3],
        "km": skenario[4],
        "bbm": skenario[5],
        "kondisi": skenario[6],
        "pajak": skenario[7],
    }
    total_bobot = sum(bobot_wp.values())
    for k in bobot_wp:
        bobot_wp[k] /= total_bobot

    hasil = model.proses_wp(bobot_wp, merek_filter=merek)
    tanggal = datetime.now().strftime('%d-%m-%Y')

    # Render template PDF
    html = render_template("mobil/pdf_wp_template.html",
                           alternatif=hasil,
                           skenario=skenario,
                           tanggal=tanggal,
                           merek=merek)

    # Konversi ke PDF
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(html, False, configuration=config)

    response = make_response(pdf)
    response.headers["Content-Disposition"] = "attachment; filename=perhitungan_wp.pdf"
    response.headers["Content-Type"] = "application/pdf"
    return response
