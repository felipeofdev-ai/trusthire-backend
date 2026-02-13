"""
TrustHire Internationalization (i18n)
Multi-language support system
"""

from typing import Dict, Any

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ENGLISH
    "en": {
        # General
        "app_name": "TrustHire Ultimate",
        "app_tagline": "AI-Powered Job Safety & Resume Optimization",
        "welcome": "Welcome to TrustHire",
        "get_started": "Get Started",
        
        # Navigation
        "nav_home": "Home",
        "nav_features": "Features",
        "nav_pricing": "Pricing",
        "nav_about": "About",
        "nav_login": "Login",
        "nav_signup": "Sign Up",
        "nav_dashboard": "Dashboard",
        "nav_logout": "Logout",
        
        # Features
        "feature_scam_detection": "Scam Detection",
        "feature_scam_detection_desc": "AI-powered analysis to identify fraudulent job offers",
        "feature_resume_optimizer": "Resume Optimizer",
        "feature_resume_optimizer_desc": "Optimize your resume for ATS systems",
        "feature_ats_compatibility": "ATS Compatibility",
        "feature_ats_compatibility_desc": "Check compatibility with major ATS platforms",
        "feature_multilingual": "Multi-language Support",
        "feature_multilingual_desc": "Available in 8+ languages",
        
        # Job Analysis
        "analyze_job": "Analyze Job Offer",
        "job_description": "Job Description",
        "company_name": "Company Name",
        "job_url": "Job URL",
        "analyze_button": "Analyze Now",
        "analyzing": "Analyzing...",
        "results": "Results",
        "risk_score": "Risk Score",
        "risk_low": "Low Risk",
        "risk_medium": "Medium Risk",
        "risk_high": "High Risk",
        "red_flags": "Red Flags",
        "recommendations": "Recommendations",
        
        # Resume Optimization
        "upload_resume": "Upload Resume",
        "paste_resume": "Or Paste Resume Text",
        "target_job": "Target Job Description",
        "select_industry": "Select Industry",
        "select_ats": "Target ATS System",
        "optimize_button": "Optimize Resume",
        "optimizing": "Optimizing...",
        "ats_score": "ATS Score",
        "keyword_match": "Keyword Match",
        "suggestions": "Suggestions",
        "download_report": "Download Report",
        
        # Industries
        "industry_technology": "Technology",
        "industry_marketing": "Marketing",
        "industry_sales": "Sales",
        "industry_finance": "Finance",
        "industry_hr": "Human Resources",
        "industry_healthcare": "Healthcare",
        
        # Pricing
        "pricing_title": "Simple, Transparent Pricing",
        "pricing_free": "Free",
        "pricing_pro": "Pro",
        "pricing_enterprise": "Enterprise",
        "pricing_monthly": "Monthly",
        "pricing_yearly": "Yearly",
        "pricing_save": "Save",
        "pricing_current_plan": "Current Plan",
        "pricing_upgrade": "Upgrade",
        "pricing_per_month": "/month",
        "pricing_per_year": "/year",
        
        # Plans Features
        "plan_free_analyses": "analyses per day",
        "plan_resume_optimizations": "resume optimizations per month",
        "plan_ai_analysis": "AI-powered analysis",
        "plan_ats_check": "ATS compatibility check",
        "plan_basic_support": "Basic support",
        "plan_priority_support": "Priority support",
        "plan_api_access": "API access",
        "plan_team_features": "Team features",
        "plan_dedicated_support": "Dedicated support",
        
        # Errors
        "error_generic": "An error occurred. Please try again.",
        "error_login": "Invalid email or password",
        "error_signup": "Could not create account",
        "error_network": "Network error. Please check your connection.",
        "error_file_size": "File is too large. Maximum size is 5MB.",
        "error_file_type": "Invalid file type. Please upload PDF, DOCX, or TXT.",
        
        # Success
        "success_login": "Login successful!",
        "success_signup": "Account created successfully!",
        "success_analysis": "Analysis completed!",
        "success_optimization": "Resume optimized!",
        "success_save": "Saved successfully!",
        
        # Buttons
        "btn_submit": "Submit",
        "btn_cancel": "Cancel",
        "btn_save": "Save",
        "btn_download": "Download",
        "btn_close": "Close",
        "btn_back": "Back",
        "btn_next": "Next",
        "btn_continue": "Continue",
        
        # Forms
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "name": "Name",
        "company": "Company",
        "forgot_password": "Forgot Password?",
        "remember_me": "Remember Me",
        "terms_agree": "I agree to the Terms of Service",
    },
    
    # PORTUGUESE (BRAZIL)
    "pt-BR": {
        # General
        "app_name": "TrustHire Ultimate",
        "app_tagline": "Segurança em Vagas & Otimização de Currículos com IA",
        "welcome": "Bem-vindo ao TrustHire",
        "get_started": "Começar",
        
        # Navigation
        "nav_home": "Início",
        "nav_features": "Recursos",
        "nav_pricing": "Preços",
        "nav_about": "Sobre",
        "nav_login": "Entrar",
        "nav_signup": "Cadastrar",
        "nav_dashboard": "Painel",
        "nav_logout": "Sair",
        
        # Features
        "feature_scam_detection": "Detecção de Fraudes",
        "feature_scam_detection_desc": "Análise com IA para identificar ofertas fraudulentas",
        "feature_resume_optimizer": "Otimizador de Currículo",
        "feature_resume_optimizer_desc": "Otimize seu currículo para sistemas ATS",
        "feature_ats_compatibility": "Compatibilidade ATS",
        "feature_ats_compatibility_desc": "Verifique compatibilidade com principais plataformas ATS",
        "feature_multilingual": "Suporte Multi-idioma",
        "feature_multilingual_desc": "Disponível em mais de 8 idiomas",
        
        # Job Analysis
        "analyze_job": "Analisar Oferta de Emprego",
        "job_description": "Descrição da Vaga",
        "company_name": "Nome da Empresa",
        "job_url": "URL da Vaga",
        "analyze_button": "Analisar Agora",
        "analyzing": "Analisando...",
        "results": "Resultados",
        "risk_score": "Pontuação de Risco",
        "risk_low": "Risco Baixo",
        "risk_medium": "Risco Médio",
        "risk_high": "Risco Alto",
        "red_flags": "Sinais de Alerta",
        "recommendations": "Recomendações",
        
        # Resume Optimization
        "upload_resume": "Enviar Currículo",
        "paste_resume": "Ou Cole o Texto do Currículo",
        "target_job": "Descrição da Vaga Desejada",
        "select_industry": "Selecionar Área",
        "select_ats": "Sistema ATS Alvo",
        "optimize_button": "Otimizar Currículo",
        "optimizing": "Otimizando...",
        "ats_score": "Pontuação ATS",
        "keyword_match": "Correspondência de Palavras-chave",
        "suggestions": "Sugestões",
        "download_report": "Baixar Relatório",
        
        # Industries
        "industry_technology": "Tecnologia",
        "industry_marketing": "Marketing",
        "industry_sales": "Vendas",
        "industry_finance": "Finanças",
        "industry_hr": "Recursos Humanos",
        "industry_healthcare": "Saúde",
        
        # Pricing
        "pricing_title": "Preços Simples e Transparentes",
        "pricing_free": "Grátis",
        "pricing_pro": "Pro",
        "pricing_enterprise": "Enterprise",
        "pricing_monthly": "Mensal",
        "pricing_yearly": "Anual",
        "pricing_save": "Economize",
        "pricing_current_plan": "Plano Atual",
        "pricing_upgrade": "Fazer Upgrade",
        "pricing_per_month": "/mês",
        "pricing_per_year": "/ano",
        
        # Plans Features
        "plan_free_analyses": "análises por dia",
        "plan_resume_optimizations": "otimizações de currículo por mês",
        "plan_ai_analysis": "Análise com IA",
        "plan_ats_check": "Verificação de compatibilidade ATS",
        "plan_basic_support": "Suporte básico",
        "plan_priority_support": "Suporte prioritário",
        "plan_api_access": "Acesso à API",
        "plan_team_features": "Recursos para equipes",
        "plan_dedicated_support": "Suporte dedicado",
        
        # Errors
        "error_generic": "Ocorreu um erro. Por favor, tente novamente.",
        "error_login": "Email ou senha inválidos",
        "error_signup": "Não foi possível criar a conta",
        "error_network": "Erro de rede. Verifique sua conexão.",
        "error_file_size": "Arquivo muito grande. Tamanho máximo é 5MB.",
        "error_file_type": "Tipo de arquivo inválido. Envie PDF, DOCX ou TXT.",
        
        # Success
        "success_login": "Login realizado com sucesso!",
        "success_signup": "Conta criada com sucesso!",
        "success_analysis": "Análise concluída!",
        "success_optimization": "Currículo otimizado!",
        "success_save": "Salvo com sucesso!",
        
        # Buttons
        "btn_submit": "Enviar",
        "btn_cancel": "Cancelar",
        "btn_save": "Salvar",
        "btn_download": "Baixar",
        "btn_close": "Fechar",
        "btn_back": "Voltar",
        "btn_next": "Próximo",
        "btn_continue": "Continuar",
        
        # Forms
        "email": "Email",
        "password": "Senha",
        "confirm_password": "Confirmar Senha",
        "name": "Nome",
        "company": "Empresa",
        "forgot_password": "Esqueceu a senha?",
        "remember_me": "Lembrar-me",
        "terms_agree": "Concordo com os Termos de Serviço",
    },
    
    # SPANISH
    "es": {
        # General
        "app_name": "TrustHire Ultimate",
        "app_tagline": "Seguridad Laboral y Optimización de CV con IA",
        "welcome": "Bienvenido a TrustHire",
        "get_started": "Comenzar",
        
        # Navigation
        "nav_home": "Inicio",
        "nav_features": "Características",
        "nav_pricing": "Precios",
        "nav_about": "Acerca de",
        "nav_login": "Iniciar Sesión",
        "nav_signup": "Registrarse",
        "nav_dashboard": "Panel",
        "nav_logout": "Cerrar Sesión",
        
        # Features
        "feature_scam_detection": "Detección de Fraudes",
        "feature_scam_detection_desc": "Análisis con IA para identificar ofertas fraudulentas",
        "feature_resume_optimizer": "Optimizador de CV",
        "feature_resume_optimizer_desc": "Optimiza tu CV para sistemas ATS",
        "feature_ats_compatibility": "Compatibilidad ATS",
        "feature_ats_compatibility_desc": "Verifica compatibilidad con principales plataformas ATS",
        "feature_multilingual": "Soporte Multi-idioma",
        "feature_multilingual_desc": "Disponible en más de 8 idiomas",
        
        # Job Analysis
        "analyze_job": "Analizar Oferta de Trabajo",
        "job_description": "Descripción del Trabajo",
        "company_name": "Nombre de la Empresa",
        "job_url": "URL del Trabajo",
        "analyze_button": "Analizar Ahora",
        "analyzing": "Analizando...",
        "results": "Resultados",
        "risk_score": "Puntuación de Riesgo",
        "risk_low": "Riesgo Bajo",
        "risk_medium": "Riesgo Medio",
        "risk_high": "Riesgo Alto",
        "red_flags": "Señales de Alerta",
        "recommendations": "Recomendaciones",
        
        # Resume Optimization
        "upload_resume": "Subir CV",
        "paste_resume": "O Pegar Texto del CV",
        "target_job": "Descripción del Trabajo Objetivo",
        "select_industry": "Seleccionar Industria",
        "select_ats": "Sistema ATS Objetivo",
        "optimize_button": "Optimizar CV",
        "optimizing": "Optimizando...",
        "ats_score": "Puntuación ATS",
        "keyword_match": "Coincidencia de Palabras Clave",
        "suggestions": "Sugerencias",
        "download_report": "Descargar Informe",
        
        # Industries
        "industry_technology": "Tecnología",
        "industry_marketing": "Marketing",
        "industry_sales": "Ventas",
        "industry_finance": "Finanzas",
        "industry_hr": "Recursos Humanos",
        "industry_healthcare": "Salud",
        
        # Pricing
        "pricing_title": "Precios Simples y Transparentes",
        "pricing_free": "Gratis",
        "pricing_pro": "Pro",
        "pricing_enterprise": "Enterprise",
        "pricing_monthly": "Mensual",
        "pricing_yearly": "Anual",
        "pricing_save": "Ahorra",
        "pricing_current_plan": "Plan Actual",
        "pricing_upgrade": "Actualizar",
        "pricing_per_month": "/mes",
        "pricing_per_year": "/año",
        
        # Plans Features
        "plan_free_analyses": "análisis por día",
        "plan_resume_optimizations": "optimizaciones de CV por mes",
        "plan_ai_analysis": "Análisis con IA",
        "plan_ats_check": "Verificación de compatibilidad ATS",
        "plan_basic_support": "Soporte básico",
        "plan_priority_support": "Soporte prioritario",
        "plan_api_access": "Acceso a API",
        "plan_team_features": "Características para equipos",
        "plan_dedicated_support": "Soporte dedicado",
        
        # Errors
        "error_generic": "Ocurrió un error. Por favor, inténtalo de nuevo.",
        "error_login": "Email o contraseña inválidos",
        "error_signup": "No se pudo crear la cuenta",
        "error_network": "Error de red. Verifica tu conexión.",
        "error_file_size": "Archivo demasiado grande. Tamaño máximo es 5MB.",
        "error_file_type": "Tipo de archivo inválido. Sube PDF, DOCX o TXT.",
        
        # Success
        "success_login": "¡Inicio de sesión exitoso!",
        "success_signup": "¡Cuenta creada exitosamente!",
        "success_analysis": "¡Análisis completado!",
        "success_optimization": "¡CV optimizado!",
        "success_save": "¡Guardado exitosamente!",
        
        # Buttons
        "btn_submit": "Enviar",
        "btn_cancel": "Cancelar",
        "btn_save": "Guardar",
        "btn_download": "Descargar",
        "btn_close": "Cerrar",
        "btn_back": "Atrás",
        "btn_next": "Siguiente",
        "btn_continue": "Continuar",
        
        # Forms
        "email": "Email",
        "password": "Contraseña",
        "confirm_password": "Confirmar Contraseña",
        "name": "Nombre",
        "company": "Empresa",
        "forgot_password": "¿Olvidaste tu contraseña?",
        "remember_me": "Recuérdame",
        "terms_agree": "Acepto los Términos de Servicio",
    },
}


class I18n:
    """Internationalization helper"""
    
    def __init__(self, language: str = "en"):
        self.language = language if language in TRANSLATIONS else "en"
    
    def t(self, key: str, **kwargs) -> str:
        """Translate a key"""
        translation = TRANSLATIONS.get(self.language, {}).get(key, key)
        
        # Simple template replacement
        if kwargs:
            for k, v in kwargs.items():
                translation = translation.replace(f"{{{k}}}", str(v))
        
        return translation
    
    def set_language(self, language: str):
        """Change language"""
        if language in TRANSLATIONS:
            self.language = language
    
    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return list(TRANSLATIONS.keys())


def get_translator(language: str = "en") -> I18n:
    """Get a translator instance"""
    return I18n(language)
