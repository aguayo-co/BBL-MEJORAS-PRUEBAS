# Biblored - Bibloteca Digital de Bogota

Aplicación web para Biblored.

## Requerimientos:

- [Docker](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Antes de empezar

- Usar [GitFlow](https://datasift.github.io/gitflow/IntroducingGitFlow.html)
- Hacer pruebas sobre la rama **develop**
- Los ejemplos asumen que usted se encuentra en la carpeta del proyecto

## Configuración

En la consola ejecutar los siguientes comandos:

```shell
# Generar los archivos de configuración En git Bash
$ docker run -ti --rm -v "c:/ruta/a/carpeta/del/proyecto":"/var/lib/dotenver/" jmfederico/dotenver

# Generar los archivos de configuración En Windows cmd
$ docker run -ti --rm -v "c:\ruta\a\carpeta\del\proyecto":"/var/lib/dotenver/" jmfederico/dotenver

# Generar los archivos de configuración En Mac, Linux o WSL
$ docker run -ti --rm -v "${PWD}:/var/lib/dotenver/" jmfederico/dotenver

# Levantar Docker
$ docker-compose build
# Si usted es usuario de MacOs omita el siguiente comando
$ docker-compose up -d

# Para crear un usuario administrador:
$ docker-compose run --rm django ./manage.py createsuperuser

# Para cargar países
$ docker-compose run --rm django ./manage.py loaddata countries

# Para crear índices de ElasticSearch
$ docker-compose run --rm django ./manage.py runscript recreate_all_indexes

# Para programar tareas de indexado por primera vez
$ docker-compose run --rm django ./manage.py runscript schedule_first_time_index_task

# Para programar tareas de indexado y cache
$ docker-compose run --rm django ./manage.py runscript schedule_tasks

# Para actualizar indices de wagtail
$ docker-compose run --rm django ./manage.py update_index
```

Visitar https://localhost.

Los navegadores mostrarán una alerta de seguridad. Esto es normal con
certificados generados localmente. Aceptar la alerta y proceder.

En Chrome es posible deshabilitar estas alertas para "localhost". Para esto
se debe navegar a "chrome://flags/#allow-insecure-localhost", y habilitar
la opción resaltada en amarillo.


# Instrucciones extra para usuarios MacOs
Si usted nota que los cambios de los archivos no se ven reflejados de forma
inmediata en Docker, utilice la alternativa de sincronización docker-sync.
Este método es muy eficiente en macOS, y de hecho es recomendado.
Para configurar docker-sync:

```shell
# Instalar docker-sync
$ gem install docker-sync
# Para levantar el proyecto.
$ make start
# Para detener el proyecto.
$ make stop
```
El paquete `gem` es instalado con `ruby`, es necesario que lo instale en su sistema a trav'es de los paquetes `ruby`, ruby-devel` o `ruby-dev` de acuerdo a su sistema operativo.

Si requiere dependencias adicionales para DockerSync puede [instalarlas manualmente](https://www.eldonaldo.com/gists/docker-sync-on-macos-big-sur/).


## Logs y errores

Para ver el log de Docker correr uno de estos siguientes comandos:

```shell
# Todos los contenedores.
$ docker-compose logs -f
# Un contenedor específico.
$ docker-compose logs -f [contenedor]
```

## Desarrollo Front-End

La compilación y manejo de archivos de archivos para front-end se manejan
por medio de [WebPack](https://webpack.js.org) y/o por medio de [archivos
estáticos](https://docs.djangoproject.com/en/dev/howto/static-files/) de Django.

Está configurado con [HMR](https://webpack.js.org/concepts/hot-module-replacement/)

### CSS y JS

El código debe estar en `resources/src`, y es compilado a `resources/static/wp`.

Incluye:
- [Babel](https://babeljs.io)
- [Postcss](https://postcss.org)

El contenido de `resources/static/wp` no debe estar en control de versiones.


### Nucleus

La guía de estilos de [Nucleus](https://holidaypirates.github.io/nucleus/) se
puede ver en https://localhost/static/styleguide/index.html.

Para compilar Nucleus y actualizar los ejemplos se debe ejecutarse el siguiente
comando:
```shell
# Sólo la primera vez, o cuando se actualicen los ejemplos.
$ docker-compose run --rm webpack npm run styleguide
```
Los estilos se actualizan de forma automática con WebPack.

Para exportar la guía de estilos a un archivo `.dev/styleguide.tar.gz`:
```shell
$ docker-compose run --rm webpack npm run styleguide:pack
```


### Templates

Los templates del proyecto deben estar en la carpeta `resources/templates/biblored`.  
Por fuera de esta sólo deben estar [templates sobre escritos](
    https://docs.djangoproject.com/en/dev/howto/overriding-templates/)
de otras aplicaciones.


## Desarrollo Back-End

### Código

Configurar el editor con las siguientes herramientas:

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

- [Black](https://github.com/ambv/black) para formatear código de Python.
- [iSort](https://github.com/timothycrosley/isort) con la configuración
compatible con [Black](https://github.com/ambv/black)
- [pycodestyle](https://github.com/PyCQA/pycodestyle) y [pydocstyle](https://github.com/PyCQA/pydocstyle)
como linters. Configurar ancho de línea para que satisfaga [Black](https://github.com/ambv/black).

[Black](https://github.com/ambv/black) debe ser quien mande ante cualquier
duda o incompatibilidad entre herramientas.

### Manejo de paquetes

- [Poetry](http://poetry.eustace.io) para dependencias. Uso dentro de docker:
`docker-compose run --rm django poetry --version`
