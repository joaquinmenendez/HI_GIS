import requests
import urllib
from functools import reduce  
import operator
import pandas as pd
import numpy as np
import geopandas
import geopy.distance as dist


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


def getFromDict(dataDict, *args):
    '''
    Esta funcion toma un diccionario y busca la key correspondiente a una concatenacion de keys
    ex: dict[key 1][key 2]...[key n]
    '''
    if len(dataDict) == 0:
        return 'NO HUBO REQUEST'
    else:
        mapList = args
        return reduce(operator.getitem, mapList, dataDict)
	
	
def getDistances(row, df_distancias, nivel = 'localidad'):
    '''
    Para cada row de un dataset (o una una Serie) devuelve una lista de tuplas con las distancias a diferentes sedes.
    :param row: pandas.Series
    :param df_distancias: pandas.DataFrame
    :param nivel: str (localidad, municipio, departamento, provincia)
    :return: numpy.Matrix
    '''
    niveles = {'municipio' : ('centroide_lat_municipio', 'centroide_lon_municipio'),
               'localidad' : ('centroide_lat_localidad', 'centroide_lon_localidad'),
               'provincia' : ('centroide_lat_provincia', 'centroide_lon_provincia'),
               'departamento': ('centroide_lat_departamento', 'centroide_lon_departamento')
              }
    dist_to_sede = []
    lat, lon = niveles[nivel] #  assign lat lon 
    lat_user, lon_user = row[lat], row[lon]
    if (not isinstance(row[lat], float)) or (pd.isna(row[lat])):
        return None # Si no hay coordenadas para poder calcular distancia devolve None
    #Si hay coordenadas calcula las distancias
    dist_to_sede = df_distancias.apply(lambda x: round(dist.distance(
																				(lon_user,lat_user),
																				(x.longitud, x.latitud)).km,
																			    3),
                                       axis = 1)
	
    #Realiza arrreglos a la matrix
    matrix = np.array([dist_to_sede,df_distancias.tipo, df_distancias.sede]).T
    return matrix 


def minPorTipo(matrix, tipo = None):
    '''
    Toma una matrix de numpy con la distancia de un sujeto a N sedes y devuelve el tipo de sede mas cercano
    :param matrix: numpy.Matrix
    :param tipo: list[str]
    :return: numpy.array
    '''
    if tipo:
        sedes_dist = []
        for t in tipo:
            val = matrix[matrix[:,1] == t] #sort by tipo
            idx = (val[:,0]).argsort()[:1] # N index sorted by minimum distance value
            sedes_dist.append(val[idx][0])
        return sedes_dist
    else:
        idx = (matrix[:,0]).argsort()[:1]
        return matrix[idx]
    
	
def getMinPorTipo(row, df_distancias, nivel = 'localidad', tipo = None):
    '''
    Toma una row de un dataset y devuelve las sedes de X tipo mas cercano a la ubicacion de esa row
    :param row: pandas.Series
    :param df_distancias: pandas.DataFrame. Dataframe con informacion de las diferentes sedes del HI
    :param nivel: str (localidad, municipio, departamento, provincia)
    :param tipo: list[str]. Posibles valores = ['CENTRO PERIFERICO', 'HOSPITAL']
    '''
    m = getDistances(row, df_distancias, nivel = nivel)
    if m is None:
        return None
    return minPorTipo(m, tipo = tipo)