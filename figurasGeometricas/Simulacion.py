# Importar el módulo tkinter con alias 'tk' para crear interfaces gráficas
import tkinter as tk
# Importar diálogos específicos de tkinter para abrir archivos y elegir colores
from tkinter import filedialog, colorchooser
# Importar clases de PIL para manejar imágenes
from PIL import Image, ImageTk, EpsImagePlugin
# Importar módulos matemáticos y de sistema operativo
import math
# Importar módulos en los cuales nos permite utilizar metodos para guardar y abrir nuestro proyecto
import pickle 
# Importar logging nos permite mostrar mensajes  en la terminal 
import logging

# Asegurarse de que Ghostscript esté instalado para manejar archivos PostScript
# En algunos sistemas, puede ser necesario configurar la ruta a Ghostscript
# EpsImagePlugin.gs_windows_binary = r'path_to_gswin64c.exe'

# Configuración del logger indicamos que tipos de mensajes podemos tener en el logger asi mismo como sera la configuracion
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de detalle (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Formato de los mensajes
    datefmt="%Y-%m-%d %H:%M:%S"  # Formato de la fecha
)
# Indicamos nombre de nuestro log que se mostrara en la terminal
logger = logging.getLogger("Aplicacion")


# Creacion de variables globales  nos permitiran almacenar todos los datos 
"""
 estas varibles son alamacenes de las figruas, putos de la flecha y asi mismo tambien 
 las imagenes en la cual despues se pueden utilizar para modificar,guardar,y abrir
"""
figuras = []  # Lista de figuras geométricas
puntosFlecha = [] # lista que almacena los puntos de las flechas
provicional = [] # lista que almacena el objeto de la figura  con los puntos 
images = [] # lista de imagenes que permite realizar el alamcenamiento de las imagenes

