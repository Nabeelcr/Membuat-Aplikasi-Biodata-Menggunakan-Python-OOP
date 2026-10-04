import tkinter as tk
from tkinter import messagebox
import datetime
import json
import logging
import re
from pathlib import Path

logging.basicConfig(
    filename="aplikasi_biodata.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Membuat kelas utama aplikasi yang mewarisi dari tk.Tk
class AplikasiBiodata(tk.Tk):
    # Metode __init__ adalah constructor yang akan dijalankan saat objek dibuat
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Biodata Mahasiswa")
        self.geometry("600x700")
        self.resizable(True, True)

        # Database user sederhana (dalam aplikasi nyata, ini akan di database)
        self.users_db = {
            "admin": "123",
            "user1": "password1",
            "mahasiswa": "123456"
        }

        # Status login
        self.current_user = None
        self.remember_file = Path(__file__).with_name("aplikasi_biodata_config.json")
        self.remembered_username = self._load_remembered_username()

        # Atribut untuk manajemen frame
        self.frame_aktif = None

        # Buat tampilan
        self._buat_tampilan_login()
        self._buat_tampilan_biodata()

        # Tampilkan frame login di awal
        self._pindah_ke(self.frame_login)
        logging.info("Aplikasi dimulai")

    def _load_remembered_username(self):
        """Muat username tersimpan jika file konfigurasinya tersedia."""
        try:
            with self.remember_file.open("r", encoding="utf-8") as file:
                return json.load(file).get("username", "")
        except (OSError, json.JSONDecodeError):
            return ""

    def _save_remembered_username(self, username):
        """Simpan atau hapus username sesuai pilihan Remember Me."""
        try:
            if self.var_remember.get():
                with self.remember_file.open("w", encoding="utf-8") as file:
                    json.dump({"username": username}, file)
                self.remembered_username = username
            else:
                self.remember_file.unlink(missing_ok=True)
                self.remembered_username = ""
        except OSError as error:
            logging.error("Could not update remembered username: %s", error)

    def _buat_tampilan_login(self):
        self.frame_login = tk.Frame(master=self, padx=20, pady=100, bg="skyblue")

        # Konfigurasi grid untuk frame login agar terpusat
        self.frame_login.grid_columnconfigure(0, weight=1)
        self.frame_login.grid_columnconfigure(1, weight=1)

        # Judul Login
        tk.Label(
            self.frame_login,
            text="HALAMAN LOGIN",
            font=("Arial", 16, "bold"),
            bg="skyblue"
        ).grid(row=0, column=0, columnspan=2, pady=20)

        # Input Username
        tk.Label(
            self.frame_login,
            text="Username:",
            font=("Arial", 12),
            bg="skyblue"
        ).grid(row=1, column=0, sticky="W", pady=5)

        self.var_username = tk.StringVar(value=self.remembered_username)
        self.entry_username = tk.Entry(
            self.frame_login,
            font=("Arial", 12),
            textvariable=self.var_username
        )
        self.entry_username.grid(row=1, column=1, pady=5, sticky="EW")

        # Input Password
        tk.Label(
            self.frame_login,
            text="Password:",
            font=("Arial", 12),
            bg="skyblue"
        ).grid(row=2, column=0, sticky="W", pady=5)

        self.entry_password = tk.Entry(
            self.frame_login,
            font=("Arial", 12),
            show="*"
        )
        self.entry_password.grid(row=2, column=1, pady=5, sticky="EW")

        self.btn_toggle_password = tk.Button(
            self.frame_login,
            text="Tampilkan",
            command=self._toggle_password_visibility
        )
        self.btn_toggle_password.grid(row=2, column=2, padx=(6, 0), pady=5)

        self.var_remember = tk.BooleanVar(value=bool(self.remembered_username))
        tk.Checkbutton(
            self.frame_login,
            text="Ingat username",
            variable=self.var_remember,
            bg="skyblue",
            activebackground="skyblue"
        ).grid(row=3, column=1, sticky="W", pady=(6, 0))

        # Tombol Login
        self.btn_login = tk.Button(
            self.frame_login,
            text="Login",
            font=("Arial", 12, "bold"),
            command=self._coba_login
        )
        self.btn_login.grid(row=4, column=0, columnspan=3, pady=20, sticky="EW")

        # Keyboard shortcuts untuk login
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda e: self._coba_login())

        # Info untuk user
        info_label = tk.Label(
            self.frame_login,
            text="Akun demo: admin (123), user1 (password1), mahasiswa (123456)",
            font=("Arial", 9),
            fg="gray",
            bg="skyblue",
            justify=tk.LEFT
        )
        info_label.grid(row=5, column=0, columnspan=3, pady=10)

    def _toggle_password_visibility(self):
        is_hidden = self.entry_password.cget("show") == "*"
        self.entry_password.config(show="" if is_hidden else "*")
        self.btn_toggle_password.config(text="Sembunyikan" if is_hidden else "Tampilkan")

    def _coba_login(self):
        """Proses login dan catat hasilnya ke log."""
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        logging.info("Login attempt for username: %s", username)

        # Validasi input kosong
        if not username or not password:
            logging.warning("Empty credentials attempt for username: %s", username)
            messagebox.showwarning("Login Gagal", "Username dan password tidak boleh kosong.")
            self.entry_username.focus_set()
            return

        # Validasi panjang minimum
        if len(username) < 3:
            logging.warning("Username too short: %s", username)
            messagebox.showwarning("Login Gagal", "Username minimal 3 karakter.")
            self.entry_username.focus_set()
            return

        # Cek kredensial di database
        if username in self.users_db and self.users_db[username] == password:
            self.current_user = username
            self._save_remembered_username(username)
            logging.info("Successful login for user: %s", username)
            messagebox.showinfo("Login Berhasil", f"Selamat datang, {username}!")
            self._reset_form_biodata()
            self._update_title_with_user()
            self._buat_menu()
            # Ganti warna background: hijau khusus untuk admin, selain itu tetap skyblue
            if username == "admin":
                self._set_theme_color("lightgreen")
            else:
                self._set_theme_color("skyblue")
            self._pindah_ke(self.frame_biodata)
            # Bersihkan field login setelah berhasil
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
        else:
            logging.warning("Failed login attempt for username: %s", username)
            messagebox.showerror("Login Gagal", "Username atau password salah.")
            # Bersihkan password dan focus ke username
            self.entry_password.delete(0, tk.END)
            self.entry_username.focus_set()

    def _pindah_ke(self, frame_tujuan):
        """Method untuk berpindah antar tampilan"""
        if self.frame_aktif is not None:
            self.frame_aktif.pack_forget()

        self.frame_aktif = frame_tujuan
        self.frame_aktif.pack(fill=tk.BOTH, expand=True)

        # Auto-focus berdasarkan frame yang ditampilkan
        if frame_tujuan == self.frame_login:
            self.after(100, lambda: self.entry_username.focus_set())
        elif frame_tujuan == self.frame_biodata:
            self.after(100, lambda: self.entry_nama.focus_set())

    def _buat_tampilan_biodata(self):
        self.var_nama = tk.StringVar()
        self.var_nim = tk.StringVar()
        self.var_jurusan = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telepon = tk.StringVar()
        self.var_tanggal_lahir = tk.StringVar()
        self.var_jk = tk.StringVar(value="Pria")
        self.var_setuju = tk.IntVar()

        self.var_nama.trace_add("write", self.validate_form)
        self.var_nim.trace_add("write", self.validate_form)
        self.var_jurusan.trace_add("write", self.validate_form)
        self.var_email.trace_add("write", self.validate_form)
        self.var_telepon.trace_add("write", self.validate_form)
        self.var_tanggal_lahir.trace_add("write", self.validate_form)

        self.frame_biodata = tk.Frame(master=self, padx=20, pady=20, bg="skyblue")
        self.frame_biodata.columnconfigure(1, weight=1)

        self.label_judul = tk.Label(
            master=self.frame_biodata,
            text="FORM BIODATA MAHASISWA",
            font=("Arial", 16, "bold"),
            bg="skyblue"
        )
        self.label_judul.grid(row=0, column=0, columnspan=2, pady=20)

        self.frame_input = tk.Frame(
            master=self.frame_biodata,
            relief=tk.GROOVE,
            borderwidth=2,
            padx=10,
            pady=10,
            bg="skyblue"
        )
        self.frame_input.grid(row=1, column=0, columnspan=2, sticky="EW")

        self.label_nama = tk.Label(
            master=self.frame_input,
            text="Nama Lengkap:",
            font=("Arial", 12),
            bg="skyblue"
        )
        self.label_nama.grid(row=0, column=0, sticky="W", pady=2)
        self.entry_nama = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_nama
        )
        self.entry_nama.grid(row=0, column=1, pady=2)

        self.label_nim = tk.Label(
            master=self.frame_input,
            text="NIM:",
            font=("Arial", 12),
            bg="skyblue"
        )
        self.label_nim.grid(row=1, column=0, sticky="W", pady=2)
        self.entry_nim = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_nim
        )
        self.entry_nim.grid(row=1, column=1, pady=2)

        self.label_jurusan = tk.Label(
            master=self.frame_input,
            text="Jurusan:",
            font=("Arial", 12),
            bg="skyblue"
        )
        self.label_jurusan.grid(row=2, column=0, sticky="W", pady=2)
        self.entry_jurusan = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_jurusan
        )
        self.entry_jurusan.grid(row=2, column=1, pady=2)

        for row, label_text, variable, label_attribute, entry_attribute in (
            (3, "Email:", self.var_email, "label_email", "entry_email"),
            (4, "Telepon:", self.var_telepon, "label_telepon", "entry_telepon"),
            (5, "Tanggal Lahir (DD/MM/YYYY):", self.var_tanggal_lahir, "label_tanggal_lahir", "entry_tanggal_lahir"),
        ):
            label = tk.Label(self.frame_input, text=label_text, font=("Arial", 12), bg="skyblue")
            label.grid(row=row, column=0, sticky="W", pady=2)
            entry = tk.Entry(self.frame_input, width=30, font=("Arial", 12), textvariable=variable)
            entry.grid(row=row, column=1, pady=2)
            setattr(self, label_attribute, label)
            setattr(self, entry_attribute, entry)

        self.label_alamat = tk.Label(
            master=self.frame_input,
            text="Alamat:",
            font=("Arial", 12),
            bg="skyblue"
        )
        self.label_alamat.grid(row=6, column=0, sticky="NW", pady=2)

        self.frame_alamat = tk.Frame(
            master=self.frame_input,
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.frame_alamat.grid(row=6, column=1, pady=2)
        self.scrollbar_alamat = tk.Scrollbar(master=self.frame_alamat)
        self.scrollbar_alamat.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_alamat = tk.Text(
            master=self.frame_alamat,
            height=5,
            width=28,
            font=("Arial", 12)
        )
        self.text_alamat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_alamat.config(command=self.text_alamat.yview)
        self.text_alamat.config(yscrollcommand=self.scrollbar_alamat.set)
        self.text_alamat.bind("<KeyRelease>", lambda event: self.validate_form())

        self.label_jk = tk.Label(
            master=self.frame_input,
            text="Jenis Kelamin:",
            font=("Arial", 12),
            bg="skyblue"
        )
        self.label_jk.grid(row=7, column=0, sticky="W", pady=2)
        self.frame_jk = tk.Frame(master=self.frame_input, bg="skyblue")
        self.frame_jk.grid(row=7, column=1, sticky="W")
        self.radio_buttons_jk = []
        for text, value in (("Pria", "Pria"), ("Wanita", "Wanita"), ("Walmart Bag", "Walmart Bag")):
            rb = tk.Radiobutton(
                master=self.frame_jk,
                text=text,
                variable=self.var_jk,
                value=value,
                bg="skyblue",
                activebackground="skyblue",
                selectcolor="lightblue"
            )
            rb.pack(side=tk.LEFT)
            self.radio_buttons_jk.append(rb)

        self.check_setuju = tk.Checkbutton(
            master=self.frame_input,
            text="Saya menyetujui pengumpulan data ini.",
            variable=self.var_setuju,
            bg="skyblue",
            command=self.validate_form
        )
        self.check_setuju.grid(row=8, column=0, columnspan=2, pady=10, sticky="W")

        self.btn_submit = tk.Button(
            master=self.frame_biodata,
            text="Submit Biodata",
            font=("Arial", 12, "bold"),
            command=self.submit_data,
            state=tk.DISABLED
        )
        self.btn_submit.grid(row=9, column=0, pady=20, padx=(0, 5), sticky="EW")
        self.btn_submit.bind("<Enter>", self.on_enter)
        self.btn_submit.bind("<Leave>", self.on_leave)

        self.btn_reset = tk.Button(
            master=self.frame_biodata,
            text="Reset Form",
            font=("Arial", 12),
            command=self._reset_form_biodata
        )
        self.btn_reset.grid(row=9, column=1, pady=20, padx=(5, 0), sticky="EW")

        self.entry_nama.bind("<Return>", self.submit_shortcut)
        self.entry_nim.bind("<Return>", self.submit_shortcut)
        self.entry_jurusan.bind("<Return>", self.submit_shortcut)
        self.text_alamat.bind("<Return>", self.submit_shortcut)

        self.label_hasil = tk.Label(
            master=self.frame_biodata,
            text="",
            font=("Arial", 12, "italic"),
            justify=tk.LEFT,
            bg="skyblue"
        )
        self.label_hasil.grid(row=10, column=0, columnspan=2, sticky="W", padx=10)

        self.validate_form()

        # Kumpulkan semua widget bertema warna di halaman biodata,
        # supaya bisa diganti warnanya sekaligus lewat _set_theme_color()
        self.themed_widgets = [
            self.frame_biodata,
            self.label_judul,
            self.frame_input,
            self.label_nama,
            self.label_nim,
            self.label_jurusan,
            self.label_email,
            self.label_telepon,
            self.label_tanggal_lahir,
            self.label_alamat,
            self.frame_jk,
            self.label_jk,
            self.check_setuju,
            self.label_hasil,
        ]

    def _set_theme_color(self, color):
        """Mengubah warna background halaman biodata (frame_biodata beserta isinya)."""
        for widget in self.themed_widgets:
            try:
                widget.configure(bg=color)
            except tk.TclError:
                pass
        for rb in self.radio_buttons_jk:
            try:
                rb.configure(bg=color, activebackground=color)
            except tk.TclError:
                pass

    def _hapus_menu(self):
        """Menghapus menu bar dari window."""
        empty_menu = tk.Menu(self)
        self.config(menu=empty_menu)

    def _logout(self):
        """Logout dan kembali ke halaman login."""
        if messagebox.askyesno("Logout", f"Apakah {self.current_user} yakin ingin logout?"):
            logging.info("User logout: %s", self.current_user)
            # Reset status user
            self.current_user = None
            # Hapus menu
            self._hapus_menu()
            # Update title
            self._update_title_with_user()
            # Bersihkan field login
            self.entry_username.delete(0, tk.END)
            if self.var_remember.get():
                self.entry_username.insert(0, self.remembered_username)
            self.entry_password.delete(0, tk.END)
            # Reset form biodata
            self._reset_form_biodata()
            # Kembalikan warna tema ke default sebelum kembali ke login
            self._set_theme_color("skyblue")
            # Kembali ke halaman login
            self._pindah_ke(self.frame_login)
            # Focus ke username field
            self.entry_username.focus_set()

    def submit_data(self):
        """Validasi dan tampilkan biodata yang dikirim."""
        try:
            if self.var_setuju.get() == 0:
                messagebox.showwarning("Data Belum Lengkap", "Anda harus menyetujui pengumpulan data.")
                return

            nama = self.entry_nama.get().strip()
            nim = self.entry_nim.get().strip()
            jurusan = self.entry_jurusan.get().strip()
            email = self.entry_email.get().strip()
            telepon = self.entry_telepon.get().strip()
            tanggal_lahir = self.entry_tanggal_lahir.get().strip()
            alamat = self.text_alamat.get("1.0", tk.END).strip()
            jenis_kelamin = self.var_jk.get()

            if not all((nama, nim, jurusan, email, telepon, tanggal_lahir, alamat)):
                messagebox.showwarning("Data Belum Lengkap", "Semua field biodata harus diisi.")
                return

            if not nim.isdigit() or len(nim) < 8:
                messagebox.showwarning("NIM Tidak Valid", "NIM harus berupa angka dengan minimal 8 digit.")
                self.entry_nim.focus_set()
                return

            if nama.isdigit():
                messagebox.showwarning("Nama Tidak Valid", "Nama tidak boleh hanya berisi angka.")
                self.entry_nama.focus_set()
                return

            if not self._valid_email(email):
                messagebox.showwarning("Email Tidak Valid", "Masukkan alamat email dengan format yang benar.")
                self.entry_email.focus_set()
                return

            if not self._valid_telepon(telepon):
                messagebox.showwarning("Telepon Tidak Valid", "Gunakan nomor Indonesia, misalnya 081234567890 atau +6281234567890.")
                self.entry_telepon.focus_set()
                return

            if not self._valid_tanggal_lahir(tanggal_lahir):
                messagebox.showwarning("Tanggal Tidak Valid", "Masukkan tanggal dengan format DD/MM/YYYY dan bukan tanggal mendatang.")
                self.entry_tanggal_lahir.focus_set()
                return

            hasil = (
                f"Nama: {nama}\nNIM: {nim}\nJurusan: {jurusan}\nEmail: {email}\n"
                f"Telepon: {telepon}\nTanggal Lahir: {tanggal_lahir}\n"
                f"Alamat: {alamat}\nJenis Kelamin: {jenis_kelamin}"
            )
            messagebox.showinfo("Biodata Tersimpan", hasil)

            hasil_lengkap = f"BIODATA TERSIMPAN:\nDiinput oleh: {self.current_user}\n\n{hasil}"
            self.label_hasil.config(text=hasil_lengkap)
            logging.info("Data submitted by user: %s - NIM: %s", self.current_user, nim)

        except Exception as e:
            logging.error("Error in submit_data by %s: %s", self.current_user, str(e))
            messagebox.showerror("Kesalahan", f"Terjadi kesalahan saat memproses data:\n{str(e)}")

    @staticmethod
    def _valid_email(email):
        return re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) is not None

    @staticmethod
    def _valid_telepon(telepon):
        nomor = re.sub(r"[\s()-]", "", telepon)
        return re.fullmatch(r"(?:0|\+?62)8\d{8,11}", nomor) is not None

    @staticmethod
    def _valid_tanggal_lahir(tanggal_lahir):
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", tanggal_lahir) is None:
            return False
        try:
            tanggal = datetime.datetime.strptime(tanggal_lahir, "%d/%m/%Y").date()
            return tanggal <= datetime.date.today()
        except ValueError:
            return False

    def validate_form(self, *args):
        nama = self.var_nama.get().strip()
        nim = self.var_nim.get().strip()
        valid = all((
            nama != "" and not nama.isdigit(),
            nim.isdigit() and len(nim) >= 8,
            self.var_jurusan.get().strip() != "",
            self._valid_email(self.var_email.get().strip()),
            self._valid_telepon(self.var_telepon.get().strip()),
            self._valid_tanggal_lahir(self.var_tanggal_lahir.get().strip()),
            self.text_alamat.get("1.0", tk.END).strip() != "",
            self.var_setuju.get() == 1,
        ))
        state = tk.NORMAL if valid else tk.DISABLED
        self.btn_submit.config(state=state)

    def on_enter(self, event):
        if self.btn_submit["state"] == tk.NORMAL:
            self.btn_submit.config(bg="lightblue")

    def on_leave(self, event):
        self.btn_submit.config(bg="SystemButtonFace")

    def submit_shortcut(self, event=None):
        if self.btn_submit["state"] == tk.NORMAL:
            self.submit_data()

    def _reset_form_biodata(self):
        """Reset semua field di form biodata"""
        self.var_nama.set("")
        self.var_nim.set("")
        self.var_jurusan.set("")
        self.var_email.set("")
        self.var_telepon.set("")
        self.var_tanggal_lahir.set("")
        self.text_alamat.delete("1.0", tk.END)
        self.var_jk.set("Pria")
        self.var_setuju.set(0)
        self.label_hasil.config(text="")

    def _update_title_with_user(self):
        """Update judul window dengan nama user yang login"""
        if self.current_user:
            self.title(f"Aplikasi Biodata Mahasiswa - User: {self.current_user}")
        else:
            self.title("Aplikasi Biodata Mahasiswa")

    def simpan_hasil(self):
        """Simpan hasil biodata ke file dengan error handling"""
        try:
            hasil_tersimpan = self.label_hasil.cget("text")

            if not hasil_tersimpan or "BIODATA TERSIMPAN" not in hasil_tersimpan:
                messagebox.showwarning("Belum Ada Data", "Kirim biodata terlebih dahulu sebelum menyimpan.")
                return

            # Buat nama file dengan timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"biodata_{self.current_user}_{timestamp}.txt"

            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"Data disimpan oleh: {self.current_user}\n")
                file.write(f"Waktu penyimpanan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("-" * 50 + "\n")
                file.write(hasil_tersimpan)

            messagebox.showinfo("Berhasil", f"Data tersimpan di '{filename}'.")

        except PermissionError:
            messagebox.showerror("Tidak Diizinkan", "Aplikasi tidak memiliki izin untuk menyimpan file di lokasi ini.")
        except Exception as e:
            messagebox.showerror("Kesalahan", f"Terjadi kesalahan saat menyimpan file:\n{str(e)}")

    def keluar_aplikasi(self):
        """Tutup aplikasi setelah konfirmasi dan catat aktivitasnya."""
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?"):
            logging.info("Application closed by user: %s", self.current_user)
            self.destroy()

    def _buat_menu(self):
        """Membuat menu bar untuk aplikasi"""
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(master=menu_bar, tearoff=0)
        file_menu.add_command(label="Simpan Hasil", command=self.simpan_hasil)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.keluar_aplikasi)

        menu_bar.add_cascade(label="File", menu=file_menu)

# Blok berikut hanya akan dieksekusi jika file ini dijalankan secara langsung
if __name__ == "__main__":
    # Membuat instance dari kelas aplikasi kita
    app = AplikasiBiodata()
    # Menjalankan mainloop dari instance tersebut
    app.mainloop()