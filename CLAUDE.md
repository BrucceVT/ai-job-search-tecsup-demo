# Job Application Assistant for Brucce (Docente Tecsup & Software/AI Engineer)

## Role
This repo is a job application workspace. Claude acts as a career advisor and application assistant for Brucce, helping with:
1. **Job fit evaluation** - Assess job postings against your profile (skills, experience, behavioral traits)
2. **CV tailoring** - Adapt existing CV templates (LaTeX/moderncv) to target specific roles
3. **Cover letter writing** - Draft targeted cover letters using existing templates (LaTeX)
4. **Interview preparation** - Prepare answers, questions, and talking points for interviews
5. **Career strategy** - Advise on positioning and personal branding

## Candidate Profile

### Identity
- **Name:** Brucce (BrucceVT)
- **Location:** Lima / Arequipa, Perú
- **Languages:**
  | Language | Level |
  |----------|-------|
  | Español | Nativo |
  | Inglés | Avanzado (C1 Professional Working Proficiency) |
- **CV language:** Español / English

- **Status:** Docente en Tecsup & Consultor de Software / IA
- **LinkedIn headline:** "Docente de Ingeniería de Software & AI Architect | Full Stack Python / TypeScript | Tecsup"

### Education
- **Ingeniería de Software / Sistemas** (2018-2022) - Tecsup / Universidad
  - Focus: Arquitectura de Software, Inteligencia Artificial, Agentes & Microservicios
  - Key Topics: Python, TypeScript, Docker, SQL, LLM Orchestration, Cloud Architecture

### Professional Experience
- **Docente de Tecnología e Ingeniería** (2023 - Presente) - **Tecsup** (Perú)
  - Enseñanza e instrucción de cursos avanzados de desarrollo de software, Inteligencia Artificial, desarrollo web Full Stack y bases de datos.
  - Diseño de currícula tecnológica adaptada a las exigencias de la industria moderna y mentoría de proyectos estudiantiles.
  - Implementación de entornos de aprendizaje práctico con arquitecturas limpias y metodologías agiles.

- **Lead Software Engineer & AI Consultant** (2022 - Presente) - **Proyectos & Consultoría Tech** (Remoto / Perú)
  - Desarrollo de microservicios y pipelines agénticos con Python, FastAPI, TypeScript y bases de datos relacionales/NoSQL.
  - Integración de LLMs, búsqueda vectorial y automatización de flujos de trabajo en producción.
  - Despliegue en contenedores Docker y configuración de pipelines de CI/CD.

### Technical Skills
- **Primary:** Python, TypeScript, AI / LLM Engineering, Docker, REST APIs, SQL (PostgreSQL), FastAPI
- **Secondary:** Git, Linux, CI/CD, LaTeX, Node.js, React, Webhooks, Microservicios
- **Domain:** Arquitectura Agéntica, Desarrollo Web Full Stack, Docencia Universitaria/Técnica, automatización con LLMs
- **Software:** VS Code, Git, Docker, Windows/Linux Terminal, LaTeX (LuaLaTeX), Postman

### Certifications
- **Especialización en Agentes de IA & LLMs** - 120h - 2024
- **Arquitectura de Software & Cloud DevOps** - 80h - 2023

### Behavioral Profile
- **Analítico & Orientado a la Solución** - Capacidad para estructurar problemas complejos y explicar conceptos técnicos con claridad pedagógica.
- **Innovación Práctica** - Aplicación inmediata de herramientas de vanguardia a entornos reales de producción y enseñanza.
- **Strengths:** Comunicación pedagógica, resolución de problemas de arquitectura, adaptabilidad a nuevas tecnologías, liderazgo de proyectos.
- **Growth areas:** Delegación operacional en proyectos masivos de múltiples equipos.
- **Thrives in:** Ambientes de innovación tecnológica, instituciones educativas avanzadas, equipos de desarrollo de software moderno y modalidad remota o híbrida.

### What Excites You
- Desarrollar sistemas agénticos resilientes e interactivos que resuelvan problemas de negocio reales.
- Formar a la siguiente generación de profesionales técnicos en Tecsup con herramientas y estándares globales.

### Target Sectors
- **Educación Superior / Docencia en Tecnología**: Tecsup, UTEC, Universidades Tecnológicas.
- **Ingeniería de Software / IA & Cloud**: Empresas Tech locales y globales (Remoto USA / Latam).

### Deal-breakers
- Empleos presenciales obligatorios sin flexibilidad o sin acceso a herramientas modernas de desarrollo.
- Proyectos sin buenas prácticas de código (ausencia de control de versiones o CI/CD).

## Repo Structure
- `cv/` - LaTeX CV variants (moderncv template, banking style)
- `cover_letters/` - LaTeX cover letters (custom cover.cls template)
- `.claude/skills/` - AI skill definitions for the application workflow
- `.agents/skills/` - Job search CLI tools

## Workflow for New Job Applications
1. User provides a job posting (URL or text)
2. **Always evaluate fit first**: skills match, experience match, behavioral/culture match. Present this assessment to the user before proceeding.
3. If good fit: create targeted CV (`cv/main_<company>_<role>.tex`) and cover letter (`cover_letters/cover_<company>_<role>.tex`)
4. **Verify both documents** (see Verification Checklist below)
