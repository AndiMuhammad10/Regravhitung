import streamlit as st

# Data tabel periodik sederhana (simbol: massa atom relatif)
periodic_table = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.011,
    "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180, "Na": 22.990, "Mg": 24.305,
    "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948,
    "K": 39.098, "Ca": 40.078, "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996,
    "Mn": 54.938, "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971, "Br": 79.904, "Kr": 83.798,
    "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.224, "Nb": 92.906, "Mo": 95.95,
    "Ag": 107.868, "Cd": 112.414, "Sn": 118.710, "Sb": 121.760, "Te": 127.60,
    "I": 126.904, "Ba": 137.327, "Pt": 195.084, "Au": 196.967, "Hg": 200.592,
    "Pb": 207.2
}

# Fungsi untuk menghitung massa molar dari rumus kimia
import re
def molar_mass(formula):
    pattern = r"([A-Z][a-z]?)(\d*)"
    mass = 0.0
    for (element, count) in re.findall(pattern, formula):
        count = int(count) if count else 1
        if element in periodic_table:
            mass += periodic_table[element] * count
        else:
            raise ValueError(f"Unsur {element} tidak ditemukan di tabel periodik.")
    return mass

# Judul aplikasi
st.title("Kalkulator Gravimetri")

# Input data
W0 = st.number_input("Berat Sampel (W₀) [g]", min_value=0.0, format="%.6f")
W1 = st.number_input("Berat Endapan (W₁) [g]", min_value=0.0, format="%.6f")
compound = st.text_input("Senyawa Endapan (misal: BaCrO4)")
target_element = st.text_input("Unsur yang Dicari (misal: Ba)")

if st.button("Calculate"):
    try:
        Mr_compound = molar_mass(compound)
        Mr_target = periodic_table[target_element]

        GF = Mr_target / Mr_compound
        percent_kadar = (W1 * GF / W0) * 100

        # Output hasil
        st.subheader("Hasil Perhitungan")
        st.write(f"**Massa molar senyawa endapan ({compound})** = {Mr_compound:.4f} g/mol")
        st.write(f"**Massa molar unsur target ({target_element})** = {Mr_target:.4f} g/mol")
        st.write(f"**Faktor Gravimetri (GF)** = {GF:.6f}")
        st.write(f"**% Kadar {target_element}** = {percent_kadar:.4f} %")

        # Langkah perhitungan
        st.subheader("Langkah Perhitungan")
        st.markdown(f"""
        1. Hitung massa molar senyawa endapan:
           \n   Mr({compound}) = {Mr_compound:.4f} g/mol
        2. Hitung massa molar unsur yang dicari:
           \n   Mr({target_element}) = {Mr_target:.4f} g/mol
        3. Hitung Faktor Gravimetri (GF):
           \n   GF = Mr({target_element}) / Mr({compound})  
           \n   GF = {Mr_target:.4f} / {Mr_compound:.4f} = {GF:.6f}
        4. Hitung kadar (%):
           \n   % Kadar = (W₁ × GF / W₀) × 100
           \n   % Kadar = ({W1} × {GF:.6f} / {W0}) × 100 = {percent_kadar:.4f} %
        """)
    except ValueError as e:
        st.error(str(e))
