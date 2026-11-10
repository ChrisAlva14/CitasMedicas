import tkinter as tk
from tkinter import messagebox, ttk

from paciente import Paciente
from tabla_consultorios import CONSULTORIOS, NUM_CONSULTORIOS, TablaConsultorios
from validaciones import (
    DEPARTAMENTOS,
    INSTITUCIONES,
    PRIORIDADES,
    validar_dui,
    validar_telefono,
)

FUENTE = "Segoe UI"

COLOR = {
    "fondo": "#eef2f7",
    "panel": "#ffffff",
    "borde": "#d4dee9",
    "texto": "#16324a",
    "suave": "#5a7085",
    "acento": "#0b6e75",
    "acento_oscuro": "#08565c",
    "navy": "#12304a",
    "navy_suave": "#1d4666",
    "alerta": "#b45309",
    "error": "#b3261e",
    "exito": "#1e7d4f",
    "nodo": "#eaf2fb",
    "nodo_borde": "#a8c3dc",
    "nuevo": "#fff6dd",
    "nuevo_borde": "#d99a1f",
    "encontrado": "#e7f8ee",
    "encontrado_borde": "#2f9e6b",
}


class EntradaConPista(ttk.Entry):
    """Entry con un texto de ejemplo que desaparece al escribir.

    ``valor()`` devuelve "" mientras solo se vea la pista, así el formulario
    nunca confunde el ejemplo con un dato real del paciente.
    """

    def __init__(self, padre, variable, pista, **opciones):
        super().__init__(padre, textvariable=variable, **opciones)
        self.variable = variable
        self.pista = pista
        self.mostrando_pista = True
        self.variable.set(pista)
        self.configure(foreground="#9aa8b4")
        self.bind("<FocusIn>", self._entrar)
        self.bind("<FocusOut>", self._salir)

    def _entrar(self, _evento):
        if self.mostrando_pista:
            self.variable.set("")
            self.configure(foreground=COLOR["texto"])
            self.mostrando_pista = False

    def _salir(self, _evento):
        if not self.variable.get().strip():
            self.mostrando_pista = True
            self.variable.set(self.pista)
            self.configure(foreground="#9aa8b4")

    def valor(self):
        return "" if self.mostrando_pista else self.variable.get().strip()

    def limpiar(self):
        # Si el campo tiene el foco (por ejemplo, tras registrar con Enter),
        # se deja vacío de verdad para que lo escrito no se mezcle con la pista.
        if self.focus_get() is self:
            self.mostrando_pista = False
            self.variable.set("")
            self.configure(foreground=COLOR["texto"])
            return
        self.mostrando_pista = True
        self.variable.set(self.pista)
        self.configure(foreground="#9aa8b4")


