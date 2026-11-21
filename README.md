# Aerotermia Clara

Web estática sobre aerotermia doméstica en España. No necesita WordPress ni servidor.

## Carpetas

- `contenido/` — los textos. Un archivo por página. Aquí se escribe y se corrige.
- `estatico/` — estilos, calculadoras (precio y potencia), esquemas en SVG y logotipo. Los fragmentos `.html` de esta carpeta se insertan en las páginas donde aparece `{{NOMBRE}}`.
- `docs/` — la web ya generada. Es lo que publica GitHub Pages. No se edita a mano.
- `build.py` — genera `docs/` a partir de `contenido/`.

## Publicar en GitHub Pages (gratis)

1. Sube este proyecto a un repositorio de GitHub.
2. En el repositorio: Settings → Pages → Source: «Deploy from a branch» → Branch `main`, carpeta `/docs` → Save.
3. En un par de minutos la web estará en `https://USUARIO.github.io/NOMBRE-DEL-REPOSITORIO/`.

## Conectar el dominio aerotermiaclara.es

1. En Settings → Pages → Custom domain escribe `aerotermiaclara.es` y guarda.
2. En el panel del registrador del dominio crea los registros DNS que indica la ayuda de GitHub Pages
   para dominios propios (cuatro registros A para el dominio y un CNAME para `www`).
3. Cuando GitHub lo verifique, marca «Enforce HTTPS».

## Añadir o cambiar un artículo

1. Copia un archivo de `contenido/` (por ejemplo `20-precio-casa-100.html`) y cámbiale el nombre.
2. Edita la cabecera (título, descripción, categoría, `slug`) y el texto.
3. Ejecuta `python3 build.py` y sube los cambios.

## Antes de pedir AdSense

- Cambia el correo de contacto en `build.py` (`CORREO`) por uno que exista.
- Revisa el aviso legal: la ley pide identificar al titular (nombre, NIF y domicilio o dirección de contacto).
- Cuando AdSense apruebe la web, pon tu identificador en `ADSENSE_ID` dentro de `build.py`,
  vuelve a generar y activa en AdSense el mensaje de consentimiento de cookies para Europa.
