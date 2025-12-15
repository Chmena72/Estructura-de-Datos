import json, csv, time, math, random
from typing import List, Dict, Optional
import matplotlib.pyplot as plt, pandas as pd, numpy as np

GRAFICAS_DISPONIBLES = True

# CLASE PRODUCTO

class ProductoInventario:
    """Clase que representa un producto en el inventario"""
    
    def __init__(self, id: str, nombre: str, categoria: str, stock: int):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.stock = stock
    
    def __str__(self):
        return f"[{self.id}] {self.nombre} - {self.categoria} (Stock: {self.stock})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'stock': self.stock
        }

# CLASE TABLA HASH

class TablaHash:
    """Implementación de Tabla Hash con encadenamiento separado para la gestión de inventario de productos"""
    
    def __init__(self, capacidad_esperada: int = 1000):
        """Inicializa la tabla hash
        Args: capacidad_esperada: Número máximo de elementos esperados"""
       
        self.capacidad_esperada = capacidad_esperada
        self.tamanio = self._siguiente_primo(int(capacidad_esperada * 1.33))
        self.tabla = [[] for _ in range(self.tamanio)]
        self.num_elementos = 0
        self.num_colisiones = 0
    
    def _es_primo(self, n: int) -> bool:
        """Verifica si un número es primo"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def _siguiente_primo(self, n: int) -> int:
        """Encuentra el siguiente número primo mayor o igual a n"""
        while not self._es_primo(n):
            n += 1
        return n
    
    def _funcion_hash(self, clave: str) -> int:
        """Función hash usando el método de multiplicación
        Args:
            clave: Clave a hashear (ID del producto)
        Returns:
            Índice en la tabla hash"""
        
        hash_value = 0
        primo = 31
        
        for char in clave:
            hash_value = (hash_value * primo + ord(char)) % self.tamanio
        
        return hash_value
    
    def insertar(self, producto: ProductoInventario) -> bool:
        """Inserta un producto en la tabla hash
        Args:
            producto: Objeto ProductoInventario a insertar
        Returns:
            True si la inserción fue exitosa, False si la clave ya existe"""
            
        indice = self._funcion_hash(producto.id)
        bucket = self.tabla[indice]
        
        # Verificar si ya existe
        for item in bucket:
            if item.id == producto.id:
                return False
        
        # Contar colisión si el bucket ya tiene elementos
        if len(bucket) > 0:
            self.num_colisiones += 1
        
        bucket.append(producto)
        self.num_elementos += 1
        return True
    
    def buscar(self, clave: str) -> Optional[ProductoInventario]:
        """Busca un producto por su ID
        Args:
            clave: ID del producto a buscar
        Returns:
            Objeto ProductoInventario si se encuentra, None en caso contrario"""
        
        indice = self._funcion_hash(clave)
        bucket = self.tabla[indice]
        
        for producto in bucket:
            if producto.id == clave:
                return producto
        
        return None
    
    def eliminar(self, clave: str) -> bool:
        """Elimina un producto de la tabla hash
        Args:
            clave: ID del producto a eliminar
        Returns:
            True si se eliminó, False si no se encontró"""
        
        indice = self._funcion_hash(clave)
        bucket = self.tabla[indice]
        
        for i, producto in enumerate(bucket):
            if producto.id == clave:
                bucket.pop(i)
                self.num_elementos -= 1
                return True
        
        return False
    
    def actualizar(self, clave: str, nombre: str = None, categoria: str = None, stock: int = None) -> bool:
        """Actualiza los datos de un producto"""
        
        producto = self.buscar(clave)
        if producto is None:
            return False
        
        if nombre is not None:
            producto.nombre = nombre
        if categoria is not None:
            producto.categoria = categoria
        if stock is not None:
            producto.stock = stock
        
        return True
    
    def factor_de_carga(self) -> float:
        """Calcula el factor de carga actual"""
        return (self.num_elementos / self.tamanio) * 100
    
    def visualizar_tabla(self, limite: int = 20):
        """Muestra el estado de la tabla hash"""
        print(f"ESTADO DE LA TABLA HASH")
        print(f"Tamaño: {self.tamanio} | Elementos: {self.num_elementos} | "
              f"Factor de carga: {self.factor_de_carga():.2f}%")
        print(f"Colisiones totales: {self.num_colisiones}")
        
        for i in range(min(limite, self.tamanio)):
            bucket = self.tabla[i]
            if len(bucket) == 0:
                print(f"[{i:4d}] -> vacío")
            else:
                print(f"[{i:4d}] -> ", end="")
                for j, prod in enumerate(bucket):
                    if j > 0:
                        print(" -> ", end="")
                    print(f"{prod}", end="")
                if len(bucket) > 1:
                    print(f" [{len(bucket)} elementos]", end="")
                print()
    
    def estadisticas(self) -> Dict:
        """Retorna estadísticas detalladas de la tabla"""
        buckets_ocupados = sum(1 for bucket in self.tabla if len(bucket) > 0)
        longitud_maxima = max((len(bucket) for bucket in self.tabla), default=0)
        
        return {
            'tamanio': self.tamanio,
            'elementos': self.num_elementos,
            'factor_carga': self.factor_de_carga(),
            'colisiones': self.num_colisiones,
            'buckets_ocupados': buckets_ocupados,
            'longitud_maxima_cadena': longitud_maxima
        }
    
    def resetear_colisiones(self):
        """Resetea el contador de colisiones"""
        self.num_colisiones = 0

# FUNCIONES DE PRUEBAS DE RENDIMIENTO

def generar_datos_prueba(n: int) -> List[Dict]:
    """Genera datos de prueba aleatorios"""
    categorias = ['Electrónica', 'Oficina', 'Accesorios', 'Almacenamiento', 'Audio']
    nombres = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Audífonos', 'Webcam', 'Impresora', 'Disco Duro', 'Cable', 'Hub USB']
    
    datos = []
    for i in range(n):
        datos.append({
            'id': f'P{i+1:04d}',
            'nombre': f'{random.choice(nombres)} {random.choice(["Pro", "Plus", "Basic"])}',
            'categoria': random.choice(categorias),
            'stock': random.randint(1, 100)
        })
    return datos

def realizar_pruebas_rendimiento(n: int, repeticiones: int = 3) -> List[Dict]:
    """Realiza pruebas de rendimiento según especificaciones del proyecto"""
    
    print(f"PRUEBAS DE RENDIMIENTO CON N={n} ELEMENTOS ({repeticiones} repeticiones)")

    
    resultados = []
    
    for rep in range(repeticiones):
        print(f"Repetición {rep + 1}/{repeticiones}...")
        
        tabla = TablaHash(1000)
        datos = generar_datos_prueba(n)
        
        # 1. Inserción por lote
        inicio = time.perf_counter()
        for item in datos:
            producto = ProductoInventario(**item)
            tabla.insertar(producto)
        tiempo_insercion = (time.perf_counter() - inicio) * 1000
        
        # 2. Factor de carga y colisiones
        factor_carga = tabla.factor_de_carga()
        colisiones = tabla.num_colisiones
        
        # 3. Búsqueda de elementos existentes (25%)
        num_busquedas = n // 4
        claves_existentes = [f'P{i+1:04d}' for i in random.sample(range(n), num_busquedas)]
        
        inicio = time.perf_counter()
        for clave in claves_existentes:
            tabla.buscar(clave)
        tiempo_busqueda_exist = (time.perf_counter() - inicio) * 1000
        
        # 4. Búsqueda de elementos no existentes (25%)
        claves_inexistentes = [f'X{i:04d}' for i in range(num_busquedas)]
        
        inicio = time.perf_counter()
        for clave in claves_inexistentes:
            tabla.buscar(clave)
        tiempo_busqueda_noexist = (time.perf_counter() - inicio) * 1000
        
        # 5. Eliminación (25%)
        claves_eliminar = [f'P{i+1:04d}' for i in random.sample(range(n), num_busquedas)]
        
        inicio = time.perf_counter()
        for clave in claves_eliminar:
            tabla.eliminar(clave)
        tiempo_eliminacion = (time.perf_counter() - inicio) * 1000
        
        resultado = {
            'n': n,
            'repeticion': rep + 1,
            'tiempo_insercion': tiempo_insercion,
            'factor_carga': factor_carga,
            'colisiones': colisiones,
            'tiempo_busqueda_existentes': tiempo_busqueda_exist,
            'tiempo_busqueda_inexistentes': tiempo_busqueda_noexist,
            'tiempo_eliminacion': tiempo_eliminacion
        }
        
        resultados.append(resultado)
        
        print(f"  Inserción: {tiempo_insercion:.4f} ms")
        print(f"  Búsqueda (exist): {tiempo_busqueda_exist:.4f} ms")
        print(f"  Búsqueda (no exist): {tiempo_busqueda_noexist:.4f} ms")
        print(f"  Eliminación: {tiempo_eliminacion:.4f} ms")
        print(f"  Colisiones: {colisiones}\n")
    
    return resultados

def calcular_promedios(resultados: List[Dict]) -> Dict:
    """Calcula promedios de múltiples repeticiones"""
    n = resultados[0]['n']
    num_reps = len(resultados)
    
    return {
        'n': n,
        'tiempo_insercion_promedio': sum(r['tiempo_insercion'] for r in resultados) / num_reps,
        'factor_carga_promedio': sum(r['factor_carga'] for r in resultados) / num_reps,
        'colisiones_promedio': sum(r['colisiones'] for r in resultados) / num_reps,
        'tiempo_busqueda_exist_promedio': sum(r['tiempo_busqueda_existentes'] for r in resultados) / num_reps,
        'tiempo_busqueda_noexist_promedio': sum(r['tiempo_busqueda_inexistentes'] for r in resultados) / num_reps,
        'tiempo_eliminacion_promedio': sum(r['tiempo_eliminacion'] for r in resultados) / num_reps
    }


def guardar_resultados(resultados: List[Dict], nombre_archivo: str = 'resultados_pruebas.csv'):
    """Guarda los resultados en un archivo CSV"""
    if not resultados:
        print("  No hay resultados para guardar.")
        return

    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.DictWriter(f, fieldnames=resultados[0].keys())
        escritor.writeheader()
        escritor.writerows(resultados)

    print(f"\n Resultados guardados en '{nombre_archivo}'")

# CLASE ANALIZADOR DE RENDIMIENTO (GRÁFICAS)

class AnalizadorRendimiento:
    """Clase para analizar y visualizar resultados de pruebas"""
    
    def __init__(self, archivo_json='resultados_pruebas.json'):
        self.archivo_json = archivo_json
        self.datos = self._cargar_datos()
        self.promedios = self._calcular_promedios()
    
    def _cargar_datos(self):
        """Carga los datos desde el archivo JSON"""
        try:
            with open(self.archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            print(f" Datos cargados desde '{self.archivo_json}'")
            return datos
        except FileNotFoundError:
            print(f" Error: Archivo '{self.archivo_json}' no encontrado")
            return []
        except json.JSONDecodeError:
            print(f" Error: El archivo no es un JSON válido")
            return []
    
    def _calcular_promedios(self):
        """Calcula los promedios por cada valor de N"""
        if not self.datos or not GRAFICAS_DISPONIBLES:
            return None
        
        df = pd.DataFrame(self.datos)
        
        promedios = df.groupby('n').agg({
            'tiempo_insercion': 'mean',
            'factor_carga': 'mean',
            'colisiones': 'mean',
            'tiempo_busqueda_existentes': 'mean',
            'tiempo_busqueda_inexistentes': 'mean',
            'tiempo_eliminacion': 'mean'
        }).reset_index()
        
        promedios.columns = [
            'N Elementos',
            'Inserción (ms)',
            'Factor Carga (%)',
            'Colisiones',
            'Búsqueda Exist. (ms)',
            'Búsqueda No Exist. (ms)',
            'Eliminación (ms)'
        ]
        
        return promedios
    
    def generar_tabla_resumen(self, guardar_csv=True):
        """Genera y muestra tabla resumen"""
        if self.promedios is None or self.promedios.empty:
            print(" No hay datos para generar tabla")
            return
        
        print("TABLA RESUMEN - PROMEDIOS DE RENDIMIENTO")
        print(self.promedios.to_string(index=False, float_format=lambda x: f'{x:.2f}'))
        
        if guardar_csv:
            archivo_csv = 'tabla_promedios.csv'
            self.promedios.to_csv(archivo_csv, index=False, encoding='utf-8')
            print(f" Tabla guardada en '{archivo_csv}'")
    
    def graficar_colisiones_vs_carga(self, ax=None):
        """Gráfica de Colisiones vs N (puede recibir un axes externo)"""
        if not GRAFICAS_DISPONIBLES or self.promedios is None:
            print(" Gráficas no disponibles")
            return

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))

        n = self.promedios['N Elementos']
        colisiones = self.promedios['Colisiones']

        ax.plot(n, colisiones, marker='o', linewidth=2, markersize=8,
                color='#e74c3c', label='Colisiones promedio')

        ax.set_xlabel('Número de Elementos (N)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Colisiones', fontsize=12, fontweight='bold')
        ax.set_title('Colisiones vs Carga de Elementos\nTabla Hash con Encadenamiento Separado',fontsize=14, fontweight='bold', pad=20)

        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=10)

        for i, (x, y) in enumerate(zip(n, colisiones)):
            ax.annotate(f'{y:.0f}', (x, y), textcoords="offset points",xytext=(0, 10), ha='center', fontsize=9)

    def graficar_tiempos_operaciones(self, ax=None):
        """Gráfica comparativa de tiempos (puede recibir un axes externo)"""
        if not GRAFICAS_DISPONIBLES or self.promedios is None:
            print(" Gráficas no disponibles")
            return

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))

        n = self.promedios['N Elementos']

        ax.plot(n, self.promedios['Inserción (ms)'],
                marker='o', linewidth=2, markersize=8, label='Inserción')
        ax.plot(n, self.promedios['Búsqueda Exist. (ms)'],
                marker='s', linewidth=2, markersize=8, label='Búsqueda (existentes)')
        ax.plot(n, self.promedios['Búsqueda No Exist. (ms)'],
                marker='^', linewidth=2, markersize=8, label='Búsqueda (no existentes)')
        ax.plot(n, self.promedios['Eliminación (ms)'],
                marker='d', linewidth=2, markersize=8, label='Eliminación')

        ax.set_xlabel('Número de Elementos (N)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Tiempo de Ejecución (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Comparación de Tiempos por Operación',fontsize=14, fontweight='bold', pad=20)

        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=10, loc='upper left')

    def generar_reporte_completo(self):
        """Genera todas las tablas y gráficas en una sola ventana"""
        if not GRAFICAS_DISPONIBLES:
            print("\n matplotlib no disponible. Solo se generará tabla CSV.")
            self.generar_tabla_resumen(guardar_csv=True)
            return

        print("GENERANDO REPORTE COMPLETO")
        
        self.generar_tabla_resumen(guardar_csv=True)

        # Crear figura con subgráficos
        fig, axes = plt.subplots(2, 1, figsize=(12, 12))

        # Graficar en los subgráficos
        self.graficar_colisiones_vs_carga(ax=axes[0])
        self.graficar_tiempos_operaciones(ax=axes[1])

        plt.tight_layout()
        archivo = 'reporte_completo.png'
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        print(f" Gráficas guardadas en '{archivo}'")

        plt.show()

        print(" REPORTE COMPLETO GENERADO")

# MENÚ PRINCIPAL

def menu_principal():
    """Menú interactivo principal"""
    tabla = None
    
    while True:
        print("SISTEMA DE TABLA HASH - INVENTARIO DE PRODUCTOS")
        print("1.  Crear nueva tabla hash")
        print("2.  Insertar producto")
        print("3.  Buscar producto")
        print("4.  Eliminar producto")
        print("5.  Actualizar producto")
        print("6.  Visualizar tabla")
        print("7.  Mostrar estadísticas")
        print("8.  Ejecutar pruebas de rendimiento")
        print("9. Cargar datos de ejemplo")
        print("10. Generar gráficas y tablas")
        print("0.  Salir")

        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            capacidad = int(input("Ingresa la capacidad esperada (default 1000): ") or 1000)
            tabla = TablaHash(capacidad)
            print(f"Tabla hash creada con tamaño {tabla.tamanio}")
        
        elif opcion == "2":
            if tabla is None:
                print("Primero crea una tabla hash (opción 1)")
                continue
            
            id_prod = input("ID del producto: ")
            nombre = input("Nombre: ")
            categoria = input("Categoría: ")
            stock = int(input("Stock: "))
            
            producto = ProductoInventario(id_prod, nombre, categoria, stock)
            if tabla.insertar(producto):
                print("Producto insertado correctamente")
            else:
                print("El ID ya existe")
        
        elif opcion == "3":
            if tabla is None:
                print("Primero crea una tabla hash")
                continue
            
            id_prod = input("ID a buscar: ")
            resultado = tabla.buscar(id_prod)
            
            if resultado:
                print(f"\n Producto encontrado:")
                print(f"  {resultado}")
            else:
                print(" Producto no encontrado")
        
        elif opcion == "4":
            if tabla is None:
                print(" Primero crea una tabla hash")
                continue
            
            id_prod = input("ID a eliminar: ")
            if tabla.eliminar(id_prod):
                print(" Producto eliminado")
            else:
                print(" Producto no encontrado")
        
        elif opcion == "5":
            if tabla is None:
                print(" Primero crea una tabla hash")
                continue
            
            id_prod = input("ID del producto a actualizar: ")
            nombre = input("Nuevo nombre (Enter para no cambiar): ") or None
            categoria = input("Nueva categoría (Enter para no cambiar): ") or None
            stock_str = input("Nuevo stock (Enter para no cambiar): ")
            stock = int(stock_str) if stock_str else None
            
            if tabla.actualizar(id_prod, nombre, categoria, stock):
                print(" Producto actualizado")
            else:
                print(" Producto no encontrado")
        
        elif opcion == "6":
            if tabla is None:
                print(" Primero crea una tabla hash")
                continue
            
            limite = int(input("¿Cuántos buckets mostrar?: ") or 20)
            tabla.visualizar_tabla(limite)
        
        elif opcion == "7":
            if tabla is None:
                print(" Primero crea una tabla hash")
                continue
            
            stats = tabla.estadisticas()
            print("ESTADÍSTICAS DE LA TABLA")
            for clave, valor in stats.items():
                print(f"{clave:30s}: {valor}")
        
        elif opcion == "8":
            print("\nEjecutando pruebas de rendimiento completas...")
            valores_n = [100, 200, 300, 500, 800, 1000]
            todos_resultados = []
            
            for n in valores_n:
                resultados = realizar_pruebas_rendimiento(n, 3)
                todos_resultados.extend(resultados)
            
            guardar_resultados(todos_resultados)
            
            print("\nRESULTADOS DE PRUEBAS DE RENDIMIENTO")
            print(f"{'N':<10}{'Inserción (ms)':<20}{'Búsq. Exist (ms)':<20}{'Búsq. No Exist (ms)':<20}{'Elimin. (ms)':<20}")
            
            for n in valores_n:
                resultados_n = [r for r in todos_resultados if r['n'] == n]
                promedios = calcular_promedios(resultados_n)
                print(f"{promedios['n']:<10}{promedios['tiempo_insercion_promedio']:<20.4f}"
                      f"{promedios['tiempo_busqueda_exist_promedio']:<20.4f}"
                      f"{promedios['tiempo_busqueda_noexist_promedio']:<20.4f}"
                      f"{promedios['tiempo_eliminacion_promedio']:<20.4f}")
        
        elif opcion == "9":
            if tabla is None:
                print(" Primero crea una tabla hash")
                continue
            
            datos_ejemplo = generar_datos_prueba(20)
            for item in datos_ejemplo:
                producto = ProductoInventario(**item)
                tabla.insertar(producto)
            print(" 20 productos de ejemplo cargados")
        
        elif opcion == "10":
            analizador = AnalizadorRendimiento()
            if analizador.datos:
                analizador.generar_reporte_completo()
            else:
                print(" Primero ejecuta las pruebas de rendimiento (opción 9)")
        
        elif opcion == "0":
            print("\n Saliendo del sistema. ¡Hasta luego!")
            break
        
        else:
            print(" Opción inválida")


if __name__ == "__main__":
    print("""
    SISTEMA DE TABLA HASH - GESTIÓN DE INVENTARIO
    Implementación con Encadenamiento Separado
    """)
    menu_principal()