from models.mobil_model import MobilModel


class MobilController:
    def __init__(self):
        self.model = MobilModel()

    def list_mobil(self):
        return self.model.get_all()

    def tambah_mobil(self, form):
        return self.model.insert({
            "kode": form['kode'],
            "merek": form['merek'],
            "model": form['model'],
            "kapasitas_mesin": form['kapasitas_mesin'],
            "kapasitas_penumpang": form['kapasitas_penumpang'],
            "tahun": form['tahun'],
            "harga": form['harga'],
            "km": form['km'],
            "bbm": form['bbm'],
            "kondisi": form['kondisi'],
            "transmisi": form['transmisi'],
            "pajak": form['pajak'],
        })

    def list_mobil_filtered(self, model=None, tahun=None, kondisi=None, merek=None):
        return self.model.get_filtered(model, tahun, kondisi, merek)

   