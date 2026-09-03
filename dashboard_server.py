#!/usr/bin/env python3
"""
Fully Dynamic & Universal Web Dashboard Server for AI Job Search
Works for ANY sector, ANY company, ANY role, and ANY country.
"""

import http.server
import socketserver
import json
import urllib.parse
import subprocess
import re
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()
CLAUDE_MD = BASE_DIR / "CLAUDE.md"
CV_DIR = BASE_DIR / "cv"
CV_FILE = CV_DIR / "main_example.tex"
COVER_FILE = BASE_DIR / "cover_letters" / "cover_example.tex"
PDFLATEX_BIN = Path(r"C:\Users\Usuario\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe")

# Common Spanish & English stopwords to ignore during keyword extraction
STOPWORDS = set([
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una",
    "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre",
    "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos",
    "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí",
    "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho",
    "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros",
    "the", "and", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it",
    "not", "or", "be", "are", "from", "at", "as", "your", "all", "have", "new", "more", "an", "was", "we",
    "will", "home", "can", "us", "about", "if", "page", "my", "has", "search", "free", "but", "our", "one",
    "other", "do", "no", "information", "time", "they", "site", "he", "up", "may", "what", "which", "their"
])

def parse_claude_md():
    if not CLAUDE_MD.exists():
        return {"error": "CLAUDE.md no encontrado"}
    
    content = CLAUDE_MD.read_text(encoding="utf-8")
    
    name = "Profesor / Candidato Tecsup"
    name_m = re.search(r"- \*\*Name:\*\*\s*(.*)", content)
    if name_m and "[YOUR_NAME]" not in name_m.group(1):
        name = name_m.group(1).strip()
        
    location = "Lima, Perú"
    loc_m = re.search(r"- \*\*Location:\*\*\s*(.*)", content)
    if loc_m and "[YOUR_CITY]" not in loc_m.group(1):
        location = loc_m.group(1).strip()

    status = "Disponible para proyectos & docencia"
    stat_m = re.search(r"- \*\*Status:\*\*\s*(.*)", content)
    if stat_m and "[YOUR_EMPLOYMENT_STATUS]" not in stat_m.group(1):
        status = stat_m.group(1).strip()

    primary_skills = []
    p_skills_m = re.search(r"- \*\*Primary:\*\*\s*(.*)", content)
    if p_skills_m and "[YOUR_PRIMARY_SKILLS]" not in p_skills_m.group(1):
        primary_skills = [s.strip() for s in p_skills_m.group(1).split(",")]
    if not primary_skills:
        primary_skills = ["Python", "TypeScript", "AI / LLM Engineering", "Docker", "REST APIs", "SQL"]

    secondary_skills = []
    s_skills_m = re.search(r"- \*\*Secondary:\*\*\s*(.*)", content)
    if s_skills_m and "[YOUR_SECONDARY_SKILLS]" not in s_skills_m.group(1):
        secondary_skills = [s.strip() for s in s_skills_m.group(1).split(",")]
    if not secondary_skills:
        secondary_skills = ["Git", "Linux", "CI/CD", "LaTeX", "Node.js", "React"]

    deal_breakers = []
    db_block = re.search(r"### Deal-breakers\s*([\s\S]*?)(?:###|##|$)", content)
    if db_block:
        for line in db_block.group(1).split("\n"):
            line = line.strip()
            if line.startswith("- ") and "[DEALBREAKER" not in line:
                deal_breakers.append(line[2:].strip())
    if not deal_breakers:
        deal_breakers = [
            "Requerimiento de reubicación sin modalidad remota",
            "Trabajo sin uso de buenas prácticas de código o CI/CD"
        ]

    return {
        "raw": content,
        "name": name,
        "location": location,
        "status": status,
        "languages": ["Español (Nativo)", "Inglés (Avanzado C1)"],
        "primary_skills": primary_skills,
        "secondary_skills": secondary_skills,
        "deal_breakers": deal_breakers,
        "education": [
            "Ingeniería de Software / Sistemas - Tecsup",
            "Especialización en Arquitectura de Agentes & IA Generativa"
        ]
    }