# Definición de la clase base 'Figura' para manejar figuras geométricas en el canvas
"""
 Esta clase nos permite tener las propiedades de las figuras estas figuras tienes 
 ciertos atributos en los cuales se manipula en el transcurso del proyecto asi como
 color, vertices, puntos etc 

"""
class Figura:
    # Método constructor de la clase Figura SOLO SE EJECUTA UNA VES CUANDO LA CLASES ES LLAMADA
    def __init__(self, canvas,color_figura =None, color_puntos="red"):
        self.canvas = canvas  # Referencia al canvas donde se dibuja la figura
        self.color_figura = color_figura  # Color de la figura (sin establecer aún)
        self.color_puntos = color_puntos  # Color de los puntos de la figura
        self.id_figura = None  # ID de la figura en el canvas
        self.vertices = []  # Lista de vértices de la figura
        self.puntos_ids = []  # IDs de los vértices en el canvas
        self.puntos_arista_ids = []  # IDs de los puntos en las aristas
        self.edge_points = []  # Coordenadas de los puntos en las aristas
        self.flechas = []  # Lista de flechas conectando puntos
        # Estado de selección de la figura
        self.seleccionada = False

    # Método que nos permite obtener el color de las figuras
    def seleccionar_color(self):
        color = colorchooser.askcolor(title="Seleccionar color")
        self.color_figura = color[1] if color[1] is not None else "black"
        logger.info(f"Se selecciono un color para la figura Color: {color} ")


    # Método que nos permite llamar el metodo  del color para asi realizar las validaciones 
    def obtener_color_figura(self):
        if self.color_figura is None:
            self.seleccionar_color()
        return self.color_figura
    
    # Método para dibujar la figura (a implementar en clases derivadas)
    def dibujar(self):
        pass

    # Método para colocar los puntos de la figura en el canvas
    def colocar_puntos(self):
        # Eliminar puntos anteriores de vértices
        for punto_id in self.puntos_ids:
            self.canvas.delete(punto_id)
        self.puntos_ids.clear()

        # Eliminar puntos anteriores de aristas
        for punto_id in self.puntos_arista_ids:
            self.canvas.delete(punto_id)
        self.puntos_arista_ids.clear()

        # Limpiar la lista de puntos en aristas
        self.edge_points.clear()

        # Crear puntos visuales para cada vértice de la figura
        for x, y in self.vertices:
            punto_id = self.canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                fill=self.color_puntos, tags="punto"
            )
            self.puntos_ids.append(punto_id)  # Guardar el ID del punto

        # Asociar eventos de clic solo a los puntos de vértices
        for punto_id in self.puntos_ids:
            self.canvas.tag_bind(punto_id, "<Button-1>", self.seleccionar_punto)

        # Crear puntos en las aristas (puntos medios) si la figura tiene aristas
        if not isinstance(self, Circulo):
            num_vertices = len(self.vertices)  # Número de vértices de la figura
            for i in range(num_vertices):
                # Obtener las coordenadas de dos vértices consecutivos
                x0, y0 = self.vertices[i]
                x1, y1 = self.vertices[(i + 1) % num_vertices]
                # Calcular el punto medio de la arista
                xm = (x0 + x1) / 2
                ym = (y0 + y1) / 2
                self.edge_points.append((xm, ym))  # Guardar coordenadas del punto en arista
                # Crear un punto visual en el punto medio de la arista
                punto_arista_id = self.canvas.create_oval(
                    xm - 5, ym - 5, xm + 5, ym + 5,
                    fill=self.color_puntos, tags="punto_arista"
                )
                self.puntos_arista_ids.append(punto_arista_id)  # Guardar el ID del punto en arista

            # Asociar eventos de clic solo a los puntos en las aristas
            for punto_arista_id in self.puntos_arista_ids:
                self.canvas.tag_bind(punto_arista_id, "<Button-1>", self.seleccionar_punto)

    # Método para mover la figura en respuesta a eventos de arrastre
    def mover(self, event):
        global arrastrando, figura_seleccionada
        arrastrando = True
        figura_seleccionada =self.canvas.find_closest(event.x, event.y)[0]

        
        # Obtener las coordenadas actuales del evento
        x = event.x
        y = event.y
        # Obtener las coordenadas actuales de la figura en el canvas
        coords = self.canvas.coords(self.id_figura)
        if isinstance(self, Circulo):
            # Para círculos, calcular el centro a partir de las coordenadas
            x0, y0 = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
        else:
            # Para otras figuras, tomar la primera coordenada como referencia
            x0, y0 = coords[0], coords[1]
        # Calcular el desplazamiento en (x) y (y)
        dx = x - x0
        dy = y - y0

        # Mover la figura en el canvas
        self.canvas.move(self.id_figura, dx, dy)

        # Mover los puntos de vértice
        for punto_id in self.puntos_ids:
            self.canvas.move(punto_id, dx, dy)

        # Mover los puntos en las aristas
        for punto_arista_id in self.puntos_arista_ids:
            self.canvas.move(punto_arista_id, dx, dy)

        # Actualizar las posiciones de los vértices con el desplazamiento
        self.vertices = [(vx + dx, vy + dy) for vx, vy in self.vertices]
        
        # Ciclo que nos pemite buscar las figuras con el id y asi remplazar los vertices para tenelos actulizados 
        for figura in figuras:
            if figura['idfigura'] == self.id_figura:
                figura['vertices'] = self.vertices
                break
    
        #looger 
        logger.info(f"Se actualizaron los vertices de figura con el id: {self.id_figura}, con los vertices de : {self.vertices}, estatus de arrastrado: {arrastrando}")
        # Recolocar los puntos después del movimiento
        self.colocar_puntos()
        # Actualizar las flechas conectadas a esta figura
        self.actualizar_flechas()
    
    
    # Método para manejar la selección de un punto
    def seleccionar_punto(self, event):
        # Obtener las coordenadas del clic
        punto = (event.x, event.y)
        # Encontrar el punto más cercano al clic
        self.encontrar_punto_mas_cercano(punto)
        # Llamar al método de la aplicación para manejar la selección
        app.seleccionar_punto(punto, self)

    # Método para agregar una flecha entre dos puntos de figuras
    def agregar_flecha(self, punto_inicio, punto_destino, otra_figura):
        try:
            # Obtener el tipo e índice del punto de inicio
            inicio_tipo, inicio_idx = self.obtener_indice_punto(punto_inicio)
            # Obtener el tipo e índice del punto de destino en otra figura
            destino_tipo, destino_idx = otra_figura.obtener_indice_punto(punto_destino)
     
            # Ciclo que nos permite recorrer las figruas y obtener la que necesitamos para asi poder manipular sus puntos 
            for figura in figuras:
                if figura['idfigura'] == self.id_figura:
                    figura['punto_inicio'] = punto_inicio
                    figura['punto_destino'] = punto_destino
                    break
            # logger
            logger.info(f"Se agrego la flecha con el id de la figura: {self.id_figura}, con el punto de inicio de: {punto_inicio}, punto de destino: {punto_destino} ")

        except ValueError:
            # Si alguno de los puntos no es válido, imprimir error y salir
            logger.error(f"Error: Uno de los puntos seleccionados no es un punto válido id de la figura: {self.id_figura}")
            return
        
        # Crear una línea (flecha) en el canvas desde el punto de inicio al destino
        flecha_id = self.canvas.create_line(
            punto_inicio[0], punto_inicio[1],
            punto_destino[0], punto_destino[1],
            fill=app.color_flecha, arrow=tk.LAST
        )
        # Almacenar la flecha con sus detalles en la lista de flechas de ambas figuras
        self.flechas.append((flecha_id, (inicio_tipo, inicio_idx), otra_figura, (destino_tipo, destino_idx)))
        otra_figura.flechas.append((flecha_id, (destino_tipo, destino_idx), self, (inicio_tipo, inicio_idx)))
        

        # Actualizar las flechas para reflejar cualquier cambio
        self.actualizar_flechas()

    # Método para actualizar la posición de todas las flechas conectadas
    def actualizar_flechas(self):
        # Imprime la lista de todas las flechas de la figura
        for flecha in self.flechas:
            logger.info(f"Lista de flechas: {flecha}")
            
        # Ciclo que nos permite actualizar las cordenadas de los puntos junto con sus flechas
        for flecha in self.flechas:
            flecha_id, inicio_idx, figura_destino, destino_idx = flecha
            # Obtener las coordenadas actuales de los puntos de inicio y destino
            punto_inicio = self.obtener_coordenada_punto(inicio_idx)
            punto_destino = figura_destino.obtener_coordenada_punto(destino_idx)
            # Actualizar las coordenadas de la flecha en el canvas
            self.canvas.coords(
                flecha_id,
                punto_inicio[0], punto_inicio[1],
                punto_destino[0], punto_destino[1]
            )
            logger.info(f"Se actializo la distancia de la flecha: {flecha_id}")
            
        


    # Método para obtener el índice y tipo de un punto dado
    def obtener_indice_punto(self, punto):
        # Determina si el punto es un vértice o un punto en la arista
        if punto in self.vertices:
            return ('vertex', self.vertices.index(punto))
        elif punto in self.edge_points:
            return ('edge', self.edge_points.index(punto))
        else:

            raise ValueError("Punto no encontrado en esta figura.")

    # Método para obtener las coordenadas de un punto dado su índice
    def obtener_coordenada_punto(self, indice):
        tipo, idx = indice
        if tipo == 'vertex':
            return self.vertices[idx]
        elif tipo == 'edge':
            return self.edge_points[idx]

    # Método para encontrar el punto más cercano a unas coordenadas dadas
    def encontrar_punto_mas_cercano(self, punto):
        x, y = punto  # Coordenadas del punto dado
        min_distancia = float("inf")  # Inicializar la distancia mínima
        punto_mas_cercano = None  # Variable para almacenar el punto más cercano
        tipo_punto = None  # Tipo del punto más cercano (vértice o arista)
        idx_mas_cercano = None  # Índice del punto más cercano

        # Revisar todos los vértices para encontrar el más cercano
        for idx, (vx, vy) in enumerate(self.vertices):
            distancia = math.sqrt((x - vx) ** 2 + (y - vy) ** 2)  # Calcular distancia euclidiana
            if distancia < min_distancia:
                min_distancia = distancia
                punto_mas_cercano = (vx, vy)
                tipo_punto = 'vertex'
                idx_mas_cercano = idx

        # Revisar todos los puntos en las aristas para encontrar el más cercano
        for idx, (ex, ey) in enumerate(self.edge_points):
            distancia = math.sqrt((x - ex) ** 2 + (y - ey) ** 2)
            if distancia < min_distancia:
                min_distancia = distancia
                punto_mas_cercano = (ex, ey)
                tipo_punto = 'edge'
                idx_mas_cercano = idx

        # Retornar el punto más cercano encontrado y su información
        
        return punto_mas_cercano, tipo_punto, idx_mas_cercano

