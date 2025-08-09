import streamlit as st
import re
from collections import defaultdict

st.set_page_config(page_title="Kalkulator Gravimetri (Streamlit)", layout="centered")

# === CSS Background Gradasi Bergerak ===
page_bg = """
<style>
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.stApp {
    background: linear-gradient(-45deg, #d6b3ff, #ffffff, #cdb4db, #f8f8f8);
    background-size: 400% 400%;
    animation: gradient 20s ease infinite;
}

/* Bikin konten transparan biar gradasi keliatan */
[data-testid="stAppViewContainer"] {
    background: transparent;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    right: 2rem;
}

/* Bayangan teks */
h1, h2, h3, h4, h5, h6, p, span, div {
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# === Tabel periodik ===
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

# === Fungsi parsing rumus kimia ===
def parse_formula(formula: str) -> dict:
    tokens = re.findall(r'([A-Z][a-z]?|\(|\)|\d+)', formula)
    stack = [defaultdict(int)]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == '(':
            stack.append(defaultdict(int))
            i += 1
        elif tok == ')':
            i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i])
                i += 1
            group = stack.pop()
            for el, cnt in group.items():
                stack[-1][el] += cnt * mult
        elif re.match(r'[A-Z][a-z]?$', tok):
            el = tok
            cnt = 1
            i += 1
            if i < len(tokens) and tokens[i].isdigit():
                cnt = int(tokens[i])
                i += 1
            stack[-1][el] += cnt
        else:
            i += 1
    return dict(stack[-1])

def molar_mass_from_formula(formula: str) -> float:
    counts = parse_formula(formula)
    mass = 0.0
    for el, cnt in counts.items():
        if el not in periodic_table:
            raise ValueError(f"Unsur '{el}' tidak ditemukan di tabel periodik internal.")
        mass += periodic_table[el] * cnt
    return mass

# === UI ===
st.title("Kalkulator Gravimetri")
st.write("Silahkan masukkan data mas bro 😎")

with st.form(key='grav_form'):
    st.subheader("Input data")
    W0 = st.number_input("W0 (g) — berat filter/timbang sebelum (tare)", min_value=0.0, format="%.6f", value=0.0000)
    W1 = st.number_input("W1 (g) — berat filter/timbang setelah endapan", min_value=0.0, format="%.6f", value=0.0000)
    volume_ml = st.number_input("Volume sampel (mL)", min_value=0.0, format="%.6f", value=1.0000)
    compound = st.text_input("Senyawa endapan (contoh: BaCrO4)", value="BaCrO4")
    target_element = st.text_input("Unsur yang dicari (contoh: Ba)", value="Ba")

    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        if volume_ml <= 0:
            st.error("Volume sampel harus > 0 mL.")
        else:
            counts = parse_formula(compound)
            Mr_compound = molar_mass_from_formula(compound)
            target_count = counts.get(target_element, 0)
            if target_element not in periodic_table:
                st.error(f"Simbol unsur '{target_element}' tidak ada di tabel periodik internal.")
            else:
                if target_count == 0:
                    st.warning(f"Unsur '{target_element}' tidak muncul di rumus '{compound}'. Menggunakan Ar tanpa koefisien.")
                    Ar = periodic_table[target_element]
                else:
                    Ar = periodic_table[target_element] * target_count

                Bm = Mr_compound
                deposit = W1 - W0
                if deposit <= 0:
                    st.warning("Perhatian: (W1 - W0) <= 0. Hasil bisa tidak valid.")

                percent_kadar = ((Ar / Bm) * (deposit / volume_ml)) * 100

                st.subheader("Perhitungan")
                st.write(f"Berat Molekul (Bm) = {Bm:.6f} g/mol")
                st.write(f"Ar {target_element} = {Ar:.6f} g/mol")
                st.write(f"Massa endapan (W1 - W0) = {deposit:.6f} g")
                st.write(f"Volume sampel = {volume_ml:.6f} mL")
                st.write(f"% Kadar ({target_element}) = {percent_kadar:.6f} %")

                with st.expander("Lihat langkah perhitungan detail"):
                    st.markdown("**1) Jumlah setiap unsur**")
                    for el, cnt in counts.items():
                        mass_el = periodic_table[el] * cnt
                        st.write(f"{el}: {periodic_table[el]:.6f} × {cnt} = {mass_el:.6f} g/mol")

                    st.markdown("**2) Hitung Bm**")
                    st.write(f"Bm({compound}) = " + " + ".join([f"{periodic_table[el]:.6f}×{cnt}" for el, cnt in counts.items()]) + f" = {Bm:.6f} g/mol")

                    st.markdown("**3) Hitung Ar**")
                    if target_count > 0:
                        st.write(f"{periodic_table[target_element]:.6f} × {target_count} = {Ar:.6f} g/mol")
                    else:
                        st.write(f"Ar = {Ar:.6f} g/mol (unsur tidak muncul di rumus)")

                    st.markdown("**4) Hitung faktor (Ar/Bm)**")
                    st.write(f"{Ar:.6f} / {Bm:.6f} = {(Ar/Bm):.8f}")

                    st.markdown("**5) Hitung massa endapan**")
                    st.write(f"{W1:.6f} - {W0:.6f} = {deposit:.6f} g")

                    st.markdown("**6) Masukkan ke rumus**")
                    st.write(f"% Kadar = ({Ar:.6f} / {Bm:.6f}) × ({deposit:.6f} / {volume_ml:.6f}) × 100 = {percent_kadar:.6f} %")

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

st.markdown("---")
st.write("Versi ini mendukung rumus dengan tanda kurung sederhana seperti (NH4)2SO4.")
