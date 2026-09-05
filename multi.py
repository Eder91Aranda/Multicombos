# -*- coding: utf-8 -*-

"""
MULTI COMBOS
Herramienta local para generar y organizar combinaciones de texto.

No realiza conexiones de red ni comprobaciones de credenciales.
Todas las operaciones se realizan localmente sobre archivos proporcionados
por el usuario.
"""

import os
import secrets
import string
import time
from typing import List, Tuple


# ============================================================
# COLORES ANSI
# ============================================================

RESET = "\033[0m"
BLANCO = "\033[97m"
AZUL = "\033[94m"
VERDE = "\033[92m"
NARANJA = "\033[93m"
ROJO = "\033[91m"
GRIS = "\033[90m"


# ============================================================
# CONFIGURACIÓN
# ============================================================

LONGITUD_PREDETERMINADA = 8
FORMATO_PREDETERMINADO = 1

CARACTERES_PASSWORD = (
    string.ascii_letters
    + string.digits
    + string.punctuation
)


# ============================================================
# DIRECTORIOS
# ============================================================

def determinar_directorio_base() -> str:
    """
    Determina dónde guardar los resultados.
    """
    android_base = os.path.join(
        os.sep,
        "storage",
        "emulated",
        "0",
        "MultiCombos"
    )

    try:
        if os.path.isdir(android_base):
            if os.access(android_base, os.W_OK):
                return android_base

        almacenamiento = os.path.dirname(android_base)

        if os.path.isdir(almacenamiento):
            if os.access(almacenamiento, os.W_OK):
                os.makedirs(android_base, exist_ok=True)
                return android_base

    except OSError:
        pass

    return os.path.abspath(
        os.path.join(".", "MultiCombos")
    )


BASE_DIR = determinar_directorio_base()

CARPETA_COMBOS = os.path.join(
    BASE_DIR,
    "Combos"
)

CARPETA_LIMPIOS = os.path.join(
    BASE_DIR,
    "SinDuplicados"
)


def preparar_directorios() -> bool:
    """
    Crea las carpetas necesarias.
    """
    try:
        os.makedirs(
            CARPETA_COMBOS,
            exist_ok=True
        )

        os.makedirs(
            CARPETA_LIMPIOS,
            exist_ok=True
        )

        return True

    except PermissionError:
        print(f"{ROJO}✗ No hay permisos para crear las carpetas.{RESET}")

    except OSError as error:
        print(f"{ROJO}✗ No se pudieron crear las carpetas: {error}{RESET}")

    return False


# ============================================================
# LIMPIAR PANTALLA Y BANNER
# ============================================================

def limpiar_pantalla() -> None:
    comando = "cls" if os.name == "nt" else "clear"
    try:
        os.system(comando)
    except OSError:
        print("\n" * 4)


def mostrar_banner() -> None:
    print(f"{AZUL}╭──────────────────────────────────────────────────╮{RESET}")
    print(f"{AZUL}│{BLANCO}                 MULTI COMBOS                   {AZUL}│{RESET}")
    print(f"{AZUL}│{VERDE}          Gestión de listas y combos            {AZUL}│{RESET}")
    print(f"{AZUL}╰──────────────────────────────────────────────────╯{RESET}")
    print(f"{GRIS}  Operaciones locales • Python 3 • Android{RESET}\n")


# ============================================================
# CARGAR ARCHIVO
# ============================================================

def cargar_archivo(ruta: str) -> Tuple[List[str], int]:
    if not ruta:
        print(f"{ROJO}✗ No se indicó ninguna ruta.{RESET}")
        return [], 0

    if not os.path.isfile(ruta):
        print(f"{ROJO}✗ El archivo no existe o la ruta no es válida.{RESET}")
        return [], 0

    lineas = None

    try:
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
        except UnicodeDecodeError:
            print(f"{NARANJA}⚠ UTF-8 no disponible. Intentando Latin-1...{RESET}")
            with open(ruta, "r", encoding="latin-1") as archivo:
                lineas = archivo.readlines()
    except PermissionError:
        print(f"{ROJO}✗ No tienes permisos para leer este archivo.{RESET}")
        return [], 0
    except OSError as error:
        print(f"{ROJO}✗ No se pudo leer el archivo: {error}{RESET}")
        return [], 0

    lineas_limpias = [l.strip() for l in lineas if l.strip()]
    unicos = list(dict.fromkeys(lineas_limpias))

    print(f"{VERDE}✓ Líneas encontradas: {len(lineas_limpias)}{RESET}")
    print(f"{VERDE}✓ Elementos únicos:   {len(unicos)}{RESET}")

    if not unicos:
        print(f"{NARANJA}⚠ El archivo está vacío o no contiene datos útiles.{RESET}")

    return unicos, len(lineas_limpias)