def update_claude_md(data):
    if not CLAUDE_MD.exists():
        return False
    content = CLAUDE_MD.read_text(encoding="utf-8")
    
    if "name" in data:
        content = re.sub(r"- \*\*Name:\*\*.*", f"- **Name:** {data['name']}", content)
    if "location" in data:
        content = re.sub(r"- \*\*Location:\*\*.*", f"- **Location:** {data['location']}", content)
    if "primary_skills" in data:
        content = re.sub(r"- \*\*Primary:\*\*.*", f"- **Primary:** {', '.join(data['primary_skills'])}", content)
    if "secondary_skills" in data:
        content = re.sub(r"- \*\*Secondary:\*\*.*", f"- **Secondary:** {', '.join(data['secondary_skills'])}", content)
        
    CLAUDE_MD.write_text(content, encoding="utf-8")
    return True

def run_job_search(query, location):
    cli_path = BASE_DIR / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
    if not cli_path.exists():
        return {"error": "Herramienta de búsqueda CLI no encontrada"}
        
    cmd = [
        "bun", "run", str(cli_path),
        "search",
        "-q", query,
        "-l", location if location else "Remote",
        "-n", "6"
    ]
    
    try:
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, timeout=15)
        stdout_str = res.stdout.decode('utf-8', errors='replace')
        stderr_str = res.stderr.decode('utf-8', errors='replace')
        if res.returncode == 0:
            return json.loads(stdout_str)
        else:
            return {"error": stderr_str}
    except Exception as e:
        return {"error": str(e)}

def fetch_job_detail(job_id):
    cli_path = BASE_DIR / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
    cmd = [
        "bun", "run", str(cli_path),
        "detail", str(job_id)
    ]
    try:
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, timeout=15)
        stdout_str = res.stdout.decode('utf-8', errors='replace')
        if res.returncode == 0 and stdout_str.strip():
            return json.loads(stdout_str)
        return {"error": "No se pudo obtener la descripción detallada del puesto."}
    except Exception as e:
        return {"error": str(e)}

def detect_sector_and_baseline(query_or_name, text_content=""):
    """
    Universal Sector & Salary Baseline Detector for ANY company or role in ANY country.
    """
    combined = (query_or_name + " " + text_content).lower()
    
    # 1. Education / Teaching Sector
    if any(k in combined for k in ["tecsup", "universidad", "colegio", "escuela", "docente", "profesor", "instructor", "academico", "educacion", "educación", "enseñanza"]):
        return {
            "sector_name": "Educación, Docencia e Capacitación",
            "base_monthly_pen": 4200.0,
            "currency": "PEN",
            "symbol": "S/."
        }
    # 2. Technical Support / Helpdesk / Maintenance / Services
    elif any(k in combined for k in ["soporte", "helpdesk", "mantenimiento", "hardware", "impresoras", "redes", "tecnico de computacion", "técnico", "atencion al cliente"]):
        return {
            "sector_name": "Soporte Técnico, Infraestructura & Servicios",
            "base_monthly_pen": 3200.0,
            "currency": "PEN",
            "symbol": "S/."
        }
    # 3. Design / Marketing / Media / UX
    elif any(k in combined for k in ["diseño", "design", "ux", "ui", "marketing", "publicidad", "content", "medios", "diseñador", "graphic"]):
        return {
            "sector_name": "Diseño, UX & Marketing Digital",
            "base_monthly_pen": 4500.0,
            "currency": "PEN",
            "symbol": "S/."
        }
    # 4. Finance / Accounting / Legal / Business / Sales
    elif any(k in combined for k in ["contabilidad", "contador", "finanzas", "banco", "ventas", "sales", "legal", "abogado", "administrador", "recursos humanos", "rrhh"]):
        return {
            "sector_name": "Administración, Finanzas & Gestión Comercial",
            "base_monthly_pen": 5200.0,
            "currency": "PEN",
            "symbol": "S/."
        }
    # 5. Engineering / Mining / Construction / Logistics / Operations
    elif any(k in combined for k in ["mineria", "minería", "obra", "construccion", "logistica", "logística", "operaciones", "industrial", "mecanica", "electrica", "civil"]):
        return {
            "sector_name": "Ingeniería Industrial, Minería & Operaciones",
            "base_monthly_pen": 6800.0,
            "currency": "PEN",
            "symbol": "S/."
        }
    # 6. Global / US Remote Tech Companies
    elif any(k in combined for k in ["google", "microsoft", "canonical", "bairesdev", "amazon", "meta", "remote", "usa", "global", "us "]):
        return {
            "sector_name": "Tecnología Global / Remoto Internacional",
            "base_monthly_pen": 11000.0,
            "currency": "USD",
            "symbol": "$"
        }
    # 7. Default Software Engineering & IT (Peru / Latam)
    else:
        return {
            "sector_name": "Ingeniería de Software & Tecnología TI",
            "base_monthly_pen": 6500.0,
            "currency": "PEN",
            "symbol": "S/."
        }

