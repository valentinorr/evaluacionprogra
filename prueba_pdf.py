import tkinter as tk
from tkinter import ttk, messagebox
from customtkinter import CTk, CTkEntry, CTkButton, CTkFrame, CTkLabel
from fpdf import FPDF
from PIL import Image, ImageTk  # Importar PIL para manejar imágenes

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

        # Cargar iconos de los menús
        self.icono_papas_fritas = ImageTk.PhotoImage(Image.open("icono_papas_fritas_64x64.png"), size =(100,100))  #No se cambia el tamaño
        self.icono_pepsi = ImageTk.PhotoImage(Image.open("icono_cola_64x64.png"), size =(100,100)) #No se cambia el tamaño
        self.icono_completo = ImageTk.PhotoImage(Image.open("icono_hotdog_sin_texto_64x64.png"), size =(100,100)) #No se cambia el tamaño
        self.icono_hamburguesa = ImageTk.PhotoImage(Image.open("icono_hamburguesa_negra_64x64.png"),size =(100,100)) #No se cambia el tamaño

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
    
        # Agregar los botones con íconos
        boton_menu_papas = CTkButton(frame_superior, image=self.icono_papas_fritas, text="Papas Fritas - $500", 
                                     command=lambda m=self.menus_disponibles[0]: self.agregar_menu_a_pedido(m))
        boton_menu_papas.grid(row=1, column=0, padx=10, pady=10)

        boton_menu_pepsi = CTkButton(frame_superior, image=self.icono_pepsi, text="Pepsi - $1100", 
                                     command=lambda m=self.menus_disponibles[1]: self.agregar_menu_a_pedido(m))
        boton_menu_pepsi.grid(row=1, column=1, padx=10, pady=10)

        boton_menu_completo = CTkButton(frame_superior, image=self.icono_completo, text="Completo - $1800", 
                                        command=lambda m=self.menus_disponibles[2]: self.agregar_menu_a_pedido(m))
        boton_menu_completo.grid(row=2, column=0, padx=10, pady=10)

        boton_menu_hamburguesa = CTkButton(frame_superior, image=self.icono_hamburguesa, text="Hamburguesa - $3500", 
                                           command=lambda m=self.menus_disponibles[3]: self.agregar_menu_a_pedido(m))
        boton_menu_hamburguesa.grid(row=2, column=1, padx=10, pady=10)

        # Treeview para mostrar los pedidos
        self.treeview_pedido = ttk.Treeview(self.tab_pedido, columns=("Menú", "Cantidad", "Precio"), show="headings", height=10)
        self.treeview_pedido.heading("Menú", text="Menú")
        self.treeview_pedido.heading("Cantidad", text="Cantidad")
        self.treeview_pedido.heading("Precio", text="Precio")
        self.treeview_pedido.column("Menú", width=250)
        self.treeview_pedido.column("Cantidad", width=250)
        self.treeview_pedido.column("Precio", width=250)
        self.treeview_pedido.pack(padx=10, pady=10)

        # Botón para eliminar del pedido
        boton_eliminar_pedido = CTkButton(self.tab_pedido, text="Eliminar del Pedido", command=self.eliminar_menu_de_pedido)
        boton_eliminar_pedido.pack(pady=5)

        # Botón para generar la boleta
        boton_generar_boleta = CTkButton(self.tab_pedido, text="Generar Boleta", command=self.generar_boleta)
        boton_generar_boleta.pack(pady=5)

    def agregar_ingrediente(self):
        nombre = self.entry_nombre.get().strip()
        cantidad = self.entry_cantidad.get().strip()

        if nombre and cantidad.isdigit():
            ingrediente = Ingrediente(nombre, int(cantidad))
            self.stock.agregar_ingrediente(ingrediente)
            self.treeview_ingredientes.insert("", "end", values=(nombre.capitalize(), cantidad))
        else:
            messagebox.showerror("Error", "Por favor ingrese un nombre y una cantidad válida")

    def eliminar_ingrediente(self):
        seleccionado = self.treeview_ingredientes.selection()
        if seleccionado:
            item = self.treeview_ingredientes.item(seleccionado)
            nombre = item['values'][0].lower()
            self.stock.eliminar_ingrediente(nombre)
            self.treeview_ingredientes.delete(seleccionado)
        else:
            messagebox.showerror("Error", "Por favor seleccione un ingrediente para eliminar")

    def agregar_menu_a_pedido(self, menu):
        if menu.es_preparable(self.stock.ingredientes):
            self.pedido.agregar_menu(menu)
            self.treeview_pedido.insert("", "end", values=(menu.nombre, 1, f"${menu.precio}"))
        else:
            messagebox.showerror("Error", f"Faltan ingredientes para preparar {menu.nombre}")

    def eliminar_menu_de_pedido(self):
        seleccionado = self.treeview_pedido.selection()
        if seleccionado:
            self.treeview_pedido.delete(seleccionado)
            # Aquí deberías eliminar también el menú del pedido, si es necesario
        else:
            messagebox.showerror("Error", "Por favor seleccione un menú para eliminar")

    def generar_boleta(self):
        self.pedido.generar_boleta()
        messagebox.showinfo("Boleta Generada", "La boleta ha sido generada exitosamente")

    def mostrar_pestaña_pedido(self):
        self.notebook.select(self.tab_pedido)

# Crear la instancia de la aplicación
app = Aplicacion()
app.mainloop()