# Clase para manejar imágenes que se pueden arrastrar en el canvas
class DraggableImage:
    def __init__(self, canvas, image, x, y, file_path=None):
        self.canvas = canvas
        self.image = image
        self.image_id = self.canvas.create_image(x, y, image=self.image, anchor=tk.NW)
        self.file_path = file_path
        self.canvas.tag_bind(self.image_id, '<B1-Motion>', self.move_image)
        self.canvas.tag_bind(self.image_id, '<Button-1>', self.select_image)
        self.selected = False
        self.border_id = None

    # Método que nos permite obtener y mover las figuras
    def move_image(self, event):
        self.canvas.coords(self.image_id, event.x, event.y)
        if self.selected and self.border_id:
            x, y = self.canvas.coords(self.image_id)
            self.canvas.coords(self.border_id, x, y, x + self.image.width(), y + self.image.height())
        logger.info(f"Se actializo las cordenadas de la imagen con el id: {self.image_id}")

    #  Método que nos permite  selecionar la imagen por el usuario
    def select_image(self, event):
        self.selected = not self.selected
        if self.selected:
            x, y = self.canvas.coords(self.image_id)
            self.border_id = self.canvas.create_rectangle(
                x, y, x + self.image.width(), y + self.image.height(),
                outline="blue", width=2
            )
            logger.info(f"Se selecciono la  imagen con el id: {self.image_id}")
        else:
            if self.border_id:
                self.canvas.delete(self.border_id)
                self.border_id = None

    # Método que nos pormite obtener las cordenadas de la figura
    def get_position(self):
        x, y = self.canvas.coords(self.image_id)
        return x, y

        

    

# Clase para representar un cuadrado, heredado de Figura
class Cuadrado(Figura):
    
    # Método para dibujar el cuadrado en el canvas
    def dibujar(self):
        # Definir las coordenadas de dos esquinas opuestas del cuadrado
        x0, y0, x1, y1 = 100, 100, 200, 200
     
        self.color_figura= self.obtener_color_figura()     
        # Crear un rectángulo en el canvas con las coordenadas definidas
        
        self.id_figura = self.canvas.create_rectangle(
            x0, y0, x1, y1,
            outline=self.color_figura, width=2, fill=self.color_figura
        )
        # Definir los vértices del cuadrado
        self.vertices = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)
    def dibujarEdicion(self):
        # Definir las coordenadas de dos esquinas opuestas del cuadrado
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")
        
        # Extraer las coordenadas de los vértices
        x0, y0 = self.vertices[0]  # Primer vértice
        x1, y1 = self.vertices[2]  # Tercer vértice (opuesto al primero)
     
        # Crear un rectángulo en el canvas con las coordenadas definidas
        
        self.id_figura = self.canvas.create_rectangle(
            x0, y0, x1, y1,
            outline=self.color_figura, width=2, fill=self.color_figura
        )
        # Definir los vértices del cuadrado
        self.vertices = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)



# Clase para representar un triángulo, heredado de Figura
class Triangulo(Figura):
   
    # Método para dibujar el triángulo en el canvas
    def dibujar(self):
        # Definir las coordenadas de los tres vértices del triángulo
        x0, y0 = 150, 100
        x1, y1 = 100, 200
        x2, y2 = 200, 200
        self.color_figura= self.obtener_color_figura()   
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            x0, y0, x1, y1, x2, y2,
            outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Definir los vértices del triángulo
        self.vertices = [(x0, y0), (x1, y1), (x2, y2)]
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)
    def dibujarEdicion(self):
        # Definir las coordenadas de dos esquinas opuestas del cuadrado
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")
        
        # Extraer las coordenadas de los vértices
        
        x0, y0 = self.vertices[0]
        x1, y1 = self.vertices[1]
        x2, y2 = self.vertices[2]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            x0, y0, x1, y1, x2, y2,
            outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Definir los vértices del triángulo
        self.vertices = [(x0, y0), (x1, y1), (x2, y2)]
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