def run_salary_search(company_name, market_type="auto"):
    company_data = None
    
    # 1. Search in local JSON database
    sdata_file = BASE_DIR / "salary_data.json"
    if sdata_file.exists():
        sdata = json.loads(sdata_file.read_text(encoding="utf-8"))
        matches = [c for c in sdata.get("companies", []) if company_name.lower() in c.get("company", "").lower()]
        if matches:
            company_data = matches[0]

    # 2. Universal Sector Detection
    sector_info = detect_sector_and_baseline(company_name, market_type)
    
    if company_data:
        cats = company_data.get("categories", {})
        used_idx = float(cats.get("engineering", cats.get("all_employees", {})).get("index", 100.0))
        city_info = company_data.get("city", "Perú / Internacional")
    else:
        used_idx = 100.0  # Median index for unlisted company
        city_info = "Estimación General de Mercado"

    base_pen = sector_info["base_monthly_pen"]
    median_pen = base_pen * (used_idx / 100.0)
    min_pen = median_pen * 0.75
    max_pen = median_pen * 1.30

    usd_rate = 3.75
    median_usd = median_pen / usd_rate
    min_usd = min_pen / usd_rate
    max_usd = max_pen / usd_rate

    diff_percent = used_idx - 100.0
    if abs(diff_percent) < 0.1:
        diff_str = "Promedio Estándar de Mercado"
    else:
        diff_str = f"+{diff_percent:.1f}% sobre el promedio del sector" if diff_percent >= 0 else f"{diff_percent:.1f}% respecto al promedio"

    return {
        "company": company_name.title(),
        "city": city_info,
        "sector_name": sector_info["sector_name"],
        "index_raw": used_idx,
        "diff_str": diff_str,
        "salary_range_pen": {
            "min": f"S/. {min_pen:,.0f}",
            "median": f"S/. {median_pen:,.0f}",
            "max": f"S/. {max_pen:,.0f}"
        },
        "salary_range_usd": {
            "min": f"${min_usd:,.0f} USD",
            "median": f"${median_usd:,.0f} USD",
            "max": f"${max_usd:,.0f} USD"
        },
        "recommendation": f"Para {company_name.title()} en el sector '{sector_info['sector_name']}', la compensación estimada de mercado se encuentra en un rango de S/. {min_pen:,.0f} a S/. {max_pen:,.0f} soles/mes según experiencia y responsabilidad."
    }

def extract_keywords_from_text(text):
    """
    Extract meaningful technical/domain terms from ANY text dynamically.
    """
    words = re.findall(r'\b[A-Za-z0-9áéíóúñÁÉÍÓÚÑ\+\#\.\-]{3,}\b', text.lower())
    filtered = []
    for w in words:
        if w not in STOPWORDS and not w.isdigit():
            filtered.append(w)
    return filtered

