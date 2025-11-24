#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador ULTRA DETALLADO de Documentación y Diagramas
- Análisis profundo de código Python mediante ast
- Genera Mermaid + Graphviz (si está disponible)
- Produce DOCUMENTACION.md, HTML, y PNG/SVG de diagramas
- CLI con muchas opciones
"""

import os
import sys
import ast
import argparse
import logging
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ---------------------------
# CONFIG & UTIL
# ---------------------------

DEFAULT_OUTPUT_DIR = "docs_auto"
IGNORED_DIRS_DEFAULT = {"__pycache__", ".git", "venv", ".venv", ".mypy_cache", ".pytest_cache", "docs", "docs/diagramas", ".idea", ".vscode", "node_modules"}

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

def setup_logging(verbose: int):
    level = logging.WARNING
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT)

def safe_read_text(path: Path):
    try:
        return path.read_text(encoding="utf8")
    except Exception as e:
        logging.debug(f"No se pudo leer {path}: {e}")
        return ""

# ---------------------------
# MERMAID TO IMAGE CONVERTER
# ---------------------------

def check_mermaid_cli():
    """Verifica si mermaid-cli (mmdc) está instalado"""
    # Intentar con diferentes rutas posibles
    possible_paths = [
        "mmdc",  # PATH global
        r"C:\Users\Terramar\AppData\Roaming\npm\mmdc.cmd",  # Windows npm global
        shutil.which("mmdc"),  # Búsqueda automática
    ]
    
    for mmdc_path in possible_paths:
        if mmdc_path is None:
            continue
        try:
            result = subprocess.run([mmdc_path, "--version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                logging.info(f"Mermaid CLI encontrado: {result.stdout.strip()}")
                return mmdc_path
        except (FileNotFoundError, Exception):
            continue
    
    logging.warning("Mermaid CLI (mmdc) no está instalado.")
    return None

def check_playwright():
    """Verifica si Playwright está instalado (necesario para mmdc)"""
    try:
        import playwright
        return True
    except ImportError:
        return False

def render_mermaid_to_image(mermaid_file: Path, output_format="png", mmdc_path="mmdc"):
    """
    Renderiza un archivo .mmd a PNG/SVG usando mermaid-cli
    
    Args:
        mermaid_file: Path al archivo .mmd
        output_format: 'png' o 'svg'
        mmdc_path: Ruta al ejecutable mmdc
    
    Returns:
        Path al archivo generado o None si falla
    """
    output_file = mermaid_file.with_suffix(f".{output_format}")
    
    try:
        cmd = [
            mmdc_path,
            "-i", str(mermaid_file),
            "-o", str(output_file),
            "-t", "default",  # tema
            "-b", "white",    # background
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True)
        
        if result.returncode == 0 and output_file.exists():
            logging.info(f"✓ Imagen generada: {output_file}")
            return output_file
        else:
            logging.error(f"Error al renderizar {mermaid_file}: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout al renderizar {mermaid_file}")
        return None
    except Exception as e:
        logging.error(f"Excepción al renderizar {mermaid_file}: {e}")
        return None

def render_mermaid_with_puppeteer(mermaid_content: str, output_file: Path):
    """
    Alternativa: renderizar con un script Node.js/Puppeteer personalizado
    (requiere tener node.js instalado)
    """
    script = """
const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
      <script>mermaid.initialize({startOnLoad:true});</script>
    </head>
    <body>
      <div class="mermaid">