# ============================================================
# GENERAR CONTRASEÑA Y PROGRESO
# ============================================================

def generar_contrasena(longitud: int) -> str:
    if longitud <= 0:
        raise ValueError("La longitud debe ser positiva.")
    return "".join(secrets.choice(CARACTERES_PASSWORD) for _ in range(longitud))


def mostrar_progreso(actual: int, total: int, ancho: int = 32) -> None:
    porcentaje = 1.0 if total <= 0 else max(0.0, min(1.0, actual / total))
    llenos = int(ancho * porcentaje)
    barra = "■" * llenos + "·" * (ancho - llenos)
    porcentaje_entero = int(porcentaje * 100)

    print(
        f"\r{AZUL}[{barra}]{RESET} "
        f"{VERDE}{porcentaje_entero:3d}%{RESET} "
        f"{GRIS}{actual}/{total}{RESET}",
        end="",
        flush=True
    )


# ============================================================
# NOMBRE Y CÁLCULO DE FORMATOS
# ============================================================

def nombre_formato(formato: int) -> str:
    formatos = {
        1: "nombre:contraseña (Aleatoria)",
        2: "contraseña:nombre (Aleatoria)",
        3: "nombre_nombre:contraseña (Aleatoria)",
        4: "Patrón Años Ampliado (2010-2030, Años Cortos, Mayús/Min)",
        5: "Patrón Numérico Ampliado (Secuencias, Mayús/Min)",
        6: "Patrón Símbolos Ampliado (@, #, $, *, Mayús/Min)",
        7: "Asignaciones Fijas Ampliado (2010-2030 + Formatos 2 dígitos)",
        8: "PLANTILLA ULTRA COMPLETA (Cientos de variaciones por nombre)",
    }
    return formatos.get(formato, "nombre:contraseña (Aleatoria)")


def obtener_variaciones_nombre(nombre: str) -> List[str]:
    """Genera variaciones de capitalización para un nombre."""
    variantes = [
        nombre,                     # Juan
        nombre.lower(),             # juan
        nombre.upper(),             # JUAN
        nombre.capitalize(),        # Juan
    ]
    return list(dict.fromkeys(variantes))


def aplicar_formato(nombre: str, contrasena: str, formato: int) -> List[str]:
    """Genera múltiples variaciones por nombre según el formato seleccionado."""
    
    variantes_nombre = obtener_variaciones_nombre(nombre)
    res = []

    if formato == 1:
        for v in variantes_nombre:
            res.append(f"{v}:{contrasena}")
        return res

    if formato == 2:
        for v in variantes_nombre:
            res.append(f"{contrasena}:{v}")
        return res

    if formato == 3:
        for v in variantes_nombre:
            res.append(f"{v}_{v}:{contrasena}")
        return res

    if formato == 4:
        anos_completos = [str(a) for a in range(2010, 2031)]  # 2010 a 2030
        anos_cortos = [f"{a:02d}" for a in range(10, 31)]       # 10 a 30

        for v in variantes_nombre:
            for ano in anos_completos:
                res.append(f"{v}:{v}{ano}")
                res.append(f"{v}:{ano}{v}")
                res.append(f"{v}{ano}:{v}")
                res.append(f"{ano}{v}:{v}")

            for ac in anos_cortos:
                res.append(f"{v}:{v}{ac}")
                res.append(f"{v}:{ac}{v}")
                res.append(f"{v}{ac}:{v}")

        return list(dict.fromkeys(res))

    if formato == 5:
        secuencias = ["123", "1234", "12345", "123456", "000", "111", "777", "999", "2025", "2026"]
        for v in variantes_nombre:
            for sec in secuencias:
                res.append(f"{v}:{v}{sec}")
                res.append(f"{v}:{sec}{v}")
                res.append(f"{v}{sec}:{v}")
                res.append(f"{sec}{v}:{v}")
        return list(dict.fromkeys(res))

    if formato == 6:
        simbolos = ["@", "#", "$", "%", "*", "&", "_", "-", "."]
        numeros = ["123", "1234", "2025", "2026"]
        for v in variantes_nombre:
            for s in simbolos:
                for n in numeros:
                    res.append(f"{v}:{s}{v}{n}")
                    res.append(f"{v}:{v}{s}{n}")
                    res.append(f"{v}:{v}{n}{s}")
                    res.append(f"{s}{v}:{n}")
        return list(dict.fromkeys(res))

    if formato == 7:
        anos = [str(a) for a in range(2010, 2031)] + [f"{a:02d}" for a in range(10, 31)]
        for v in variantes_nombre:
            for ano in anos:
                res.append(f"{v}:{ano}")
                res.append(f"{v}:{v}_{ano}")
        return list(dict.fromkeys(res))

    if formato == 8:
        f4 = aplicar_formato(nombre, contrasena, 4)
        f5 = aplicar_formato(nombre, contrasena, 5)
        f6 = aplicar_formato(nombre, contrasena, 6)
        f7 = aplicar_formato(nombre, contrasena, 7)
        return list(dict.fromkeys(f4 + f5 + f6 + f7))

    return [f"{nombre}:{contrasena}"]


