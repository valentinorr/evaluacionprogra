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

        # Añadir las pestañas al notebook
        self.notebook.add(self.tab_ingredientes, text="Ingreso de Ingredientes")
        self.notebook.add(self.tab_pedido, text="Pedido")

        # Configurar las interfaces dentro de cada pestaña
        self.crear_interfaz_ingredientes()
        self.crear_interfaz_pedido()

    def crear_interfaz_ingredientes(self):
        # Colocar el label y entry para el nombre del ingrediente
        label_nombre = CTkLabel(self.tab_ingredientes, text="Nombre del Ingrediente:")
        label_nombre.grid(row=0, column=0, padx=10, pady=10)
        self.entry_nombre = CTkEntry(self.tab_ingredientes)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10)

        # Colocar el label y entry para la cantidad
        label_cantidad = CTkLabel(self.tab_ingredientes, text="Cantidad:")
        label_cantidad.grid(row=1, column=0, padx=10, pady=10)
        self.entry_cantidad = CTkEntry(self.tab_ingredientes)
        self.entry_cantidad.grid(row=1, column=1, padx=10, pady=10)

        # Botón para ingresar ingrediente
        boton_ingresar = CTkButton(self.tab_ingredientes, text="Ingresar Ingrediente", command=self.agregar_ingrediente)
        boton_ingresar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Treeview para mostrar los ingredientes
        self.treeview_ingredientes = ttk.Treeview(self.tab_ingredientes, columns=("Nombre", "Cantidad"), show="headings")
        self.treeview_ingredientes.heading("Nombre", text="Nombre")
        self.treeview_ingredientes.heading("Cantidad", text="Cantidad")
        self.treeview_ingredientes.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Botón para eliminar ingrediente
        boton_eliminar = CTkButton(self.tab_ingredientes, text="Eliminar Ingrediente", command=self.eliminar_ingrediente)
        boton_eliminar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Botón para generar menú
        boton_generar_menu = CTkButton(self.tab_ingredientes, text="Generar Menú", command=self.mostrar_pestaña_pedido)
        boton_generar_menu.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def agregar_ingrediente(self):
        nombre = self.entry_nombre.get().strip().lower()
        cantidad = self.entry_cantidad.get().strip()

        if not nombre or not cantidad.isdigit():
            messagebox.showerror("Error", "Por favor, ingrese un nombre válido y una cantidad numérica.")
            return

        cantidad = int(cantidad)
        ingrediente = Ingrediente(nombre, cantidad)
        self.stock.agregar_ingrediente(ingrediente)

        # Actualizar el Treeview
        self.treeview_ingredientes.insert('', 'end', values=(nombre, cantidad))

        # Limpiar las entradas
        self.entry_nombre.delete(0, tk.END)
        self.entry_cantidad.delete(0, tk.END)

    def eliminar_ingrediente(self):
        # agregar la lógica para eliminar un ingrediente del stock y del Treeview
        pass

    def mostrar_pestaña_pedido(self):
        # agregar la lógica para mostrar la pestaña del pedido o cualquier otra funcionalidad
        pass

    def crear_interfaz_pedido(self):
        # agregar el código para la pestaña de "Pedido"
        pass

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
