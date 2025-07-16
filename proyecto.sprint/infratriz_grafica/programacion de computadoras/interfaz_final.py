import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
from PIL import Image, ImageTk
import os
import json
import datetime
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Archivos de Datos (Persistencia) ---
ARCHIVO_DATOS = "data.json" # Para usuarios
HISTORIAL_COMPRAS_FILE = "historial_compra.json" # Para el registro de ventas
PRODUCTOS_FILE = "productos.json" # Para los productos de la tienda

# --- Variables Globales ---
usuario_actual = None
root_tienda_app = None # Variable para la ventana principal de la tienda

# Es crucial que esta ruta sea accesible para tus imágenes.
# Si tus imágenes están en una subcarpeta llamada 'assets' dentro del mismo directorio del script,
# podrías usar: IMG_BASE = os.path.join(os.path.dirname(__file__), "assets")
IMG_BASE = "C:\\Users\\kevin\\OneDrive\\Documents\\proyectos de programacion\\Nueva-carpeta\\interfaz graf 2\\infratriz_grafica\\programacion de computadoras"

# --- Funciones de Utilidad JSON ---
def cargar_json(filepath):
    """
    Carga datos desde un archivo JSON. Si el archivo no existe, está vacío o corrupto,
    devuelve una lista vacía para evitar errores.
    """
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if data is not None else []
    except json.JSONDecodeError:
        messagebox.showerror("¡Ups, un archivo dañado!", f"Parece que el archivo '{filepath}' está un poco revuelto o vacío. ¡No te preocupes, lo reiniciaremos para ti!")
        return []
    except Exception as e:
        messagebox.showerror("Error al cargar", f"No pudimos leer '{filepath}'. Algo inesperado pasó: {e}")
        return []

