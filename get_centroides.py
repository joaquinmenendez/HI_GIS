import requests
import urllib

def get_centroides(endpoint, nombre, **kwargs):
    '''
    La funcion toma un endpoint y un nombre y realiza una request a la API del gobierno argentino
    (https://apis.datos.gob.ar/georef/api/). Devuele un diccionario con los centroides para dicho endpoint
    :param endpoint: str - ['provincias','departamentos','municipios','localidades']
    :param nombre: str
    :param kwargs: var = value (consultar los distinto campos en GeoRefAR)
        ex: max = 1 (devuelve 1 solo valor,  el mas probable)
            provincia = 'BA' o 'Buenos Aires' (filtra los valores por provincia)
    :return: list - Lista de diccionarios (json) con diferentes campos devueltos
                    dependiendo del endpoint seleccionado ('centroide','id', 'nombre')
    '''
    API_BASE_URL = "https://apis.datos.gob.ar/georef/api/"
    url = f"{API_BASE_URL}{endpoint}?{urllib.parse.urlencode(kwargs)}"
    return requests.get(url).json()[endpoint]


def filter_loc(list_localidades, provincia):
    '''
    Filtra localidad por provincia. Asume que localidad es un valor unico y no se repite por provincia
    :param list_localidades: list
    :param provincia: str
    :return: list[dict]
    '''
    prov_loc = []
    for item in list_localidades:
        if item['provincia']['nombre'] == provincia:
            prov_loc.append(item)
    return prov_loc


def get_localidad(provincia,localidad):
    '''
    Funcion para obtener una unica localidad usando la provincia y la localidad reportada.
    Asume que localidad es un valor unico por provincia.
    Se puede optar por filtrar esta informacion usando el criterio max = 1 en get_centroides
    :param provincia: str
    :param localidad: str
    :return: list[dict]
    '''
    list_localidades = get_centroides('localidades', localidad)
    return filter_loc(list_localidades, provincia)