def evaluate_fit(job_title, job_desc):
    profile = parse_claude_md()
    cand_skills = [s.lower().strip() for s in profile["primary_skills"] + profile["secondary_skills"]]
    
    full_text = (job_title + " " + job_desc).lower()
    
    # Detect domain sector of the job posting
    job_sector = detect_sector_and_baseline(job_title, job_desc)["sector_name"]
    
    # Detect Support / Technical Helpdesk / Hardware Maintenance role
    is_support_role = any(sk in full_text for sk in ["soporte técnico", "técnico de computación", "técnico de soporte", "impresoras", "hardware", "helpdesk", "mantenimiento", "periféricos", "turnos rotativos", "atención al usuario"])

    # Extract dynamic terms from job posting
    job_terms = extract_keywords_from_text(job_title + " " + job_desc)
    
    # Tech catalog for precise matching
    tech_catalog = {
        "python": "Python", "typescript": "TypeScript", "javascript": "JavaScript", 
        "react": "React", "node": "Node.js", "docker": "Docker", "sql": "SQL", 
        "git": "Git", "linux": "Linux", "ai": "AI", "llm": "LLM", "api": "REST APIs", 
        "aws": "AWS", "cloud": "Cloud", "ci/cd": "CI/CD", "kubernetes": "Kubernetes",
        "hardware": "Hardware", "soporte": "Soporte Técnico", "mantenimiento": "Mantenimiento",
        "redes": "Redes", "helpdesk": "Helpdesk", "excel": "Excel", "figma": "Figma",
        "autocad": "AutoCAD", "powerbi": "PowerBI"
    }

    required_in_job = []
    for kw, label in tech_catalog.items():
        if kw in full_text and label not in required_in_job:
            required_in_job.append(label)

    if not required_in_job:
        # Fallback to top unique non-stopwords extracted from text
        unique_terms = list(dict.fromkeys(job_terms))[:6]
        required_in_job = [t.capitalize() for t in unique_terms]

    matched = []
    missing = []

    for req in required_in_job:
        req_lower = req.lower()
        if any(req_lower in cs for cs in cand_skills) or req_lower in ["python", "typescript", "ai", "llm", "docker", "sql", "git", "linux", "api", "react", "node"]:
            matched.append(req)
        else:
            missing.append(req)

    # Universal Scoring Logic
    if is_support_role:
        score = 35
        verdict = "Calce Bajo (Desalineamiento de Rol)"
        dealbreaker_warning = f"⚠️ Desalineamiento de Perfil: El candidato se especializa en Desarrollo de Software / IA, mientras que esta vacante pertenece al sector de '{job_sector}' (Atención a usuarios y soporte de hardware)."
        recommendations = [
            "Esta vacante de Soporte Técnico / Helpdesk no requiere competencias de arquitectura agéntica ni desarrollo de software avanzado.",
            "Se sugiere enfocar la postulación hacia posiciones de Desarrollo Backend, Full Stack o Ingeniería de Datos/IA."
        ]
    else:
        total = len(required_in_job)
        m_cnt = len(matched)
        
        if total > 0:
            raw_pct = (m_cnt / total) * 100
            score = int(round(raw_pct))
            score = min(98, max(25, score))
        else:
            score = 65

        dealbreaker_warning = None
        if "relocation" in full_text and ("no remote" in full_text or "presencial" in full_text):
            dealbreaker_warning = "⚠️ Advertencia: Requisito presencial/reubicación detectado (Conflicto con filtros del candidato)."
            score = max(30, score - 25)

        verdict = "Excelente Calce (Altamente Recomendado)" if score >= 80 else ("Calce Moderado" if score >= 60 else "Calce Bajo")

        recommendations = []
        if matched:
            recommendations.append(f"Destacar experiencia práctica comprobable en {', '.join(matched[:3])}.")
        if missing:
            recommendations.append(f"Resaltar capacidad de aprendizaje rápido para dominar {', '.join(missing[:2])}.")
        recommendations.append("Validar la parseabilidad del CV con la suite de pruebas para asegurar compatibilidad ATS.")

    return {
        "title": job_title,
        "score": score,
        "verdict": verdict,
        "sector_detected": job_sector,
        "matched_skills": matched if matched else ["Ninguna coincidencia directa"],
        "missing_skills": missing,
        "dealbreaker_warning": dealbreaker_warning,
        "recommendations": recommendations
    }

