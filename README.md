# Mente Serena

Sitio estático publicado con GitHub Pages:

`https://hospsiqui-maker.github.io/menteserena/`

## Estructura

- `index.html`: contenido, estilos y comportamiento del sitio.
- `sitemap.xml`: mapa del sitio para buscadores.
- `robots.txt`: reglas de rastreo y referencia al sitemap.
- `google265c39322475edcf.html`: verificación de Google.
- `privacidad.html`: Política de Privacidad y Tratamiento de Datos Personales.
- `terminos.html`: Términos y Condiciones de Uso y Servicio.

## Servicios presentados

- Medicina del Sueño mediante el método Neurorest.
- Psicoterapia mediante el método Vertex.

## Contacto y privacidad

La página no incluye formularios ni captura datos. Existe un único acceso flotante que abre directamente WhatsApp con un mensaje inicial breve.

Mente Serena ofrece atención presencial y virtual. La modalidad disponible y la identidad del profesional asignado se comunican de forma privada durante el contacto inicial.

## Publicación

El sitio no requiere dependencias, compilación ni instalación. GitHub Pages sirve directamente los archivos de la rama configurada.

## Validación automática

El comando local es:

`python scripts/check_site.py`

El flujo `.github/workflows/validate.yml` ejecuta la misma revisión en cada actualización del repositorio. Comprueba SEO básico, nueve bloques principales, enlaces internos, un único acceso a WhatsApp, contenido esencial y que el sitio no contenga formularios.

También valida la etiqueta robots, `robots.txt`, el sitemap y el bloque JSON-LD de `MedicalBusiness`.

La revisión incluye las páginas legales, sus rutas públicas, metadatos, enlaces comunes y la ausencia de formularios, almacenamiento local, cookies propias o scripts externos.

## Decisiones de la auditoría SEO

- Se añadió rastreo explícito, `robots.txt`, sitemap actualizado y datos estructurados.
- El JSON-LD usa cobertura en Colombia y no publica una dirección no confirmada.
- No se añadieron imágenes sin un recurso visual aprobado, para evitar enlaces rotos y mantener el rendimiento.
- No se añadieron testimonios ficticios por tratarse de servicios de salud.
- No se añadieron librerías, fuentes externas, CDNs, blog ni recursos descargables.
- Se mantuvo el título porque ya describe los servicios y la intención de búsqueda con claridad.

## Validaciones pendientes

- Revisar el contenido clínico con el responsable de Mente Serena.
- Revisar periódicamente los textos legales aplicables en Colombia.