def estimar_maximo_combinaciones(nombres: List[str], formato: int) -> int:
    if not nombres:
        return 0
    muestra = aplicar_formato(nombres[0], "pass1234", formato)
    return len(nombres) * len(muestra)


# ============================================================
# CONFIGURAR FORMATO
# ============================================================

def configurar_formato(formato_actual: int) -> int:
    print()
    print(f"{AZUL}Selecciona el patrón de combinación:{RESET}")
    print(f"{BLANCO}[1]{RESET} nombre:contraseña (Generación aleatoria)")
    print(f"{BLANCO}[2]{RESET} contraseña:nombre (Generación aleatoria)")
    print(f"{BLANCO}[3]{RESET} nombre_nombre:contraseña (Generación aleatoria)")
    print(f"{GRIS}──────────────────────────────────────────────────{RESET}")
    print(f"{BLANCO}[4]{RESET} Patrón Años Ampliado (2010-2030, Años Cortos '26, Mayús/Min)")
    print(f"{BLANCO}[5]{RESET} Patrón Numérico Ampliado (Secuencias 123, 12345, Mayús/Min)")
    print(f"{BLANCO}[6]{RESET} Patrón Símbolos Ampliado (@, #, $, *, Mayús/Min)")
    print(f"{BLANCO}[7]{RESET} Asignaciones Fijas (2010-2030 + Años cortos)")
    print(f"{VERDE}[8] ULTRA PLANTILLA (Millones de variaciones combinando todo){RESET}")

    opcion = input(f"\n{NARANJA}Opción: {RESET}").strip()

    try:
        nuevo = int(opcion)
        if 1 <= nuevo <= 8:
            print(f"{VERDE}✓ Formato establecido: {nombre_formato(nuevo)}{RESET}")
            return nuevo
    except ValueError:
        pass

    print(f"{ROJO}✗ Opción inválida. Se conserva el formato anterior.{RESET}")
    return formato_actual


# ============================================================
# CREAR COMBOS EN DISTRIBUCIÓN EQUITATIVA (RONDAS)
# ============================================================

def crear_combos(
    nombres: List[str],
    longitud_pass: int,
    formato: int,
    limite_combinaciones: int
) -> List[str]:
    """
    Genera combinaciones entrelazadas por RONDAS.
    Garantiza que se incluyan TODOS los nombres de la lista (de la A a la Z).
    """
    total_nombres = len(nombres)

    if total_nombres == 0 or limite_combinaciones <= 0:
        return []

    print()
    print(f"{AZUL}Preparando matriz de variantes para {total_nombres:,} nombres...{RESET}")

    # Generamos la lista de variaciones para cada nombre de la lista base
    matriz_variaciones = []
    for nombre in nombres:
        contrasena = generar_contrasena(longitud_pass)
        matriz_variaciones.append(aplicar_formato(nombre, contrasena, formato))

    combos = []
    max_variaciones = max(len(v) for v in matriz_variaciones) if matriz_variaciones else 0

    print(f"{AZUL}Generando {limite_combinaciones:,} combinaciones de forma equitativa...{RESET}")

    # Iteramos ronda por ronda a través de TODOS los nombres
    for r in range(max_variaciones):
        for i, variaciones in enumerate(matriz_variaciones):
            if r < len(variaciones):
                combos.append(variaciones[r])
                
                # Actualizamos la barra de progreso
                if len(combos) % 500 == 0 or len(combos) == limite_combinaciones:
                    mostrar_progreso(len(combos), limite_combinaciones)

                if len(combos) == limite_combinaciones:
                    print()
                    return combos

    print()
    return combos


