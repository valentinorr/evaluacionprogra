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
        
        # Información del restaurante
        pdf.cell(200, 10, txt="Restaurante XYZ", ln=True, align="C")
        pdf.cell(200, 10, txt="RUT: 99.999.999-9", ln=True, align="C")
        pdf.cell(200, 10, txt="Dirección: Calle Falsa 123", ln=True, align="C")
        pdf.cell(200, 10, txt="Teléfono: +56 9 9999 9999", ln=True, align="C")
        pdf.cell(200, 10, txt="=================================", ln=True, align="C")

        # Tabla de pedidos
        pdf.cell(100, 10, txt="Menú", border=1)
        pdf.cell(40, 10, txt="Cantidad", border=1)
        pdf.cell(50, 10, txt="Precio", border=1, ln=True)

        for menu in self.menus:
            pdf.cell(100, 10, txt=menu.nombre, border=1)
            pdf.cell(40, 10, txt="1", border=1)
            pdf.cell(50, 10, txt=f"${menu.precio}", border=1, ln=True)

        # Cálculos de total, IVA y subtotal
        subtotal = self.total()
        iva = subtotal * 0.19
        total = subtotal + iva

        pdf.cell(200, 10, txt="=================================", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Subtotal: ${subtotal:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"IVA (19%): ${iva:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Total: ${total:.2f}", ln=True)

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
        # Marco para organizar la entrada de ingredientes
        frame_izquierdo = CTkFrame(self.tab_ingredientes)
        frame_izquierdo.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        label_nombre = CTkLabel(frame_izquierdo, text="Nombre del Ingrediente:")
        label_nombre.grid(row=0, column=0, padx=10, pady=10)
        self.entry_nombre = CTkEntry(frame_izquierdo)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10)

        label_cantidad = CTkLabel(frame_izquierdo, text="Cantidad:")
        label_cantidad.grid(row=1, column=0, padx=10, pady=10)
        self.entry_cantidad = CTkEntry(frame_izquierdo)
        self.entry_cantidad.grid(row=1, column=1, padx=10, pady=10)

        boton_ingresar = CTkButton(frame_izquierdo, text="Ingresar Ingrediente", command=self.agregar_ingrediente)
        boton_ingresar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Treeview para mostrar los ingredientes, alineado a la derecha
        frame_derecho = CTkFrame(self.tab_ingredientes)
        frame_derecho.grid(row=0, column=1, padx=10, pady=20, sticky="n")
        self.treeview_ingredientes = ttk.Treeview(frame_derecho, columns=("Nombre", "Cantidad"), show="headings", height=20)
        self.treeview_ingredientes.heading("Nombre", text="Nombre")
        self.treeview_ingredientes.heading("Cantidad", text="Cantidad")
        self.treeview_ingredientes.column("Nombre", width=200)
        self.treeview_ingredientes.column("Cantidad", width=200)
        self.treeview_ingredientes.grid(row=0, column=0, padx=10, pady=10)

        # Botón para eliminar ingrediente
        boton_eliminar = CTkButton(frame_derecho, text="Eliminar Ingrediente", command=self.eliminar_ingrediente)
        boton_eliminar.grid(row=1, column=0, padx=10, pady=10)

        # Botón para generar menú
        boton_generar_menu = CTkButton(self.tab_ingredientes, text="Generar Menú", command=self.mostrar_pestaña_pedido)
        boton_generar_menu.grid(row=1, column=1, padx=10, pady=10, sticky="s")

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
        self.treeview_pedido.column("Nombre", width=200)
        self.treeview_pedido.column("Cantidad", width=100)
        self.treeview_pedido.column("Precio Unitario", width=100)
        self.treeview_pedido.grid(row=0, column=0, padx=5, pady=5)

        boton_eliminar_pedido = CTkButton(frame_intermedio, text="Eliminar Menú del Pedido", 
                                          command=self.eliminar_menu_del_pedido)
        boton_eliminar_pedido.grid(row=1, column=0, padx=5, pady=5)

        frame_inferior = CTkFrame(self.tab_pedido)
        frame_inferior.pack(fill="x", padx=10, pady=5)

        boton_generar_boleta = CTkButton(frame_inferior, text="Generar Boleta", command=self.generar_boleta)
        boton_generar_boleta.grid(row=0, column=0, padx=5, pady=5)

    def agregar_ingrediente(self):
        nombre = self.entry_nombre.get()
        cantidad = self.entry_cantidad.get()

        if not nombre or not cantidad.isdigit():
            messagebox.showerror("Error", "Nombre inválido o cantidad no numérica")
            return

        ingrediente = Ingrediente(nombre, int(cantidad))
        self.stock.agregar_ingrediente(ingrediente)
        self.actualizar_vista_ingredientes()

    def actualizar_vista_ingredientes(self):
        for i in self.treeview_ingredientes.get_children():
            self.treeview_ingredientes.delete(i)

        for nombre, cantidad in self.stock.ingredientes.items():
            self.treeview_ingredientes.insert("", "end", values=(nombre, cantidad))

    def eliminar_ingrediente(self):
        seleccion = self.treeview_ingredientes.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un ingrediente para eliminar")
            return

        ingrediente_seleccionado = self.treeview_ingredientes.item(seleccion)["values"][0]
        self.stock.eliminar_ingrediente(ingrediente_seleccionado)
        self.actualizar_vista_ingredientes()

    def agregar_menu_a_pedido(self, menu):
        if menu.preparar(self.stock.ingredientes):
            self.pedido.agregar_menu(menu)
            self.actualizar_vista_pedido()
        else:
            messagebox.showerror("Error", f"No hay suficientes ingredientes para preparar {menu.nombre}")

    def actualizar_vista_pedido(self):
        for i in self.treeview_pedido.get_children():
            self.treeview_pedido.delete(i)

        for menu in self.pedido.menus:
            self.treeview_pedido.insert("", "end", values=(menu.nombre, 1, menu.precio))

    def eliminar_menu_del_pedido(self):
        seleccion = self.treeview_pedido.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un menú para eliminar")
            return

        menu_seleccionado = self.treeview_pedido.item(seleccion)["values"][0]
        for menu in self.pedido.menus:
            if menu.nombre == menu_seleccionado:
                self.pedido.eliminar_menu(menu)
                break

        self.actualizar_vista_pedido()

    def mostrar_pestaña_pedido(self):
        self.notebook.select(self.tab_pedido)

    def generar_boleta(self):
        self.pedido.generar_boleta("boleta_restaurante.pdf")
        messagebox.showinfo("Boleta", "Boleta generada exitosamente como 'boleta_restaurante.pdf'")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
