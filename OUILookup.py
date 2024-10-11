#Joaquin Astudillo
#Bruno Osega

import requests
import sys
import getopt
import subprocess
import time


def help():
    return """
Uso: python OUILookup.py --mac <mac> | --arp | [--help]
--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
--arp: muestra los fabricantes de los hosts disponibles en la tabla ARP.
--help: muestra este mensaje y termina.
    """

# Funcion para consultar la direcion mac
def mac(mac_obtenido):

    def solicitud():
        url = f"https://api.maclookup.app/v2/macs/{mac_obtenido}"  # URL de la API con la MAC como parametro
        tiempo = time.time()  # Registrar el tiempo antes de la solicitud
        repuesta = requests.get(url)  # Realizar la solicitud HTTP
        tiempo_ms = (time.time() - tiempo) * 1000  # Calcular el tiempo de respuesta en ms
        return repuesta, tiempo_ms

    try:
        # Realizar la consulta a la API
        repuesta, tiempo_ms = solicitud()

        # Verificar si la solicitud fue exitosa
        if repuesta.status_code == 200:
            data = repuesta.json()  # Obtener la respuesta
            if 'company' in data:
                # Mostrar  resultado de la consulta
                resultado = (f"MAC address : {mac_obtenido}\n"
                             f"Fabricante  : {data['company']}\n"
                             f"Tiempo de respuesta: {tiempo_ms:.0f}ms")
            else:
                # Si la MAC no esta en la base de datos
                resultado = (f"Fabricante para {mac_obtenido}: No encontrado\n"
                             f"Tiempo de respuesta: {tiempo_ms:.0f}ms")
        else:
            # Si la API devolvio un error, mostrar el codigo de estado
            resultado = f"Error en la solicitud HTTP. Codigo de estado: {repuesta.status_code}"
        return resultado
    
    except requests.exceptions.RequestException as e:
        # Manejar cualquier error relacionado con la red o la API
        return f"Error al consultar la MAC {mac_obtenido}: {e}"

# Funcion para consultar la tabla ARP y mostrar los fabricantes de las MACs
def arp():
    # Funcion interna para ejecutar el comando "arp -a" en Windows y obtener la salida
    def comando_arp():
        return subprocess.check_output("arp -a", shell=True).decode('cp1252').splitlines()

    # Funcion para extraer la MAC y consultar su fabricante
    def obtener_mac(linea):
        parts = linea.split()  # Dividir la linea en partes
        ip_address = parts[0]  # Primera parte: direccion IP
        mac_obtenido = parts[1].replace('-', ':')  # Segunda parte: direccion MAC, convertida a formato con ":"
        return f"Consultando fabricante para IP: {ip_address}, MAC: {mac_obtenido}\n{mac(mac_obtenido)}\n---"
    
    try:
        # Obtener la salida del comando "arp -a"
        lines = comando_arp()
        # Procesar cada linea y consultar los fabricantes de las MACs encontradas
        return '\n'.join([obtener_mac(line) for line in lines if '-' in line or ':' in line])
    
    except subprocess.CalledProcessError as e:
        # Manejar errores si el comando "arp -a" falla
        return f"Error al ejecutar el comando ARP: {e}"

# Funcion principal para procesar los argumentos de la linea de comandos usando getopt
def main(argv):
    try:
        # Definir los parametros esperados: "help", "mac=<mac>", "arp"
        opts, args = getopt.getopt(argv, "h", ["help", "mac=", "arp"])
    except getopt.GetoptError:
        # Si los argumentos no son validos, mostrar la ayuda
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # Mostrar la ayuda si se pasa el parametro "--help"
            print(help())
            sys.exit()
        elif opt == "--mac":
            # Si se pasa el parametro "--mac", consultar la MAC proporcionada
            print(mac(arg))
            sys.exit()
        elif opt == "--arp":
            # Si se pasa el parametro "--arp", consultar la tabla ARP
            print(arp())
            sys.exit()

    # Si no se pasa ningun parametro valido, mostrar la ayuda
    print(help())

# Ejecutar la funcion principal si el script es llamado directamente
if __name__ == "__main__":
    main(sys.argv[1:])