# Clase para representar un círculo, heredado de Figura
class Circulo(Figura):

    

    # Método para dibujar el círculo en el canvas
    def dibujar(self):
        # Definir el centro y el radio del círculo
        x0, y0 = 150, 150
        radio = 80
        self.color_figura= self.obtener_color_figura()   
        # Crear un óvalo en el canvas que representa el círculo
        self.id_figura = self.canvas.create_oval(
            x0 - radio, y0 - radio, x0 + radio, y0 + radio,
            outline=self.color_figura, width=2, fill=self.color_figura
        )
        # Definir puntos en la circunferencia del círculo
        num_puntos = 8  # Número de puntos equidistantes
        self.vertices = []
        for i in range(num_puntos):
            # Calcular el ángulo para cada punto
            angulo = math.radians(360 / num_puntos * i)
            # Calcular las coordenadas del punto en la circunferencia
            x = x0 + radio * math.cos(angulo)
            y = y0 + radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

    #METODO PARA DIBUJAR LA FIGURA DESPUES DE GUARDARLO
    
    # Método para dibujar el círculo en el canvas
    def dibujarCarga(self):
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")
        
        # Extraer las coordenadas de los vértices
        x0, y0 = self.vertices[0]  # Primer vértice
        radio = 80
        # Crear un óvalo en el canvas que representa el círculo
        self.id_figura = self.canvas.create_oval(
            x0 - radio, y0 - radio, x0 + radio, y0 + radio,
            outline=self.color_figura, width=2, fill=self.color_figura
        )
        # Definir puntos en la circunferencia del círculo
        num_puntos = 8  # Número de puntos equidistantes
        self.vertices = []
        for i in range(num_puntos):
            # Calcular el ángulo para cada punto
            angulo = math.radians(360 / num_puntos * i)
            # Calcular las coordenadas del punto en la circunferencia
            x = x0 + radio * math.cos(angulo)
            y = y0 + radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

    # Método para mover el círculo correctamente
    def mover(self, event):
        # Obtener las coordenadas actuales del evento
        x = event.x
        y = event.y
        # Obtener las coordenadas actuales del círculo en el canvas
        coords = self.canvas.coords(self.id_figura)
        # Calcular el centro del círculo
        x0, y0 = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
        # Calcular el desplazamiento en (x) y (y)
        dx = x - x0
        dy = y - y0

        # Mover el círculo en el canvas
        self.canvas.move(self.id_figura, dx, dy)

        # Mover los puntos de vértice
        for punto_id in self.puntos_ids:
            self.canvas.move(punto_id, dx, dy)

        # No hay puntos en las aristas para el círculo, así que no se mueven

        # Actualizar las posiciones de los vértices con el desplazamiento
        self.vertices = [(vx + dx, vy + dy) for vx, vy in self.vertices]
        print("SE ACTUALIZO EL MOVIMIENTO")
        # Recolocar los puntos después del movimiento
        print("--------------------METODO PARA MOVER LA FIGURA-------------------------------")
        print("verticesx actualizdos",self.vertices)
        print("obtener tipo de figura", self.id_figura)
    
        for figura in figuras:
            if figura['idfigura'] == self.id_figura:
                figura['vertices'] = self.vertices
                break
        
        for figura in figuras:
            print(figura)
        
        print("---------------------------------------------FIN-------------------------------")
        self.colocar_puntos()
        # Actualizar las flechas conectadas a esta figura
        self.actualizar_flechas()

    # Método para colocar los puntos específicos del círculo en el canvas
    def colocar_puntos(self):
        # Eliminar puntos anteriores de vértices
        for punto_id in self.puntos_ids:
            self.canvas.delete(punto_id)
        self.puntos_ids.clear()

        # No hay puntos en las aristas para el círculo, así que eliminarlos si existen
        for punto_id in self.puntos_arista_ids:
            self.canvas.delete(punto_id)
        self.puntos_arista_ids.clear()
        self.edge_points.clear()

        # Crear puntos visuales para cada vértice (circunferencia)
        for x, y in self.vertices:
            punto_id = self.canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                fill=self.color_puntos, tags="punto"
            )
            self.puntos_ids.append(punto_id)  # Guardar el ID del punto

        # Asociar eventos de clic solo a los puntos de vértices
        for punto_id in self.puntos_ids:
            self.canvas.tag_bind(punto_id, "<Button-1>", self.seleccionar_punto)

# Clase para representar un pentágono, heredado de Figura
class Pentagono(Figura):
    
    # Método para dibujar el pentágono en el canvas
    def dibujar(self):
        # Definir el centro y el radio del pentágono
        centro_x, centro_y = 150, 150
        radio = 80
        self.color_figura= self.obtener_color_figura()   
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(5):
            # Calcular el ángulo para cada vértice del pentágono
            angulo = math.radians(90 + i * 72)
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)
    def dibujarEdicion(self):
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")
        # Extraer las coordenadas de los vértices
        # Primer vértice
        # Definir el centro y el radio del pentágono
        centro_x, centro_y = self.vertices[0]
        radio = 80
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(5):
            # Calcular el ángulo para cada vértice del pentágono
            angulo = math.radians(90 + i * 72)
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

# Clase para representar un hexágono, heredado de Figura
class Hexagono(Figura):
    
    # Método para dibujar el hexágono en el canvas
    def dibujar(self):
        # Definir el centro y el radio del hexágono
        centro_x, centro_y = 150, 150
        radio = 80
        self.color_figura= self.obtener_color_figura()   
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(6):
            # Calcular el ángulo para cada vértice del hexágono
            angulo = math.radians(90 + i * 60)
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)
    def dibujarEdicion(self):
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")
        # Definir el centro y el radio del hexágono
        centro_x, centro_y = self.vertices[0]
        radio = 80
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(6):
            # Calcular el ángulo para cada vértice del hexágono
            angulo = math.radians(90 + i * 60)
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

# Clase para representar un heptágono, heredado de Figura
class Heptagono(Figura):
   
    # Método para dibujar el heptágono en el canvas
    def dibujar(self):
        # Definir el centro y el radio del heptágono
        centro_x, centro_y = 150, 150
        radio = 80
        self.color_figura= self.obtener_color_figura()   
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(7):
            # Calcular el ángulo para cada vértice del heptágono
            angulo = math.radians(90 + i * (360 / 7))
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)
    
    # Método para dibujar el heptágono en el canvas
    def dibujarEdicion(self):
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")

        # Definir el centro y el radio del heptágono
        centro_x, centro_y = self.vertices[0]
        radio = 80
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(7):
            # Calcular el ángulo para cada vértice del heptágono
            angulo = math.radians(90 + i * (360 / 7))
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

# Clase para representar un octágono, heredado de Figura
class Octagono(Figura):
    # Método para dibujar el octágono en el canvas

    def dibujar(self):
        # Definir el centro y el radio del octágono
        centro_x, centro_y = 150, 150
        radio = 80
        self.color_figura= self.obtener_color_figura()   
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(8):
            # Calcular el ángulo para cada vértice del octágono, iniciando en 22.5 grados para alinear
            angulo = math.radians(22.5 + i * 45)
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)
    def dibujarEdicion(self):
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")
        # Definir el centro y el radio del octágono
        centro_x, centro_y = self.vertices[0]
        radio = 80
        self.vertices = []  # Lista para almacenar los vértices
        for i in range(8):
            # Calcular el ángulo para cada vértice del octágono, iniciando en 22.5 grados para alinear
            angulo = math.radians(22.5 + i * 45)
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

