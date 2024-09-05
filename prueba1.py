import tkinter as tk
from tkinter import ttk, messagebox
from customtkinter import CTk, CTkEntry, CTkButton, CTkFrame, CTkLabel
from fpdf import FPDF

class Ingrediente:
    def __init__(self, nombre, cantidad):
        self.nombre = nombre.strip().lower()
        self.cantidad = cantidad

class Menu:
    def __init__(self, nombre, precio, ingredientes):
        self.nombre = nombre
        self.precio = precio
        self.ingredientes = ingredientes

    def es_preparable(self, stock):
        for ingrediente, cantidad_necesaria in self.ingredientes.items():
            if stock.get(ingrediente, 0) < cantidad_necesaria:
                return False
        return True

    def preparar(self, stock):
        if self.es_preparable(stock):
            for ingrediente, cantidad_necesaria in self.ingredientes.items():
                stock[ingrediente] -= cantidad_necesaria
            return True
        return False

class Stock:
    def __init__(self):
        self.ingredientes = {}

    def agregar_ingrediente(self, ingrediente):
        nombre = ingrediente.nombre
        if nombre in self.ingredientes:
            self.ingredientes[nombre] += ingrediente.cantidad
        else:
            self.ingredientes[nombre] = ingrediente.cantidad

    def eliminar_ingrediente(self, nombre):
        nombre = nombre.strip().lower()
        if nombre in self.ingredientes:
            del self.ingredientes[nombre]

class Pedido:
    def __init__(self):
        self.menus = []

    def agregar_menu(self, menu):
        self.menus.append(menu)

    def eliminar_menu(self, menu):
        self.menus.remove(menu)

    def total(self):
        return sum(menu.precio for menu in self.menus)

    def generar_boleta(self, archivo_pdf="boleta.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Boleta de Compra", ln=True, align="C")

        for menu in self.menus:
            pdf.cell(200, 10, txt=f"{menu.nombre} - ${menu.precio}", ln=True)

        pdf.cell(200, 10, txt=f"Total: ${self.total()}", ln=True)
        pdf.output(archivo_pdf)

class Aplicacion(CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Restaurante")
        self.geometry("800x600")
        self.stock = Stock()
        self.pedido = Pedido()

        self.menus_disponibles = [
            Menu("Papas Fritas", 500, {"papas": 5}),
            Menu("Pepsi", 1100, {"bebida": 1}),
            Menu("Completo", 1800, {"vienesa": 1, "pan de completo": 1, "tomate": 1, "palta": 1}),
            Menu("Hamburguesa", 3500, {"pan de hamburguesa": 1, "lamina de queso": 1, "hamburguesa de carne": 1})
        ]

        # Crear el notebook para las pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Crear las pestañas
        self.tab_ingredientes = CTkFrame(self.notebook)
        self.tab_pedido = CTkFrame(self.notebook)

        self.notebook.add(self.tab_ingredientes, text="Ingreso de Ingredientes")
        self.notebook.add(self.tab_pedido, text="Pedido")

        # Configurar las interfaces dentro de cada pestaña
        self.crear_interfaz_ingredientes()
        self.crear_interfaz_pedido()

    def crear_interfaz_ingredientes(self):
        label_nombre = CTkLabel(self.tab_ingredientes, text="Nombre del Ingrediente:")
        label_nombre.grid(row=0, column=0, padx=10, pady=10)
        self.entry_nombre = CTkEntry(self.tab_ingredientes)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10)

        label_cantidad = CTkLabel(self.tab_ingredientes, text="Cantidad:")
        label_cantidad.grid(row=1, column=0, padx=10, pady=10)
        self.entry_cantidad = CTkEntry(self.tab_ingredientes)
        self.entry_cantidad.grid(row=1, column=1, padx=10, pady=10)

        boton_ingresar = CTkButton(self.tab_ingredientes, text="Ingresar Ingrediente", command=self.agregar_ingrediente)
        boton_ingresar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Treeview para mostrar los ingredientes
        self.treeview_ingredientes = ttk.Treeview(self.tab_ingredientes, columns=("Nombre", "Cantidad"), show="headings")
        self.treeview_ingredientes.heading("Nombre", text="Nombre")
        self.treeview_ingredientes.heading("Cantidad", text="Cantidad")
        self.treeview_ingredientes.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        boton_eliminar = CTkButton(self.tab_ingredientes, text="Eliminar Ingrediente", command=self.eliminar_ingrediente)
        boton_eliminar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        boton_generar_menu = CTkButton(self.tab_ingredientes, text="Generar Menú", command=self.mostrar_pestaña_pedido)
        boton_generar_menu.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def crear_interfaz_pedido(self):
        frame_superior = CTkFrame(self.tab_pedido)
        frame_superior.pack(fill="x", padx=10, pady=5)

        label_menus = CTkLabel(frame_superior, text="Menús Disponibles:")
        label_menus.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        for idx, menu in enumerate(self.menus_disponibles):
            boton_menu = CTkButton(frame_superior, text=f"{menu.nombre} - ${menu.precio}", 
                                   command=lambda m=menu: self.agregar_menu_a_pedido(m))
            boton_menu.grid(row=idx+1, column=0, padx=5, pady=5)

        frame_intermedio = CTkFrame(self.tab_pedido)
        frame_intermedio.pack(fill="x", padx=10, pady=5)

        self.treeview_pedido = ttk.Treeview(frame_intermedio, columns=("Nombre", "Cantidad", "Precio Unitario"), show="headings")
        self.treeview_pedido.heading("Nombre", text="Nombre del Menú")
        self.treeview_pedido.heading("Cantidad", text="Cantidad")
        self.treeview_pedido.heading("Precio Unitario", text="Precio Unitario")
        self.treeview_pedido.pack(side="left", fill="x", expand=True)

        self.label_total = CTkLabel(frame_intermedio, text="Total: $0")
        self.label_total.pack(side="right", padx=10)

        boton_eliminar_menu = CTkButton(frame_intermedio, text="Eliminar Menú", command=self.eliminar_menu_del_pedido)
        boton_eliminar_menu.pack(side="right", padx=10)

        frame_inferior = CTkFrame(self.tab_pedido)
        frame_inferior.pack(fill="x", padx=10, pady=5)

        boton_generar_boleta = CTkButton(frame_inferior, text="Generar Boleta", command=self.generar_boleta)
        boton_generar_boleta.pack(padx=10, pady=10)
