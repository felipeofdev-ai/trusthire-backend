"""
TrustHire Resume Optimizer
AI-powered resume optimization for ATS systems
"""

from typing import Dict, List, Optional, Any
import re
from datetime import datetime
from config import settings
from utils.logger import get_logger

logger = get_logger("resume_optimizer")


class ATSResumeOptimizer:
    """
    Optimizes resumes for Applicant Tracking Systems (ATS)
    Supports: Workday, Greenhouse, Lever, BambooHR, iCIMS, SmartRecruiters, etc.
    """

    # ATS-friendly keywords by industry
    ATS_KEYWORDS = {
        "technology": [
            "Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes",
            "CI/CD", "Agile", "Scrum", "Git", "API", "Microservices",
            "Machine Learning", "AI", "Data Analysis", "SQL", "NoSQL"
        ],
        "marketing": [
            "SEO", "SEM", "Content Marketing", "Social Media", "Google Analytics",
            "Campaign Management", "Brand Strategy", "Digital Marketing",
            "Email Marketing", "Marketing Automation", "CRM"
        ],
        "sales": [
            "B2B Sales", "Account Management", "Lead Generation", "CRM",
            "Sales Strategy", "Negotiation", "Revenue Growth", "Pipeline Management",
            "Customer Acquisition", "Salesforce"
        ],
        "finance": [
            "Financial Analysis", "Budgeting", "Forecasting", "Excel", "SAP",
            "Financial Modeling", "Accounting", "GAAP", "SOX Compliance",
            "Risk Management", "Audit"
        ],
        "human_resources": [
            "Talent Acquisition", "Recruiting", "HRIS", "Onboarding",
            "Performance Management", "Employee Relations", "Compensation",
            "Benefits Administration", "Workday", "ADP"
        ],
        "healthcare": [
            "Patient Care", "HIPAA", "EMR", "Clinical", "Healthcare Management",
            "Medical Terminology", "CPR", "Licensed", "Certified"
        ]
    }

    # Common ATS parsing issues
    ATS_COMPATIBILITY_RULES = {
        "avoid_headers_footers": "Headers and footers may not be parsed correctly",
        "avoid_tables": "Complex tables can confuse ATS parsers",
        "avoid_images": "Images and logos are not readable by ATS",
        "avoid_special_characters": "Special characters may cause parsing errors",
        "use_standard_fonts": "Use standard fonts (Arial, Calibri, Times New Roman)",
        "use_standard_sections": "Use standard section headings (Experience, Education, Skills)",
        "avoid_columns": "Multi-column layouts can scramble text",
        "save_as_pdf_or_docx": "PDF or DOCX are the most ATS-friendly formats"
    }

    def __init__(self, ai_client=None):
        self.ai_client = ai_client

    async def analyze_resume(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None,
        target_ats: Optional[str] = None,
        industry: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze resume for ATS compatibility and provide optimization suggestions
        """
        
        analysis = {
            "ats_score": 0,
            "compatibility": {},
            "keywords": {},
            "suggestions": [],
            "optimized_sections": {},
            "format_issues": [],
            "missing_sections": [],
            "timestamp": datetime.utcnow().isoformat()
        }

        # 1. Check ATS compatibility
        compatibility_score, issues = self._check_ats_compatibility(resume_text)
        analysis["ats_score"] = compatibility_score
        analysis["format_issues"] = issues

        # 2. Check standard sections
        missing_sections = self._check_standard_sections(resume_text, language)
        analysis["missing_sections"] = missing_sections

        # 3. Keyword analysis
        if job_description:
            keyword_match = self._analyze_keywords(resume_text, job_description, industry)
            analysis["keywords"] = keyword_match

        # 4. AI-powered suggestions (if available)
        if self.ai_client and settings.ANTHROPIC_API_KEY:
            ai_suggestions = await self._get_ai_suggestions(
                resume_text, 
                job_description, 
                target_ats,
                language
            )
            analysis["suggestions"] = ai_suggestions

        # 5. Generate optimized sections
        if job_description:
            optimized = await self._generate_optimized_sections(
                resume_text,
                job_description,
                industry,
                language
            )
            analysis["optimized_sections"] = optimized

        return analysis

    def _check_ats_compatibility(self, resume_text: str) -> tuple[int, List[str]]:
        """
        Check resume for ATS compatibility issues
        Returns: (score out of 100, list of issues)
        """
        score = 100
        issues = []

        # Check for problematic patterns
        if re.search(r'\t', resume_text):
            score -= 10
            issues.append("Contains tab characters - use spaces instead")

        if re.search(r'[^\x00-\x7F]', resume_text):
            # Has special unicode characters
            special_chars = len(re.findall(r'[^\x00-\x7F]', resume_text))
            if special_chars > 10:
                score -= 15
                issues.append(f"Contains {special_chars} special characters - may cause parsing issues")

        # Check length
        word_count = len(resume_text.split())
        if word_count < 200:
            score -= 20
            issues.append("Resume too short - aim for 400-800 words")
        elif word_count > 1200:
            score -= 10
            issues.append("Resume too long - consider condensing to 1-2 pages")

        # Check for contact information
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text))
        has_phone = bool(re.search(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text))
        
        if not has_email:
            score -= 15
            issues.append("Missing email address")
        if not has_phone:
            score -= 10
            issues.append("Missing phone number")

        return max(0, score), issues

    def _check_standard_sections(self, resume_text: str, language: str = "en") -> List[str]:
        """Check for standard resume sections"""
        
        section_patterns = {
            "en": {
                "experience": r'(work\s+experience|professional\s+experience|employment|experience)',
                "education": r'(education|academic|qualifications)',
                "skills": r'(skills|technical\s+skills|competencies|expertise)',
                "summary": r'(summary|objective|profile|about)',
            },
            "pt-BR": {
                "experience": r'(experiência|experiência\s+profissional|histórico\s+profissional)',
                "education": r'(educação|formação|formação\s+acadêmica)',
                "skills": r'(habilidades|competências|conhecimentos)',
                "summary": r'(resumo|objetivo|perfil|sobre)',
            },
            "es": {
                "experience": r'(experiencia|experiencia\s+laboral|historial\s+profesional)',
                "education": r'(educación|formación|formación\s+académica)',
                "skills": r'(habilidades|competencias|conocimientos)',
                "summary": r'(resumen|objetivo|perfil|acerca\s+de)',
            }
        }

        patterns = section_patterns.get(language, section_patterns["en"])
        missing = []

        for section, pattern in patterns.items():
            if not re.search(pattern, resume_text, re.IGNORECASE):
                missing.append(section)

        return missing

    def _analyze_keywords(
        self, 
        resume_text: str, 
        job_description: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze keyword match between resume and job description"""
        
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        
        # Check which keywords are in resume
        resume_lower = resume_text.lower()
        matched_keywords = [kw for kw in job_keywords if kw.lower() in resume_lower]
        
        # Add industry-specific keywords
        if industry and industry in self.ATS_KEYWORDS:
            industry_keywords = self.ATS_KEYWORDS[industry]
            matched_industry = [kw for kw in industry_keywords if kw.lower() in resume_lower]
            missing_industry = [kw for kw in industry_keywords if kw.lower() not in resume_lower]
        else:
            matched_industry = []
            missing_industry = []

        match_rate = len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0

        return {
            "match_rate": round(match_rate, 1),
            "matched_keywords": matched_keywords[:10],  # Top 10
            "missing_keywords": [kw for kw in job_keywords if kw not in matched_keywords][:10],
            "industry_keywords_matched": matched_industry[:10],
            "industry_keywords_missing": missing_industry[:10],
            "total_job_keywords": len(job_keywords),
            "total_matched": len(matched_keywords)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        
        # Common words to ignore
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can'
        }

        # Extract words and phrases
        words = re.findall(r'\b[A-Za-z][A-Za-z+#\.]{2,}\b', text)
        
        # Filter and count
        keywords = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in stop_words and len(word) > 2:
                keywords[word] = keywords.get(word, 0) + 1

        # Sort by frequency
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        
        return [kw[0] for kw in sorted_keywords[:50]]  # Top 50 keywords

    async def _get_ai_suggestions(
        self,
        resume_text: str,
        job_description: Optional[str],
        target_ats: Optional[str],
        language: str
    ) -> List[str]:
        """Get AI-powered optimization suggestions"""
        
        if not self.ai_client:
            return []

        prompts = {
            "en": f"""Analyze this resume for ATS optimization{f' targeting {target_ats}' if target_ats else ''}.

Resume:
{resume_text[:2000]}

{f'Job Description: {job_description[:1000]}' if job_description else ''}

Provide 5-7 specific, actionable suggestions to improve ATS compatibility and match rate.
Focus on: keywords, formatting, section structure, and content optimization.
Be concise and specific.""",
            
            "pt-BR": f"""Analise este currículo para otimização de ATS{f' direcionado para {target_ats}' if target_ats else ''}.

Currículo:
{resume_text[:2000]}

{f'Descrição da vaga: {job_description[:1000]}' if job_description else ''}

Forneça 5-7 sugestões específicas e acionáveis para melhorar a compatibilidade com ATS.
Foco em: palavras-chave, formatação, estrutura de seções e otimização de conteúdo.
Seja conciso e específico.""",
            
            "es": f"""Analiza este currículum para optimización de ATS{f' dirigido a {target_ats}' if target_ats else ''}.

Currículum:
{resume_text[:2000]}

{f'Descripción del trabajo: {job_description[:1000]}' if job_description else ''}

Proporciona 5-7 sugerencias específicas y accionables para mejorar la compatibilidad con ATS.
Enfoque en: palabras clave, formato, estructura de secciones y optimización de contenido.
Sé conciso y específico."""
        }

        prompt = prompts.get(language, prompts["en"])

        try:
            response = await self.ai_client.messages.create(
                model=settings.AI_MODEL,
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestions_text = response.content[0].text
            
            # Parse suggestions (assuming they're in a list format)
            suggestions = [
                line.strip('- •123456789. ') 
                for line in suggestions_text.split('\n') 
                if line.strip() and len(line.strip()) > 20
            ]
            
            return suggestions[:7]
            
        except Exception as e:
            logger.error(f"AI suggestions error: {e}")
            return []

    async def _generate_optimized_sections(
        self,
        resume_text: str,
        job_description: str,
        industry: Optional[str],
        language: str
    ) -> Dict[str, str]:
        """Generate optimized versions of resume sections"""
        
        if not self.ai_client:
            return {}

        prompts = {
            "en": f"""Based on this job description, rewrite the Professional Summary section to be ATS-optimized.

Job Description:
{job_description[:1000]}

Current Resume:
{resume_text[:1500]}

Industry: {industry or 'General'}

Generate a compelling, keyword-rich professional summary (3-4 sentences) that:
1. Matches the job requirements
2. Includes relevant keywords
3. Is ATS-friendly
4. Highlights top qualifications

Return ONLY the summary text, no explanations.""",
            
            "pt-BR": f"""Com base nesta descrição de vaga, reescreva a seção de Resumo Profissional para ser otimizada para ATS.

Descrição da Vaga:
{job_description[:1000]}

Currículo Atual:
{resume_text[:1500]}

Área: {industry or 'Geral'}

Gere um resumo profissional atraente e rico em palavras-chave (3-4 frases) que:
1. Corresponda aos requisitos da vaga
2. Inclua palavras-chave relevantes
3. Seja compatível com ATS
4. Destaque as principais qualificações

Retorne APENAS o texto do resumo, sem explicações."""
        }

        prompt = prompts.get(language, prompts["en"])

        try:
            response = await self.ai_client.messages.create(
                model=settings.AI_MODEL,
                max_tokens=500,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "professional_summary": response.content[0].text.strip()
            }
            
        except Exception as e:
            logger.error(f"Section optimization error: {e}")
            return {}

    def generate_ats_report(self, analysis: Dict[str, Any], language: str = "en") -> str:
        """Generate a human-readable ATS compatibility report"""
        
        translations = {
            "en": {
                "title": "ATS Compatibility Report",
                "score": "ATS Score",
                "format_issues": "Format Issues",
                "missing_sections": "Missing Sections",
                "keyword_match": "Keyword Match Rate",
                "suggestions": "Optimization Suggestions",
                "no_issues": "No issues found",
                "none": "None"
            },
            "pt-BR": {
                "title": "Relatório de Compatibilidade com ATS",
                "score": "Pontuação ATS",
                "format_issues": "Problemas de Formatação",
                "missing_sections": "Seções Ausentes",
                "keyword_match": "Taxa de Correspondência de Palavras-chave",
                "suggestions": "Sugestões de Otimização",
                "no_issues": "Nenhum problema encontrado",
                "none": "Nenhum"
            },
            "es": {
                "title": "Informe de Compatibilidad con ATS",
                "score": "Puntuación ATS",
                "format_issues": "Problemas de Formato",
                "missing_sections": "Secciones Faltantes",
                "keyword_match": "Tasa de Coincidencia de Palabras Clave",
                "suggestions": "Sugerencias de Optimización",
                "no_issues": "No se encontraron problemas",
                "none": "Ninguno"
            }
        }

        t = translations.get(language, translations["en"])

        report = f"""
# {t['title']}

## {t['score']}: {analysis.get('ats_score', 0)}/100

## {t['format_issues']}:
"""
        
        if analysis.get('format_issues'):
            for issue in analysis['format_issues']:
                report += f"- {issue}\n"
        else:
            report += f"{t['no_issues']}\n"

        report += f"\n## {t['missing_sections']}:\n"
        if analysis.get('missing_sections'):
            for section in analysis['missing_sections']:
                report += f"- {section}\n"
        else:
            report += f"{t['none']}\n"

        if analysis.get('keywords', {}).get('match_rate'):
            report += f"\n## {t['keyword_match']}: {analysis['keywords']['match_rate']}%\n"

        if analysis.get('suggestions'):
            report += f"\n## {t['suggestions']}:\n"
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                report += f"{i}. {suggestion}\n"

        return report
