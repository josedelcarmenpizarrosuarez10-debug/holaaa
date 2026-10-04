"""MetraP - metrado de cunetas desde un plano DXF (interfaz grafica y linea de comandos).

Uso grafico:   python metrap.py
Uso en consola: python metrap.py --dxf PERFIL.dxf --plantilla plantilla/PLANTILLA_METRADO_CUNETAS.xlsx --salida METRADO.xlsx [--config metrap_config.json]
"""
import os, sys, argparse, threading, traceback, json

AQUI = os.path.dirname(os.path.abspath(sys.argv[0] if getattr(sys, "frozen", False) else __file__))
BASE = getattr(sys, "_MEIPASS", AQUI)          # carpeta de recursos cuando corre como .exe (PyInstaller)
sys.path.insert(0, BASE); sys.path.insert(0, AQUI)
import metrap_engine as ME

PLANTILLA_DEF = os.path.join(BASE, "plantilla", "PLANTILLA_METRADO_CUNETAS.xlsx")
CONFIG_DEF = os.path.join(AQUI, "metrap_config.json")
if not os.path.exists(CONFIG_DEF): CONFIG_DEF = os.path.join(BASE, "metrap_config.json")
VERSION = "1.0"


def correr(dxf, plantilla, salida, config, escribir=print):
    salida = os.path.abspath(salida)
    if not salida.lower().endswith(".xlsx"): salida += ".xlsx"
    E, fn, pend, log = ME.ejecutar(dxf, plantilla, salida, config)
    for l in log: escribir(l)
    escribir("")
    escribir("ARCHIVO GENERADO: " + fn)
    if pend:
        escribir("")
        escribir("DATOS QUE FALTAN (no estan en el DXF, completar a mano en la planilla):")
        for p in pend: escribir(" - " + p)
    return fn


def gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    root = tk.Tk(); root.title("MetraP %s - Metrado de cunetas desde DXF" % VERSION); root.geometry("860x600")
    v_dxf = tk.StringVar(); v_pla = tk.StringVar(value=PLANTILLA_DEF); v_sal = tk.StringVar(); v_cfg = tk.StringVar(value=CONFIG_DEF)
    frm = ttk.Frame(root, padding=10); frm.pack(fill="both", expand=True)

    def fila(r, etiqueta, var, tipo, ext):
        ttk.Label(frm, text=etiqueta).grid(row=r, column=0, sticky="w", pady=3)
        ttk.Entry(frm, textvariable=var, width=80).grid(row=r, column=1, sticky="we", padx=5)
        def elegir():
            if tipo == "abrir": f = filedialog.askopenfilename(filetypes=ext)
            else: f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=ext)
            if f:
                var.set(f)
                if var is v_dxf and not v_sal.get(): v_sal.set(os.path.splitext(f)[0] + "_METRADO.xlsx")
        ttk.Button(frm, text="...", width=4, command=elegir).grid(row=r, column=2)
    fila(0, "Plano DXF (perfiles de cunetas):", v_dxf, "abrir", [("DXF", "*.dxf")])
    fila(1, "Plantilla Excel del proyecto:", v_pla, "abrir", [("Excel", "*.xlsx")])
    fila(2, "Archivo de salida (.xlsx):", v_sal, "guardar", [("Excel", "*.xlsx")])
    fila(3, "Configuracion (.json):", v_cfg, "abrir", [("JSON", "*.json")])
    frm.columnconfigure(1, weight=1)
    txt = scrolledtext.ScrolledText(frm, height=22, font=("Consolas", 9)); txt.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=8)
    frm.rowconfigure(5, weight=1)
    btn = ttk.Button(frm, text="METRAR")

    import queue
    cola = queue.Queue()

    def escribir(s):
        cola.put(("txt", s))                     # el hilo de calculo solo encola; la ventana se actualiza en el hilo principal

    def vaciar_cola():
        try:
            while True:
                tipo, dato = cola.get_nowait()
                if tipo == "txt": txt.insert("end", dato + "\n"); txt.see("end")
                elif tipo == "ok": btn.config(state="normal"); messagebox.showinfo("MetraP", "Metrado generado:\n" + dato)
                elif tipo == "error": btn.config(state="normal"); messagebox.showerror("MetraP", dato)
        except queue.Empty:
            pass
        root.after(100, vaciar_cola)
    root.after(100, vaciar_cola)

    def tarea():
        try:
            fn = correr(v_dxf.get(), v_pla.get(), v_sal.get(), v_cfg.get() or None, escribir)
            cola.put(("ok", fn))
        except Exception as e:
            escribir("ERROR: " + str(e)); escribir(traceback.format_exc()); cola.put(("error", str(e)))

    def iniciar():
        if not (v_dxf.get() and os.path.exists(v_dxf.get())): messagebox.showwarning("MetraP", "Elija el plano DXF"); return
        if not (v_pla.get() and os.path.exists(v_pla.get())): messagebox.showwarning("MetraP", "Elija la plantilla Excel"); return
        if not v_sal.get(): messagebox.showwarning("MetraP", "Indique el archivo de salida"); return
        txt.delete("1.0", "end"); btn.config(state="disabled")
        threading.Thread(target=tarea, daemon=True).start()
    btn.config(command=iniciar); btn.grid(row=4, column=1, pady=6)
    ttk.Label(frm, text="Regla: cunetas con H > 0.40 m (desde el NCT) llevan acero; las tapadas siempre. Azul = tramo abierto, verde = tapado. Editar metrap_config.json para otro proyecto.", foreground="#555").grid(row=6, column=0, columnspan=3, sticky="w")
    root.mainloop()


def main():
    ap = argparse.ArgumentParser(description="MetraP: metrado de cunetas desde DXF")
    ap.add_argument("--dxf"); ap.add_argument("--plantilla", default=PLANTILLA_DEF); ap.add_argument("--salida"); ap.add_argument("--config", default=CONFIG_DEF)
    a = ap.parse_args()
    if a.dxf:
        salida = a.salida or os.path.splitext(a.dxf)[0] + "_METRADO.xlsx"
        correr(a.dxf, a.plantilla, salida, a.config if os.path.exists(a.config) else None)
    else:
        gui()


if __name__ == "__main__":
    main()