# ============================================================
# GUARDAR COMBOS
# ============================================================

def guardar_combos(combos: List[str], ruta: str, nombre_archivo: str) -> bool:
    if not combos:
        print(f"{NARANJA}⚠ No hay combinaciones para guardar.{RESET}")
        return False

    nombre_archivo = nombre_archivo.strip()
    if not nombre_archivo:
        print(f"{ROJO}✗ El nombre del archivo no puede estar vacío.{RESET}")
        return False

    if not nombre_archivo.lower().endswith(".txt"):
        nombre_archivo += ".txt"

    try:
        os.makedirs(ruta, exist_ok=True)
        ruta_completa = os.path.join(ruta, nombre_archivo)

        with open(ruta_completa, "w", encoding="utf-8") as archivo:
            archivo.write("\n".join(combos))
            archivo.write("\n")

        print()
        print(f"{VERDE}✓ ARCHIVO GUARDADO CORRECTAMENTE{RESET}")
        print(f"{BLANCO}Ruta: {ruta_completa}{RESET}")
        return True

    except PermissionError:
        print(f"{ROJO}✗ No tienes permisos para guardar en esa carpeta.{RESET}")
    except OSError as error:
        print(f"{ROJO}✗ No se pudo guardar el archivo: {error}{RESET}")

    return False


# ============================================================
# ELIMINAR DUPLICADOS
# ============================================================

def eliminar_duplicados() -> None:
    print()
    print(f"{AZUL}┌─ LIMPIEZA DE ARCHIVO ──────────────────────────┐{RESET}")
    ruta_entrada = input(f"{NARANJA}Ruta del archivo: {RESET}").strip()

    if not ruta_entrada or not os.path.isfile(ruta_entrada):
        print(f"{ROJO}✗ Archivo no válido o inexistente.{RESET}")
        return

    try:
        try:
            with open(ruta_entrada, "r", encoding="utf-8") as archivo:
                contenido = archivo.readlines()
        except UnicodeDecodeError:
            with open(ruta_entrada, "r", encoding="latin-1") as archivo:
                contenido = archivo.readlines()
    except Exception as error:
        print(f"{ROJO}✗ Error al leer archivo: {error}{RESET}")
        return

    lineas = [l.strip() for l in contenido if l.strip()]
    unicas = list(dict.fromkeys(lineas))
    eliminados = len(lineas) - len(unicas)

    try:
        os.makedirs(CARPETA_LIMPIOS, exist_ok=True)
        nombre_base = os.path.basename(ruta_entrada)
        salida = os.path.join(CARPETA_LIMPIOS, "LIMPIO_" + nombre_base)

        with open(salida, "w", encoding="utf-8") as archivo:
            if unicas:
                archivo.write("\n".join(unicas) + "\n")

    except Exception as error:
        print(f"{ROJO}✗ Error al guardar: {error}{RESET}")
        return

    print(f"\n{VERDE}✓ Proceso terminado.{RESET}")
    print(f"  Líneas originales:     {len(lineas):,}")
    print(f"  Líneas únicas:         {len(unicas):,}")
    print(f"  Duplicados eliminados: {eliminados:,}")
    print(f"  Archivo guardado en:   {salida}")


# ============================================================
# CONFIGURACIONES Y MENÚS
# ============================================================

def pedir_longitud(longitud_actual: int) -> int:
    valor = input(f"{NARANJA}Nueva longitud (actual: {longitud_actual}): {RESET}").strip()
    if not valor:
        return longitud_actual
    try:
        nueva = int(valor)
        if nueva > 0:
            return nueva
    except ValueError:
        pass
    print(f"{ROJO}✗ Introduce un número entero positivo.{RESET}")
    return longitud_actual


def esperar_enter() -> None:
    try:
        input(f"\n{GRIS}Presiona Enter para continuar...{RESET}")
    except (EOFError, KeyboardInterrupt):
        print()