def guardar_json(datos, filepath):
    """
    Guarda datos en un archivo JSON.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False) # ensure_ascii=False para caracteres especiales
    except IOError as e:
        messagebox.showerror("Problemas al guardar", f"No pudimos guardar tus cambios en '{filepath}'. Revisa si hay algún problema de permisos: {e}")

# --- Funciones de Carga de Imágenes ---
def load_icon(path):
    """Carga y redimensiona un icono para los botones de navegación."""
    try:
        image = Image.open(path)
        image = image.resize((30, 30), Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"No pude cargar el icono en '{path}'. ¿Está ahí?: {e}")
        return None

def load_image(path, size=(80, 80)):
    """Carga y redimensiona una imagen de producto."""
    try:
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"No pude cargar la imagen en '{path}'. ¿Está ahí?: {e}")
        return None

# --- Autenticación ---
def iniciar_autenticacion():
    """Maneja el inicio de sesión y registro de usuarios."""
    def login():
        nonlocal root
        global usuario_actual # Importante: 'usuario_actual' es global
        user = entry_user.get()
        password = entry_pass.get()
        
        datos_usuarios = cargar_json(ARCHIVO_DATOS)
        
        for u in datos_usuarios:
            if u["user"] == user and u["pass"] == password:
                usuario_actual = u
                messagebox.showinfo("¡Bienvenido de nuevo!", f"¡Hola {user}, qué bueno verte por aquí!")
                root.destroy()
                abrir_tienda()
                return
        messagebox.showerror("Acceso denegado", "¡Uy! Parece que tu usuario o contraseña no son correctos. Intenta de nuevo.")

    def registrar():
        user = entry_new_user.get().strip()
        password = entry_new_pass.get().strip()
        if not user or not password:
            messagebox.showerror("¡Faltan datos!", "Por favor, llena todos los campos para registrarte.")
            return

        datos_usuarios = cargar_json(ARCHIVO_DATOS)
        for u in datos_usuarios:
            if u["user"] == user:
                messagebox.showerror("Usuario ya existe", "¡Vaya! Parece que ese nombre de usuario ya está en uso. Elige otro, por favor.")
                return
        
        datos_usuarios.append({"user": user, "pass": password, "foto": ""})
        guardar_json(datos_usuarios, ARCHIVO_DATOS)
        messagebox.showinfo("¡Registro exitoso!", "¡Felicidades! Ya estás registrado. Ahora puedes iniciar sesión.")
        
        # Volver a la pantalla de inicio de sesión después del registro exitoso
        frame_reg.pack_forget()
        frame_login.pack()
        entry_new_user.delete(0, tk.END)
        entry_new_pass.delete(0, tk.END)

    root = tk.Tk()
    root.title("¡Bienvenido a AGRO.MAX!")
    root.geometry("300x400")
    root.configure(bg="#195E5E")

    # Cargar logo
    try:
        img_path = os.path.join(IMG_BASE, "unnamed.png")
        img = Image.open(img_path).resize((100, 100))
        logo = ImageTk.PhotoImage(img)
        tk.Label(root, image=logo, bg="#195E5E").pack(pady=10)
    except Exception as e:
        print(f"No pude cargar el logo: {e}. Quizás la imagen no está en la ruta correcta.")
        tk.Label(root, text="AGRO.MAX", font=("Arial", 20, "bold"), bg="#195E5E", fg="white").pack(pady=10)

    # Marco para iniciar sesión
    frame_login = tk.Frame(root, bg="#195E5E")
    tk.Label(frame_login, text="Tu Usuario", bg="#195E5E", fg="white").pack()
    entry_user = tk.Entry(frame_login)
    entry_user.pack()
    tk.Label(frame_login, text="Tu Contraseña", bg="#195E5E", fg="white").pack()
    entry_pass = tk.Entry(frame_login, show="*")
    entry_pass.pack()
    tk.Button(frame_login, text="Entrar", command=login, bg="#B7CE63").pack(pady=10)
    tk.Button(frame_login, text="¿Eres nuevo? Regístrate aquí", command=lambda: switch(True)).pack()
    frame_login.pack()

    # Marco para registrarse
    frame_reg = tk.Frame(root, bg="#195E5E")
    tk.Label(frame_reg, text="Elige un nuevo usuario", bg="#195E5E", fg="white").pack()
    entry_new_user = tk.Entry(frame_reg)
    entry_new_user.pack()
    tk.Label(frame_reg, text="Crea tu contraseña", bg="#195E5E", fg="white").pack()
    entry_new_pass = tk.Entry(frame_reg, show="*")
    entry_new_pass.pack()
    tk.Button(frame_reg, text="Crear cuenta", command=registrar, bg="#B7CE63").pack(pady=10)
    tk.Button(frame_reg, text="¡Ya tengo cuenta! Iniciar sesión", command=lambda: switch(False)).pack()

    def switch(to_reg):
        """Alterna entre las vistas de inicio de sesión y registro."""
        if to_reg:
            frame_login.pack_forget()
            frame_reg.pack()
        else:
            frame_reg.pack_forget()
            frame_login.pack()
            
    root.mainloop()

# --- Aplicación Principal de la Tienda ---
def abrir_tienda():
    """Configura y ejecuta la interfaz principal de la tienda."""
    global root_tienda_app
    global productos_disponibles # Aseguramos que podemos modificar la lista global

    root_tienda_app = tk.Tk()
    root_tienda_app.geometry("700x800")
    root_tienda_app.title("AGRO.MAX - Tu tienda de confianza")

    # Cargar productos al iniciar la tienda
    productos_disponibles = cargar_json(PRODUCTOS_FILE)
    # Si el archivo de productos está vacío, inicializa con los productos de ejemplo
    if not productos_disponibles:
        productos_disponibles.extend([
            {"nombre": "comida para gatos", "precio": "15000", "imagen": os.path.join(IMG_BASE, "ringogato.png"), "stock": 10,
             "descripcion": "Alimento completo y balanceado para gatos adultos de todas las razas. Rico en proteínas y nutrientes esenciales para una vida sana y feliz, apoyando su sistema digestivo y un pelaje brillante."},
            {"nombre": "comida para perro", "precio": "25000", "imagen": os.path.join(IMG_BASE, "perro.png"), "stock": 15,
             "descripcion": "Nutrición superior para perros adultos, con ingredientes seleccionados para una digestión óptima y un pelaje brillante. Contiene vitaminas y minerales esenciales para mantener a tu mejor amigo lleno de energía y vitalidad."},
            {"nombre": "comida para gatos pequenos", "precio": "10000", "imagen": os.path.join(IMG_BASE, "gato_pequeño.png"), "stock": 20,
             "descripcion": "Fórmula especial para gatitos y gatos jóvenes, que apoya su crecimiento y desarrollo con un sabor irresistible. Pequeñas croquetas fáciles de masticar, ricas en proteínas para huesos y músculos fuertes."},
            {"nombre": "comida para cachorros", "precio": "20000", "imagen": os.path.join(IMG_BASE, "perros_pequeños.png"), "stock": 12,
             "descripcion": "Diseñada para cachorros en crecimiento, con el equilibrio perfecto de vitaminas y minerales para huesos fuertes y mucha energía. Contribuye al desarrollo cognitivo y a un sistema inmunológico saludable."},
        ])
        guardar_json(productos_disponibles, PRODUCTOS_FILE) # Guarda los productos iniciales si no existían

    # El área principal donde se mostrará todo el contenido
    frame = tk.Frame(root_tienda_app, bg="white")
    frame.pack(fill="both", expand=True)

    # La barra de navegación en la parte de abajo.
    nav = tk.Frame(root_tienda_app, height=60, bg="white")
    nav.pack(side="bottom", fill="x")

    # Cargamos los pequeños iconos para la navegación.
    icon_inicio = load_icon(os.path.join(IMG_BASE, "inicio.png"))
    icon_buscar = load_icon(os.path.join(IMG_BASE, "lupa.png"))
    icon_usuario = load_icon(os.path.join(IMG_BASE, "usuario.png"))
    icon_carrito = load_icon(os.path.join(IMG_BASE, "carrito.png"))
    icon_admin = load_icon(os.path.join(IMG_BASE, "admin.png"))

    carrito = [] # Guardar lo que el cliente ponga en su carrito

    def limpiar():
        """Elimina todos los widgets del frame principal para cambiar de vista."""
        for widget in frame.winfo_children():
            widget.destroy()

    def go_inicio():
        """Muestra la vista de inicio con la lista de productos."""
        limpiar()
        tk.Label(frame, text="Nuestros Productos", font=("Arial", 16, "bold"), bg="white", fg="#195E5E").pack(pady=10)

        if not productos_disponibles:
            tk.Label(frame, text="¡Vaya! Parece que no hay productos disponibles en este momento.", bg="white", fg="gray").pack(pady=20)
            return

        # Mostramos cada producto.
        for prod in productos_disponibles:
            f = tk.Frame(frame, bg="white", relief="solid", bd=1, padx=5, pady=5)
            f.pack(padx=5, pady=5, fill="x")

            img = load_image(prod["imagen"])
            if img:
                lbl_img = tk.Label(f, image=img, bg="white", cursor="hand2") # Cursor para indicar que es clicable
                lbl_img.pack(side="left")
                lbl_img.image = img # ¡Importante! Mantenemos la referencia para que no se borre
                # Enlazar el clic de la imagen a la función mostrar_detalle_producto
                lbl_img.bind("<Button-1>", lambda event, p=prod: mostrar_detalle_producto(p))
            else:
                tk.Label(f, text="[IMAGEN NO DISPONIBLE]", bg="white", width=10, height=5, relief="groove").pack(side="left")

            info = tk.Frame(f, bg="white")
            info.pack(side="left", padx=10, expand=True, fill="x")

            tk.Label(info, text=prod["nombre"], bg="white", font=("Arial", 12)).pack(anchor="w")
            tk.Label(info, text=f"Precio: ${int(prod['precio']):,}", bg="white", fg="green").pack(anchor="w")
            tk.Label(info, text=f"En stock: {prod['stock']}", bg="white", fg="blue").pack(anchor="w")

            if prod["stock"] > 0:
                tk.Button(info, text="comprar", command=lambda p=prod: agregar_carrito(p), bg="#C8E6C9").pack(anchor="e", pady=5)
            else:
                tk.Label(info, text="¡AGOTADO!", bg="white", fg="red", font=("Arial", 10, "bold")).pack(anchor="e", pady=5)

    def mostrar_detalle_producto(producto):
        """
        Muestra una ventana detallada con la imagen ampliada, descripción y datos del producto.
        """
        detalle_window = tk.Toplevel(root_tienda_app)
        detalle_window.title(f"Detalle de {producto['nombre']}")
        detalle_window.geometry("450x650")
        detalle_window.transient(root_tienda_app) # Hazla dependiente de la ventana principal
        detalle_window.grab_set() # Bloquea la interacción con la ventana principal hasta que esta se cierre

        detalle_frame = tk.Frame(detalle_window, bg="white", padx=20, pady=20)
        detalle_frame.pack(fill="both", expand=True)

        # Cargar y mostrar la imagen más grande
        img_grande = load_image(producto["imagen"], size=(200, 200))
        if img_grande:
            lbl_img_detalle = tk.Label(detalle_frame, image=img_grande, bg="white")
            lbl_img_detalle.image = img_grande # Importante para evitar que se borre
            lbl_img_detalle.pack(pady=10)
        else:
            tk.Label(detalle_frame, text="[IMAGEN NO DISPONIBLE]", bg="white", width=25, height=10, relief="groove").pack(pady=10)

        tk.Label(detalle_frame, text=producto["nombre"], font=("Arial", 18, "bold"), bg="white", fg="#195E5E").pack(pady=5)
        tk.Label(detalle_frame, text=f"Precio: ${int(producto['precio']):,}", font=("Arial", 14, "bold"), bg="white", fg="green").pack(pady=5)
        tk.Label(detalle_frame, text=f"Stock Disponible: {producto['stock']}", font=("Arial", 12), bg="white", fg="blue").pack(pady=5)

        tk.Frame(detalle_frame, height=1, bg="lightgray").pack(fill="x", pady=10) # Separador

        # Descripción del producto
        tk.Label(detalle_frame, text="Descripción del Producto:", font=("Arial", 12, "underline"), bg="white").pack(pady=5, anchor="w")
        descripcion_text = tk.Text(detalle_frame, wrap="word", height=8, width=40, bg="white", font=("Arial", 10))
        # Usamos .get() para obtener la descripción, con un mensaje por defecto si no existe
        descripcion_text.insert(tk.END, producto.get("descripcion", "No hay descripción disponible para este producto."))
        descripcion_text.config(state="disabled") # Para que el usuario no pueda editar la descripción
        descripcion_text.pack(pady=5, fill="both", expand=True)

        # Botón para añadir al carrito desde la ventana de detalle
        if producto["stock"] > 0:
            tk.Button(detalle_frame, text="Añadir al Carrito", command=lambda p=producto: [agregar_carrito(p), detalle_window.destroy()], bg="#B7CE63").pack(pady=15)
        else:
            tk.Label(detalle_frame, text="¡AGOTADO!", bg="white", fg="red", font=("Arial", 12, "bold")).pack(pady=15)

        # Botón para cerrar la ventana de detalle
        tk.Button(detalle_frame, text="Cerrar", command=detalle_window.destroy, bg="lightgray").pack(pady=5)

        detalle_window.mainloop() # Mantener esta ventana activa hasta que se cierre

    def go_buscar():
        """Muestra la vista de búsqueda de productos."""
        limpiar()
        tk.Label(frame, text="Busca tus productos favoritos", font=("Arial", 16, "bold"), bg="white", fg="#195E5E").pack(pady=10)

        search_frame = tk.Frame(frame, bg="white")
        search_frame.pack(pady=10)

        query = tk.Entry(search_frame, width=30)
        query.pack(side="left", padx=5)

        results_frame = tk.Frame(frame, bg="white")
        results_frame.pack(pady=10, fill="both", expand=True)

        def buscar():
            """Realiza la búsqueda de productos y actualiza los resultados."""
            for widget in results_frame.winfo_children():
                widget.destroy() # Borra los resultados anteriores

            search_term = query.get().lower()
            resultados = [p for p in productos_disponibles if search_term in p["nombre"].lower() or search_term in p.get("descripcion", "").lower()]

            if not resultados:
                tk.Label(results_frame, text="¡Uy! No encontramos productos con ese nombre. Intenta de nuevo.", bg="white", fg="gray").pack(pady=10)
                return

            for p in resultados:
                f_res = tk.Frame(results_frame, bg="white", relief="solid", bd=1, padx=5, pady=5)
                f_res.pack(padx=5, pady=2, fill="x")

                tk.Label(f_res, text=f"{p['nombre']} - ${int(p['precio']):,} - En stock: {p['stock']}", bg="white").pack(side="left")

                if p["stock"] > 0:
                    tk.Button(f_res, text="comprar", command=lambda prod_item=p: agregar_carrito(prod_item), bg="#C8E6C9").pack(side="right", padx=5)
                else:
                    tk.Label(f_res, text="¡AGOTADO!", bg="white", fg="red", font=("Arial", 9, "bold")).pack(side="right", padx=5)

        tk.Button(search_frame, text="Buscar", command=buscar, bg="#AED581").pack(side="left", padx=5)

    def go_usuario():
        """Muestra la vista del perfil de usuario, permitiendo editar información y cerrar sesión."""
        limpiar()
        tk.Label(frame, text="Tu Perfil", font=("Arial", 16, "bold"), bg="white", fg="#195E5E").pack(pady=10)

        path = usuario_actual.get("foto", "")
        img = load_image(path, size=(120, 120))
        if img:
            lbl = tk.Label(frame, image=img, bg="white")
            lbl.image = img
            lbl.pack(pady=10)
        else:
            tk.Label(frame, text="¡Aún no tienes una foto de perfil!", bg="white", fg="gray").pack(pady=10)

        tk.Button(frame, text="Cambiar mi foto", command=cambiar_foto, bg="lightblue").pack(pady=5)
        tk.Label(frame, text=f"Tu usuario: {usuario_actual['user']}", bg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(frame, text="Editar mi información y contraseña", command=editar_perfil, bg="lightsteelblue").pack(pady=5)
        tk.Button(frame, text="Eliminar mi cuenta (¡Cuidado!)", command=eliminar_cuenta, bg="salmon").pack(pady=5)
        tk.Button(frame, text="Cerrar Sesión", command=lambda: cerrar_sesion(root_tienda_app), bg="khaki").pack(pady=5)

    def cambiar_foto():
        """Permite al usuario seleccionar y guardar una nueva foto de perfil."""
        path = filedialog.askopenfilename(title="Elige tu nueva foto de perfil", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif")])
        if path:
            usuario_actual["foto"] = path
            datos = cargar_json(ARCHIVO_DATOS)
            for u in datos:
                if u["user"] == usuario_actual["user"]:
                    u["foto"] = path
            guardar_json(datos, ARCHIVO_DATOS)
            messagebox.showinfo("¡Foto actualizada!", "¡Tu foto de perfil ha sido cambiada exitosamente!")
            go_usuario() # Volvemos a cargar el perfil para que veas tu nueva foto

    def editar_perfil():
        """Permite al usuario cambiar su nombre de usuario o contraseña."""
        nuevo_user = simpledialog.askstring("Cambiar Usuario", "Escribe tu nuevo nombre de usuario:", initialvalue=usuario_actual["user"])
        nueva_pass = simpledialog.askstring("Cambiar Contraseña", "Escribe tu nueva contraseña (déjalo en blanco si no quieres cambiarla):", show="*")

        cambios_realizados = False
        if nuevo_user and nuevo_user != usuario_actual["user"]:
            datos = cargar_json(ARCHIVO_DATOS)
            if any(u["user"] == nuevo_user for u in datos if u["user"] != usuario_actual["user"]):
                messagebox.showerror("¡Usuario no disponible!", "¡Lo sentimos! Ese nombre de usuario ya lo tiene otra persona.")
                return
            usuario_actual["user"] = nuevo_user
            cambios_realizados = True

        if nueva_pass:
            usuario_actual["pass"] = nueva_pass
            cambios_realizados = True

        if cambios_realizados:
            datos = cargar_json(ARCHIVO_DATOS)
            for i, u in enumerate(datos):
                if u["user"] == (nuevo_user if ('nuevo_user' in locals() and nuevo_user) else usuario_actual["user"]):
                    datos[i] = usuario_actual
                    break
            guardar_json(datos, ARCHIVO_DATOS)
            messagebox.showinfo("¡Perfil actualizado!", "¡Tu información ha sido guardada con éxito!")
            go_usuario() # Recargamos la vista del perfil para que veas los cambios
        else:
            messagebox.showinfo("¡Todo igual!", "No hiciste ningún cambio en tu perfil.")

    def eliminar_cuenta():
        """Permite al usuario eliminar su cuenta permanentemente."""
        if messagebox.askyesno("¡Atención! Eliminar Cuenta", "¿Estás segur@ de que quieres eliminar tu cuenta?\n¡Esta acción no se puede deshacer!"):
            global usuario_actual
            datos = cargar_json(ARCHIVO_DATOS)
            datos = [u for u in datos if u["user"] != usuario_actual["user"]]
            guardar_json(datos, ARCHIVO_DATOS)
            messagebox.showinfo("¡Cuenta eliminada!", "¡Tu cuenta ha sido eliminada con éxito!")
            cerrar_sesion(root_tienda_app) # Cerramos la tienda y volvemos a la pantalla de inicio

    def cerrar_sesion(root_tienda_app_param):
        """Cierra la sesión actual y regresa a la pantalla de autenticación."""
        global usuario_actual
        usuario_actual = None # Desvinculamos el usuario actual
        root_tienda_app_param.destroy() # Cerramos la ventana de la tienda
        iniciar_autenticacion() # Volvemos a la pantalla de inicio de sesión

    def go_carrito():
        """Muestra la vista del carrito de compras."""
        limpiar()
        tk.Label(frame, text="Carrito de Compras", font=("Arial", 16, "bold"), bg="white", fg="#195E5E").pack(pady=10)

        if not carrito:
            tk.Label(frame, text="¡Tu carrito está vacío! ¿Qué esperas? ¡Agrega productos!", bg="white", fg="gray").pack(pady=20)
            return

        total = 0
        # Agrupar los productos para mostrarlos de forma ordenada y calcular el total
        productos_agrupados = defaultdict(int)
        for item in carrito:
            productos_agrupados[item["nombre"]] += 1
            total += int(item["precio"])

        for nombre_prod, cantidad in productos_agrupados.items():
            # Buscar el precio original del producto para mostrarlo
            precio_unitario = 0
            for p in productos_disponibles:
                if p["nombre"] == nombre_prod:
                    precio_unitario = int(p["precio"])
                    break

            item_frame = tk.Frame(frame, bg="white", relief="groove", bd=1)
            item_frame.pack(anchor="w", padx=20, pady=2, fill="x")
            tk.Label(item_frame, text=f"{nombre_prod} (x{cantidad}) - ${precio_unitario * cantidad:,}", bg="white").pack(side="left", fill="x", expand=True)
            tk.Button(item_frame, text="Quitar uno", command=lambda name=nombre_prod: quitar_del_carrito(name), bg="lightcoral").pack(side="right", padx=5)

        tk.Frame(frame, height=2, bg="lightgray").pack(fill="x", padx=15, pady=10) # Una línea bonita para separar
        tk.Label(frame, text=f"Total a pagar: ${total:,}", bg="white", font=("Arial", 14, "bold"), fg="green").pack(pady=10)

        if carrito: # Mostrar el botón de pagar si hay algo en el carrito
            tk.Button(frame, text="Proceder al Pago", command=lambda: pagar_con_opciones(total), bg="#B7CE63").pack(pady=10)

    def pagar_con_opciones(total_a_pagar):
        """Muestra una ventana para seleccionar el método de pago y finalizar la compra."""
        if not carrito:
            messagebox.showerror("¡Carrito vacío!", "Por favor, agrega algunos productos antes de intentar pagar.")
            return

        pago_window = tk.Toplevel(root_tienda_app) # Abrir una ventana para el pago
        pago_window.title("Confirmar tu Pago")
        pago_window.geometry("350x400")
        pago_window.transient(root_tienda_app)
        pago_window.grab_set() # Bloquea la interacción con la ventana principal hasta que esta se cierre

        pago_frame = tk.Frame(pago_window, bg="white", padx=20, pady=20)
        pago_frame.pack(fill="both", expand=True)

        tk.Label(pago_frame, text="¿Cómo quieres pagar?", font=("Arial", 14, "bold"), bg="white", fg="#195E5E").pack(pady=10)
        tk.Label(pago_frame, text=f"Total a Pagar: ${total_a_pagar:,}", font=("Arial", 12, "bold"), bg="white", fg="green").pack(pady=5)

        metodo_pago_var = tk.StringVar(value="Efectivo") # Por defecto, pago en efectivo

        card_details_frame = tk.Frame(pago_frame, bg="white")

        def mostrar_campos_tarjeta():
            """Muestra u oculta los campos de entrada para detalles de tarjeta."""
            for widget in card_details_frame.winfo_children():
                widget.destroy() # Borramos los campos anteriores
            if metodo_pago_var.get() in ["Tarjeta Visa", "Mastercard"]:
                tk.Label(card_details_frame, text="Número de Tarjeta:", bg="white").pack(anchor="w", pady=(10,0))
                entry_card_number = tk.Entry(card_details_frame, width=30)
                entry_card_number.pack(fill="x", pady=2)

                tk.Label(card_details_frame, text="Fecha de Vencimiento (MM/AA):", bg="white").pack(anchor="w", pady=(10,0))
                entry_expiry = tk.Entry(card_details_frame, width=10)
                entry_expiry.pack(fill="x", pady=2)

                tk.Label(card_details_frame, text="Código de Seguridad (CVV):", bg="white").pack(anchor="w", pady=(10,0))
                entry_cvv = tk.Entry(card_details_frame, width=5, show="*")
                entry_cvv.pack(fill="x", pady=2)
            card_details_frame.pack(fill="x", pady=5) # Mostramos el marco de los detalles de la tarjeta

        tk.Radiobutton(pago_frame, text="Efectivo", variable=metodo_pago_var, value="Efectivo", bg="white", command=mostrar_campos_tarjeta).pack(anchor="w", pady=5)
        tk.Radiobutton(pago_frame, text="Tarjeta Visa", variable=metodo_pago_var, value="Tarjeta Visa", bg="white", command=mostrar_campos_tarjeta).pack(anchor="w", pady=5)
        tk.Radiobutton(pago_frame, text="Mastercard", variable=metodo_pago_var, value="Mastercard", bg="white", command=mostrar_campos_tarjeta).pack(anchor="w", pady=5)

        # Para que se muestren los campos de la tarjeta al inicio si ya está seleccionada esa opción
        mostrar_campos_tarjeta()

        def finalizar_pago():
            """Procesa el pago, registra la compra y vacía el carrito."""
            metodo_seleccionado = metodo_pago_var.get()

            if metodo_seleccionado in ["Tarjeta Visa", "Mastercard"]:
                entries = [w for w in card_details_frame.winfo_children() if isinstance(w, tk.Entry)]
                if len(entries) < 3:
                    messagebox.showerror("Error de Pago", "¡Ups! Algo salió mal con los campos de la tarjeta. Intenta de nuevo.")
                    return

                card_num = entries[0].get().strip()
                expiry = entries[1].get().strip()
                cvv = entries[2].get().strip()

                if not card_num or not expiry or not cvv:
                    messagebox.showerror("¡Faltan datos de la tarjeta!", "Por favor, completa todos los campos de tu tarjeta para continuar.")
                    return
                
                # Validaciones básicas de formato para tarjeta
                if not card_num.isdigit() or not (13 <= len(card_num) <= 19):
                    messagebox.showerror("Número de tarjeta inválido", "El número de tarjeta debe contener solo dígitos y tener entre 13 y 19 números.")
                    return
                if not expiry.count('/') == 1 or not all(part.isdigit() for part in expiry.split('/')) or len(expiry) != 5:
                    messagebox.showerror("Fecha de vencimiento inválida", "El formato de la fecha de vencimiento debe ser MM/AA.")
                    return
                if not cvv.isdigit() or not (3 <= len(cvv) <= 4):
                    messagebox.showerror("CVV inválido", "El CVV debe ser de 3 o 4 dígitos numéricos.")
                    return

            # Registrar la compra en el historial
            historial = cargar_json(HISTORIAL_COMPRAS_FILE)

            # Organizamos los productos del carrito para el registro
            items_comprados_historial = defaultdict(lambda: {"precio_unitario": 0, "cantidad": 0})
            for item_c in carrito:
                items_comprados_historial[item_c["nombre"]]["precio_unitario"] = int(item_c["precio"])
                items_comprados_historial[item_c["nombre"]]["cantidad"] += 1

            lista_items_historial = []
            for nombre, datos in items_comprados_historial.items():
                lista_items_historial.append({
                    "nombre": nombre,
                    "precio_unitario": datos["precio_unitario"],
                    "cantidad": datos["cantidad"]
                })

            registro_compra = {
                "id_transaccion": datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"), # Un número único para cada compra
                "usuario": usuario_actual["user"],
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "metodo_pago": metodo_seleccionado,
                "total_pagado": total_a_pagar,
                "productos": lista_items_historial # Tus productos con cantidades y precios
            }
            historial.append(registro_compra)
            guardar_json(historial, HISTORIAL_COMPRAS_FILE)

            carrito.clear() # Vaciar el carrito después de la compra
            messagebox.showinfo("¡Compra Exitosa!", f"¡Tu compra de ${total_a_pagar:,} ha sido procesada con éxito usando {metodo_seleccionado}! ¡Muchas gracias por tu compra!")
            pago_window.destroy() # Cerrar la ventana de pago
            go_carrito() # Actualizar la vista del carrito

        tk.Button(pago_frame, text="Confirmar Pago", command=finalizar_pago, bg="#B7CE63").pack(pady=20, fill="x")
        pago_window.mainloop() # Mantener esta ventana activa hasta que se cierre

    def agregar_carrito(prod_to_add):
        """Añade un producto al carrito y actualiza su stock."""
        found_product = None
        for p in productos_disponibles:
            if p["nombre"] == prod_to_add["nombre"]:
                found_product = p
                break

        if found_product and found_product["stock"] > 0:
            found_product["stock"] -= 1 # Restamos uno al stock
            carrito.append(found_product) # Añadir el producto al carrito
            guardar_json(productos_disponibles, PRODUCTOS_FILE) # Guardar cambio de stock
            messagebox.showinfo("¡Al carrito!", f"¡'{prod_to_add['nombre']}' se ha añadido a tu carrito!")
            go_inicio() # Refrescar la vista de inicio para mostrar el stock actualizado
        elif found_product and found_product["stock"] <= 0:
            messagebox.showerror("¡Sin stock!", f"¡Lo sentimos mucho! '{prod_to_add['nombre']}' se ha agotado.")
        else:
            messagebox.showerror("¡Producto no encontrado!", "Parece que hubo un problema y no pudimos encontrar este producto.")

    def go_admin():
        """Muestra el panel de administración para gestionar productos y ver estadísticas."""
        limpiar()
        tk.Label(frame, text="Panel de Administración", font=("Arial", 16, "bold"), bg="white", fg="#195E5E").pack(pady=10)

        # Sección para añadir producto
        add_frame = tk.LabelFrame(frame, text="Agregar un Producto Nuevo", bg="white", padx=10, pady=10)
        add_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(add_frame, text="Nombre del Producto:", bg="white").pack(anchor="w")
        nombre_entry = tk.Entry(add_frame)
        nombre_entry.pack(fill="x")

        tk.Label(add_frame, text="Precio ($):", bg="white").pack(anchor="w")
        precio_entry = tk.Entry(add_frame)
        precio_entry.pack(fill="x")

        tk.Label(add_frame, text="Cantidad en Stock:", bg="white").pack(anchor="w")
        stock_entry = tk.Entry(add_frame)
        stock_entry.insert(0, "1") # Valor inicial sugerido.
        stock_entry.pack(fill="x")

        tk.Label(add_frame, text="Descripción:", bg="white").pack(anchor="w")
        descripcion_entry = tk.Text(add_frame, wrap="word", height=3, width=40)
        descripcion_entry.pack(fill="x")

        selected_image_path = {"path": ""} # Usamos un diccionario para guardar la ruta de la imagen.

        def seleccionar_imagen_admin():
            """Abre un diálogo para que el administrador elija una imagen para el producto."""
            filepath = filedialog.askopenfilename(title="Elige una imagen para tu producto", filetypes=[("Archivos de Imagen", "*.png;*.jpg;*.jpeg;*.gif")])
            if filepath:
                selected_image_path["path"] = filepath
                messagebox.showinfo("¡Imagen lista!", f"Seleccionaste: {os.path.basename(filepath)}")

        tk.Button(add_frame, text="Elegir Imagen", command=seleccionar_imagen_admin, bg="#B7CE63").pack(pady=5)

        def agregar():
            """Añade el nuevo producto a la lista de productos disponibles y lo guarda."""
            nombre = nombre_entry.get().strip()
            precio_str = precio_entry.get().strip()
            stock_str = stock_entry.get().strip()
            imagen_path = selected_image_path["path"]
            descripcion = descripcion_entry.get("1.0", tk.END).strip() # Obtener texto del widget Text

            if not nombre or not precio_str or not stock_str or not imagen_path or not descripcion:
                messagebox.showerror("¡Faltan campos!", "Por favor, llena todos los campos, selecciona una imagen y añade una descripción para el producto.")
                return

            try:
                precio = int(precio_str)
                stock = int(stock_str)
                if precio <= 0 or stock < 0:
                    messagebox.showerror("¡Valores incorrectos!", "El precio debe ser un número positivo y el stock no puede ser negativo.")
                    return
            except ValueError:
                messagebox.showerror("¡Error de números!", "El precio y el stock deben ser números válidos. ¡Revísalos!")
                return

            if any(p["nombre"].lower() == nombre.lower() for p in productos_disponibles):
                messagebox.showerror("¡Nombre duplicado!", f"¡Oops! Ya tienes un producto llamado '{nombre}'. Por favor, elige otro nombre.")
                return

            productos_disponibles.append({"nombre": nombre, "precio": str(precio), "imagen": imagen_path, "stock": stock, "descripcion": descripcion})
            guardar_json(productos_disponibles, PRODUCTOS_FILE) # Guardar el nuevo producto
            
            messagebox.showinfo("¡Producto añadido!", "¡Tu nuevo producto ha sido agregado con éxito!")
            
            # Limpiamos los campos para que puedas añadir otro.
            nombre_entry.delete(0, tk.END)
            precio_entry.delete(0, tk.END)
            stock_entry.delete(0, tk.END)
            stock_entry.insert(0, "1")
            descripcion_entry.delete("1.0", tk.END) # Limpiar el campo de descripción
            selected_image_path["path"] = ""
            go_admin() # Recargamos la vista de administración para ver el nuevo producto.

        tk.Button(add_frame, text="Añadir Producto", command=agregar, bg="#AED581").pack(pady=10)

        # Sección para gestionar productos existentes
        manage_frame = tk.LabelFrame(frame, text="Administra tus Productos Existentes", bg="white", padx=10, pady=10)
        manage_frame.pack(padx=10, pady=10, fill="x")

        if not productos_disponibles:
            tk.Label(manage_frame, text="¡Aún no tienes productos para gestionar!", bg="white", fg="gray").pack(pady=10)
        else:
            for i, p in enumerate(productos_disponibles):
                f_prod_item = tk.Frame(manage_frame, bg="white", relief="solid", bd=1)
                f_prod_item.pack(fill="x", padx=5, pady=2)
                tk.Label(f_prod_item, text=f"{p['nombre']} - ${int(p['precio']):,} - Stock: {p['stock']}", bg="white").pack(side="left", padx=5, expand=True, fill="x")
                
                # --- NUEVO BOTÓN DE EDITAR ---
                tk.Button(f_prod_item, text="Editar", command=lambda idx=i: editar_producto_admin(idx), bg="lightgoldenrod").pack(side="right", padx=5)
                # -----------------------------
                
                tk.Button(f_prod_item, text="Eliminar", command=lambda idx=i: eliminar(idx), bg="salmon").pack(side="right", padx=5)

        def eliminar(index):
            """Elimina un producto de la lista y lo guarda."""
            if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar '{productos_disponibles[index]['nombre']}'?\n¡Esta acción no se puede deshacer!"):
                del productos_disponibles[index]
                guardar_json(productos_disponibles, PRODUCTOS_FILE) # Guardar el cambio
                messagebox.showinfo("¡Producto eliminado!", "¡El producto ha sido eliminado con éxito!")
                go_admin() # Recargamos la vista de administración.

        # --- NUEVA FUNCIÓN DE EDICIÓN ---
        def editar_producto_admin(index):
            """Abre una ventana para editar un producto existente."""
            producto_a_editar = productos_disponibles[index]

            edit_window = tk.Toplevel(root_tienda_app)
            edit_window.title(f"Editar Producto: {producto_a_editar['nombre']}")
            edit_window.geometry("400x600")
            edit_window.transient(root_tienda_app)
            edit_window.grab_set() # Bloquea la ventana principal

            edit_frame = tk.Frame(edit_window, bg="white", padx=20, pady=20)
            edit_frame.pack(fill="both", expand=True)

            tk.Label(edit_frame, text="Editar Detalles del Producto", font=("Arial", 14, "bold"), bg="white", fg="#195E5E").pack(pady=10)

            tk.Label(edit_frame, text="Nombre del Producto:", bg="white").pack(anchor="w")
            edit_nombre_entry = tk.Entry(edit_frame)
            edit_nombre_entry.insert(0, producto_a_editar["nombre"])
            edit_nombre_entry.pack(fill="x")

            tk.Label(edit_frame, text="Precio ($):", bg="white").pack(anchor="w", pady=(10,0))
            edit_precio_entry = tk.Entry(edit_frame)
            edit_precio_entry.insert(0, str(producto_a_editar["precio"])) # Asegurar que es string para Entry
            edit_precio_entry.pack(fill="x")

            tk.Label(edit_frame, text="Cantidad en Stock:", bg="white").pack(anchor="w", pady=(10,0))
            edit_stock_entry = tk.Entry(edit_frame)
            edit_stock_entry.insert(0, str(producto_a_editar["stock"])) # Asegurar que es string para Entry
            edit_stock_entry.pack(fill="x")

            tk.Label(edit_frame, text="Descripción:", bg="white").pack(anchor="w", pady=(10,0))
            edit_descripcion_text = tk.Text(edit_frame, wrap="word", height=5, width=40)
            edit_descripcion_text.insert("1.0", producto_a_editar.get("descripcion", "")) # Cargar descripción existente
            edit_descripcion_text.pack(fill="x", expand=True)

            current_image_path = {"path": producto_a_editar["imagen"]}

            def seleccionar_nueva_imagen_admin():
                """Permite seleccionar una nueva imagen para el producto durante la edición."""
                filepath = filedialog.askopenfilename(title="Elige una nueva imagen para el producto", filetypes=[("Archivos de Imagen", "*.png;*.jpg;*.jpeg;*.gif")])
                if filepath:
                    current_image_path["path"] = filepath
                    messagebox.showinfo("¡Imagen seleccionada!", f"Nueva imagen: {os.path.basename(filepath)}")

            tk.Button(edit_frame, text="Cambiar Imagen", command=seleccionar_nueva_imagen_admin, bg="#B7CE63").pack(pady=10)
            tk.Label(edit_frame, text=f"Imagen actual: {os.path.basename(producto_a_editar['imagen'])}", bg="white").pack()


            def guardar_edicion():
                """Guarda los cambios del producto editado."""
                nuevo_nombre = edit_nombre_entry.get().strip()
                nuevo_precio_str = edit_precio_entry.get().strip()
                nuevo_stock_str = edit_stock_entry.get().strip()
                nueva_descripcion = edit_descripcion_text.get("1.0", tk.END).strip()
                nueva_imagen_path = current_image_path["path"]

                if not nuevo_nombre or not nuevo_precio_str or not nuevo_stock_str or not nueva_imagen_path or not nueva_descripcion:
                    messagebox.showerror("¡Faltan datos!", "Todos los campos (nombre, precio, stock, descripción e imagen) son obligatorios.")
                    return

                try:
                    nuevo_precio = int(nuevo_precio_str)
                    nuevo_stock = int(nuevo_stock_str)
                    if nuevo_precio <= 0 or nuevo_stock < 0:
                        messagebox.showerror("¡Valores incorrectos!", "El precio debe ser positivo y el stock no puede ser negativo.")
                        return
                except ValueError:
                    messagebox.showerror("¡Error de números!", "El precio y el stock deben ser números válidos.")
                    return
                
                # Validar que el nuevo nombre no esté duplicado, excepto para el mismo producto
                for i, p in enumerate(productos_disponibles):
                    if i != index and p["nombre"].lower() == nuevo_nombre.lower():
                        messagebox.showerror("¡Nombre duplicado!", "Ya existe otro producto con este nombre. Por favor, elige uno diferente.")
                        return

                # Actualizar el producto en la lista global
                productos_disponibles[index]["nombre"] = nuevo_nombre
                productos_disponibles[index]["precio"] = str(nuevo_precio) # Guardar como string
                productos_disponibles[index]["stock"] = nuevo_stock
                productos_disponibles[index]["descripcion"] = nueva_descripcion
                productos_disponibles[index]["imagen"] = nueva_imagen_path

                guardar_json(productos_disponibles, PRODUCTOS_FILE)
                messagebox.showinfo("¡Actualización exitosa!", "¡El producto ha sido actualizado con éxito!")
                edit_window.destroy()
                go_admin() # Recargar la vista de administración para ver los cambios

            tk.Button(edit_frame, text="Guardar Cambios", command=guardar_edicion, bg="#AED581").pack(pady=15, fill="x")
            tk.Button(edit_frame, text="Cancelar", command=edit_window.destroy, bg="lightgray").pack(pady=5, fill="x")

            edit_window.mainloop()
        # -------------------------------

        # Botón para ver estadísticas
        tk.Button(frame, text="Ver Estadísticas y Reportes de Ventas", command=mostrar_estadisticas_admin, bg="#B7CE63").pack(pady=15)

    def mostrar_estadisticas_admin():
        """Muestra una ventana con gráficos de estadísticas de ventas usando Pandas y Matplotlib."""
        stats_window = tk.Toplevel(root_tienda_app)
        stats_window.title("Estadísticas Clave de tu Tienda")
        stats_window.geometry("800x950")
        stats_window.transient(root_tienda_app)
        stats_window.grab_set() # Obliga a interactuar con esta ventana antes de volver a la principal.

        stats_frame = tk.Frame(stats_window, bg="white")
        stats_frame.pack(fill="both", expand=True)

        tk.Label(stats_frame, text="Un Vistazo a tus Ventas", font=("Arial", 18, "bold"), bg="white", fg="#195E5E").pack(pady=10)

        historial_raw = cargar_json(HISTORIAL_COMPRAS_FILE)

        if not historial_raw:
            tk.Label(stats_frame, text="¡Parece que aún no hay datos de compras para mostrarte estadísticas!", bg="white", fg="gray").pack(pady=20)
            tk.Button(stats_frame, text="Volver al Panel de Administración", command=stats_window.destroy, bg="lightgray").pack(pady=10)
            stats_window.mainloop()
            return

        df_compras = pd.DataFrame(historial_raw)

        # Convertir a tipos numéricos y de fecha
        df_compras['total_pagado'] = pd.to_numeric(df_compras['total_pagado'], errors='coerce')
        df_compras['fecha'] = pd.to_datetime(df_compras['fecha'], errors='coerce')

        df_compras.dropna(subset=['total_pagado', 'fecha'], inplace=True) # Eliminar filas con valores nulos

        # Desglosar productos comprados para análisis detallado
        productos_comprados_list = []
        for _, row in df_compras.iterrows():
            fecha = row['fecha']
            usuario = row['usuario']
            metodo_pago = row['metodo_pago']
            # Asegúrate de que 'productos' es una lista antes de iterar
            if isinstance(row['productos'], list):
                for prod in row['productos']:
                    productos_comprados_list.append({
                        'fecha': fecha,
                        'usuario': usuario,
                        'metodo_pago': metodo_pago,
                        'nombre_producto': prod['nombre'],
                        'precio_unitario': prod['precio_unitario'],
                        'cantidad': prod['cantidad'],
                        'subtotal': prod['precio_unitario'] * prod['cantidad'],
                        'id_transaccion': row['id_transaccion'] # Asegúrate de pasar el ID de transacción al detalle
                    })
        df_productos_detallado = pd.DataFrame(productos_comprados_list)

        if df_compras.empty or df_productos_detallado.empty:
            tk.Label(stats_frame, text="¡No hay datos válidos para generar estadísticas!", bg="white", fg="gray").pack(pady=20)
            tk.Button(stats_frame, text="Volver al Panel de Administración", command=stats_window.destroy, bg="lightgray").pack(pady=10)
            stats_window.mainloop()
            return

        # --- Variables disponibles para ambos ejes ---
        # Mapeo de nombres "amigables" a las columnas reales del DataFrame o lógicas de agrupación
        available_variables = {
            "Fecha (Diario)": {"df": df_compras, "column_or_logic": lambda df: df['fecha'].dt.date, "type": "temporal", "display_name": "Fecha"},
            "Fecha (Mensual)": {"df": df_compras, "column_or_logic": lambda df: df['fecha'].dt.to_period('M').astype(str), "type": "temporal", "display_name": "Fecha"},
            "Producto": {"df": df_productos_detallado, "column_or_logic": 'nombre_producto', "type": "categorical", "display_name": "Producto"},
            "Usuario": {"df": df_compras, "column_or_logic": 'usuario', "type": "categorical", "display_name": "Usuario"},
            "Método de Pago": {"df": df_compras, "column_or_logic": 'metodo_pago', "type": "categorical", "display_name": "Método de Pago"},
            "Total Pagado": {"df": df_compras, "column_or_logic": 'total_pagado', "type": "numerical", "display_name": "Total Pagado"},
            "Número de Transacciones": {"df": df_compras, "column_or_logic": 'id_transaccion', "type": "numerical_count", "display_name": "Número de Transacciones"},
            "Cantidad Vendida": {"df": df_productos_detallado, "column_or_logic": 'cantidad', "type": "numerical", "display_name": "Cantidad Vendida"}
        }
        
        # Opciones para los Comboboxes, usando solo las claves amigables
        # Ahora, ambas listas de opciones son idénticas al inicio.
        all_axis_options = list(available_variables.keys())


        # Controles para la selección de la gráfica
        controls_frame = tk.LabelFrame(stats_frame, text="Personaliza tu Gráfica", bg="white", padx=10, pady=10)
        controls_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(controls_frame, text="Tipo de Gráfica:", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        chart_type_options = ["Barras", "Líneas", "Pastel"]
        chart_type_cb = ttk.Combobox(controls_frame, values=chart_type_options, state="readonly")
        chart_type_cb.set("Barras")
        chart_type_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(controls_frame, text="Eje X:", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        x_axis_cb = ttk.Combobox(controls_frame, values=all_axis_options, state="readonly")
        x_axis_cb.set("Fecha (Diario)") # Valor por defecto
        x_axis_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(controls_frame, text="Eje Y:", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        y_axis_cb = ttk.Combobox(controls_frame, values=all_axis_options, state="readonly") # Ambos tienen las mismas opciones
        y_axis_cb.set("Total Pagado") # Valor por defecto
        y_axis_cb.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # La función update_y_options ya no es necesaria con esta lógica,
        # pero la dejo comentada o removida si no la usas.
        # En su lugar, la validación se hace al generar el gráfico.
        # x_axis_cb.bind("<<ComboboxSelected>>", update_y_options) # Remover si no se usa


        # Canvas para la gráfica
        graph_canvas_frame = tk.Frame(stats_frame, bg="white", relief="groove", bd=1)
        graph_canvas_frame.pack(pady=10, padx=20, fill="both", expand=True)

        canvas = None

        def generar_y_mostrar_grafica():
            """Genera y muestra la gráfica según las selecciones del usuario."""
            nonlocal canvas

            if canvas:
                canvas.get_tk_widget().destroy()
                plt.close('all')

            tipo_grafica = chart_type_cb.get()
            eje_x_key = x_axis_cb.get()
            eje_y_key = y_axis_cb.get()

            if not eje_x_key or not eje_y_key:
                messagebox.showerror("¡Faltan selecciones!", "Por favor, elige tanto la categoría del eje X como el valor del eje Y.")
                return

            # --- LA VALIDACIÓN CLAVE ---
            if eje_x_key == eje_y_key:
                messagebox.showerror("¡Selección Inválida!", "¡No puedes seleccionar la misma variable para ambos ejes (X e Y)! Por favor, elige variables diferentes.")
                return

            try:
                fig, ax = plt.subplots(figsize=(7, 5))
                plt.style.use('ggplot')

                # Obtener la información de las variables seleccionadas
                x_info = available_variables[eje_x_key]
                y_info = available_variables[eje_y_key]

                x_labels = []
                y_data = []

                # Lógica de agrupamiento y obtención de datos
                if x_info["type"] == "temporal":
                    # Agrupación temporal
                    if "Diario" in eje_x_key:
                        grouped_df = df_compras.groupby(df_compras['fecha'].dt.date)
                        grouped_prod_df = df_productos_detallado.groupby(df_productos_detallado['fecha'].dt.date)
                    else: # Mensual
                        grouped_df = df_compras.groupby(df_compras['fecha'].dt.to_period('M'))
                        grouped_prod_df = df_productos_detallado.groupby(df_productos_detallado['fecha'].dt.to_period('M'))
                    
                    x_labels = [str(item) for item in grouped_df.groups.keys()]
                    
                    if y_info["display_name"] == "Total Pagado":
                        y_data = grouped_df['total_pagado'].sum().values
                    elif y_info["display_name"] == "Número de Transacciones":
                        y_data = grouped_df.size().values
                    elif y_info["display_name"] == "Cantidad Vendida":
                        # Usar el DataFrame de detalle de productos para Cantidad Vendida
                        # Es crucial que los índices de ambas agrupaciones (si provienen de diferentes DFs) sean compatibles
                        # Aquí, asumimos que se pueden alinear por fecha.
                        y_data_temp = grouped_prod_df['cantidad'].sum()
                        y_data = y_data_temp.reindex(grouped_df.groups.keys(), fill_value=0).values # Alinear y rellenar si faltan fechas
                    else:
                        raise ValueError(f"Combinación de ejes X='{eje_x_key}' e Y='{eje_y_key}' no es compatible.")

                elif x_info["type"] == "categorical":
                    # Agrupación categórica
                    if x_info["display_name"] == "Producto":
                        grouped_data = df_productos_detallado.groupby('nombre_producto')
                        x_labels = list(grouped_data.groups.keys())
                        if y_info["display_name"] == "Cantidad Vendida":
                            y_data = grouped_data['cantidad'].sum().values
                        elif y_info["display_name"] == "Total Pagado":
                            y_data = grouped_data['subtotal'].sum().values
                        elif y_info["display_name"] == "Número de Transacciones":
                            # Contar transacciones únicas que incluyen ese producto
                            y_data = grouped_data['id_transaccion'].nunique().values
                        else:
                            raise ValueError(f"Combinación de ejes X='{eje_x_key}' e Y='{eje_y_key}' no es compatible para 'Producto'.")
                    
                    elif x_info["display_name"] == "Usuario":
                        grouped_data_users = df_compras.groupby('usuario')
                        x_labels = list(grouped_data_users.groups.keys())
                        if y_info["display_name"] == "Total Pagado":
                            y_data = grouped_data_users['total_pagado'].sum().values
                        elif y_info["display_name"] == "Número de Transacciones":
                            y_data = grouped_data_users.size().values
                        elif y_info["display_name"] == "Cantidad Vendida":
                            # Agrupar df_productos_detallado por usuario y sumar cantidad
                            grouped_prod_users = df_productos_detallado.groupby('usuario')['cantidad'].sum()
                            y_data = grouped_prod_users.reindex(x_labels, fill_value=0).values
                        else:
                            raise ValueError(f"Combinación de ejes X='{eje_x_key}' e Y='{eje_y_key}' no es compatible para 'Usuario'.")

                    elif x_info["display_name"] == "Método de Pago":
                        grouped_data_method = df_compras.groupby('metodo_pago')
                        x_labels = list(grouped_data_method.groups.keys())
                        if y_info["display_name"] == "Total Pagado":
                            y_data = grouped_data_method['total_pagado'].sum().values
                        elif y_info["display_name"] == "Número de Transacciones":
                            y_data = grouped_data_method.size().values
                        elif y_info["display_name"] == "Cantidad Vendida":
                            # Requiere unir df_compras con df_productos_detallado por id_transaccion
                            merged_df = pd.merge(df_compras, df_productos_detallado, on=['id_transaccion', 'fecha', 'usuario', 'metodo_pago'], how='inner', suffixes=('_compra', '_prod'))
                            grouped_qty_method = merged_df.groupby('metodo_pago')['cantidad_prod'].sum()
                            y_data = grouped_qty_method.reindex(x_labels, fill_value=0).values
                        else:
                            raise ValueError(f"Combinación de ejes X='{eje_x_key}' e Y='{eje_y_key}' no es compatible para 'Método de Pago'.")
                
                elif x_info["type"] in ["numerical", "numerical_count"]:
                    # Si el Eje X es numérico, las gráficas de barras/líneas usualmente esperan categorías.
                    # Aquí vamos a agrupar por los valores únicos del Eje X para permitir la graficación.
                    # Esto podría resultar en muchos puntos si hay muchos valores únicos.
                    if x_info["display_name"] == "Total Pagado":
                        grouped_x = df_compras.groupby('total_pagado')
                        x_labels = [str(val) for val in grouped_x.groups.keys()]
                        if y_info["display_name"] == "Número de Transacciones":
                            y_data = grouped_x.size().values
                        elif y_info["display_name"] == "Cantidad Vendida":
                            # Requiere unir y agrupar
                            merged_df = pd.merge(df_compras, df_productos_detallado, on=['id_transaccion', 'fecha', 'usuario', 'metodo_pago', 'total_pagado'], how='inner', suffixes=('_compra', '_prod'))
                            grouped_y = merged_df.groupby('total_pagado')['cantidad_prod'].sum()
                            y_data = grouped_y.reindex(grouped_x.groups.keys(), fill_value=0).values
                        else:
                            raise ValueError(f"Combinación de ejes X='{eje_x_key}' e Y='{eje_y_key}' no es compatible para 'Total Pagado' como Eje X.")
                    
                    elif x_info["display_name"] == "Cantidad Vendida":
                        grouped_x = df_productos_detallado.groupby('cantidad')
                        x_labels = [str(val) for val in grouped_x.groups.keys()]
                        if y_info["display_name"] == "Total Pagado":
                            y_data = grouped_x['subtotal'].sum().values
                        elif y_info["display_name"] == "Número de Transacciones":
                            y_data = grouped_x['id_transaccion'].nunique().values
                        else:
                            raise ValueError(f"Combinación de ejes X='{eje_x_key}' e Y='{eje_y_key}' no es compatible para 'Cantidad Vendida' como Eje X.")
                    
                    elif x_info["display_name"] == "Número de Transacciones":
                        # Esto es más complejo ya que 'Número de Transacciones' es una métrica en sí misma.
                        # Una gráfica de barras con 'Número de Transacciones' en el eje X y algo más en Y
                        # implicaría agrupar por el *conteo* de transacciones, lo cual es inusual.
                        # Podríamos mostrar la distribución de 'Número de Transacciones' o forzar un scatter plot.
                        messagebox.showwarning("Eje X Numérico", "Graficar 'Número de Transacciones' como Eje X puede ser complejo para barras/líneas. Considera otros tipos de gráficos o variables categóricas/temporales para el Eje X.")
                        # Como una solución simple, agruparemos por el ID de transacción y tomaremos el número de productos como el eje X,
                        # y luego la suma de 'Total Pagado' para ese número de productos.
                        # Esto es una interpretación muy específica y podría no ser lo que el usuario espera.
                        # Por defecto, en este caso, se podría agrupar por el conteo de productos por transacción.
                        trans_product_counts = df_productos_detallado.groupby('id_transaccion')['cantidad'].sum().reset_index()
                        grouped_x = trans_product_counts.groupby('cantidad')
                        x_labels = [str(val) for val in grouped_x.groups.keys()]
                        
                        if y_info["display_name"] == "Total Pagado":
                            # Sumar el total pagado para transacciones con esa cantidad de productos
                            merged_df_for_nt = pd.merge(trans_product_counts, df_compras, on='id_transaccion')
                            grouped_y = merged_df_for_nt.groupby('cantidad')['total_pagado'].sum()
                            y_data = grouped_y.reindex(grouped_x.groups.keys(), fill_value=0).values
                        else:
                            raise ValueError(f"Combinación de ejes X='{eje_x_key}' e Y='{eje_y_key}' no es compatible para 'Número de Transacciones' como Eje X.")
                else:
                    raise ValueError("Tipo de variable no manejado para el eje X.")


                # Crear la gráfica según el tipo seleccionado
                if tipo_grafica == "Barras":
                    ax.bar(x_labels, y_data, color='#195E5E')
                    ax.set_ylabel(y_info["display_name"])
                elif tipo_grafica == "Líneas":
                    ax.plot(x_labels, y_data, marker='o', color='#B7CE63')
                    ax.set_ylabel(y_info["display_name"])
                elif tipo_grafica == "Pastel":
                    if x_info["type"] not in ["categorical", "temporal"]:
                        messagebox.showerror("Gráfica de Pastel", "Las gráficas de Pastel requieren una variable categórica o temporal en el Eje X para mostrar proporciones.")
                        return
                    if y_info["type"] not in ["numerical", "numerical_count"]:
                        messagebox.showerror("Gráfica de Pastel", "Las gráficas de Pastel requieren una variable numérica (como 'Total Pagado', 'Cantidad Vendida' o 'Número de Transacciones') en el Eje Y.")
                        return

                    # Re-agrupación específica para pastel, que requiere una única serie de valores
                    labels_pie = []
                    values_pie = []

                    if x_info["display_name"] == "Fecha":
                        if "Diario" in eje_x_key:
                            grouped_for_pie = df_compras.groupby(df_compras['fecha'].dt.date)
                            grouped_prod_for_pie = df_productos_detallado.groupby(df_productos_detallado['fecha'].dt.date)
                        else:
                            grouped_for_pie = df_compras.groupby(df_compras['fecha'].dt.to_period('M'))
                            grouped_prod_for_pie = df_productos_detallado.groupby(df_productos_detallado['fecha'].dt.to_period('M'))
                        
                        if y_info["display_name"] == "Total Pagado":
                            total_by_group = grouped_for_pie['total_pagado'].sum()
                        elif y_info["display_name"] == "Número de Transacciones":
                            total_by_group = grouped_for_pie.size()
                        elif y_info["display_name"] == "Cantidad Vendida":
                            total_by_group = grouped_prod_for_pie['cantidad'].sum()
                        else:
                            raise ValueError("Combinación de ejes no válida para gráfico de pastel con Fechas.")
                        labels_pie = [str(item) for item in total_by_group.index]
                        values_pie = total_by_group.values

                    elif x_info["display_name"] == "Producto":
                        grouped_for_pie = df_productos_detallado.groupby('nombre_producto')
                        if y_info["display_name"] == "Cantidad Vendida":
                            total_by_group = grouped_for_pie['cantidad'].sum()
                        elif y_info["display_name"] == "Total Pagado":
                            total_by_group = grouped_for_pie['subtotal'].sum()
                        elif y_info["display_name"] == "Número de Transacciones":
                            total_by_group = grouped_for_pie['id_transaccion'].nunique()
                        else:
                            raise ValueError("Combinación de ejes no válida para gráfico de pastel con Productos.")
                        labels_pie = total_by_group.index
                        values_pie = total_by_group.values

                    elif x_info["display_name"] == "Usuario":
                        grouped_for_pie = df_compras.groupby('usuario')
                        if y_info["display_name"] == "Total Pagado":
                            total_by_group = grouped_for_pie['total_pagado'].sum()
                        elif y_info["display_name"] == "Número de Transacciones":
                            total_by_group = grouped_for_pie.size()
                        elif y_info["display_name"] == "Cantidad Vendida":
                            # Requiere agrupar df_productos_detallado por usuario
                            total_by_group = df_productos_detallado.groupby('usuario')['cantidad'].sum()
                        else:
                            raise ValueError("Combinación de ejes no válida para gráfico de pastel con Usuarios.")
                        labels_pie = total_by_group.index
                        values_pie = total_by_group.values

                    elif x_info["display_name"] == "Método de Pago":
                        grouped_for_pie = df_compras.groupby('metodo_pago')
                        if y_info["display_name"] == "Total Pagado":
                            total_by_group = grouped_for_pie['total_pagado'].sum()
                        elif y_info["display_name"] == "Número de Transacciones":
                            total_by_group = grouped_for_pie.size()
                        elif y_info["display_name"] == "Cantidad Vendida":
                            # Requiere unir df_compras con df_productos_detallado por id_transaccion
                            merged_df_for_pie = pd.merge(df_compras, df_productos_detallado, on=['id_transaccion', 'fecha', 'usuario', 'metodo_pago'], how='inner', suffixes=('_compra', '_prod'))
                            total_by_group = merged_df_for_pie.groupby('metodo_pago')['cantidad_prod'].sum()
                        else:
                            raise ValueError("Combinación de ejes no válida para gráfico de pastel con Métodos de Pago.")
                        labels_pie = total_by_group.index
                        values_pie = total_by_group.values
                    
                    if len(values_pie) == 0 or sum(values_pie) == 0:
                         messagebox.showwarning("Sin datos para Pastel", "No hay datos para la combinación seleccionada o los valores son cero para generar un gráfico de pastel.")
                         return

                    ax.pie(values_pie, labels=labels_pie, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                    ax.axis('equal') # Asegura que el pastel sea circular

                ax.set_title(f'{tipo_grafica} de {y_info["display_name"]} por {x_info["display_name"]}')
                ax.set_xlabel(x_info["display_name"])
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=graph_canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            except Exception as e:
                messagebox.showerror("Error al generar gráfica", f"Ocurrió un error: {e}. Asegúrate de que las variables seleccionadas sean compatibles con el tipo de gráfica y que haya datos para ellas.")
                if canvas:
                    canvas.get_tk_widget().destroy()
                plt.close('all')


        tk.Button(controls_frame, text="Generar Gráfica", command=generar_y_mostrar_grafica, bg="#AED581").grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(stats_frame, text="Volver al Panel de Administración", command=stats_window.destroy, bg="lightgray").pack(pady=10)

        # Generar la gráfica inicial al abrir la ventana de estadísticas
        generar_y_mostrar_grafica()

        stats_window.mainloop()

    # --- Configuración de la Barra de Navegación ---
    tk.Button(nav, image=icon_inicio, command=go_inicio, bg="white").pack(side="left", expand=True)
    tk.Button(nav, image=icon_buscar, command=go_buscar, bg="white").pack(side="left", expand=True)
    tk.Button(nav, image=icon_carrito, command=go_carrito, bg="white").pack(side="left", expand=True)
    tk.Button(nav, image=icon_usuario, command=go_usuario, bg="white").pack(side="left", expand=True)
    tk.Button(nav, image=icon_admin, command=go_admin, bg="white").pack(side="left", expand=True)

    # Iniciar la aplicación en la vista de inicio por defecto
    go_inicio()
    root_tienda_app.mainloop()

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    iniciar_autenticacion()