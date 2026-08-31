from app.sources.website import WebsiteProvider


def test_structural_extraction_preserves_tabbed_business_content():
    html = """
    <html>
        <head>
            <title>AI Solutions</title>
        </head>

        <body>
            <nav>
                Home
                Services
                Contact
            </nav>

            <section>
                <h5>Key Focus Areas</h5>

                <div class="tabs">
                    <div class="tab-pane">
                        <div class="tab-info">
                            <h2>
                                Predictive Analytics & Machine Learning
                            </h2>

                            <p>
                                Turn your data into a strategic advantage.
                            </p>

                            <ul>
                                <li>
                                    Predictive Modelling & Forecasting
                                </li>
                                <li>
                                    Risk Scoring & Anomaly Detection
                                </li>
                            </ul>
                        </div>
                    </div>

                    <div class="tab-pane">
                        <div class="tab-info">
                            <h2>
                                Generative AI
                            </h2>

                            <p>
                                We build Generative AI solutions.
                            </p>

                            <ul>
                                <li>
                                    RAG (Retrieval Augmented Generation)
                                </li>
                                <li>
                                    Chatbots & Conversational AI
                                </li>
                                <li>
                                    Agentic AI
                                </li>
                            </ul>
                        </div>
                    </div>

                    <div class="tab-pane">
                        <div class="tab-info">
                            <h2>
                                Business Intelligence Dashboards
                            </h2>

                            <ul>
                                <li>
                                    BI Dashboard Design
                                </li>
                                <li>
                                    Executive Analytics Portals
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            <footer>
                Copyright Example Company
            </footer>
        </body>
    </html>
    """

    provider = WebsiteProvider()

    text = provider._extract_structural_content(
        html
    )

    assert (
        "Predictive Analytics & Machine Learning"
        in text
    )

    assert (
        "Generative AI"
        in text
    )

    assert (
        "RAG (Retrieval Augmented Generation)"
        in text
    )

    assert (
        "Agentic AI"
        in text
    )

    assert (
        "Business Intelligence Dashboards"
        in text
    )

    assert (
        "Copyright Example Company"
        not in text
    )


def test_structural_extraction_removes_navigation():
    html = """
    <html>
        <body>
            <nav>
                Home Services About Contact
            </nav>

            <main>
                <h1>AI Solutions</h1>
                <p>
                    Enterprise artificial intelligence services.
                </p>
            </main>
        </body>
    </html>
    """

    provider = WebsiteProvider()

    text = provider._extract_structural_content(
        html
    )

    assert "AI Solutions" in text

    assert (
        "Enterprise artificial intelligence services."
        in text
    )

    assert (
        "Home Services About Contact"
        not in text
    )


def test_merge_does_not_duplicate_existing_content():
    provider = WebsiteProvider()

    primary = """
    ## Generative AI

    We build Generative AI solutions.

    RAG (Retrieval Augmented Generation)
    """

    supplemental = """
    ## Generative AI

    We build Generative AI solutions.

    - RAG (Retrieval Augmented Generation)

    - Agentic AI
    """

    result = provider._merge_extractions(
        primary=primary,
        supplemental=supplemental,
    )

    assert (
        result.casefold().count(
            "generative ai solutions"
        )
        == 1
    )

    assert (
        result.casefold().count(
            "rag (retrieval augmented generation)"
        )
        == 1
    )

    assert (
        result.casefold().count(
            "agentic ai"
        )
        == 1
    )


def test_hybrid_extraction_preserves_structural_content():
    html = """
    <html>
        <body>
            <main>
                <h1>AI & Data Science</h1>

                <p>
                    We build machine learning solutions.
                </p>

                <section>
                    <div class="tab-pane">
                        <h2>Generative AI</h2>

                        <ul>
                            <li>
                                RAG (Retrieval Augmented Generation)
                            </li>

                            <li>
                                Agentic AI
                            </li>
                        </ul>
                    </div>
                </section>
            </main>
        </body>
    </html>
    """

    provider = WebsiteProvider()

    text, strategy = provider._extract_content(
        html_document=html,
        url="https://example.com/ai",
    )

    assert "Generative AI" in text

    assert (
        "RAG (Retrieval Augmented Generation)"
        in text
    )

    assert "Agentic AI" in text

    assert strategy in {
        "trafilatura+structural-html-v1",
        "structural-html-v1",
    }