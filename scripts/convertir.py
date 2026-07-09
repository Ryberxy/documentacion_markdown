# scripts/convertir.py
import sys
import os
import yaml
import markdown
from weasyprint import HTML
from pathlib import Path

def leer_frontmatter(contenido):
    """Extrae el frontmatter YAML y el cuerpo del markdown"""
    if not contenido.startswith('---'):
        return {}, contenido
    
    partes = contenido.split('---', 2)
    if len(partes) < 3:
        return {}, contenido
    
    meta = yaml.safe_load(partes[1])
    cuerpo = partes[2]
    return meta, cuerpo

def md_a_pdf(fichero_md, directorio_salida):
    with open(fichero_md, 'r', encoding='utf-8') as f:
        contenido = f.read()

    meta, cuerpo = leer_frontmatter(contenido)
    tipo = meta.get('tipo', 'documento')
    titulo = meta.get('titulo', Path(fichero_md).stem)

    # CSS según el tipo
    if tipo == 'presentacion':
        css = """
        body { font-family: Arial, sans-serif; font-size: 24px; }
        h1 { page-break-before: always; color: #2c3e50; font-size: 36px; }
        h2 { color: #3498db; font-size: 28px; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
        """
    else:
        css = """
        body { font-family: Arial, sans-serif; font-size: 12px; 
               max-width: 800px; margin: auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
        h2 { color: #2980b9; }
        h3 { color: #16a085; }
        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
        strong { color: #2c3e50; }
        """

    html_cuerpo = markdown.markdown(cuerpo, extensions=['fenced_code', 'tables'])
    html_completo = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>{css}</style>
    </head>
    <body>
        <h1>{titulo}</h1>
        {html_cuerpo}
    </body>
    </html>
    """

    nombre_pdf = Path(fichero_md).stem + '.pdf'
    ruta_pdf = os.path.join(directorio_salida, nombre_pdf)
    HTML(string=html_completo).write_pdf(ruta_pdf)
    print(f">>> PDF generado: {ruta_pdf}")

# Main
ficheros_modificados = sys.argv[1]
os.makedirs('/tmp/pdfs', exist_ok=True)

with open(ficheros_modificados, 'r') as f:
    ficheros = [l.strip() for l in f.readlines() if l.strip().endswith('.md')]

for fichero in ficheros:
    if os.path.exists(fichero):
        md_a_pdf(fichero, '/tmp/pdfs')
