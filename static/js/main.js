// Data mobil contoh
const mobil = [
    {
        id: 1,
        merek: "Toyota",
        model: "Camry",
        tahun: 2022,
        harga: 28000,
        bbm: 32,
        jarak: 15000,
        keamanan: 8.5,
        gambar: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8"
    },
    {
        id: 2,
        merek: "Honda",
        model: "Civic",
        tahun: 2023,
        harga: 24000,
        bbm: 36,
        jarak: 5000,
        keamanan: 9.2,
        gambar: "https://images.unsplash.com/photo-1558981806-ec527fa84c39"
    },
    {
        id: 3,
        merek: "BMW",
        model: "3 Series",
        tahun: 2021,
        harga: 42000,
        bbm: 28,
        jarak: 18000,
        keamanan: 9.0,
        gambar: "https://images.unsplash.com/photo-1616788494707-ec28f08fd05a"
    }
];

// Tampilkan kartu mobil
function tampilkanMobil(data = mobil) {
    const container = document.getElementById("car-cards-container");
    if (!container) return;
    container.innerHTML = "";

    data.forEach((m) => {
        const card = document.createElement("div");
        card.className = "bg-white rounded-lg shadow-md overflow-hidden transition duration-300";
        card.innerHTML = `
      <img src="${m.gambar}" alt="${m.merek} ${m.model}" class="w-full h-48 object-cover">
      <div class="p-4">
        <h3 class="text-lg font-bold text-gray-900">${m.merek} ${m.model}</h3>
        <p class="text-sm text-gray-600 mb-2">${m.tahun}</p>
        <p class="text-sm text-gray-800">Harga: $${m.harga.toLocaleString()}</p>
        <p class="text-sm text-gray-800">Irit BBM: ${m.bbm} mpg</p>
        <p class="text-sm text-gray-800">Jarak Tempuh: ${m.jarak.toLocaleString()} km</p>
        <p class="text-sm text-gray-800">Keamanan: ${m.keamanan.toFixed(1)} / 10</p>
      </div>
    `;
        container.appendChild(card);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    tampilkanMobil();
    setupSliderEvents();
    setupPerhitunganWP();
});

// Update tampilan nilai slider
function setupSliderEvents() {
    const sliders = ["price", "year", "mpg", "mileage", "safety"];
    sliders.forEach((kriteria) => {
        const slider = document.getElementById(`${kriteria}-weight`);
        const value = document.getElementById(`${kriteria}-weight-value`);
        if (slider && value) {
            value.textContent = slider.value;
            slider.addEventListener("input", () => {
                value.textContent = slider.value;
                perbaruiChartKriteria();
            });
        }
    });
}

// Kalkulasi WP
function setupPerhitunganWP() {
    const tombolHitung = document.getElementById("calculate-ranking");
    if (!tombolHitung) return;

    tombolHitung.addEventListener("click", () => {
        const w = {
            harga: parseInt(document.getElementById("price-weight").value),
            tahun: parseInt(document.getElementById("year-weight").value),
            bbm: parseInt(document.getElementById("mpg-weight").value),
            jarak: parseInt(document.getElementById("mileage-weight").value),
            keamanan: parseInt(document.getElementById("safety-weight").value),
        };

        const total = Object.values(w).reduce((a, b) => a + b, 0);
        const bobot = {
            harga: w.harga / total,
            tahun: w.tahun / total,
            bbm: w.bbm / total,
            jarak: w.jarak / total,
            keamanan: w.keamanan / total,
        };

        const minHarga = Math.min(...mobil.map((m) => m.harga));
        const maxTahun = Math.max(...mobil.map((m) => m.tahun));
        const maxBBM = Math.max(...mobil.map((m) => m.bbm));
        const minJarak = Math.min(...mobil.map((m) => m.jarak));
        const maxKeamanan = 10;

        const skor = mobil.map((m) => {
            const nHarga = 1 - (m.harga - minHarga) / minHarga;
            const nTahun = (m.tahun - 2010) / (maxTahun - 2010);
            const nBBM = m.bbm / maxBBM;
            const nJarak = 1 - (m.jarak - minJarak) / 100000;
            const nKeamanan = m.keamanan / maxKeamanan;

            const Si =
                Math.pow(nHarga, bobot.harga) *
                Math.pow(nTahun, bobot.tahun) *
                Math.pow(nBBM, bobot.bbm) *
                Math.pow(nJarak, bobot.jarak) *
                Math.pow(nKeamanan, bobot.keamanan);

            return { ...m, Si };
        });

        const totalSi = skor.reduce((a, b) => a + b.Si, 0);
        const hasil = skor
            .map((m) => ({
                ...m,
                Vi: m.Si / totalSi,
            }))
            .sort((a, b) => b.Vi - a.Vi);

        tampilkanRanking(hasil);
    });
}

// Tampilkan hasil peringkat
function tampilkanRanking(data) {
    const container = document.getElementById("ranking-results");
    if (!container) return;
    container.innerHTML = "";

    data.forEach((m, i) => {
        const row = document.createElement("tr");
        row.innerHTML = `
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${i + 1}</td>
      <td class="px-6 py-4 whitespace-nowrap">
        <div class="flex items-center">
          <img src="${m.gambar}" class="h-10 w-10 rounded-full mr-2" alt="">
          <div>
            <div class="text-sm font-medium text-gray-900">${m.merek} ${m.model}</div>
            <div class="text-sm text-gray-500">${m.tahun}</div>
          </div>
        </div>
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
        <div class="w-full bg-gray-200 rounded-full h-2.5">
          <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${(m.Vi * 100).toFixed(2)}%"></div>
        </div>
        <span class="ml-2">${(m.Vi * 100).toFixed(2)}%</span>
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-blue-600">-</td>
    `;
        container.appendChild(row);
    });
}

// Chart bobot kriteria
let chart;
function perbaruiChartKriteria() {
    const ctx = document.getElementById("criteriaChart")?.getContext("2d");
    if (!ctx) return;

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Harga", "Tahun", "BBM", "Jarak", "Keamanan"],
            datasets: [
                {
                    data: [
                        parseInt(document.getElementById("price-weight").value),
                        parseInt(document.getElementById("year-weight").value),
                        parseInt(document.getElementById("mpg-weight").value),
                        parseInt(document.getElementById("mileage-weight").value),
                        parseInt(document.getElementById("safety-weight").value)
                    ],
                    backgroundColor: [
                        "rgba(59, 130, 246, 0.7)",
                        "rgba(16, 185, 129, 0.7)",
                        "rgba(245, 158, 11, 0.7)",
                        "rgba(239, 68, 68, 0.7)",
                        "rgba(139, 92, 246, 0.7)"
                    ],
                    borderColor: [
                        "rgba(59, 130, 246, 1)",
                        "rgba(16, 185, 129, 1)",
                        "rgba(245, 158, 11, 1)",
                        "rgba(239, 68, 68, 1)",
                        "rgba(139, 92, 246, 1)"
                    ],
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}
// Export ke PDF
document.getElementById("export-pdf")?.addEventListener("click", () => {
    const doc = new jspdf.jsPDF();
    doc.text("Laporan Peringkat Mobil - AutoSelect", 14, 14);
    doc.autoTable({
        startY: 20,
        head: [["Peringkat", "Merek", "Model", "Tahun", "Nilai WP"]],
        body: mobilRanking.map((m, i) => [
            i + 1,
            m.merek,
            m.model,
            m.tahun,
            `${(m.Vi * 100).toFixed(2)}%`,
        ]),
    });
    doc.save("peringkat-mobil.pdf");
});

// Export ke Excel
document.getElementById("export-excel")?.addEventListener("click", () => {
    const rows = mobilRanking.map((m, i) => ({
        Peringkat: i + 1,
        Merek: m.merek,
        Model: m.model,
        Tahun: m.tahun,
        "Nilai WP": `${(m.Vi * 100).toFixed(2)}%`,
    }));

    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Peringkat Mobil");

    XLSX.writeFile(workbook, "peringkat-mobil.xlsx");
});
