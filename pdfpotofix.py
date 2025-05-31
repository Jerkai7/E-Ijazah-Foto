import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import io
import zipfile
import os

st.title("📎 Tempelkan Foto Ke PDF")

uploaded_pdf = st.file_uploader("📄 Upload PDF Multi-Halaman", type=["pdf"])

metode = st.radio("📂 Pilih Metode Input Foto", ["Upload Banyak Gambar", "Upload File ZIP Foto"], horizontal=True)

uploaded_images = []
if metode == "Upload Banyak Gambar":
    uploaded_images = st.file_uploader("🖼️ Upload Foto-foto (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
elif metode == "Upload File ZIP Foto":
    uploaded_zip = st.file_uploader("🗜️ Upload File ZIP berisi Foto (nama: 1.jpg, 2.jpg, dst)", type=["zip"])
    if uploaded_zip:
        with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
            file_list = sorted(zip_ref.namelist(), key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            for file_name in file_list:
                if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    with zip_ref.open(file_name) as file:
                        img_data = file.read()
                        uploaded_images.append(io.BytesIO(img_data))

# Default Setting
st.markdown("### ⚙️ Pengaturan Foto (dalam cm)")

col1, col2 = st.columns(2)
with col1:
    width_cm = st.number_input("Lebar Foto", min_value=1.0, value=3.70, step=0.1)
    height_cm = st.number_input("Tinggi Foto", min_value=1.0, value=4.90, step=0.1)
with col2:
    margin_bottom = st.number_input("Jarak dari Bawah", min_value=0.0, value=27.49, step=0.1)
    margin_right = st.number_input("Jarak dari Kanan", min_value=0.0, value=11.30, step=0.1)

if uploaded_pdf and uploaded_images and st.button("📌 Tempel Foto ke PDF"):
    dpi = 72
    width_px = int((width_cm / 2.54) * dpi)
    height_px = int((height_cm / 2.54) * dpi)
    bottom_px = (margin_bottom / 2.54) * dpi
    right_px = (margin_right / 2.54) * dpi

    # Buka PDF
    pdf = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    num_pages = len(pdf)

    if len(uploaded_images) != num_pages:
        st.error(f"⚠️ Jumlah foto ({len(uploaded_images)}) harus sama dengan jumlah halaman PDF ({num_pages}).")
    else:
        for i in range(num_pages):
            page = pdf[i]
            page_width = page.rect.width
            page_height = page.rect.height

            # Hitung posisi foto
            x1 = page_width - right_px
            y0 = bottom_px
            x0 = x1 - width_px
            y1 = y0 + height_px

            # Buka dan resize gambar
            img = Image.open(uploaded_images[i]).resize((width_px, height_px))

            # Simpan ke buffer
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            # Tempelkan gambar
            page.insert_image(fitz.Rect(x0, y0, x1, y1), stream=img_buffer)

        # Simpan hasil PDF
        output = io.BytesIO()
        pdf.save(output)
        pdf.close()

        st.success("✅ Foto berhasil ditempel ke semua halaman PDF!")
        st.download_button(
            label="⬇️ Download PDF Hasil",
            data=output.getvalue(),
            file_name="hasil_tempel_foto.pdf",
            mime="application/pdf"
        )
st.markdown("---")
st.markdown("<center><sub>© 2025 • Aplikasi ini dikembangkan oleh <b>Jerkai Jerkai</b></sub></center>", unsafe_allow_html=True)