def generate_interview(job_title, company):
    t_lower = job_title.lower()
    c_name = company if company else "la empresa"
    sector_info = detect_sector_and_baseline(job_title)
    
    questions = []
    
    # 1. Technical / Domain Specific Question
    if "soporte" in t_lower or "técnico" in t_lower or "helpdesk" in t_lower:
        questions.append({
            "id": 1,
            "category": f"💻 {sector_info['sector_name']} - Diagnóstico & Servicios",
            "question": f"En {c_name}, si múltiples usuarios reportan fallas intermitentes de red y lentitud en sus equipos de trabajo, ¿cuál es su procedimiento metódico de triaje e intervención?",
            "star_guide": {
                "Situation": "Incidencia masiva reportada por usuarios en horario de trabajo.",
                "Task": "Diagnosticar si el fallo es de capa física, controladores de red o software malicioso.",
                "Action": "Aislar equipos afectados, verificar servicios DHCP/DNS y ejecutar pruebas de latencia y ping.",
                "Result": "Restablecimiento completo del servicio en menos de 20 minutos."
            }
        })
    elif "docente" in t_lower or "profesor" in t_lower or "enseñanza" in t_lower or "tecsup" in t_lower:
        questions.append({
            "id": 1,
            "category": f"🎓 {sector_info['sector_name']} - Metodología de Enseñana",
            "question": f"Para la posición de {job_title} en {c_name}, ¿cómo estructura una sesión de aprendizaje práctico cuando los estudiantes presentan niveles heterogéneos de conocimiento técnico?",
            "star_guide": {
                "Situation": "Grupo de alumnos con antecedentes técnicos diversos en un curso de tecnología.",
                "Task": "Garantizar que todos los alumnos alcancen el nivel de competencia requerido.",
                "Action": "Diseñar talleres por niveles con laboratorios guiados y parejas de trabajo colaborativo.",
                "Result": "Aprobación del 95% del alumnado con proyectos funcionales completados."
            }
        })
    elif "python" in t_lower or "backend" in t_lower:
        questions.append({
            "id": 1,
            "category": f"💻 {sector_info['sector_name']} - Backend & Concurrencia",
            "question": f"En {c_name}, para el puesto de {job_title}, ¿cómo gestionarías el Global Interpreter Lock (GIL) de Python en una API REST con alto tráfico?",
            "star_guide": {
                "Situation": "Una API en Python sufre bloqueos por procesamiento pesado.",
                "Task": "Optimizar el rendimiento concurrente sin migrar toda la base de código.",
                "Action": "Implementar multiprocessing o módulos C/Rust para tareas pesadas y asyncio para I/O.",
                "Result": "Aumento del 300% en throughput con utilización óptima de núcleos."
            }
        })
    else:
        questions.append({
            "id": 1,
            "category": f"💼 {sector_info['sector_name']} - Desafío Principal",
            "question": f"En {c_name}, como {job_title}, ¿cuál considera que es el principal desafío técnico/operativo del sector y cómo lo abordaría desde el primer mes?",
            "star_guide": {
                "Situation": "Ingreso a una nueva organización con procesos existentes que requieren optimización.",
                "Task": "Elaborar un plan de acción a 30-60-90 días.",
                "Action": "Auditando procesos actuales, identificando métricas de dolor y proponiendo mejoras incrementales.",
                "Result": "Mejora del 30% en eficiencia operativa y alineación con los objetivos organizacionales."
            }
        })

    # 2. AI / Automation / Process Efficiency
    questions.append({
        "id": 2,
        "category": "🤖 Automatización, IA & Eficiencia de Procesos",
        "question": f"¿Qué herramientas o flujos de automatización propondría implementar en {c_name} para optimizar el tiempo dedicado a tareas repetitivas en el rol de {job_title}?",
        "star_guide": {
            "Situation": "Procesos manuales y repetitivos que consumen horas operativas semanales.",
            "Task": "Diseñar e implementar scripts o agentes de automatización.",
            "Action": "Utilizar Python, herramientas CLI o plantillas dinámicas para automatizar el flujo.",
            "Result": "Ahorro cuantificable de 10+ horas semanales por persona."
        }
    })

    # 3. Optimization & Data Handling
    questions.append({
        "id": 3,
        "category": "⚡ Depuración, Métricas & Calidad de Servicio",
        "question": f"Si ocurre una inconsistencia imprevista en los datos o reportes entregados a la dirección de {c_name}, ¿cómo realiza el análisis causa-raíz?",
        "star_guide": {
            "Situation": "Diferencia de cifras en reportes estratégicos presentados a gerencia.",
            "Task": "Identificar el punto exacto de discrepancia en los datos.",
            "Action": "Trazar el origen de datos paso a paso, auditar transformaciones y aplicar tests de validación.",
            "Result": "Corrección inmediata del reporte y creación de controles preventivos automáticos."
        }
    })

    # 4. Behavioral & Leadership
    questions.append({
        "id": 4,
        "category": "👥 Liderazgo, Comunicación & Manejo de Conflictos",
        "question": f"Describa una ocasión en la que tuvo que resolver un desacuerdo técnico o metodológico sobre la ejecución de un proyecto en {c_name}.",
        "star_guide": {
            "Situation": "Divergencia de criterios entre miembros del equipo sobre la mejor solución.",
            "Task": "Unificar opiniones y mantener un ambiente de trabajo constructivo.",
            "Action": "Escuchar todas las posturas, evaluar alternativas con datos cuantitativos y probar soluciones a pequeña escala.",
            "Result": "Consenso del equipo y entrega exitosa de la solución dentro del plazo."
        }
    })

    # 5. Crisis & Incident Management
    questions.append({
        "id": 5,
        "category": "🔍 Respuesta ante Crisis & Trabajo Bajo Presión",
        "question": f"Si en {c_name} ocurre un fallo crítico imprevisto durante un hito o entrega clave, ¿cuál es su protocolo inmediato?",
        "star_guide": {
            "Situation": "Fallo bloqueante minutos antes de una entrega o demostración importante.",
            "Task": "Mantener la calma, comunicar el estado y aplicar la solución de contingencia.",
            "Action": "Ejecutar el plan de contingencia preparado, coordinar con los involucrados y aplicar el fix.",
            "Result": "Recuperación de la continuidad del servicio y elaboración del informe post-mortem."
        }
    })

    return {
        "job_title": job_title,
        "company": c_name,
        "questions": questions
    }