def mostrar_menu(longitud: int, formato: int) -> None:
    print(f"{AZUL}╭──────────────────────────────────────────────────╮{RESET}")
    print(f"{BLANCO}│                 MENÚ PRINCIPAL                   │{RESET}")
    print(f"{AZUL}├──────────────────────────────────────────────────┤{RESET}")
    print(f"{VERDE}│ [1] Crear combos desde una lista                 │{RESET}")
    print(f"{BLANCO}│ [2] Eliminar duplicados de un archivo             │{RESET}")
    print(f"{NARANJA}│ [3] Configurar longitud de contraseña             │{RESET}")
    print(f"{AZUL}│ [4] Cambiar formato de combinación                │{RESET}")
    print(f"{ROJO}│ [0] Salir de Multi Combos                         │{RESET}")
    print(f"{AZUL}├──────────────────────────────────────────────────┤{RESET}")
    print(f"{GRIS}│ Longitud: {longitud:<4} Formato: {nombre_formato(formato):<25}│{RESET}")
    print(f"{AZUL}╰──────────────────────────────────────────────────╯{RESET}")


# ============================================================
# EJECUTAR CREACIÓN
# ============================================================

def ejecutar_creacion(longitud: int, formato: int) -> None:
    print()
    print(f"{AZUL}┌─ CREAR COMBOS ─────────────────────────────────┐{RESET}")
    ruta = input(f"{NARANJA}Ruta del archivo de entrada: {RESET}").strip()

    elementos, _ = cargar_archivo(ruta)
    if not elementos:
        return

    formato_elegido = configurar_formato(formato)

    longitud_elegida = longitud
    if formato_elegido in (1, 2, 3):
        print()
        longitud_elegida = pedir_longitud(longitud)

    max_posibles = estimar_maximo_combinaciones(elementos, formato_elegido)

    print()
    print(f"{BLANCO}Nombres cargados: {len(elementos):,}{RESET}")
    print(f"{BLANCO}Máximo de combinaciones únicas posibles a generar: {max_posibles:,}{RESET}")

    limite = max_posibles
    limite_str = input(
        f"\n{NARANJA}"
        f"¿Cuántas combinaciones posibles deseas generar? [Enter para máximo {max_posibles:,}]: "
        f"{RESET}"
    ).strip()

    if limite_str:
        try:
            limite = int(limite_str)
            if limite <= 0:
                print(f"{ROJO}✗ La cantidad debe ser mayor a 0.{RESET}")
                return
            if limite > max_posibles:
                print(f"{NARANJA}⚠ Solicitaste {limite:,}, pero el máximo con esta configuración es {max_posibles:,}.{RESET}")
                limite = max_posibles
        except ValueError:
            print(f"{NARANJA}⚠ Entrada no válida. Se generará el máximo disponible ({max_posibles:,}).{RESET}")
            limite = max_posibles

    print()
    print(f"{BLANCO}Resumen de trabajo:{RESET}")
    print(f"  Nombres disponibles:       {len(elementos):,}")
    print(f"  Formato / Patrón:          {nombre_formato(formato_elegido)}")
    print(f"  Combinaciones solicitadas: {limite:,}")

    combos = crear_combos(
        elementos,
        longitud_elegida,
        formato_elegido,
        limite
    )

    nombre = input(f"\n{NARANJA}Nombre para guardar el archivo (ej. resultado.txt): {RESET}").strip()
    guardar_combos(combos, CARPETA_COMBOS, nombre)


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

def main() -> None:
    preparar_directorios()
    longitud = LONGITUD_PREDETERMINADA
    formato = FORMATO_PREDETERMINADO

    while True:
        limpiar_pantalla()
        mostrar_banner()
        mostrar_menu(longitud, formato)

        opcion = input(f"\n{NARANJA}Selecciona una opción: {RESET}").strip()

        if opcion == "1":
            ejecutar_creacion(longitud, formato)
            esperar_enter()
        elif opcion == "2":
            eliminar_duplicados()
            esperar_enter()
        elif opcion == "3":
            longitud = pedir_longitud(longitud)
            esperar_enter()
        elif opcion == "4":
            formato = configurar_formato(formato)
            esperar_enter()
        elif opcion == "0":
            print(f"\n{VERDE}¡Hasta luego!{RESET}\n")
            break
        else:
            print(f"\n{ROJO}✗ Opción no válida.{RESET}")
            esperar_enter()


if __name__ == "__main__":
    main()