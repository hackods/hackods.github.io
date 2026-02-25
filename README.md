# HackODS UNAM 2026

Sitio web del primer hackatón de la UNAM para transformar datos abiertos en soluciones sostenibles.

Sitio oficial: [hackods.unam.mx](https://www.hackods.unam.mx/)

## Descripción

HackODS es una experiencia de innovación y colaboración universitaria que busca convertir los desafíos de los Objetivos de Desarrollo Sostenible (ODS) en narrativas visuales accesibles, usando herramientas de código abierto y datos públicos.

## Estructura del sitio

```
├── index.qmd          # Página principal
├── tableros.qmd       # Reglamento de tableros
├── _quarto.yml         # Configuración del sitio Quarto
├── styles.css          # Estilos personalizados (fuentes)
├── logo.png            # Logo del navbar
├── fonts/              # Fuentes locales (Kusanagi)
└── docs/               # Salida del render (GitHub Pages)
```

## Tecnologías

- [Quarto](https://quarto.org/) — generación del sitio web
- Tema: darkly / zephyr (dark/light mode)
- Fuentes: Kusanagi (headings), Inter (body)

## Desarrollo local

```bash
quarto preview
```

## Render y publicación

```bash
quarto render
```

La salida se genera en `docs/` para GitHub Pages.

## Contacto

- Correo: hackods@ier.unam.mx
- Sitio oficial: [hackods.unam.mx](https://www.hackods.unam.mx/)
