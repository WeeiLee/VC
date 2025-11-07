#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Labelador de matrículas para YOLO + OCR
- Redimensiona imagen para ocupar todo el espacio disponible.
- Sin atajos de teclado que interfieran (solo Esc para salir).
- Click izquierdo: dibujar recuadro.
- Click derecho: reiniciar selección.
- Guarda progreso (última imagen) en session.json al salir.
"""

from __future__ import annotations
import argparse
from pathlib import Path
from dataclasses import dataclass
import csv
import sys
import json
from typing import Optional
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

@dataclass
class Box:
    x1: int
    y1: int
    x2: int
    y2: int

    def norm(self):
        x1, y1, x2, y2 = self.ordered()
        return x1, y1, x2, y2

    def ordered(self):
        return (min(self.x1, self.x2), min(self.y1, self.y2),
                max(self.x1, self.x2), max(self.y1, self.y2))

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def yolo_from_box(box: Box, img_w: int, img_h: int):
    x1, y1, x2, y2 = box.norm()
    bw, bh = x2 - x1, y2 - y1
    cx, cy = x1 + bw / 2, y1 + bh / 2
    return cx / img_w, cy / img_h, bw / img_w, bh / img_h

class PlateLabeler(tk.Tk):
    def __init__(self, imgs_dir: Path, out_dir: Path):
        super().__init__()
        self.title("Plate Labeler - YOLO + OCR")
        self.geometry("1100x800")

        self.imgs_dir = imgs_dir
        self.out_dir = out_dir
        self.labels_dir = out_dir / "labels"
        ensure_dir(self.labels_dir)
        self.ocr_csv = out_dir / "ocr.csv"
        self.session_file = out_dir / "session.json"

        self.images = sorted([p for p in imgs_dir.iterdir() if p.suffix.lower() in IMG_EXTS])
        if not self.images:
            messagebox.showerror("Error", f"No hay imágenes en {imgs_dir}")
            self.destroy()
            return

        self.index = self._load_last_index()
        self.current_img = None
        self.tk_img = None
        self.scale = 1.0
        self.offset = (0, 0)
        self.box_on_display: Optional[Box] = None
        self.box_on_original: Optional[Box] = None
        self.start_pt = (0, 0)
        self.drawing = False

        self._build_ui()
        self._load_image()

        # Interceptar cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self._quit)

    # ---------------- Sesión ----------------
    def _load_last_index(self) -> int:
        """Lee el índice guardado en session.json si existe"""
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text(encoding="utf-8"))
                idx = int(data.get("last_index", 0))
                return max(0, min(idx, len(self.images) - 1))
            except Exception:
                pass
        return 0

    def _save_last_index(self):
        """Guarda el índice actual"""
        try:
            self.session_file.write_text(
                json.dumps({"last_index": self.index}, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    # ---------------- UI ----------------
    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        self.lbl_idx = ttk.Label(top, text="0/0")
        self.lbl_idx.pack(side=tk.LEFT)
        self.btn_quit = ttk.Button(top, text="Salir", command=self._quit)
        self.btn_quit.pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0, cursor="tcross")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Eventos del ratón
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Button-3>", self._on_right_click)  # click derecho para reset
        self.canvas.bind("<Configure>", lambda e: self._fit_and_draw())

        bottom = ttk.Frame(self)
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)
        ttk.Label(bottom, text="Matrícula:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(bottom, width=40)
        self.entry.pack(side=tk.LEFT, padx=(6, 10))
        self.entry.bind("<Return>", self._on_enter)

        self.info_var = tk.StringVar(value="Arrastra con el ratón para seleccionar la placa.")
        ttk.Label(bottom, textvariable=self.info_var).pack(side=tk.LEFT)

        # Solo mantener Escape para salir
        self.bind("<Escape>", lambda e: self._quit())

    # ---------------- Carga imagen ----------------
    def _load_image(self):
        img_path = self.images[self.index]
        self.current_img = Image.open(img_path).convert("RGB")
        self.lbl_idx.config(text=f"{self.index+1}/{len(self.images)} - {img_path.name}")
        self.box_on_display = None
        self.box_on_original = None
        self.entry.delete(0, tk.END)
        self._fit_and_draw()

    def _fit_and_draw(self):
        if not self.current_img:
            return
        c_w = max(100, self.canvas.winfo_width())
        c_h = max(100, self.canvas.winfo_height())

        img_w, img_h = self.current_img.size
        scale = min(c_w / img_w, c_h / img_h)
        self.scale = scale
        disp = self.current_img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(disp)

        dx = (c_w - disp.width) // 2
        dy = (c_h - disp.height) // 2
        self.offset = (dx, dy)

        self.canvas.delete("all")
        self.canvas.create_image(dx, dy, anchor="nw", image=self.tk_img)

        if self.box_on_original:
            x1, y1, x2, y2 = self.box_on_original.norm()
            sx1, sy1 = self._to_display(x1, y1)
            sx2, sy2 = self._to_display(x2, y2)
            self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline="#00FF00", width=2)

    # ---------------- Eventos ----------------
    def _on_mouse_down(self, e):
        self.drawing = True
        self.start_pt = (e.x, e.y)
        self.box_on_display = Box(e.x, e.y, e.x, e.y)
        self._fit_and_draw()

    def _on_mouse_drag(self, e):
        if not self.drawing:
            return
        self.box_on_display = Box(self.start_pt[0], self.start_pt[1], e.x, e.y)
        self._fit_and_draw()
        x1, y1, x2, y2 = self.box_on_display.norm()
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00FF00", width=2)

    def _on_mouse_up(self, e):
        if not self.drawing:
            return
        self.drawing = False
        if not self.box_on_display:
            return
        x1, y1, x2, y2 = self.box_on_display.norm()
        ox1, oy1 = self._to_original(x1, y1)
        ox2, oy2 = self._to_original(x2, y2)
        self.box_on_original = Box(int(ox1), int(oy1), int(ox2), int(oy2))
        self.entry.focus_set()
        self.entry.selection_range(0, tk.END)
        self._fit_and_draw()

    def _on_right_click(self, event):
        """Click derecho → reset selección"""
        self.box_on_original = None
        self.box_on_display = None
        self._fit_and_draw()
        self.info_var.set("Selección reiniciada. Dibuja nuevamente la placa.")

    # ---------------- Guardado ----------------
    def _on_enter(self, _event=None):
        plate = self.entry.get().strip()
        if not self.box_on_original:
            self.info_var.set("Dibuja primero el recuadro.")
            return
        self._save_current(plate)
        self._next_image()

    def _next_image(self):
        if self.index < len(self.images) - 1:
            self.index += 1
            self._save_last_index()
            self._load_image()
        else:
            messagebox.showinfo("Fin", "No hay más imágenes.")
            self._quit()

    def _save_current(self, plate_text: str):
        img_path = self.images[self.index]
        iw, ih = self.current_img.size
        x, y, w, h = yolo_from_box(self.box_on_original, iw, ih)
        (self.labels_dir / f"{img_path.stem}.txt").write_text(f"0 {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

        new_file = not self.ocr_csv.exists()
        with self.ocr_csv.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(["filename", "plate_text", "x1", "y1", "x2", "y2"])
            x1, y1, x2, y2 = self.box_on_original.norm()
            writer.writerow([img_path.name, plate_text, x1, y1, x2, y2])
        self.info_var.set("Guardado correctamente.")

    # ---------------- Utilidades ----------------
    def _to_original(self, sx, sy):
        dx, dy = self.offset
        x = (sx - dx) / self.scale
        y = (sy - dy) / self.scale
        return x, y

    def _to_display(self, ox, oy):
        dx, dy = self.offset
        x = int(ox * self.scale + dx)
        y = int(oy * self.scale + dy)
        return x, y

    def _quit(self):
        self._save_last_index()
        self.destroy()

# ---------------- Main ----------------
def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    return ap.parse_args()

def main():
    args = parse_args()
    ensure_dir(args.out)
    app = PlateLabeler(args.images, args.out)
    app.mainloop()

if __name__ == "__main__":
    main()