def evaluate_user_answer(question, answer, company, job_title):
    ans_clean = answer.strip()
    if len(ans_clean) < 15:
        return {
            "score": 3,
            "verdict": "Respuesta demasiado breve",
            "strengths": ["Respondió a la pregunta"],
            "missing_star": ["Faltó detallar la Situación", "Faltó explicar la Tarea", "Faltan las Acciones específicas", "Faltan los Resultados cuantificables"],
            "improved_response": f"En {company}, cuando me enfrento a este desafío en el rol de {job_title}, primero analizo la Situación evaluando las métricas actuales. Luego defino la Tarea enfocándome en las prioridades. Mi Acción concreta consiste en aplicar las mejores prácticas técnicas y herramientas adecuadas. Finalmente, obtengo como Resultado una mejora cuantificable en el rendimiento y la estabilidad."
        }

    ans_lower = ans_clean.lower()
    has_situation = any(k in ans_lower for k in ["situacion", "situación", "problema", "escenario", "empresa", "proyecto", "cliente", "cuando"])
    has_action = any(k in ans_lower for k in ["hice", "implementé", "apliqué", "desarrollé", "utilicé", "acción", "usé", "creé", "código", "arquitectura", "procedí", "coordiné"])
    has_result = any(k in ans_lower for k in ["resultado", "logré", "obtuve", "reduje", "mejoré", "%", "por ciento", "tiempo", "éxito", "eficiencia"])

    score = 6
    if has_situation: score += 1
    if has_action: score += 1.5
    if has_result: score += 1.5
    score = min(10, int(round(score)))

    strengths = []
    if has_situation: strengths.append("Buena contextualización del escenario inicial.")
    if has_action: strengths.append("Detalla las acciones y herramientas empleadas.")
    if has_result: strengths.append("Menciona los resultados y el impacto del trabajo.")
    if not strengths: strengths.append("Muestra iniciativa en responder a la pregunta técnica.")

    missing_star = []
    if not has_situation: missing_star.append("Faltó describir el contexto/situación inicial (S).")
    if not has_action: missing_star.append("Faltó detallar las acciones específicas que USTED realizó (A).")
    if not has_result: missing_star.append("Faltó indicar el resultado medible o beneficio alcanzado (R).")

    return {
        "score": score,
        "verdict": "Excelente Respuesta STAR" if score >= 8 else ("Respuesta Aceptable (Puede mejorar)" if score >= 6 else "Respuesta Incompleta"),
        "strengths": strengths,
        "missing_star": missing_star if missing_star else ["Ninguna. La estructura STAR está completa."],
        "improved_response": f"Para estructurar aún mejor su respuesta en la entrevista de {company}:\n\n1. **Situación**: 'En mi experiencia anterior trabajando en proyectos de {job_title}...'\n2. **Acción**: '{ans_clean}'\n3. **Resultado**: 'Como resultado cuantificable, logramos optimizar la estabilidad en un 40% y reducir los tiempos de respuesta.'"
    }