class AplicacionCitas:
    """Ventana principal con el formulario a la izquierda y la tabla a la derecha."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.tabla = TablaConsultorios()

        # DUI que se resalta en el dibujo: el recién insertado y el buscado.
        self.nuevo = None
        self.resaltado = None
        self.dui_gestion = None
        self._redibujo_pendiente = None

        self._configurar_ventana()
        self._configurar_estilos()
        self._construir_encabezado()
        self._construir_cuerpo()
        self._construir_pie()

        self.actualizar_resumen()
        self.raiz.after(80, self.dibujar_tabla)

    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA VENTANA
    # ------------------------------------------------------------------
    def _configurar_ventana(self):
        self.raiz.title("Registro de Citas Médicas - El Salvador")
        self.raiz.geometry("1180x840")
        self.raiz.minsize(1020, 780)
        self.raiz.configure(bg=COLOR["fondo"])
        self.raiz.columnconfigure(0, weight=1)
        self.raiz.rowconfigure(1, weight=1)

    def _configurar_estilos(self):
        estilo = ttk.Style(self.raiz)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure("TFrame", background=COLOR["fondo"])
        estilo.configure("Panel.TFrame", background=COLOR["panel"])
        estilo.configure("Pagina.TFrame", background=COLOR["panel"])
        estilo.configure(
            "TLabel",
            background=COLOR["fondo"],
            foreground=COLOR["texto"],
            font=(FUENTE, 10),
        )
        estilo.configure(
            "Panel.TLabel",
            background=COLOR["panel"],
            foreground=COLOR["texto"],
            font=(FUENTE, 10),
        )
        estilo.configure(
            "Titulo.TLabel",
            background=COLOR["panel"],
            foreground=COLOR["texto"],
            font=(FUENTE, 13, "bold"),
        )
        estilo.configure(
            "Suave.TLabel",
            background=COLOR["panel"],
            foreground=COLOR["suave"],
            font=(FUENTE, 9),
        )
        estilo.configure(
            "Campo.TLabel",
            background=COLOR["panel"],
            foreground=COLOR["suave"],
            font=(FUENTE, 9, "bold"),
        )
        estilo.configure(
            "Estado.TLabel",
            background=COLOR["navy"],
            foreground="#cfe3f1",
            font=(FUENTE, 9),
        )
        estilo.configure("TButton", font=(FUENTE, 10), padding=(8, 6))
        estilo.configure(
            "Accion.TButton",
            background=COLOR["acento"],
            foreground="white",
            font=(FUENTE, 10, "bold"),
            padding=(10, 8),
            borderwidth=0,
        )
        estilo.map(
            "Accion.TButton",
            background=[("active", COLOR["acento_oscuro"]), ("disabled", "#a9bcc9")],
            foreground=[("disabled", "#f0f4f7")],
        )
        estilo.configure(
            "Secundario.TButton",
            background="#e6edf4",
            foreground=COLOR["texto"],
            padding=(10, 8),
            borderwidth=0,
        )
        estilo.map("Secundario.TButton", background=[("active", "#d5e1ec")])
        estilo.configure(
            "Peligro.TButton",
            background="#fdeceb",
            foreground=COLOR["error"],
            font=(FUENTE, 10, "bold"),
            padding=(10, 8),
            borderwidth=0,
        )
        estilo.map(
            "Peligro.TButton",
            background=[("active", "#f9d8d5"), ("disabled", "#f1f3f5")],
            foreground=[("disabled", "#9aa8b4")],
        )
        estilo.configure("TNotebook", background=COLOR["fondo"], borderwidth=0)
        estilo.configure(
            "TNotebook.Tab",
            background="#dde6ef",
            foreground=COLOR["suave"],
            padding=(16, 9),
            font=(FUENTE, 10),
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", COLOR["panel"])],
            foreground=[("selected", COLOR["acento"])],
        )
        estilo.configure("TEntry", padding=5)
        estilo.configure("TCombobox", padding=4)

    def _construir_encabezado(self):
        encabezado = tk.Frame(self.raiz, bg=COLOR["navy"], height=78)
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_propagate(False)

        caja = tk.Frame(encabezado, bg=COLOR["navy"])
        caja.pack(side="left", padx=24, pady=14)

        tk.Label(
            caja,
            text="Registro de Citas Médicas",
            bg=COLOR["navy"],
            fg="white",
            font=(FUENTE, 19, "bold"),
        ).pack(anchor="w")
        tk.Label(
            caja,
            text="El Salvador · Hashing abierto con 4 consultorios · listas enlazadas",
            bg=COLOR["navy"],
            fg="#a9c9de",
            font=(FUENTE, 9),
        ).pack(anchor="w")

        insignia = tk.Frame(encabezado, bg=COLOR["navy_suave"])
        insignia.pack(side="right", padx=24)
        tk.Label(
            insignia,
            text="m = 4",
            bg=COLOR["navy_suave"],
            fg="white",
            font=(FUENTE, 15, "bold"),
        ).pack(padx=18, pady=4)
        tk.Label(
            insignia,
            text="consultorio = DUI % 4",
            bg=COLOR["navy_suave"],
            fg="#a9c9de",
            font=(FUENTE, 8),
        ).pack(padx=18, pady=(0, 6))

    def _construir_cuerpo(self):
        cuerpo = ttk.Frame(self.raiz, padding=14)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.columnconfigure(0, minsize=410, weight=0)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        self.cuaderno = ttk.Notebook(cuerpo)
        self.cuaderno.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        self._pestana_registrar()
        self._pestana_consultar()
        self._pestana_gestionar()

        self._panel_derecho(cuerpo)

    # ------------------------------------------------------------------
    # PESTAÑA: REGISTRAR
    # ------------------------------------------------------------------
    def _pestana_registrar(self):
        marco = ttk.Frame(self.cuaderno, padding=16, style="Pagina.TFrame")
        self.cuaderno.add(marco, text="Registrar")

        titulo = ttk.Label(marco, text="Nueva cita", style="Titulo.TLabel")
        titulo.grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            marco,
            text="El consultorio lo decide el hash, no el motivo.",
            style="Suave.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.var_dui = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_motivo = tk.StringVar()
        self.var_departamento = tk.StringVar(value="San Salvador")
        self.var_institucion = tk.StringVar(value="MINSAL")
        self.var_prioridad = tk.StringVar(value="Media")

        self.entradas = {}
        self._etiqueta_campo(marco, 2, 0, "DUI (########-#)")
        self._etiqueta_campo(marco, 2, 1, "Teléfono (####-####)")
        self._entrada_campo(marco, 2, 0, self.var_dui, "04567812-3", "dui")
        self._entrada_campo(marco, 2, 1, self.var_telefono, "7781-2043", "telefono")

        self._etiqueta_campo(marco, 4, 0, "Nombre completo", 2)
        self._entrada_campo(
            marco, 4, 0, self.var_nombre, "María José Hernández Flores", "nombre", 2
        )

        self._etiqueta_campo(marco, 6, 0, "Departamento")
        self._etiqueta_campo(marco, 6, 1, "Institución")
        self._combo_campo(marco, 6, 0, self.var_departamento, DEPARTAMENTOS)
        self._combo_campo(marco, 6, 1, self.var_institucion, INSTITUCIONES)

        self._etiqueta_campo(marco, 8, 0, "Motivo de consulta", 2)
        self._entrada_campo(marco, 8, 0, self.var_motivo, "Control prenatal", "motivo", 2)

        self._etiqueta_campo(marco, 10, 0, "Prioridad")
        self._combo_campo(marco, 10, 0, self.var_prioridad, PRIORIDADES)

        fila = 12
        botones = ttk.Frame(marco, style="Panel.TFrame")
        botones.grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(14, 6))

        ttk.Button(
            botones,
            text="Registrar cita",
            style="Accion.TButton",
            command=self.registrar_cita,
        ).pack(side="left")
        ttk.Button(
            botones,
            text="Limpiar",
            style="Secundario.TButton",
            command=self.limpiar_formulario,
        ).pack(side="left", padx=8)

        self.lbl_resultado = ttk.Label(
            marco,
            text="Complete los datos y presione Registrar cita.",
            style="Suave.TLabel",
            wraplength=330,
            justify="left",
        )
        self.lbl_resultado.grid(row=fila + 1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        nota = tk.Frame(
            marco,
            bg="#f4f8fb",
            highlightbackground="#dbe7f1",
            highlightthickness=1,
        )
        nota.grid(row=fila + 2, column=0, columnspan=2, sticky="sew", pady=(16, 0))
        tk.Label(
            nota,
            text=(
                "¿Cómo funciona el hash?\n"
                "Se quita el guion del DUI, se convierte a número entero y se calcula "
                "DUI % 4. Ese resultado es el consultorio. Si ya tiene pacientes, el "
                "nuevo nodo se enlaza al final de esa misma lista."
            ),
            bg="#f4f8fb",
            fg=COLOR["suave"],
            font=(FUENTE, 8),
            justify="left",
            wraplength=330,
        ).pack(anchor="w", padx=10, pady=8)

        for columna in (0, 1):
            marco.columnconfigure(columna, weight=1, uniform="formulario")
        marco.rowconfigure(fila + 2, weight=1)

        # Enter dentro de un campo registra la cita.
        self.raiz.bind("<Return>", self._enter_registrar)

    def _enter_registrar(self, evento):
        if self.cuaderno.index("current") == 0:
            self.registrar_cita()

    def _etiqueta_campo(self, padre, fila, columna, texto, columnas=1):
        margen = (0, 8) if columna == 0 and columnas == 1 else 0
        ttk.Label(padre, text=texto, style="Campo.TLabel").grid(
            row=fila,
            column=columna,
            columnspan=columnas,
            sticky="w",
            pady=(7, 2),
            padx=margen,
        )

    def _entrada_campo(self, padre, fila, columna, variable, pista, clave, columnas=1):
        margen = (0, 8) if columna == 0 and columnas == 1 else 0
        entrada = EntradaConPista(
            padre, variable, pista, width=(20 if columnas == 1 else 40)
        )
        entrada.grid(
            row=fila + 1,
            column=columna,
            columnspan=columnas,
            sticky="ew",
            padx=margen,
        )
        self.entradas[clave] = entrada

    def _combo_campo(self, padre, fila, columna, variable, opciones, columnas=1):
        margen = (0, 8) if columna == 0 and columnas == 1 else 0
        combo = ttk.Combobox(
            padre,
            textvariable=variable,
            values=opciones,
            state="readonly",
            width=(18 if columnas == 1 else 38),
        )
        combo.grid(
            row=fila + 1,
            column=columna,
            columnspan=columnas,
            sticky="ew",
            padx=margen,
        )

    # ------------------------------------------------------------------
    # PESTAÑA: CONSULTAR
    # ------------------------------------------------------------------
    def _pestana_consultar(self):
        marco = ttk.Frame(self.cuaderno, padding=16, style="Pagina.TFrame")
        self.cuaderno.add(marco, text="Consultar")

        ttk.Label(marco, text="Buscar turno por DUI", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            marco,
            text="Se recorre solo la cadena del consultorio calculado.",
            style="Suave.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.var_busqueda = tk.StringVar()
        ttk.Label(marco, text="DUI (formato ########-#)", style="Campo.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 2)
        )
        entrada = ttk.Entry(marco, textvariable=self.var_busqueda, width=42)
        entrada.grid(row=3, column=0, columnspan=2, sticky="ew")
        entrada.bind("<Return>", lambda e: self.buscar_turno())

        ttk.Button(
            marco,
            text="Buscar turno",
            style="Accion.TButton",
            command=self.buscar_turno,
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 10))

        self.texto_busqueda = self._crear_texto(marco, fila=5, alto=13)
        marco.rowconfigure(5, weight=1)
        marco.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # PESTAÑA: GESTIONAR
    # ------------------------------------------------------------------
    def _pestana_gestionar(self):
        marco = ttk.Frame(self.cuaderno, padding=16, style="Pagina.TFrame")
        self.cuaderno.add(marco, text="Cancelar / Atender")

        ttk.Label(marco, text="Cancelar o atender cita", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            marco,
            text="Al eliminar se desenlaza el nodo y la cadena se reconecta.",
            style="Suave.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.var_gestion = tk.StringVar()
        ttk.Label(marco, text="DUI (formato ########-#)", style="Campo.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 2)
        )
        entrada = ttk.Entry(marco, textvariable=self.var_gestion, width=42)
        entrada.grid(row=3, column=0, columnspan=2, sticky="ew")
        entrada.bind("<Return>", lambda e: self.buscar_gestion())

        ttk.Button(
            marco,
            text="Buscar cita",
            style="Secundario.TButton",
            command=self.buscar_gestion,
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 8))

        self.boton_eliminar = ttk.Button(
            marco,
            text="Cancelar / marcar como atendida",
            style="Peligro.TButton",
            command=self.eliminar_cita,
            state="disabled",
        )
        self.boton_eliminar.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.texto_gestion = self._crear_texto(marco, fila=6, alto=11)
        marco.rowconfigure(6, weight=1)
        marco.columnconfigure(0, weight=1)

    def _crear_texto(self, padre, fila, alto):
        caja = tk.Frame(padre, bg=COLOR["borde"], padx=1, pady=1)
        caja.grid(row=fila, column=0, columnspan=2, sticky="nsew")
        texto = tk.Text(
            caja,
            height=alto,
            width=42,
            wrap="word",
            font=(FUENTE, 9),
            bg="#f8fbfe",
            fg=COLOR["texto"],
            relief="flat",
            padx=10,
            pady=8,
            state="disabled",
            cursor="arrow",
        )
        texto.pack(fill="both", expand=True)
        return texto

    # ------------------------------------------------------------------
    # PANEL DERECHO: DIBUJO DE LA TABLA HASH
    # ------------------------------------------------------------------
    def _panel_derecho(self, padre):
        panel = tk.Frame(padre, bg=COLOR["panel"], highlightbackground=COLOR["borde"],
                         highlightthickness=1)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        cabecera = tk.Frame(panel, bg=COLOR["panel"])
        cabecera.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))
        tk.Label(
            cabecera,
            text="Tabla hash · encadenamiento separado",
            bg=COLOR["panel"],
            fg=COLOR["texto"],
            font=(FUENTE, 12, "bold"),
        ).pack(side="left")

        self.lbl_total = tk.StringVar(value="0 pacientes")
        tk.Label(
            cabecera,
            textvariable=self.lbl_total,
            bg="#e6f2f2",
            fg=COLOR["acento"],
            font=(FUENTE, 9, "bold"),
            padx=10,
            pady=3,
        ).pack(side="right")

        leyenda = tk.Frame(panel, bg=COLOR["panel"])
        leyenda.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 6))
        self._chip_leyenda(leyenda, COLOR["nuevo"], COLOR["nuevo_borde"], "recién insertado")
        self._chip_leyenda(leyenda, COLOR["encontrado"], COLOR["encontrado_borde"], "encontrado")
        self._chip_leyenda(leyenda, COLOR["nodo"], COLOR["nodo_borde"], "nodo de la cadena")

        self.lienzo = tk.Canvas(
            panel,
            bg=COLOR["panel"],
            highlightthickness=0,
            height=456,
        )
        self.lienzo.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 8))
        self.lienzo.bind("<Configure>", self._al_redimensionar)

        resumen = tk.Frame(panel, bg="#f7fafc", highlightbackground=COLOR["borde"],
                           highlightthickness=1)
        resumen.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 14))
        resumen.columnconfigure(0, weight=1)

        superior = tk.Frame(resumen, bg="#f7fafc")
        superior.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))

        self.var_fila_larga = tk.StringVar(value="Fila más larga: —")
        tk.Label(
            superior,
            textvariable=self.var_fila_larga,
            bg="#f7fafc",
            fg=COLOR["suave"],
            font=(FUENTE, 9),
            anchor="w",
        ).pack(side="left")

        tk.Button(
            superior,
            text="Resumen detallado",
            command=self.mostrar_resumen,
            bg="#e6f2f2",
            fg=COLOR["acento"],
            activebackground="#d3e8e8",
            activeforeground=COLOR["acento_oscuro"],
            relief="flat",
            borderwidth=0,
            font=(FUENTE, 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2,
        ).pack(side="right")

        chips = tk.Frame(resumen, bg="#f7fafc")
        chips.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 9))
        chips.columnconfigure(0, weight=1)
        chips.columnconfigure(1, weight=1)
        self.vars_consultorio = []
        for box in range(NUM_CONSULTORIOS):
            variable = tk.StringVar()
            self.vars_consultorio.append(variable)
            tk.Label(
                chips,
                textvariable=variable,
                bg="white",
                fg=COLOR["texto"],
                font=(FUENTE, 8),
                padx=10,
                pady=5,
                anchor="w",
                highlightbackground=COLOR["borde"],
                highlightthickness=1,
                justify="left",
            ).grid(row=box // 2, column=box % 2, sticky="ew", padx=4, pady=2)

    def _chip_leyenda(self, padre, relleno, borde, texto):
        caja = tk.Frame(padre, bg=COLOR["panel"])
        caja.pack(side="left", padx=(0, 14))
        tk.Frame(caja, bg=relleno, highlightbackground=borde, highlightthickness=1,
                 width=14, height=14).pack(side="left", pady=1)
        tk.Label(
            caja,
            text=texto,
            bg=COLOR["panel"],
            fg=COLOR["suave"],
            font=(FUENTE, 8),
        ).pack(side="left", padx=5)

    def _construir_pie(self):
        pie = tk.Frame(self.raiz, bg=COLOR["navy"], height=30)
        pie.grid(row=2, column=0, sticky="ew")
        pie.grid_propagate(False)

        self.var_estado = tk.StringVar(
            value="Listo. La tabla comienza vacía: registre el primer paciente."
        )
        tk.Label(
            pie,
            textvariable=self.var_estado,
            bg=COLOR["navy"],
            fg="#cfe3f1",
            font=(FUENTE, 9),
            anchor="w",
        ).pack(side="left", padx=20, pady=6)
        tk.Label(
            pie,
            text="hashes con listas enlazadas · sin dict ni set",
            bg=COLOR["navy"],
            fg="#7fa4bf",
            font=(FUENTE, 8),
        ).pack(side="right", padx=20)

    # ------------------------------------------------------------------
    # DIBUJO
    # ------------------------------------------------------------------
    def _al_redimensionar(self, _evento=None):
        if self._redibujo_pendiente is not None:
            self.raiz.after_cancel(self._redibujo_pendiente)
        self._redibujo_pendiente = self.raiz.after(60, self.dibujar_tabla)

    def _recortar(self, texto, maximo):
        texto = texto or ""
        if maximo < 4:
            maximo = 4
        if len(texto) <= maximo:
            return texto
        return texto[: maximo - 1].rstrip() + "…"

    def _dibujar_flecha(self, x, cy, largo):
        self.lienzo.create_line(
            x + 4,
            cy,
            x + largo - 4,
            cy,
            fill="#8aa4bb",
            width=2,
            arrow="last",
            arrowshape=(7, 9, 3),
        )

    def _dibujar_nodo(self, x, y, ancho, paciente):
        alto = 40
        if paciente.dui == self.resaltado:
            relleno, borde, grosor = (
                COLOR["encontrado"],
                COLOR["encontrado_borde"],
                2,
            )
        elif paciente.dui == self.nuevo:
            relleno, borde, grosor = (COLOR["nuevo"], COLOR["nuevo_borde"], 2)
        else:
            relleno, borde, grosor = (COLOR["nodo"], COLOR["nodo_borde"], 1)

        self.lienzo.create_rectangle(
            x, y, x + ancho, y + alto, fill=relleno, outline=borde, width=grosor
        )
        self.lienzo.create_text(
            x + ancho / 2,
            y + 13,
            text=paciente.dui,
            font=(FUENTE, 9, "bold"),
            fill=COLOR["texto"],
        )
        maximo = max(6, int((ancho - 8) / 4.6))
        self.lienzo.create_text(
            x + ancho / 2,
            y + 28,
            text=self._recortar(paciente.nombre, maximo),
            font=(FUENTE, 7),
            fill=COLOR["suave"],
        )

    def dibujar_tabla(self):
        """Dibuja los 4 consultorios y sus cadenas de nodos."""
        self._redibujo_pendiente = None
        lienzo = self.lienzo
        lienzo.delete("all")

        ancho = lienzo.winfo_width()
        if ancho < 320:
            ancho = 720

        alto_lienzo = lienzo.winfo_height()
        if alto_lienzo < 380:
            alto_lienzo = 456

        # Las 4 filas se reparten la altura disponible del lienzo.
        alto_fila = (alto_lienzo - 8) / NUM_CONSULTORIOS
        alto_fila = max(96.0, min(118.0, alto_fila))

        for box in range(NUM_CONSULTORIOS):
            y = 4 + box * alto_fila
            alto_caja = alto_fila - 6
            cy = y + alto_caja - 10 - 20  # centro vertical del nodo

            lienzo.create_rectangle(
                6,
                y,
                ancho - 6,
                y + alto_caja,
                fill="#ffffff",
                outline=COLOR["borde"],
            )

            centro = y + 20
            lienzo.create_oval(
                17, centro - 12, 41, centro + 12, fill=COLOR["acento"], outline=""
            )
            lienzo.create_text(
                29,
                centro,
                text=str(box + 1),
                fill="white",
                font=(FUENTE, 11, "bold"),
            )

            lienzo.create_text(
                50,
                y + 12,
                text=CONSULTORIOS[box],
                anchor="w",
                fill=COLOR["texto"],
                font=(FUENTE, 10, "bold"),
            )

            cantidad = self.tabla.contar_consultorio(box)
            etiqueta = "1 paciente" if cantidad == 1 else f"{cantidad} pacientes"
            lienzo.create_text(
                50,
                y + 29,
                text=etiqueta,
                anchor="w",
                fill=COLOR["suave"],
                font=(FUENTE, 8),
            )

            if cantidad >= 2:
                lienzo.create_text(
                    ancho - 18,
                    y + 18,
                    text=f"COLISIÓN · {cantidad} encadenados",
                    anchor="e",
                    fill=COLOR["alerta"],
                    font=(FUENTE, 8, "bold"),
                )

            cadena = []
            actual = self.tabla.consultorios[box]
            while actual is not None:
                cadena.append(actual)
                actual = actual.siguiente

            if not cadena:
                lienzo.create_text(
                    20,
                    cy,
                    text="NULL",
                    anchor="w",
                    fill="#9aa8b4",
                    font=(FUENTE, 9, "bold"),
                )
                lienzo.create_text(
                    68,
                    cy,
                    text="(consultorio vacío)",
                    anchor="w",
                    fill="#9aa8b4",
                    font=(FUENTE, 8),
                )
                continue

            n = len(cadena)
            separacion = 30
            disponible = ancho - 40 - 58
            ancho_nodo = min(150, max(96, (disponible - (n - 1) * separacion) / n))

            x = 18
            for indice, paciente in enumerate(cadena):
                self._dibujar_nodo(x, cy - 20, ancho_nodo, paciente)
                x += ancho_nodo
                if indice < n - 1:
                    self._dibujar_flecha(x, cy, separacion)
                    x += separacion

            self._dibujar_flecha(x, cy, 28)
            lienzo.create_text(
                x + 34,
                cy,
                text="NULL",
                anchor="w",
                fill="#9aa8b4",
                font=(FUENTE, 9, "bold"),
            )

    # ------------------------------------------------------------------
    # RESUMEN
    # ------------------------------------------------------------------
    def actualizar_resumen(self):
        total = self.tabla.total_pacientes
        self.lbl_total.set(f"{total} paciente" if total == 1 else f"{total} pacientes")

        for box in range(NUM_CONSULTORIOS):
            cantidad = self.tabla.contar_consultorio(box)
            texto = f"{CONSULTORIOS[box]}\n{cantidad} paciente"
            if cantidad != 1:
                texto += "s"
            self.vars_consultorio[box].set(texto)

        if total == 0:
            self.var_fila_larga.set("Fila más larga: —")
            return

        largos = [self.tabla.contar_consultorio(box) for box in range(NUM_CONSULTORIOS)]
        maximo = max(largos)
        indices = [box for box in range(NUM_CONSULTORIOS) if largos[box] == maximo]
        if len(indices) == 1:
            box = indices[0]
            self.var_fila_larga.set(
                f"Fila más larga: {CONSULTORIOS[box]} con {maximo} paciente(s)"
            )
        else:
            nombres = ", ".join(CONSULTORIOS[box] for box in indices)
            self.var_fila_larga.set(f"Fila más larga: empate entre {nombres} con {maximo}")

    def _texto_resumen(self):
        """Arma el resumen completo: consultorios, departamentos y fila más larga."""
        total = self.tabla.total_pacientes
        lineas = [
            "RESUMEN DE LA UNIDAD DE SALUD",
            "",
            f"Total de pacientes: {total}",
            "",
            "Pacientes por consultorio:",
        ]
        for box in range(NUM_CONSULTORIOS):
            lineas.append(
                f"  {CONSULTORIOS[box]}: "
                f"{self.tabla.contar_consultorio(box)}"
            )

        # Conteo por departamento hecho a mano (sin dict ni set).
        conteo = []  # cada elemento es [departamento, cantidad]
        for box in range(NUM_CONSULTORIOS):
            actual = self.tabla.consultorios[box]
            while actual is not None:
                encontrado = False
                for item in conteo:
                    if item[0] == actual.departamento:
                        item[1] += 1
                        encontrado = True
                        break
                if not encontrado:
                    conteo.append([actual.departamento, 1])
                actual = actual.siguiente

        lineas += ["", "Pacientes por departamento:"]
        if not conteo:
            lineas.append("  No hay pacientes registrados.")
        else:
            # Ordenamiento manual de mayor a menor por cantidad.
            for i in range(len(conteo)):
                for j in range(i + 1, len(conteo)):
                    if conteo[j][1] > conteo[i][1]:
                        conteo[i], conteo[j] = conteo[j], conteo[i]
            for departamento, cantidad in conteo:
                lineas.append(f"  {departamento}: {cantidad}")

        lineas += ["", "Consultorio con la fila más larga:"]
        if total == 0:
            lineas.append("  Aún no hay pacientes registrados.")
        else:
            largos = [
                self.tabla.contar_consultorio(box) for box in range(NUM_CONSULTORIOS)
            ]
            maximo = max(largos)
            indices = [box for box in range(NUM_CONSULTORIOS) if largos[box] == maximo]
            if len(indices) == 1:
                box = indices[0]
                lineas.append(
                    f"  {CONSULTORIOS[box]} con {maximo} paciente(s)."
                )
            else:
                nombres = ", ".join(
                    CONSULTORIOS[box] for box in indices
                )
                lineas.append(
                    f"  Empate entre {nombres}, con {maximo} paciente(s) cada uno."
                )

        return "\n".join(lineas)

    def mostrar_resumen(self):
        """Abre una ventana con el resumen completo de la unidad de salud."""
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Resumen de la unidad de salud")
        ventana.configure(bg=COLOR["panel"])
        ventana.transient(self.raiz)
        ventana.resizable(False, False)

        caja = tk.Frame(ventana, bg=COLOR["panel"], padx=16, pady=14)
        caja.pack(fill="both", expand=True)

        tk.Label(
            caja,
            text="Resumen de la unidad de salud",
            bg=COLOR["panel"],
            fg=COLOR["texto"],
            font=(FUENTE, 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        texto = tk.Text(
            caja,
            width=50,
            height=23,
            wrap="word",
            font=(FUENTE, 9),
            bg="#f8fbfe",
            fg=COLOR["texto"],
            relief="flat",
            padx=10,
            pady=8,
            state="disabled",
            cursor="arrow",
            highlightbackground=COLOR["borde"],
            highlightthickness=1,
        )
        texto.pack(fill="both", expand=True)
        self._escribir(texto, self._texto_resumen())

        ttk.Button(
            caja,
            text="Cerrar",
            style="Secundario.TButton",
            command=ventana.destroy,
        ).pack(anchor="e", pady=(10, 0))

        ventana.update_idletasks()
        x = self.raiz.winfo_rootx() + (self.raiz.winfo_width() - ventana.winfo_width()) // 2
        y = self.raiz.winfo_rooty() + (self.raiz.winfo_height() - ventana.winfo_height()) // 2
        ventana.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # ------------------------------------------------------------------
    # ACCIONES
    # ------------------------------------------------------------------
    def registrar_cita(self):
        dui = self.entradas["dui"].valor()
        nombre = self.entradas["nombre"].valor()
        telefono = self.entradas["telefono"].valor()
        motivo = self.entradas["motivo"].valor()

        if not validar_dui(dui):
            return self._error_registro("DUI inválido. Use el formato ########-#, ejemplo 04567812-3.")
        if not nombre:
            return self._error_registro("Escriba el nombre completo del paciente.")
        if not validar_telefono(telefono):
            return self._error_registro("Teléfono inválido. Use el formato ####-####, ejemplo 7781-2043.")
        if not motivo:
            return self._error_registro("Escriba el motivo de consulta.")

        existente, _, _ = self.tabla.buscar(dui)
        if existente is not None:
            return self._error_registro(
                f"El DUI {dui} ya tiene una cita a nombre de {existente.nombre}."
            )

        paciente = Paciente(
            dui,
            nombre,
            telefono,
            self.var_departamento.get(),
            self.var_institucion.get(),
            motivo,
            self.var_prioridad.get(),
        )

        try:
            consultorio, colision = self.tabla.insertar(paciente)
        except ValueError as error:
            return self._error_registro(str(error))

        self.nuevo = dui
        self.resaltado = None
        self.actualizar_resumen()
        self.dibujar_tabla()

        numero = dui.replace("-", "")
        lineas = [
            f"Cita registrada: {nombre}",
            f"{numero} % {NUM_CONSULTORIOS} = {paciente.dui_numerico() % NUM_CONSULTORIOS}"
            f"  →  {CONSULTORIOS[consultorio]}",
        ]
        if colision:
            lineas.append("¡Colisión! Se encadena al final de la fila de ese consultorio.")
        else:
            lineas.append("El consultorio estaba vacío: el paciente es el primero en la fila.")

        self.lbl_resultado.configure(
            text="\n".join(lineas), foreground=COLOR["exito"]
        )
        self.var_estado.set(
            f"Registrado {paciente.dui} en el {CONSULTORIOS[consultorio]}"
            + (" (colisión resuelta por encadenamiento)." if colision else ".")
        )
        self.limpiar_formulario(silencioso=True)

    def _error_registro(self, mensaje):
        self.lbl_resultado.configure(text=mensaje, foreground=COLOR["error"])
        self.var_estado.set("No se registró la cita: revise los datos.")

    def limpiar_formulario(self, silencioso=False):
        self.entradas["dui"].limpiar()
        self.entradas["nombre"].limpiar()
        self.entradas["telefono"].limpiar()
        self.entradas["motivo"].limpiar()
        self.var_departamento.set("San Salvador")
        self.var_institucion.set("MINSAL")
        self.var_prioridad.set("Media")
        if not silencioso:
            self.lbl_resultado.configure(
                text="Formulario limpio. Complete los datos y presione Registrar cita.",
                foreground=COLOR["suave"],
            )
            self.var_estado.set("Formulario limpio.")

    def _leer_dui(self, variable):
        """Devuelve el DUI del campo o None (mostrando el error)."""
        dui = variable.get().strip()
        if not validar_dui(dui):
            messagebox.showwarning(
                "DUI inválido",
                "El DUI debe tener el formato ########-#.\nEjemplo: 04567812-3",
                parent=self.raiz,
            )
            return None
        return dui

    def buscar_turno(self):
        dui = self._leer_dui(self.var_busqueda)
        if dui is None:
            return

        paciente, consultorio, por_delante = self.tabla.buscar(dui)

        if paciente is None:
            self.resaltado = None
            self.dibujar_tabla()
            self._escribir(
                self.texto_busqueda,
                f"No existe una cita con el DUI {dui}.\n\n"
                f"El hash lo enviaría al {CONSULTORIOS[consultorio]} "
                f"y esa cadena no lo contiene.",
            )
            self.var_estado.set(f"Sin resultados para el DUI {dui}.")
            return

        self.resaltado = dui
        self.nuevo = None
        self.dibujar_tabla()

        detalle = [
            "CITA ENCONTRADA",
            "",
            f"DUI:          {paciente.dui}",
            f"Nombre:       {paciente.nombre}",
            f"Teléfono:     {paciente.telefono}",
            f"Departamento: {paciente.departamento}",
            f"Institución:  {paciente.institucion}",
            f"Motivo:       {paciente.motivo}",
            f"Prioridad:    {paciente.prioridad}",
            "",
            f"Consultorio:  {CONSULTORIOS[consultorio]}",
            f"Posición en la fila: {por_delante + 1}",
            f"Personas por delante: {por_delante}",
        ]
        if por_delante == 0:
            detalle.append("Es el próximo paciente en ser atendido.")
        self._escribir(self.texto_busqueda, "\n".join(detalle))
        self.var_estado.set(
            f"DUI {dui} encontrado en el {CONSULTORIOS[consultorio]}, "
            f"posición {por_delante + 1}."
        )

    def buscar_gestion(self):
        dui = self._leer_dui(self.var_gestion)
        if dui is None:
            return

        paciente, consultorio, por_delante = self.tabla.buscar(dui)
        self.dui_gestion = None
        self.boton_eliminar.configure(state="disabled")
        self.resaltado = None
        self.dibujar_tabla()

        if paciente is None:
            self._escribir(
                self.texto_gestion,
                f"No existe una cita con el DUI {dui}.",
            )
            self.var_estado.set(f"Sin resultados para el DUI {dui}.")
            return

        self.dui_gestion = dui
        self.resaltado = dui
        self.boton_eliminar.configure(state="normal")
        self.dibujar_tabla()

        detalle = [
            "CITA SELECCIONADA",
            "",
            f"DUI:          {paciente.dui}",
            f"Nombre:       {paciente.nombre}",
            f"Teléfono:     {paciente.telefono}",
            f"Departamento: {paciente.departamento}",
            f"Institución:  {paciente.institucion}",
            f"Motivo:       {paciente.motivo}",
            f"Prioridad:    {paciente.prioridad}",
            "",
            f"Consultorio:  {CONSULTORIOS[consultorio]}",
            f"Personas por delante: {por_delante}",
            "",
            "Puede cancelarla o marcarla como atendida con el botón rojo.",
        ]
        self._escribir(self.texto_gestion, "\n".join(detalle))
        self.var_estado.set(f"Cita seleccionada: {paciente.nombre}.")

    def eliminar_cita(self):
        if not self.dui_gestion:
            return

        paciente, consultorio, _ = self.tabla.buscar(self.dui_gestion)
        if paciente is None:
            self.boton_eliminar.configure(state="disabled")
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Cancelar o marcar como atendida la cita de:\n\n"
            f"{paciente.nombre}\nDUI {paciente.dui}\n"
            f"{CONSULTORIOS[consultorio]}\n\n"
            f"El nodo se desenlazará de la cadena.",
            parent=self.raiz,
        )
        if not confirmar:
            self.var_estado.set("Operación cancelada: el paciente sigue en la fila.")
            return

        eliminado = self.tabla.eliminar(self.dui_gestion)
        if eliminado is None:
            messagebox.showerror("Error", "No fue posible eliminar la cita.", parent=self.raiz)
            return

        self.dui_gestion = None
        self.resaltado = None
        self.nuevo = None
        self.boton_eliminar.configure(state="disabled")
        self.actualizar_resumen()
        self.dibujar_tabla()
        self._escribir(
            self.texto_gestion,
            f"Cita eliminada.\n\n{eliminado.nombre}\nDUI {eliminado.dui}\n\n"
            f"La cadena del {CONSULTORIOS[consultorio]} quedó reenlazada.",
        )
        self.var_estado.set(
            f"Cita de {eliminado.dui} eliminada del {CONSULTORIOS[consultorio]}."
        )

    def _escribir(self, widget, texto):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)
        widget.configure(state="disabled")


def main():
    # Texto nítido en pantallas con escalado de Windows.
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    raiz = tk.Tk()
    AplicacionCitas(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
