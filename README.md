# Oantek IPTV Playlist Builder

**Oantek IPTV Playlist Builder** adalah skrip Python yang secara otomatis menggabungkan saluran-saluran IPTV dari berbagai sumber publik, mencocokkannya dengan daftar yang telah ditentukan (`channels.txt`), menyusun urutan berdasarkan prioritas domain (`priority.txt`), dan menghasilkan file `oantek.m3u` siap pakai.

## Fitur

- **Agregasi Multi-Sumber:** Mengunduh playlist IPTV dari banyak URL terpercaya.
- **Normalisasi Nama:** Menyelaraskan nama saluran untuk mencocokkan dan menghindari duplikasi.
- **Prioritas Domain:** Memilih stream berdasarkan domain pilihan jika tersedia.
- **Metadata Lengkap:** Menambahkan `group-title`, `tvg-logo`, dan `tvg-id` ke setiap entri saluran.
- **Log Kesalahan:** Semua kegagalan unduh dicatat ke `log.txt`.
- **Daftar Saluran Tak Cocok:** Saluran yang tidak ditemukan dicatat ke `tidakcocok.txt`.

## Struktur File

- `channels.txt`: Daftar saluran IPTV yang ingin ditampilkan, beserta metadata seperti nama, grup, dan logo.
- `priority.txt`: Daftar domain prioritas untuk setiap saluran. Format: `Nama Channel = domainpilihan.com`
- `oantek.m3u`: File playlist hasil akhir.
- `log.txt`: Log kesalahan unduhan.
- `tidakcocok.txt`: Saluran dalam `channels.txt` yang tidak ditemukan di sumber mana pun.

## Cara Penggunaan

1. **Instalasi Dependensi**

   Pastikan Python 3.x telah terinstal. Kemudian install dependensi:

   ```bash
   pip install requests
   ```

2. **Edit `channels.txt` dan `priority.txt`**

   - `channels.txt`: Tambahkan daftar saluran yang ingin dimasukkan.
   - `priority.txt` *(opsional)*: Tentukan domain utama untuk saluran tertentu.

3. **Jalankan Skrip**

   ```bash
   python oantek_builder.py
   ```

4. **Output**

   File `oantek.m3u` akan dibuat di direktori yang sama, siap digunakan di aplikasi pemutar IPTV seperti VLC atau Kodi.

## Format `channels.txt`

```text
===== group-title="Sports"
Name="MNC Sports" tvg-logo="https://example.com/logo/mncsports.png"
Name="Champions TV 1" tvg-logo="https://example.com/logo/champ1.png"
```

## Format `priority.txt`

```text
MNC Sports = mncsports.terabit.web.id
Champions TV 1 = champions.fastiptv.net
```

## Sumber Playlist

Daftar sumber berada di dalam variabel `URL_SRCS` pada skrip. Anda dapat menambah/menghapus URL sesuai kebutuhan.

## Lisensi

Proyek ini dirilis dengan lisensi [MIT License](LICENSE).

## Catatan

Skrip ini hanya digunakan untuk keperluan edukasi dan eksperimen pribadi. Pastikan untuk menghormati hak cipta dan ketentuan layanan dari masing-masing penyedia konten.