${process.argv[2]}
      </div>
    </body>
    </html>
  `;
  
  await page.setContent(html);
  await page.waitForSelector('.mermaid svg');
  
  const element = await page.$('.mermaid');
  await element.screenshot({path: process.argv[3]});
  
  await browser.close();
})();
"""
    try:
        script_file = output_file.parent / "render_mermaid.js"
        script_file.write_text(script)
        
        subprocess.run(
            ["node", str(script_file), mermaid_content, str(output_file)],
            check=True,
            timeout=30
        )
        
        if output_file.exists():
            logging.info(f"✓ Imagen generada con Puppeteer: {output_file}")
            script_file.unlink()  # limpiar
            return output_file
    except Exception as e:
        logging.error(f"Error con Puppeteer: {e}")
    
    return None

# ---------------------------
# AST ANALYZER
# ---------------------------

class ModuleInfo:
    def __init__(self, path: Path):
        self.path = path
        self.module_name = str(path)
        self.source = safe_read_text(path)
        self.tree = None
        self.functions = {}
        self.classes = {}
        self.imports = set()
        self.from_imports = set()
        self.calls = []
        self.entry_points = []
        self.parse()

    def parse(self):
        if not self.source:
            return
        try:
            self.tree = ast.parse(self.source, filename=str(self.path))
        except Exception as e:
            logging.warning(f"AST parse error en {self.path}: {e}")
            return

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self.functions[node.name] = node
            elif isinstance(node, ast.AsyncFunctionDef):
                self.functions[node.name] = node
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name] = node
            elif isinstance(node, ast.Import):
                for n in node.names:
                    self.imports.add(n.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                self.from_imports.add(module)

        # heuristics para entry points
        if "streamlit" in self.source or "st." in self.source:
            self.entry_points.append(("streamlit", None))
        if "__name__" in self.source and "__main__" in self.source:
            self.entry_points.append(("if_main", None))
        if "Flask" in self.source or "flask" in self.imports:
            self.entry_points.append(("flask", None))
        if "FastAPI" in self.source or "fastapi" in self.imports:
            self.entry_points.append(("fastapi", None))

    def _enclosing_function(self, node):
        if not self.tree:
            return None
        lineno = getattr(node, "lineno", None)
        if lineno is None:
            return None
        candidate = None
        for name, func in self.functions.items():
            start = getattr(func, "lineno", 0)
            end = self._infer_end_lineno(func)
            if start <= lineno <= end:
                candidate = name
                break
        return candidate

    def _infer_end_lineno(self, node):
        max_ln = getattr(node, "lineno", 0)
        for n in ast.walk(node):
            if hasattr(n, "lineno"):
                max_ln = max(max_ln, n.lineno)
        return max_ln

# ---------------------------
# PROJECT SCANNER
# ---------------------------

def scan_project(root_dir=".", exclude_dirs=None, max_depth=None):
    if exclude_dirs is None:
        exclude_dirs = set()

    root = Path(root_dir)
    modules = {}
    logging.info(f"Escaneando proyecto en {root.resolve()} ...")
    
    for dirpath, dirnames, filenames in os.walk(root):
        parts = Path(dirpath).parts
        if any(p in exclude_dirs for p in parts):
            logging.debug(f"Omitiendo carpeta: {dirpath}")
            continue
            
        if max_depth is not None:
            depth = len(Path(dirpath).relative_to(root).parts)
            if depth > max_depth:
                continue
                
        for filename in filenames:
            if filename.endswith(".py"):
                path = Path(dirpath) / filename
                try:
                    info = ModuleInfo(path)
                    modules[str(path)] = info
                    logging.debug(f"Analizado: {path}")
                except Exception as e:
                    logging.warning(f"No se pudo analizar {path}: {e}")
                    
    logging.info(f"Escaneo finalizado: {len(modules)} módulos")
    return modules

# ---------------------------
# CALLGRAPH
# ---------------------------

def build_call_graph(modules):
    nodes = set()
    edges = set()
    func_map = defaultdict(list)
    
    for mpath, minfo in modules.items():
        module_label = os.path.relpath(mpath)
        for fname in minfo.functions:
            identifier = f"{module_label}:{fname}"
            func_map[fname].append(identifier)
            nodes.add(identifier)
            
    logging.info(f"Call graph: {len(nodes)} nodos")
    return {"nodes": nodes, "edges": edges, "func_map": func_map}

# ---------------------------
# MERMAID GENERATORS
# ---------------------------

def mermaid_architecture(modules, callgraph=None):
    lines = ["flowchart TD", f'    %% Arquitectura generada {datetime.now().isoformat()}']
    
    # Agrupar módulos por carpeta
    folders = defaultdict(list)
    for mpath in modules.keys():
        folder = os.path.dirname(os.path.relpath(mpath))
        if folder == ".":
            folder = "Raíz del Proyecto"
        folders[folder].append(mpath)
    
    # Crear subgrafos por carpeta
    for folder, mpaths in sorted(folders.items()):
        folder_safe = folder.replace("\\", "/").replace(".", "_").replace('"', '')
        # SOLUCIÓN: Escapar comillas en el label
        folder_label = folder.replace('"', '')
        lines.append(f'    subgraph {folder_safe}["{folder_label}"]')
        
        for mpath in mpaths:
            minfo = modules[mpath]
            label = os.path.basename(mpath)
            node = f"mod_{abs(hash(mpath))}"
            lines.append(f'        {node}(["{label}"]):::module')
            
            # Agregar funciones principales (máximo 3)
            for fname in list(minfo.functions.keys())[:3]:
                # SOLUCIÓN: Escapar caracteres especiales en nombres de función
                safe_fname = fname.replace('(', '').replace(')', '').replace('"', '')
                fid = f'{node}_fn_{abs(hash(fname))}'
                lines.append(f'        {fid}[{safe_fname}]:::function')
                lines.append(f'        {node} --> {fid}')
        
        lines.append('    end')
    
    # Agregar conexiones entre módulos (imports)
    for mpath, minfo in modules.items():
        src_node = f"mod_{abs(hash(mpath))}"
        for imp in minfo.imports | minfo.from_imports:
            # Buscar si el import corresponde a algún módulo local
            for candidate_path in modules.keys():
                candidate_name = os.path.basename(candidate_path).replace(".py", "")
                if imp == candidate_name or imp.endswith(candidate_name):
                    tgt_node = f"mod_{abs(hash(candidate_path))}"
                    lines.append(f'    {src_node} -.->|imports| {tgt_node}')
                    break

    styles = """
    classDef module fill:#0b2545,stroke:#fff,color:#fff;
    classDef function fill:#0b7a9e,stroke:#fff,color:#fff;
    """
    lines.append(styles)
    return "\n".join(lines)

def mermaid_flowchart(modules, callgraph):
    lines = ["flowchart TD", f'    %% Flujo generado {datetime.now().isoformat()}']
    lines.append('    Start((INICIO)):::start')
    
    # Buscar entry points más inteligentemente
    entry_modules = []
    main_files = []
    
    for mpath, minfo in modules.items():
        basename = os.path.basename(mpath)
        # Priorizar main.py, __main__.py, app.py
        if basename in ["main.py", "__main__.py", "app.py"]:
            main_files.append(mpath)
        elif minfo.entry_points:
            entry_modules.append(mpath)
    
    # Usar main files primero, luego entry points
    priority_modules = main_files + entry_modules
    if not priority_modules:
        priority_modules = list(modules.keys())[:5]  # Primeros 5 módulos
    
    prev = "Start"
    node_counter = 1
    processed = set()
    
    # Procesar módulos prioritarios
    for entry in priority_modules[:5]:
        if entry in processed:
            continue
        processed.add(entry)
        
        mlabel = os.path.relpath(entry).replace("\\", "/")
        nid = f"N{node_counter}"
        node_counter += 1
        lines.append(f'    {nid}["{mlabel}"]:::process')
        lines.append(f'    {prev} --> {nid}')
        
        # Agregar funciones principales del módulo
        minfo = modules[entry]
        func_names = list(minfo.functions.keys())[:3]
        
        for fname in func_names:
            fid = f"F{node_counter}"
            node_counter += 1
            # SOLUCIÓN: Remover paréntesis de nombres de función
            safe_fname = fname.replace('(', '').replace(')', '').replace('"', '')
            lines.append(f'    {fid}[{safe_fname}]:::function')
            lines.append(f'    {nid} --> {fid}')
        
        prev = nid
        
        # Conectar a módulos importados locales
        for imp in list(minfo.imports | minfo.from_imports)[:2]:
            for candidate in modules.keys():
                if candidate in processed:
                    continue
                candidate_name = os.path.basename(candidate).replace(".py", "")
                if imp == candidate_name or imp.endswith(candidate_name):
                    imp_label = os.path.relpath(candidate).replace("\\", "/")
                    imp_nid = f"N{node_counter}"
                    node_counter += 1
                    lines.append(f'    {imp_nid}["{imp_label}"]:::imported')
                    lines.append(f'    {nid} -.->|usa| {imp_nid}')
                    processed.add(candidate)
                    break
    
    lines.append('    EndNode((FIN)):::endstyle')
    lines.append(f'    {prev} --> EndNode')
    
    styles = """
    classDef start fill:#76b852,color:#fff;
    classDef endstyle fill:#d9534f,color:#fff;
    classDef process fill:#2b7a78,color:#fff;
    classDef function fill:#0174a8,color:#fff;
    classDef imported fill:#f0ad4e,color:#000;
    """
    lines.append(styles)
    return "\n".join(lines)

# ---------------------------
# GRAPHVIZ DOT
# ---------------------------

def generate_dot_from_callgraph(callgraph, out_path):
    dot_lines = ["digraph callgraph {", "rankdir=LR;", "node [shape=box, style=filled, color=lightblue];"]
    
    for n in sorted(list(callgraph["nodes"])[:50]):  # limitar a 50 nodos
        safe_n = n.replace('"', '\\"')
        dot_lines.append(f'"{safe_n}";')
        
    dot_lines.append("}")
    dot_text = "\n".join(dot_lines)
    
    dot_file = out_path / "callgraph.dot"
    dot_file.write_text(dot_text, encoding="utf8")
    logging.info(f"DOT generado: {dot_file}")
    
    try:
        subprocess.run(["dot", "-V"], capture_output=True, check=True)
        png_file = out_path / "callgraph.png"
        subprocess.run(["dot", "-Tpng", str(dot_file), "-o", str(png_file)], check=True)
        logging.info(f"✓ PNG de callgraph: {png_file}")
        return True
    except:
        logging.warning("Graphviz no disponible")
        return False

# ---------------------------
# MARKDOWN & HTML
# ---------------------------

def render_markdown(output_dir: Path, modules, mermaid_arch, mermaid_flow, has_images=False):
    md_file = output_dir / "DOCUMENTACION_ULTRA.md"
    now = datetime.now().isoformat()
    
    lines = [
        f"# Documentación ULTRA - {now}\n",
        "## Contenido\n",
        "- Diagrama de arquitectura",
        "- Diagrama de flujo",
        "- Desglose de módulos\n",
    ]
    
    lines.append("## Diagrama de Arquitectura\n")
    if has_images and (output_dir / "mermaid" / "architecture.png").exists():
        lines.append("![Arquitectura](mermaid/architecture.png)\n")
    lines.append("```mermaid\n" + mermaid_arch + "\n```\n")
    
    lines.append("## Diagrama de Flujo\n")
    if has_images and (output_dir / "mermaid" / "flowchart.png").exists():
        lines.append("![Flujo](mermaid/flowchart.png)\n")
    lines.append("```mermaid\n" + mermaid_flow + "\n```\n")
    
    lines.append("## Módulos del Proyecto\n")
    for path, info in sorted(modules.items()):
        lines.append(f"### `{os.path.relpath(path)}`\n")
        lines.append(f"- **Funciones**: {len(info.functions)}")
        lines.append(f"- **Clases**: {len(info.classes)}")
        lines.append(f"- **Entry points**: {', '.join(str(x[0]) for x in info.entry_points) or 'ninguno'}\n")
    
    md_file.write_text("\n".join(lines), encoding="utf8")
    logging.info(f"✓ Markdown: {md_file}")
    return md_file

def render_html(output_dir: Path, md_path: Path):
    html_file = output_dir / "DOCUMENTACION_ULTRA.html"
    md_text = md_path.read_text(encoding="utf8")
    
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>Documentación ULTRA</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true, theme:'default'}});</script>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 2rem; background: #f5f5f5; }}
h1 {{ color: #0b2545; }}
h2 {{ color: #0b7a9e; border-bottom: 2px solid #0b7a9e; padding-bottom: 0.5rem; }}
pre, code {{ background:#2d2d2d; color:#f8f8f2; padding: 1rem; overflow:auto; border-radius: 5px; }}
.mermaid {{ background: #fff; border: 1px solid #ddd; padding: 1rem; margin: 1rem 0; border-radius: 5px; }}
img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
</style>
</head>
<body>
{md_text.replace('```mermaid', '<div class="mermaid">').replace('```', '</div>')}
</body></html>
"""
    html_file.write_text(html, encoding="utf8")
    logging.info(f"✓ HTML: {html_file}")
    return html_file

# ---------------------------
# MAIN
# ---------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Generador ULTRA de documentación con imágenes de diagramas.")
    p.add_argument("--root", "-r", default=".", help="Directorio raíz del proyecto")
    p.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR, help="Directorio de salida")
    p.add_argument("--exclude", "-e", nargs="*", default=[], help="Carpetas a excluir")
    p.add_argument("--formats", "-f", nargs="*", default=["md","html","png"], help="Formatos: md, html, png, svg")
    p.add_argument("--max-depth", type=int, default=None, help="Profundidad máxima de escaneo")
    p.add_argument("--verbose", "-v", action="count", default=0, help="Verbosidad (-v, -vv)")
    p.add_argument("--generate-dot", action="store_true", help="Generar callgraph con Graphviz")
    p.add_argument("--image-format", default="png", choices=["png","svg"], help="Formato de imágenes Mermaid")
    return p.parse_args()

def main():
    args = parse_args()
    setup_logging(args.verbose)
    
    print("\n" + "="*60)
    print("  GENERADOR ULTRA DE DOCUMENTACIÓN")
    print("="*60 + "\n")
    
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Verificar herramientas
    mmdc_path = check_mermaid_cli()
    has_mmdc = mmdc_path is not None
    
    if not has_mmdc and ("png" in args.formats or "svg" in args.formats):
        print("\n⚠️  IMPORTANTE: Para generar imágenes de diagramas, instala Mermaid CLI:")
        print("   npm install -g @mermaid-js/mermaid-cli")
        print("   (Requiere Node.js instalado)\n")
    
    exclude = set(IGNORED_DIRS_DEFAULT) | set(args.exclude)
    modules = scan_project(root_dir=args.root, exclude_dirs=exclude, max_depth=args.max_depth)
    
    if not modules:
        logging.error("❌ No se encontraron módulos Python")
        sys.exit(1)
    
    callgraph = build_call_graph(modules)
    
    # Generar Mermaid
    mermaid_arch = mermaid_architecture(modules, callgraph)
    mermaid_flow = mermaid_flowchart(modules, callgraph)
    
    mermaid_dir = out_dir / "mermaid"
    mermaid_dir.mkdir(exist_ok=True)
    
    arch_file = mermaid_dir / "architecture.mmd"
    flow_file = mermaid_dir / "flowchart.mmd"
    
    arch_file.write_text(mermaid_arch, encoding="utf8")
    flow_file.write_text(mermaid_flow, encoding="utf8")
    
    print(f"✓ Archivos Mermaid generados en {mermaid_dir}")
    
    # Generar imágenes
    images_generated = False
    if has_mmdc and (args.image_format in args.formats or "png" in args.formats or "svg" in args.formats):
        print("\nGenerando imágenes de diagramas...")
        
        arch_img = render_mermaid_to_image(arch_file, args.image_format, mmdc_path)
        flow_img = render_mermaid_to_image(flow_file, args.image_format, mmdc_path)
        
        if arch_img and flow_img:
            images_generated = True
            print(f"✓ Imágenes generadas exitosamente")
    
    # Graphviz
    if args.generate_dot:
        callgraph_dir = out_dir / "callgraph"
        callgraph_dir.mkdir(exist_ok=True)
        generate_dot_from_callgraph(callgraph, callgraph_dir)
    
    # Markdown y HTML
    md_path = render_markdown(out_dir, modules, mermaid_arch, mermaid_flow, images_generated)
    
    if "html" in args.formats:
        render_html(out_dir, md_path)
    
    print("\n" + "="*60)
    print(f"✓ Documentación completa en: {out_dir.resolve()}")
    print("="*60 + "\n")
    
    if not has_mmdc and ("png" in args.formats or "svg" in args.formats):
        print("💡 Tip: Instala Mermaid CLI para generar imágenes automáticamente:")
        print("   npm install -g @mermaid-js/mermaid-cli\n")

if __name__ == "__main__":
    main()