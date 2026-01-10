"""
AI Prompt Templates for Tender Analysis

This file contains all prompts used by the AI system. You can customize
these prompts to change how AI processes tenders without modifying code.

Prompts are organized by function:
- SUMMARIZATION_PROMPTS: For generating tender summaries
- EXTRACTION_PROMPTS: For extracting structured information
- SYSTEM_PROMPTS: System messages that guide AI behavior
"""

# ============================================================================
# SUMMARIZATION PROMPTS
# ============================================================================

TENDER_SUMMARY_SYSTEM_MESSAGE = """You are an expert at analyzing and summarizing tender documents for procurement professionals.
Provide clear, concise, actionable summaries that help businesses understand what they need to do to bid.
Format your summary with clear paragraphs separating different aspects."""

TENDER_SUMMARY_USER_PROMPT = """Analyze the following tender document and provide a professional summary in 4 paragraphs.

CRITICAL INSTRUCTIONS (Must follow):
1. PARAGRAPH 1 - ORGANIZATION & SCOPE: Start with the organization name clearly stated. Be SPECIFIC about what is being procured (not generic). Include location if mentioned.
   DO NOT use generic phrases like "procurement process" or "qualified bidders".
   DO INCLUDE actual item names, quantities, project types (construction, supply, services, etc).

2. PARAGRAPH 2 - REQUIREMENTS: List specific bidder requirements clearly (licenses, certifications, experience). Use bullet-style formatting with semicolons between items.
   DO NOT say "bidders must meet eligibility requirements" - instead list what those requirements ARE.
   DO INCLUDE: Trade licenses, tax clearance, VAT registration, TIN, experience requirements, financial qualifications.

3. PARAGRAPH 3 - DOCUMENT ACCESS: Explain clearly how to get tender documents (online, in-person, website, office).
   DO INCLUDE: Specific website URLs if available, office addresses, document fees (if any), office hours.
   DO NOT be vague - provide specific locations and methods.

4. PARAGRAPH 4 - DEADLINES & CONTACT: Provide specific deadlines for bid submission, opening date/time, and contact information.
   DO INCLUDE: Actual phone numbers, email addresses, department names, office locations, specific times not just "deadline".
   DO NOT say "contact the issuing organization" - provide actual contact details.

ADDITIONAL RULES:
- Use actual numbers, amounts, and values found in the document (not placeholders like "Amount" or "Fee")
- Be specific about deadline dates and times
- Extract actual organization/department names, not generic "organization"
- If information is not available, say so briefly instead of using generic template text
- Keep summary professional but informative

Keep the summary under {max_words} words while maintaining all 4 paragraphs with specific information.

Tender Document:
{text}

Summary:"""

QUICK_SCAN_SYSTEM_MESSAGE = """You provide quick, actionable insights for business opportunities in one sentence."""

QUICK_SCAN_USER_PROMPT = """Provide a single-sentence quick insight about this tender opportunity in {max_words} words or less.

Title: {title}
Description: {description}

Quick Insight:"""

# ============================================================================
# DETAILED EXTRACTION PROMPTS
# ============================================================================

TENDER_DETAILS_SYSTEM_MESSAGE = """You are an expert at extracting and organizing tender information.
Return only factual information found in the document.
Format your response clearly with section headers and bullet points.
CRITICAL: Do NOT include budget, cost estimates, bid amounts, or any pricing/financial information.
Extract only operational and procedural details that help bidders understand what they need to do.
Be specific and concise - extract actual details, not generic statements."""

TENDER_DETAILS_USER_PROMPT = """Analyze this tender document and extract the following information.
Return ONLY the information that is explicitly mentioned in the document.

IMPORTANT: Completely exclude budget, total project cost, estimated price, or any financial amount representing the contract value.
Bid security amounts and financial requirements for qualification are OK to include (they help bidders understand what they need).

Extract and format each section with a clear header and bullet points:

SCOPE OF WORK
- What is being procured or requested?
- What are the main deliverables or services?
- What is the expected timeframe or duration?

ISSUER INFORMATION
- Name of the organization issuing the tender
- Brief description of what they do (if mentioned)
- Which department or branch is issuing it?

REGION / LOCATION
- Where is the project or service location?
- Which regions or areas are covered?

QUALIFICATION CRITERIA
- What licenses or certifications are required?
- What experience level or years of operation is needed?
- Are there any specific standards (ISO, professional memberships)?
- What legal requirements or eligibility conditions must be met?
- What documents must bidders submit to prove their qualifications?

BID SECURITY / BOND
- Is bid security required?
- What amount or type is required?
- What form should it take (bank guarantee, bond, etc.)?

TERMS OF REFERENCE (TOR)
- How should TOR be obtained? (email, download, in-person, etc.)
- Where should TOR be requested from?
- Is there a cost for TOR?

CONTACT FOR CLARIFICATION
- Contact person name and title (if mentioned)
- Department or office name
- Phone number(s)
- Email address(es)
- Physical address or office location

BID SUBMISSION METHOD
- How should bids be submitted? (email, physical, online portal, etc.)
- What is the submission deadline and time?
- Where should bids be sent?
- Should documents be sealed or in specific format?

SPECIAL REQUIREMENTS
- Any other important procedural requirements
- Language requirements (if specified)
- Any specific forms or templates required
- Any restrictions or special conditions

Tender Document:
{text}

Structured Details:"""

# ============================================================================
# SYSTEM PROMPTS - These guide AI behavior
# ============================================================================

FACTUAL_EXTRACTION_SYSTEM = """You extract factual information only. Do not infer or assume.
Only include information that is explicitly stated in the document.
Format response with clear section headers and bullet points.
Use professional language appropriate for business procurement."""

# ============================================================================
# CONFIGURATION NOTES
# ============================================================================

"""
To customize prompts:

1. Edit the prompt text directly in this file
2. Use placeholders like {text}, {max_words}, {title}, {description}
3. These will be replaced automatically by the system
4. Test changes with actual tenders first

Prompt best practices:
- Be specific about what you want
- Use bullet points for lists
- Mention formatting preferences (paragraphs, bullets, etc.)
- Exclude what you DON'T want explicitly
- Use professional language
- Keep instructions clear and concise
"""
