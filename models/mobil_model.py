from db import mysql


class MobilModel:
    def get_all(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mobil")
        result = cur.fetchall()
        cur.close()
        return result

    def insert(self, data):
        cur = mysql.connection.cursor()
        sql = """
                INSERT INTO mobil (kode, merek, model, kapasitas_mesin, kapasitas_penumpang,
                tahun, harga, km, bbm, kondisi, transmisi, pajak)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        values = (
            data['kode'], data['merek'], data['model'], data['kapasitas_mesin'], data['kapasitas_penumpang'],
            data['tahun'], data['harga'], data['km'], data['bbm'], data['kondisi'], data['transmisi'], data['pajak']
        )
        cur.execute(sql, values)
        mysql.connection.commit()
        cur.close()

    def get_filtered(self, model, tahun, kondisi, merek):
        cur = mysql.connection.cursor()

        sql = "SELECT * FROM mobil WHERE 1=1"
        params = []

        if model:
            sql += " AND model LIKE %s"
            params.append(f"%{model}%")
        if tahun:
            sql += " AND tahun = %s"
            params.append(tahun)
        if kondisi:
            sql += " AND kondisi = %s"
            params.append(kondisi)
        if merek:
            sql += " AND merek = %s"
            params.append(merek)
        cur.execute(sql, tuple(params))
        result = cur.fetchall()
        cur.close()
        return result

    def get_all_skenario(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nama_skenario FROM skenario_bobot")
        result = cur.fetchall()
        cur.close()
        return result

    def get_skenario_by_id(self, skenario_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM skenario_bobot WHERE id = %s",
                    (skenario_id,))
        result = cur.fetchone()
        cur.close()
        return result

    def count_mobil(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM mobil")
        result = cur.fetchone()[0]
        cur.close()
        return result

    def total_harga(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT SUM(harga) FROM mobil")
        result = cur.fetchone()[0]
        cur.close()
        return result or 0

    def rata_rata_tahun(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT AVG(tahun) FROM mobil")
        result = cur.fetchone()[0]
        cur.close()
        return round(result) if result else 0

    def get_jumlah_mobil_per_tahun(self):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT tahun, COUNT(*) AS jumlah
            FROM mobil
            GROUP BY tahun
            ORDER BY tahun
        """)
        result = cur.fetchall()
        cur.close()
        return result


def proses_wp(self, skenario_bobot):
    data = self.get_all()

    # Ambil semua nilai per kriteria
    harga = [d['harga'] for d in data]
    tahun = [d['tahun'] for d in data]
    km = [d['km'] for d in data]
    bbm = [d['bbm'] for d in data]
    kondisi = [d['kondisi'] for d in data]
    pajak = [d['pajak'] for d in data]

    # Normalisasi: benefit dan cost
    def normalize(arr, benefit=True):
        arr = [float(v) for v in arr]
        if benefit:
            max_val = max(arr)
            return [v / max_val for v in arr]
        else:
            min_val = min(arr)
            return [min_val / v for v in arr]

    norm_harga = normalize(harga, benefit=False)
    norm_tahun = normalize(tahun, benefit=True)
    norm_km = normalize(km, benefit=False)
    norm_bbm = normalize(bbm, benefit=True)
    norm_kondisi = normalize(kondisi, benefit=True)
    norm_pajak = normalize(pajak, benefit=True)

    # Hitung WP
    hasil = []
    for i, d in enumerate(data):
        skor = (
            norm_harga[i] ** skenario_bobot['harga'] *
            norm_tahun[i] ** skenario_bobot['tahun'] *
            norm_km[i] ** skenario_bobot['km'] *
            norm_bbm[i] ** skenario_bobot['bbm'] *
            norm_kondisi[i] ** skenario_bobot['kondisi'] *
            norm_pajak[i] ** skenario_bobot['pajak']
        )
        hasil.append({
            "kode": d['kode'],
            "merek": d['merek'],
            "model": d['model'],
            "skor": round(skor, 6)
        })
    return sorted(hasil, key=lambda x: x['skor'], reverse=True)
