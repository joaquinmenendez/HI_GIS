# Ubicacion y Geolocalizacion de usuarios
## Basados en codigo postal argentino y localidad reportada

El proyecto cuenta con dos notebooks, uno exploratorio (`Explorando_GeoRefAR`) y uno mostrando los pasos utilizados para asignar geolocalizacion en una base compuesta por `loc_part` y 'cp_part`. (`Geocodificando_usuarios`)

Para realizar esto creamos una base de datos (SQLite3) con todos los codigos postales utilizando diferentes fuentes. El Codigo Postal Argentino (CPA) que usamos aqui es el de 4 digitos, no el nuevo el cual contiene 4 letras ([referencia]( https://en.wikipedia.org/wiki/Postal_codes_in_Argentina)).
En est repositorio pueden encontrarse los codigos utilizados para crear esta base de datos. Tambien puede accederse a la infroamcion en formato pickle (binary).  Luego utilizamos la api de [GeoRefAR](https://datosgobar.github.io/georef-ar-api/) para asignar las georeferencias para los distintas lcoalidades, departamentos y provinicias. 

En order para recrear la tabla:

En nuestro caso usamos SQLite3, pero usted puede usar la base de datos que prefiera (debera realizar modificaciones minimas al codigo).

- Instalar slite3 en la computadora local

```bash
cd ./SQL
cat create_tables_provincia_localidad.sql | sqlite3 CPA.db
cat add_data_to_CPA.sql | sqlite3 CPA.db
cat add_capital_to_CPA.sql | sqlite3 CPA.db

```

Ante cualquier consulta o errores en la informacion por favor crear a 'new issue' o enviar un mail a joaquin14@gmail.com
