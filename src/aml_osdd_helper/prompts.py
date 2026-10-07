SINGLE_SOURCE_Distillation_PROMPT = """
You are a senior AML compliance investigator evaluating open-source data for: "{entity}".
Source URL: {url}
Category: {category}

Content:
{content}

Extract relevant AML/OSDD information strictly matching this format instructions:
{format_instructions}
"""

FINAL_ANALYST_PROMPT = """You are a Principal AML Compliance Officer and Forensic Due Diligence Specialist.
Synthesize the structured evidence below to generate an exhaustive Open Source Due Diligence (OSDD) report for:
Entity Target: "{entity}"
Provided Address Reference: "{address}"

Retrieved Source Evidence Dossier:
{dossier}

Discovered Candidate Addresses: {candidate_addresses}
Discovered Related Entities: {candidate_relations}
Verified Source URLs: {all_urls}
Negative News Sources: {neg_urls}

Requirements:
1. Retain and evaluate every single risk indicator, adverse finding, and relationship present in the dossier.
2. Ensure all relevant retrieved URLs from the dossier are preserved in `sources` or `negative_news_sources`.
3. Provide realistic risk scoring (0-100), risk levels, and confidence estimations based strictly on evidence.
4. Strictly follow these schema output instructions:
{format_instructions}
"""