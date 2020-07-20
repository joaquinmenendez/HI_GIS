import requests
import urllib

API_BASE_URL = "https://apis.datos.gob.ar/georef/api/"
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
    #API_BASE_URL = "https://apis.datos.gob.ar/georef/api/"
    kwargs["nombre"] = nombre
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


def post_centroides(endpoint, prov_loc, prov = True):
    """
    Realiza un POST para una lista de provincias y localidades. La funcion retorna una lista con la localidad mas probable para esa combinacion.
    En caso de que no se desee proveer las provincias la API inferira la localidad solo con el nombre.
    :param endpoint: str
    :param prov_loc: list[(str,str)] o list[str]
    'param prov: boolean default True
    :returns: list[dict]
    """
    #API_BASE_URL = "https://apis.datos.gob.ar/georef/api/"
    if prov:
        data = {
                endpoint: [ {"nombre": loc, "max": 1, 'provincia' : prov} for prov,loc in prov_loc]
                }
    else:
        data = {
                endpoint: [ {"nombre": loc, "max": 1} for prov,loc in prov_loc]
                }
    url = API_BASE_URL + endpoint
    results = requests.post(url, json = data, headers={"Content-Type": "application/json"}).json()

    # convierte a una lista de "resultado más probable" o "vacío" cuando no hay
    parsed_results = [
        single_result[endpoint][0] if single_result[endpoint] else {}
        for single_result in results["resultados"]
    ]

    return parsed_results