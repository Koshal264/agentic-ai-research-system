from agents.research_agent import research_agent


def supervisor_agent(
    query: str,
    image_path: str = None,
    source: str = None,
    is_voice: bool = False
) -> str:

    query_lower = query.lower().strip()


    # =====================================================
    # VOICE AGENT
    # =====================================================

    if is_voice:

        from agents.voice_agent import voice_agent

        return voice_agent(
            query=query
        )


    # =====================================================
    # VISION AGENT
    # =====================================================

    if image_path:

        from agents.vision_agent import vision_agent

        return vision_agent(
            image_path=image_path,
            query=query
        )


    # =====================================================
    # MAINTENANCE AGENT
    # =====================================================

    maintenance_words = [
        "maintenance",
        "maintain",
        "repair",
        "servicing",
        "service",
        "troubleshoot",
        "troubleshooting",
        "fault",
        "equipment problem",
        "equipment issue",
        "machine problem",
        "machine issue",
        "preventive maintenance",
        "corrective maintenance",
        "maintenance schedule",
        "maintenance checklist"
    ]


    if any(
        word in query_lower
        for word in maintenance_words
    ):

        from agents.maintenance_agent import maintenance_agent

        return maintenance_agent(
            query=query
        )


    # =====================================================
    # VOICE KEYWORDS
    # =====================================================

    voice_words = [
        "voice",
        "voice query",
        "voice request",
        "spoken query",
        "speech",
        "audio query"
    ]


    if any(
        word in query_lower
        for word in voice_words
    ):

        from agents.voice_agent import voice_agent

        return voice_agent(
            query=query
        )


    # =====================================================
    # COMPLIANCE AGENT
    # =====================================================

    compliance_words = [
        "compliance",
        "policy compliance",
        "regulatory requirement",
        "regulatory requirements",
        "regulation",
        "audit requirement",
        "audit requirements",
        "privacy compliance",
        "security compliance",
        "data protection",
        "compliance check",
        "compliance gap",
        "compliance checklist"
    ]


    if any(
        word in query_lower
        for word in compliance_words
    ):

        from agents.compliance_agent import compliance_agent

        return compliance_agent(
            query=query,
            source=source
        )


    # =====================================================
    # DATA ANALYTICS AGENT
    # =====================================================

    analytics_words = [
        "data analysis",
        "data analytics",
        "analyze data",
        "analyse data",
        "dataset",
        "csv",
        "xlsx",
        "statistics",
        "statistical analysis",
        "data insights",
        "analyze this data",
        "analyse this data",
        "analyze dataset",
        "analyse dataset"
    ]


    if any(
        word in query_lower
        for word in analytics_words
    ):

        from agents.data_analytics_agent import data_analytics_agent

        return data_analytics_agent(
            query=query,
            file_path=source
        )


    # =====================================================
    # REPORT AGENT
    # =====================================================

    report_words = [
        "report",
        "detailed report",
        "make a report",
        "create a report",
        "analysis",
        "analyze",
        "analyse",
        "summarize",
        "summarise",
        "summary"
    ]


    if source and any(
        word in query_lower
        for word in report_words
    ):

        from agents.report_agent import report_agent

        return report_agent(
            query=query,
            source=source
        )


    # =====================================================
    # DOCUMENT / RAG AGENT
    # =====================================================

    document_words = [
        "pdf",
        "document",
        "uploaded pdf",
        "this pdf",
        "the pdf",
        "uploaded document",
        "this document",
        "the document",
        "according to the pdf",
        "according to this pdf",
        "according to the document",
        "according to this document",
        "in the pdf",
        "in this pdf",
        "from the pdf",
        "from this pdf",
        "in the document",
        "in this document",
        "from the document",
        "from this document",
        "according to the notes",
        "in the notes",
        "from the notes"
    ]


    if source and any(
        word in query_lower
        for word in document_words
    ):

        from agents.document_agent import document_agent

        return document_agent(
            query=query,
            source=source
        )


    # =====================================================
    # DEFAULT → RESEARCH AGENT
    # =====================================================

    return research_agent(
        query
    )


# ==================================================
# PROJECT COMMANDS
# ==================================================

# cd /Users/koshalmehra/New_project
# source venv/bin/activate

# export HF_HUB_OFFLINE=1
# export TRANSFORMERS_OFFLINE=1
# export HF_DATASETS_OFFLINE=1
# export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# python -m worker.main

# uvicorn api.server:app --reload --port 8000
# ollama run gemma3:4b
# 

# python -m http.server 5500