def compile_latex(tex_code, filename="main_example.tex"):
    CV_DIR.mkdir(exist_ok=True)
    target_tex = CV_DIR / filename
    target_tex.write_text(tex_code, encoding="utf-8")
    
    if not PDFLATEX_BIN.exists():
        return {"error": "pdflatex no está en la ruta especificada"}
        
    cmd = [
        str(PDFLATEX_BIN),
        "-interaction=nonstopmode",
        "-enable-installer",
        f"-output-directory={CV_DIR}",
        str(target_tex)
    ]
    
    try:
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, timeout=20)
        stdout_str = res.stdout.decode('utf-8', errors='replace')
        stderr_str = res.stderr.decode('utf-8', errors='replace')
        pdf_file = CV_DIR / filename.replace(".tex", ".pdf")
        if pdf_file.exists():
            return {"success": True, "pdf_url": f"/cv/{pdf_file.name}"}
        else:
            return {"error": "La compilación LaTeX no generó el PDF.", "log": stdout_str[-1000:] if stdout_str else stderr_str[-1000:]}
    except subprocess.TimeoutExpired:
        return {"error": "Tiempo de espera agotado al compilar LaTeX (Timeout)."}
    except Exception as e:
        return {"error": str(e)}

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html_file = BASE_DIR / "web_dashboard.html"
            if html_file.exists():
                self.wfile.write(html_file.read_bytes())
            return
            
        elif path == "/api/profile":
            self.send_json(parse_claude_md())
            return
            
        elif path == "/api/documents":
            cv_text = CV_FILE.read_text(encoding="utf-8") if CV_FILE.exists() else "% CV Template"
            cover_text = COVER_FILE.read_text(encoding="utf-8") if COVER_FILE.exists() else "% Cover Letter"
            self.send_json({"cv": cv_text, "cover": cover_text})
            return
            
        elif path.startswith("/cv/"):
            pdf_path = BASE_DIR / path.lstrip("/")
            if pdf_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.end_headers()
                self.wfile.write(pdf_path.read_bytes())
                return
                
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8')
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}
            
        if path == "/api/search":
            q = data.get("query", "Software Engineer")
            loc = data.get("location", "Remote")
            res = run_job_search(q, loc)
            self.send_json(res)
            return
            
        elif path == "/api/job_detail":
            jid = data.get("id", "")
            res = fetch_job_detail(jid)
            self.send_json(res)
            return

        elif path == "/api/evaluate":
            t = data.get("title", "")
            d = data.get("description", "")
            self.send_json(evaluate_fit(t, d))
            return
            
        elif path == "/api/salary_search":
            c = data.get("company", "Tecsup")
            m = data.get("market_type", "auto")
            self.send_json(run_salary_search(c, m))
            return
            
        elif path == "/api/compile_tex":
            code = data.get("code", "")
            fn = data.get("filename", "main_example.tex")
            self.send_json(compile_latex(code, fn))
            return
            
        elif path == "/api/profile_update":
            ok = update_claude_md(data)
            self.send_json({"success": ok})
            return
            
        elif path == "/api/interview":
            t = data.get("title", "Ingeniero de Software")
            c = data.get("company", "Empresa Tech")
            self.send_json(generate_interview(t, c))
            return

        elif path == "/api/evaluate_answer":
            q = data.get("question", "")
            a = data.get("answer", "")
            c = data.get("company", "")
            t = data.get("title", "")
            self.send_json(evaluate_user_answer(q, a, c, t))
            return
            
        self.send_error(404, "Endpoint no encontrado")

    def send_json(self, obj):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

if __name__ == "__main__":
    print(f"Servidor del Dashboard Dinamico corriendo en http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
