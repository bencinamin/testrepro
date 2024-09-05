import requests
import pandas as pd
import numpy as np
import datetime

# Configuración para mostrar todas las columnas de un DataFrame
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# Definición de funciones auxiliares para extraer información usando la API de SpaceX

# Función para obtener el nombre del booster (cohete)
def getBoosterVersion(data):
    for x in data['rocket']:
        if x:
            response = requests.get("https://api.spacexdata.com/v4/rockets/" + str(x)).json()
            BoosterVersion.append(response['name'])

# Función para obtener el nombre del sitio de lanzamiento y su ubicación (longitud, latitud)
def getLaunchSite(data):
    for x in data['launchpad']:
        if x:
            response = requests.get("https://api.spacexdata.com/v4/launchpads/" + str(x)).json()
            Longitude.append(response['longitude'])
            Latitude.append(response['latitude'])
            LaunchSite.append(response['name'])

# Función para obtener la masa y la órbita de la carga útil
def getPayloadData(data):
    for load in data['payloads']:
        if load:
            response = requests.get("https://api.spacexdata.com/v4/payloads/" + load).json()
            PayloadMass.append(response['mass_kg'])
            Orbit.append(response['orbit'])

# Función para obtener datos sobre el núcleo (core) del cohete
def getCoreData(data):
    for core in data['cores']:
        if core['core'] is not None:
            response = requests.get("https://api.spacexdata.com/v4/cores/" + core['core']).json()
            Block.append(response['block'])
            ReusedCount.append(response['reuse_count'])
            Serial.append(response['serial'])
        else:
            Block.append(None)
            ReusedCount.append(None)
            Serial.append(None)
        Outcome.append(str(core['landing_success']) + ' ' + str(core['landing_type']))
        Flights.append(core['flight'])
        GridFins.append(core['gridfins'])
        Reused.append(core['reused'])
        Legs.append(core['legs'])
        LandingPad.append(core['landpad'])

# Solicitar los datos de lanzamiento de SpaceX
spacex_url = "https://api.spacexdata.com/v4/launches/past"
response = requests.get(spacex_url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    print("Conexión exitosa a la API de SpaceX")
else:
    print("Error al conectar con la API de SpaceX")

# Convertir los datos a un DataFrame de Pandas
data = pd.json_normalize(response.json())

# Filtrar el conjunto de datos
data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
data = data[data['cores'].map(len) == 1]
data = data[data['payloads'].map(len) == 1]
data['cores'] = data['cores'].map(lambda x: x[0])
data['payloads'] = data['payloads'].map(lambda x: x[0])
data['date'] = pd.to_datetime(data['date_utc']).dt.date
data = data[data['date'] <= datetime.date(2020, 11, 13)]

# Variables globales para almacenar los datos extraídos
BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []

# Llamar a las funciones de extracción de datos
getBoosterVersion(data)
getLaunchSite(data)
getPayloadData(data)
getCoreData(data)

# Crear un diccionario con los datos obtenidos
launch_dict = {
    'FlightNumber': list(data['flight_number']),
    'Date': list(data['date']),
    'BoosterVersion': BoosterVersion,
    'PayloadMass': PayloadMass,
    'Orbit': Orbit,
    'LaunchSite': LaunchSite,
    'Outcome': Outcome,
    'Flights': Flights,
    'GridFins': GridFins,
    'Reused': Reused,
    'Legs': Legs,
    'LandingPad': LandingPad,
    'Block': Block,
    'ReusedCount': ReusedCount,
    'Serial': Serial,
    'Longitude': Longitude,
    'Latitude': Latitude
}

# Crear un DataFrame de Pandas a partir del diccionario
df = pd.DataFrame(launch_dict)

# Filtrar solo los lanzamientos de Falcon 9
data_falcon9 = df[df['BoosterVersion'] != 'Falcon 1'].reset_index(drop=True)

# Actualizar la columna FlightNumber
data_falcon9.loc[:, 'FlightNumber'] = list(range(1, data_falcon9.shape[0] + 1))

# Manejar los valores faltantes
mean_payload_mass = data_falcon9['PayloadMass'].mean()
data_falcon9['PayloadMass'].replace(np.nan, mean_payload_mass, inplace=True)

# Exportar el DataFrame a un archivo CSV
data_falcon9.to_csv('dataset_part_1.csv', index=False)

print("Proceso completado y archivo CSV generado.")