# Clase para representar una estrella, heredado de Figura
class Estrella(Figura):
   
    # Método para dibujar la estrella en el canvas
    def dibujar(self):
        # Definir el centro y los radios de la estrella
        centro_x, centro_y = 150, 150
        radio_externo = 80  # Radio de las puntas externas
        radio_interno = 35  # Radio de las puntas internas
        self.color_figura= self.obtener_color_figura()   
        self.vertices = []  # Lista para almacenar los vértices
        num_puntas = 5  # Número de puntas de la estrella
        for i in range(2 * num_puntas):
            # Calcular el ángulo para cada vértice de la estrella
            angulo = math.radians(90 + i * (360 / (2 * num_puntas)))
            # Alternar entre radio externo e interno
            if i % 2 == 0:
                radio = radio_externo
            else:
                radio = radio_interno
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)
    # Método para dibujar la estrella en el canvas
    def dibujarEdicion(self):
        if not self.vertices:
            raise ValueError("Los vértices no están definidos para dibujar la figura.")
        # Definir el centro y los radios de la estrella
        centro_x, centro_y = self.vertices[0]
        radio_externo = 80  # Radio de las puntas externas
        radio_interno = 35  # Radio de las puntas internas
        self.vertices = []  # Lista para almacenar los vértices
        num_puntas = 5  # Número de puntas de la estrella
        for i in range(2 * num_puntas):
            # Calcular el ángulo para cada vértice de la estrella
            angulo = math.radians(90 + i * (360 / (2 * num_puntas)))
            # Alternar entre radio externo e interno
            if i % 2 == 0:
                radio = radio_externo
            else:
                radio = radio_interno
            # Calcular las coordenadas del vértice
            x = centro_x + radio * math.cos(angulo)
            y = centro_y - radio * math.sin(angulo)
            self.vertices.append((x, y))
        # Preparar las coordenadas para crear el polígono
        puntos = [coord for vertex in self.vertices for coord in vertex]
        # Crear un polígono en el canvas con las coordenadas definidas
        self.id_figura = self.canvas.create_polygon(
            puntos, outline=self.color_figura, fill=self.color_figura, width=2
        )
        # Colocar los puntos de la figura en el canvas
        self.colocar_puntos()
        # Asociar el evento de movimiento del mouse al método mover
        self.canvas.tag_bind(self.id_figura, "<B1-Motion>", self.mover)

