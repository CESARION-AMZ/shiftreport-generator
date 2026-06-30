"""App de escritorio para ShiftReport (tkinter, sin dependencias extra)."""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path
from tkinter import Tk, StringVar, BooleanVar, filedialog, messagebox
from tkinter import ttk

from shiftreport.reader import load_rows, detect_numeric_columns
from shiftreport.report import summarize, write_excel, write_html

BG = "#0f1720"
CARD = "#1b2836"
INK = "#eaf2f7"
ACC = "#2dd4bf"
MUT = "#8aa0b2"


class App:
    def __init__(self, root: Tk) -> None:
        self.root = root
        root.title("ShiftReport Generator")
        root.configure(bg=BG)
        root.geometry("600x520")
        root.minsize(560, 480)

        self.path = StringVar()
        self.title_var = StringVar(value="Reporte de turno")
        self.group_var = StringVar()
        self.html_var = BooleanVar(value=True)
        self.excel_var = BooleanVar(value=True)
        self.headers: list[str] = []

        self._style()
        self._build()

    def _style(self) -> None:
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass
        s.configure("TCombobox", fieldbackground=CARD, background=CARD,
                    foreground=INK, arrowcolor=ACC)
        s.configure("Accent.TButton", background=ACC, foreground="#06231f",
                    font=("Segoe UI", 11, "bold"), borderwidth=0, padding=10)
        s.map("Accent.TButton", background=[("active", "#26b8a6")])

    def _label(self, parent, text, size=10, color=MUT, bold=False):
        from tkinter import Label
        f = ("Segoe UI", size, "bold" if bold else "normal")
        return Label(parent, text=text, bg=BG, fg=color, font=f, anchor="w")

    def _build(self) -> None:
        from tkinter import Frame, Entry, Checkbutton, Label, Button

        pad = {"padx": 24}
        Label(self.root, text="ShiftReport Generator", bg=BG, fg=INK,
              font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(20, 0), **pad)
        self._label(self.root, "De un CSV/Excel de turno a un reporte formateado, en un clic.").pack(anchor="w", **pad)

        # archivo
        self._label(self.root, "1. Archivo de entrada (.csv o .xlsx)", bold=True, color=INK).pack(anchor="w", pady=(20, 4), **pad)
        row = Frame(self.root, bg=BG); row.pack(fill="x", **pad)
        Entry(row, textvariable=self.path, bg=CARD, fg=INK, insertbackground=INK,
              relief="flat", font=("Segoe UI", 10)).pack(side="left", fill="x", expand=True, ipady=6)
        Button(row, text="Examinar...", command=self.pick_file, bg=CARD, fg=ACC,
               relief="flat", font=("Segoe UI", 10, "bold"), padx=14).pack(side="left", padx=(8, 0))

        # titulo
        self._label(self.root, "2. Titulo del reporte", bold=True, color=INK).pack(anchor="w", pady=(16, 4), **pad)
        Entry(self.root, textvariable=self.title_var, bg=CARD, fg=INK, insertbackground=INK,
              relief="flat", font=("Segoe UI", 10)).pack(fill="x", ipady=6, **pad)

        # agrupar por
        self._label(self.root, "3. Agrupar por columna", bold=True, color=INK).pack(anchor="w", pady=(16, 4), **pad)
        self.combo = ttk.Combobox(self.root, textvariable=self.group_var, state="readonly")
        self.combo.pack(fill="x", ipady=4, **pad)

        # formatos
        opts = Frame(self.root, bg=BG); opts.pack(anchor="w", pady=(16, 0), **pad)
        Checkbutton(opts, text="Excel (.xlsx)", variable=self.excel_var, bg=BG, fg=INK,
                    selectcolor=CARD, activebackground=BG, activeforeground=INK,
                    font=("Segoe UI", 10)).pack(side="left")
        Checkbutton(opts, text="HTML", variable=self.html_var, bg=BG, fg=INK,
                    selectcolor=CARD, activebackground=BG, activeforeground=INK,
                    font=("Segoe UI", 10)).pack(side="left", padx=(16, 0))

        # boton generar
        ttk.Button(self.root, text="Generar reporte", style="Accent.TButton",
                   command=self.generate).pack(fill="x", pady=(24, 8), **pad)

        self.status = Label(self.root, text="Elige un archivo para empezar.", bg=BG, fg=MUT,
                            font=("Segoe UI", 9), wraplength=540, justify="left")
        self.status.pack(anchor="w", **pad)

    def pick_file(self) -> None:
        f = filedialog.askopenfilename(
            title="Elige el archivo de turno",
            filetypes=[("Datos", "*.csv *.xlsx *.xlsm"), ("Todos", "*.*")],
        )
        if not f:
            return
        self.path.set(f)
        try:
            self.headers, _ = load_rows(f)
            self.combo["values"] = self.headers
            numeric = set(detect_numeric_columns(self.headers, load_rows(f)[1]))
            text_cols = [h for h in self.headers if h not in numeric]
            if text_cols:
                self.group_var.set(text_cols[0])
            self._set_status(f"Archivo cargado: {len(self.headers)} columnas detectadas.", ACC)
        except Exception as e:
            self._set_status(f"No se pudo leer el archivo: {e}", "#ff7a7a")

    def generate(self) -> None:
        path = self.path.get().strip()
        if not path:
            messagebox.showwarning("Falta el archivo", "Elige primero un archivo de entrada.")
            return
        try:
            headers, rows = load_rows(path)
            if not rows:
                self._set_status("El archivo no tiene filas de datos.", "#ff7a7a")
                return
            group = self.group_var.get() or None
            summary = summarize(headers, rows, title=self.title_var.get() or "Reporte", group_by=group)

            out_dir = Path(path).parent / "shiftreport_outputs"
            from datetime import datetime
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            slug = (self.title_var.get() or "reporte").lower().replace(" ", "_")
            done = []
            if self.excel_var.get():
                p = write_excel(summary, rows, headers, out_dir / f"{slug}_{stamp}.xlsx")
                done.append(p)
            if self.html_var.get():
                p = write_html(summary, out_dir / f"{slug}_{stamp}.html")
                done.append(p)

            if not done:
                self._set_status("Marca al menos un formato (Excel o HTML).", "#ff7a7a")
                return

            self._set_status(f"Listo: {summary.row_count} registros. Abriendo carpeta...", ACC)
            try:
                os.startfile(out_dir)  # type: ignore[attr-defined]
                if done and self.html_var.get():
                    os.startfile([d for d in done if str(d).endswith(".html")][0])  # type: ignore[attr-defined]
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"{e}\n\n{traceback.format_exc()}")
            self._set_status(f"Error: {e}", "#ff7a7a")

    def _set_status(self, text: str, color: str = MUT) -> None:
        self.status.config(text=text, fg=color)


def main() -> int:
    root = Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
