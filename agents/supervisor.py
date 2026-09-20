from agents.research_agent import research_agent


def supervisor_agent(
    query: str,
    image_path: str = None,
    source: str = None
) -> str:

    # IMAGE REQUEST
    if image_path:
        from agents.vision_agent import vision_agent

        return vision_agent(
            image_path=image_path,
            query=query
        )

    # PDF REQUEST
    if source:

        query_lower = query.lower()

        report_words = [
            "report",
            "detailed report",
            "analysis",
            "analyze",
            "summarize",
            "summary"
        ]

        if any(word in query_lower for word in report_words):

            from agents.report_agent import report_agent

            return report_agent(
                query=query,
                source=source
            )

        from agents.document_agent import document_agent

        return document_agent(
            query=query,
            source=source
        )

    # NORMAL QUESTION
    return research_agent(query)