# Clase principal de la aplicación
class Aplicacion:
    # Método constructor de la clase Aplicacion
    def __init__(self):
        self.ventana = tk.Tk()  # Crear la ventana principal
        self.ventana.title("Aplicación de Figuras Geométricas")  # Título de la ventana
        # Configurar el tamaño de la ventana para que ocupe toda la pantalla
        self.ventana.geometry("{0}x{1}+0+0".format(
            self.ventana.winfo_screenwidth(), self.ventana.winfo_screenheight()
        ))
        self.canvas = tk.Canvas(self.ventana, bg="white")  # Crear un canvas con fondo blanco
        self.canvas.pack(fill=tk.BOTH, expand=True)  # Empaquetar el canvas para que ocupe todo el espacio

        # Crear la barra de menú
        self.barramenu = tk.Menu(self.ventana)
        self.ventana.config(menu=self.barramenu)  # Configurar la barra de menú en la ventana

        # Crear el menú de Archivo
        self.menu_archivo = tk.Menu(self.barramenu, tearoff=0)
        # Agregar opciones al menú de Archivo para abrir imágenes y guardar el canvas
        self.menu_archivo.add_command(label="Abrir proyecto", command=self.cargar_figuras)
        self.menu_archivo.add_command(label="Guardar proyecto", command=self.guardar_canvas)
        # Añadir el menú de Archivo a la barra de menú principal
        self.barramenu.add_cascade(label="Archivo", menu=self.menu_archivo)

        # Crear el menú de Figuras
        self.menu_figuras = tk.Menu(self.barramenu, tearoff=0)
        # Agregar opciones al menú de Figuras para añadir diferentes formas
        self.menu_figuras.add_command(label="Agregar cuadrado", command= lambda:self.agregar_cuadrado('cuadrado'))
        self.menu_figuras.add_command(label="Agregar triángulo", command=lambda:self.agregar_triangulo('triangulo'))
        self.menu_figuras.add_command(label="Agregar círculo", command=lambda:self.agregar_circulo('circulo'))
        self.menu_figuras.add_command(label="Agregar pentágono", command=lambda:self.agregar_pentagono('pentago'))
        self.menu_figuras.add_command(label="Agregar hexágono", command=lambda:self.agregar_hexagono('hexagono'))
        self.menu_figuras.add_command(label="Agregar heptágono", command=lambda:self.agregar_heptagono('heptagono'))
        self.menu_figuras.add_command(label="Agregar octágono", command=lambda:self.agregar_octagono('octagono'))
        self.menu_figuras.add_command(label="Agregar estrella", command=lambda:self.agregar_estrella('estrella'))
        # Añadir el menú de Figuras a la barra de menú principal
        self.barramenu.add_cascade(label="Figuras", menu=self.menu_figuras)

        
        #crear menu para imagenes
        self.menu_imagenes = tk.Menu(self.barramenu, tearoff=0)
        self.menu_imagenes.add_command(label="Agregar Imagen", command=self.agregar_imagen)
        self.barramenu.add_cascade(label="Imagenes", menu=self.menu_imagenes)

        # Crear el menú de Flechas
        self.menu_flechas = tk.Menu(self.barramenu, tearoff=0)
        # Agregar opción para cambiar el color de las flechas
        self.menu_flechas.add_command(label="Color de flechas", command=self.cambiar_color_flecha)
        # Añadir el menú de Flechas a la barra de menú principal
        self.barramenu.add_cascade(label="Flechas", menu=self.menu_flechas)
        #Agregar opcion ayuda
        self.menu_ayuda = tk.Menu(self.barramenu, tearoff=0)
        self.menu_ayuda.add_command(label="Esta es una aplicación de ejemplo.")
        self.barramenu.add_cascade(label="Ayuda", menu=self.menu_ayuda)
        #Agregar version
        self.menu_acercade = tk.Menu(self.barramenu, tearoff=0)
        self.menu_acercade.add_command(label="Aplicación de Ejemplo\nVersión 2.0\n© 2025 Ejemplo Inc.")
        self.barramenu.add_cascade(label="Acerca de...", menu=self.menu_acercade)
         
        
        

        # Inicializar listas para almacenar figuras y imágenes
       
         # Lista para almacenar las imágenes arrastrables
        # Variables para manejar la selección de puntos para crear flechas
        self.punto_seleccionado = None
        self.figura_seleccionada = None
        self.tipo_punto_seleccionado = None
        self.idx_punto_seleccionado = None
        self.color_flecha = "black"  # Color por defecto de las flechas
        self.figurase = Figura(self.canvas)  # Pass `canvas` to Figura
    # Método para agregar una imagen al canvas
    def agregar_imagen(self):

        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.gif")]
        )
        if ruta_archivo:
            try:
                img = Image.open(ruta_archivo)
                img.thumbnail((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                new_image = DraggableImage(self.canvas, img_tk, 100, 100, ruta_archivo)
                images.append(new_image)
                logger.info(f"Se agrego la imagen en la ruta de: {ruta_archivo}")
                
                for imgfor in images:
                    logger.info(f"Imagenes cargadas: {imgfor}")
                    
            except Exception as e:
                print(f"[ERROR] Error al agregar la imagen: {e}")


    # Método para abrir una imagen (no utilizado actualmente)
    def abrir_imagen(self):
        # Esta función puede ser eliminada si ya no es necesaria
        # Ya que agregamos la funcionalidad en 'agregar_imagen'
        pass

    # Método para guardar el contenido del canvas como una imagen PNG
    def guardar_canvas(self):

        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])

        

        if ruta_archivo:
            estado = []
            for img in images:
                x, y = img.get_position()
                estado.append({'file_path': img.file_path, 'position': (x, y)})

        
        # Serializar las figuras y guardarlas en el archivo seleccionado
            with open(ruta_archivo, 'wb') as archivo_pkl:
                pickle.dump((figuras,puntosFlecha,estado), archivo_pkl)
            logger.info(f"Se guardo el proyecto en la ruta: {ruta_archivo}") 
            print("-------------------------Datos a guardar---------------------")
            print("Imagenes\n")
            for img in images:
                print(img)
            print("Figuras\n")
            for f in figuras:
                print(f)
            print("Puntos de las flechas\n")
            for p in puntosFlecha:
                print(p)
            print("---------------------------FIN-------------------------------")
               
           

        # Limpiar el canvas después de guardar
        
        self.limpiar_canvas()
        self.limpiar()

    def limpiar(self):
        figuras.clear()         # Limpia la lista de figuras
        puntosFlecha.clear()    # Limpia la lista de puntos de flecha
        provicional.clear()     # Limpia la lista de objetos provisionales
        images.clear()

    def cargar_figuras(self):
        self.limpiar()
        global figuras
        global puntosFlecha
        
    # Abrir cuadro de diálogo para seleccionar el archivo PKL
        file_path = filedialog.askopenfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
        if file_path:
            
        # Cargar el archivo PKL seleccionado
            with open(file_path, 'rb') as archivo_pkl:
                
                figuras_cargadas, puntosFlecha,estado = pickle.load(archivo_pkl)
                logger.info(f"Se cargo el proyecto en la ruta: {file_path}") 
                

            # Limpiar el canvas antes de dibujar las figuras cargadas
                self.limpiar_canvas()
                # Ciclo que nos permite obtener las figuras
                for img in images:
                    self.canvas.delete(img.image_id)
                images.clear()
                # ciclo para determinar las posiones de la figura y colocarla
                for data in estado:
                    img = Image.open(data['file_path'])
                    img.thumbnail((100, 100))
                    img_tk = ImageTk.PhotoImage(img)
                    x, y = data['position']
                    new_image = DraggableImage(self.canvas, img_tk, x, y, data['file_path'])
                    images.append(new_image)
                logger.info(f"Se cargo correctamente las imagenes de la ruta: {file_path}") 
                
                
                """
                Este ciclo recorre las figuras asi mismo cada ves que corre las figuras obtenemos el tipo de esta misma
                al obtener el tipo de figura indicamos una condicion para asi poder dibujarlo con los tributos guardados
                """
                figuras = figuras_cargadas
                for Recore in figuras:
                    if Recore['tipo'] == 'cuadrado':
                        figura = Cuadrado(self.canvas)  # Crear una instancia de Cuadrado
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        figura.dibujarEdicion()  # Dibujar el cuadrado en el canvas}
                        logger.info(f"Se creo la figura del tipo de: Cuadrado, con el id de: {figura.id_figura} con el objeto de: {figura}") 
                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                        }
                       
                        provicional.append(nuevaCargda)
                        
                    
                    if Recore['tipo'] == 'triangulo':
                        figura = Triangulo(self.canvas)  # Crear una instancia de Triangulo
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        figura.dibujarEdicion()  # Dibujar el Triangulo en el canvas}
                        logger.info(f"Se creo la figura del tipo de: triangulo, con el id de: {figura.id_figura} con el objeto de: {figura}")
                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                        }
                        
                        provicional.append(nuevaCargda)

                    if Recore['tipo'] == 'circulo':
                        figura = Circulo(self.canvas)  # Crear una instancia de circulo
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        
                        
                        figura.dibujarCarga()  # Dibujar el circulo en el canvas}
                        logger.info(f"Se creo la figura del tipo de: Circulo, con el id de: {figura.id_figura} con el objeto de: {figura}")
                        
                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                             
                        }
                       
                        provicional.append(nuevaCargda) 

                    if Recore['tipo'] == 'pentago':
                        figura = Pentagono(self.canvas)  # Crear una instancia de pentagoono
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        
                        
                        figura.dibujarEdicion()  # Dibujar el pentagono en el canvas}
                        logger.info(f"Se creo la figura del tipo de: pentagono, con el id de: {figura.id_figura} con el objeto de: {figura}")
                        

                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                             
                        }
                        
                        provicional.append(nuevaCargda)
                    if Recore['tipo'] == 'hexagono':
                        figura = Hexagono(self.canvas)  # Crear una instancia de hexagono
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        
                        
                        figura.dibujarEdicion()  # Dibujar el hexagono en el canvas}
                        logger.info(f"Se creo la figura del tipo de: hexagono, con el id de: {figura.id_figura} con el objeto de: {figura}")
                        

                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                             
                        }
                        
                        provicional.append(nuevaCargda) 
                    if Recore['tipo'] == 'heptagono':
                        figura = Heptagono(self.canvas)  # Crear una instancia de heptagono
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        
                        
                        figura.dibujarEdicion()  # Dibujar el heptagono en el canvas}
                        logger.info(f"Se creo la figura del tipo de: heptagono, con el id de: {figura.id_figura} con el objeto de: {figura}")
                        

                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                             
                        }
                       
                        provicional.append(nuevaCargda)
                    if Recore['tipo'] == 'octagono':
                        figura = Octagono(self.canvas)  # Crear una instancia de octagono
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        
                        
                        figura.dibujarEdicion()  # Dibujar el octagono en el canvas}
                        logger.info(f"Se creo la figura del tipo de: octagono, con el id de: {figura.id_figura} con el objeto de: {figura}")
                        

                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                             
                        }
                        
                        provicional.append(nuevaCargda)
                    if Recore['tipo'] == 'estrella':
                        figura = Estrella(self.canvas)  # Crear una instancia de estrella
                        figura.color_figura =Recore['color']
                        figura.vertices = Recore['vertices']
                        figura.id_figura = Recore['idfigura']
                        
                        
                        figura.dibujarEdicion()  # Dibujar el estrella en el canvas}
                        logger.info(f"Se creo la figura del tipo de: estrella, con el id de: {figura.id_figura} con el objeto de: {figura}")
                        

                        nuevaCargda ={
                            'idfigura' : Recore['idfigura'],
                            'figura': figura,
                            'idFiguraNueva': figura.id_figura
                             
                        }
                        
                        provicional.append(nuevaCargda)
                       

                print("-------------------------------------------------")
                for nuevafigura in provicional:
                    print(nuevafigura)
                listapuntonunevo =[]
                for elemento1 in puntosFlecha:
                    for elemento2 in figuras:
                        if elemento1['idfigura'] == elemento2['idfigura']:
                            # Llama al método si se encuentra una coincidencia
                            resultados = []
                            resultados = self.buscar_por_id(provicional, elemento2['idfigura'])
                          
                            figura = resultados[0]['figura']  # Accede al primer elemento de la lista
                            lip ={
                                'idpuntoactualizacoid':elemento2 ['idfigura'],
                                'puntoactuali':resultados[0]['idFiguraNueva']
                            }
                            listapuntonunevo.append(lip)
                            self.seleccionar_puntoCarga(elemento1['punto'],figura)
                

                print("punrtos felchas ")
                for elemento1 in puntosFlecha:
                     print(elemento1)
                for elemento1 in puntosFlecha:
                    for elemento2 in figuras:
                        if elemento1['idfigura'] == elemento2['idfigura']:
                            # Llama al método si se encuentra una coincidencia
                            resultados = []
                            resultados = self.buscar_por_id(provicional, elemento2['idfigura']) 
                            figura = resultados[0]['figura']  # Accede al primer elemento de la lista
                            elemento2 ['idfigura'] = resultados[0]['idFiguraNueva']
                           
                

                for d in figuras:
                    print(d)
                for elemento1 in listapuntonunevo:
                     print(elemento1)  # Imprimir el diccionario
                self.actualizar_puntos(puntosFlecha, listapuntonunevo)

                for elemento1 in puntosFlecha:
                     print(elemento1)
                
                
                


                                         



    def actualizar_puntos(self,puntosflecha, puntosnuevos):
    # Crear un diccionario de actualización basado en puntos nuevos
        actualizacion_dict = {item['idpuntoactualizacoid']: item['puntoactuali'] for item in puntosnuevos}

    # Actualizar los valores de idfigura en puntosflecha
        for punto in puntosflecha:
            if punto['idfigura'] in actualizacion_dict:
                punto['idfigura'] = actualizacion_dict[punto['idfigura']]

    def buscar_por_id(self,lista, idfigura):
        resultados = []
        for elemento in lista:
            if elemento.get('idfigura') == idfigura:
                resultados.append(elemento)
        return resultados  # Devuelve una lista de coincidencias
           

    # Método para cambiar el color de las flechas mediante un selector de colores
    def cambiar_color_flecha(self):
        # Abrir un diálogo para elegir un color
        color = colorchooser.askcolor(title="Seleccionar color para las flechas")
        if color[1]:
            self.color_flecha = color[1]  # Actualizar el color de las flechas

    # Métodos para agregar diferentes figuras geométricas al canvas
    def agregar_cuadrado(self, tipo):
        figura = Cuadrado(self.canvas)  # Crear una instancia de Cuadrado
        logger.info(f"Se agrego un figura(Cuadrado) nueva: {figura}") 
        figura.dibujar()  # Dibujar el cuadrado en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura 
        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def mostrar_figuras(self):
        if figuras:
            print("Lista de figuras:\n")
            for figura in figuras:
                logger.info(f"{figura}") 
                
        else:
            logger.error(f"La lista de figuras está vacía.")
            

    def agregar_triangulo(self, tipo):
        figura = Triangulo(self.canvas)  # Crear una instancia de Triangulo
        logger.info(f"Se agrego un figura(Triangulo) nueva: {figura}") 
        figura.dibujar()  # Dibujar el triángulo en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura
            

        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def agregar_circulo(self,tipo):
        figura = Circulo(self.canvas)  # Crear una instancia de Circulo
        logger.info(f"Se agrego un figura(Circulo) nueva: {figura}") 

        figura.dibujar()  # Dibujar el círculo en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura    
        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def agregar_pentagono(self,tipo):
        figura = Pentagono(self.canvas)  # Crear una instancia de Pentagono
        logger.info(f"Se agrego un figura(Pentagono) nueva: {figura}") 
        figura.dibujar()  # Dibujar el pentágono en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura
            

        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def agregar_hexagono(self,tipo):
        figura = Hexagono(self.canvas)  # Crear una instancia de Hexagono
        logger.info(f"Se agrego un figura(Hexagono) nueva: {figura}") 
        figura.dibujar()  # Dibujar el hexágono en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura
            
        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def agregar_heptagono(self,tipo):
        figura = Heptagono(self.canvas)  # Crear una instancia de Heptagono
        logger.info(f"Se agrego un figura(Heptagono) nueva: {figura}") 
        figura.dibujar()  # Dibujar el heptágono en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura
            

        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def agregar_octagono(self,tipo):
        figura = Octagono(self.canvas)  # Crear una instancia de Octagono
        logger.info(f"Se agrego un figura(Octagono) nueva: {figura}") 
        figura.dibujar()  # Dibujar el octágono en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura
            

        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def agregar_estrella(self,tipo):
        figura = Estrella(self.canvas)  # Crear una instancia de Estrella
        logger.info(f"Se agrego un figura(Estrella) nueva: {figura}") 
        figura.dibujar()  # Dibujar la estrella en el canvas
        figura = {
            'tipo': tipo,
            'color': figura.color_figura,
            'vertices':figura.vertices,
            'idfigura': figura.id_figura
            

        }
        figuras.append(figura)  # Agregar el cuadrado a la lista de figuras
        self.mostrar_figuras()

    def limpiar_canvas(self):
        self.canvas.delete("all")

    # Método para manejar la selección de un punto para crear flechas
    def seleccionar_punto(self, punto, figura):
        # Encontrar el punto más cercano al clic dentro de la figura\
        logger.info(f"Se selecciono un punto: {punto}, con el id de la figura: {figura.id_figura}") 
       
        puntosSelecionados = {    
            'punto': punto,
            'idfigura':figura.id_figura
        }
        puntosFlecha.append(puntosSelecionados)  # Agregar el cuadrado a la lista de figuras

        punto_mas_cercano, tipo_punto, idx_mas_cercano = figura.encontrar_punto_mas_cercano(punto)
        if punto_mas_cercano:
            if self.punto_seleccionado is None:
                # Si no hay un punto previamente seleccionado, seleccionar el actual
                self.punto_seleccionado = punto_mas_cercano
                self.figura_seleccionada = figura
                self.tipo_punto_seleccionado = tipo_punto
                self.idx_punto_seleccionado = idx_mas_cercano
                # Cambiar el color del punto seleccionado para indicar la selección
                if tipo_punto == 'vertex':
                    self.canvas.itemconfig(
                        figura.puntos_ids[idx_mas_cercano],
                        fill="blue"
                    )
                elif tipo_punto == 'edge':
                    self.canvas.itemconfig(
                        figura.puntos_arista_ids[idx_mas_cercano],
                        fill="blue"
                    )
            else:
                # Si ya hay un punto seleccionado, crear una flecha entre ambos puntos
                otro_punto = punto_mas_cercano
                otra_figura = figura
                tipo_otro_punto = tipo_punto
                idx_otro_punto = idx_mas_cercano
                # Evitar crear una flecha desde un punto a sí mismo

                if (self.punto_seleccionado != otro_punto) or (self.figura_seleccionada != otra_figura):
                    
                    
                    self.figura_seleccionada.agregar_flecha(
                        self.punto_seleccionado,
                        otro_punto,
                        otra_figura
                    )
                    logger.info(f"Puntos selecionoados") 
                    for puntodf in puntosFlecha:
                        print(puntodf)

                # Restaurar el color del punto seleccionado original
                if self.tipo_punto_seleccionado == 'vertex':
                    self.canvas.itemconfig(
                        self.figura_seleccionada.puntos_ids[self.idx_punto_seleccionado],
                        fill=self.figura_seleccionada.color_puntos
                    )
                elif self.tipo_punto_seleccionado == 'edge':
                    self.canvas.itemconfig(
                        self.figura_seleccionada.puntos_arista_ids[self.idx_punto_seleccionado],
                        fill=self.figura_seleccionada.color_puntos
                    )
                # Resetear la selección para futuros puntos
                

                self.punto_seleccionado = None
                self.figura_seleccionada = None
                self.tipo_punto_seleccionado = None
                self.idx_punto_seleccionado = None

    def seleccionar_puntoCarga(self, punto, figura):
       

        punto_mas_cercano, tipo_punto, idx_mas_cercano = figura.encontrar_punto_mas_cercano(punto)
        if punto_mas_cercano:
            if self.punto_seleccionado is None:
                # Si no hay un punto previamente seleccionado, seleccionar el actual
                self.punto_seleccionado = punto_mas_cercano
                self.figura_seleccionada = figura
                self.tipo_punto_seleccionado = tipo_punto
                self.idx_punto_seleccionado = idx_mas_cercano
                # Cambiar el color del punto seleccionado para indicar la selección
                if tipo_punto == 'vertex':
                    self.canvas.itemconfig(
                        figura.puntos_ids[idx_mas_cercano],
                        fill="blue"
                    )
                elif tipo_punto == 'edge':
                    self.canvas.itemconfig(
                        figura.puntos_arista_ids[idx_mas_cercano],
                        fill="blue"
                    )
            else:
                # Si ya hay un punto seleccionado, crear una flecha entre ambos puntos
                otro_punto = punto_mas_cercano
                otra_figura = figura
                tipo_otro_punto = tipo_punto
                idx_otro_punto = idx_mas_cercano
                # Evitar crear una flecha desde un punto a sí mismo

                if (self.punto_seleccionado != otro_punto) or (self.figura_seleccionada != otra_figura):
                   
                    
                    self.figura_seleccionada.agregar_flecha(
                        self.punto_seleccionado,
                        otro_punto,
                        otra_figura
                    )
                    logger.info(f"Puntos selecionoados") 
                    for puntodf in puntosFlecha:
                        print(puntodf)

                # Restaurar el color del punto seleccionado original
                if self.tipo_punto_seleccionado == 'vertex':
                    self.canvas.itemconfig(
                        self.figura_seleccionada.puntos_ids[self.idx_punto_seleccionado],
                        fill=self.figura_seleccionada.color_puntos
                    )
                elif self.tipo_punto_seleccionado == 'edge':
                    self.canvas.itemconfig(
                        self.figura_seleccionada.puntos_arista_ids[self.idx_punto_seleccionado],
                        fill=self.figura_seleccionada.color_puntos
                    )
                # Resetear la selección para futuros puntos
                

                self.punto_seleccionado = None
                self.figura_seleccionada = None
                self.tipo_punto_seleccionado = None
                self.idx_punto_seleccionado = None
           

# Bloque principal para ejecutar la aplicación
if __name__ == "__main__":
    app = Aplicacion()  # Crear una instancia de la aplicación
    app.ventana.mainloop()  # Iniciar el bucle principal de la interfaz gráfica
