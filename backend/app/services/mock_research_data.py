"""Deterministic mock research fixture for offline evaluation and testing.

Clearly labeled provider: MOCK_ADAPTER (Offline Evaluation Mode).
Contains realistic public website snippets and evidence items for the 10 target
Indian SMB SaaS companies as documented in PRD.md and DATABASE.md.
"""

from typing import Any

MOCK_RESEARCH_PAYLOADS: dict[str, dict[str, Any]] = {
    "khatabook.com": {
        "company_name": "Khatabook",
        "hq_location": "Bengaluru, Karnataka, India",
        "employee_range": "250-500",
        "sources": [
            {
                "url": "https://khatabook.com",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "Khatabook helps Indian MSMEs and Kirana store owners record transactions, "
                    "track customer credit, and send automated payment reminders directly via WhatsApp. "
                    "Available as Android APK and web portal."
                ),
            },
            {
                "url": "https://khatabook.com/pricing",
                "page_type": "PRICING",
                "raw_text_snippet": (
                    "Starter Plan: ₹499/month billed annually. Designed for single-counter retail shops. "
                    "Premium Plan: ₹999/month with multi-staff access and automated bank sync."
                ),
            },
            {
                "url": "https://khatabook.com/blog/product-update-2024",
                "page_type": "BLOG",
                "raw_text_snippet": (
                    "September 2024 Product Update: Launched 1-click UPI QR billing and automated GST invoice "
                    "generation for merchants across Tier 2 and Tier 3 Indian towns."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Explicitly targets Indian Kiranas and micro/small retailers.",
                "exact_quote": "Khatabook helps Indian MSMEs and Kirana store owners record transactions",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "INR_PRICING",
                "claim_text": "Transparent software pricing in Indian Rupees (INR).",
                "exact_quote": "Starter Plan: ₹499/month billed annually.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MOBILE_WHATSAPP_ONBOARDING",
                "claim_text": "Supports WhatsApp notification and mobile-first workflow.",
                "exact_quote": "send automated payment reminders directly via WhatsApp.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Cloud-hosted multi-tenant web and mobile software delivery.",
                "exact_quote": "Available as Android APK and web portal.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "TRANSPARENT_TIER_PRICING",
                "claim_text": "Public self-serve pricing tiers available without custom quote.",
                "exact_quote": "Starter Plan: ₹499/month billed annually.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "GROWTH_SIGNAL",
                "rubric_criterion": "RECENT_PRODUCT_UPDATE",
                "claim_text": "Active product release within past 12 months.",
                "exact_quote": "September 2024 Product Update: Launched 1-click UPI QR billing",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 2,
            },
        ],
    },
    "mybillbook.in": {
        "company_name": "myBillBook (FloBiz)",
        "hq_location": "Bengaluru, Karnataka, India",
        "employee_range": "100-250",
        "sources": [
            {
                "url": "https://mybillbook.in",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "myBillBook by FloBiz is India's leading GST billing and accounting app for small businesses, "
                    "wholesalers, and distributors. Create bills on mobile and PC, share via WhatsApp in seconds."
                ),
            },
            {
                "url": "https://mybillbook.in/pricing",
                "page_type": "PRICING",
                "raw_text_snippet": (
                    "Silver Plan: ₹799/year. Gold Plan: ₹1,499/year for multi-device sync and barcode scanning. "
                    "Free 14-day trial without credit card."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Tailored for small businesses, wholesalers, and distributors in India.",
                "exact_quote": "India's leading GST billing and accounting app for small businesses",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "INR_PRICING",
                "claim_text": "Annual subscription pricing published in Indian Rupees.",
                "exact_quote": "Silver Plan: ₹799/year.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MOBILE_WHATSAPP_ONBOARDING",
                "claim_text": "Enables instant invoice delivery through WhatsApp.",
                "exact_quote": "Create bills on mobile and PC, share via WhatsApp in seconds.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Cloud sync across mobile and desktop applications.",
                "exact_quote": "multi-device sync and barcode scanning.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "TRANSPARENT_TIER_PRICING",
                "claim_text": "Low friction self-serve pricing tiers.",
                "exact_quote": "Free 14-day trial without credit card.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
        ],
    },
    "mydukaan.io": {
        "company_name": "Dukaan",
        "hq_location": "Bengaluru, Karnataka, India",
        "employee_range": "50-100",
        "sources": [
            {
                "url": "https://mydukaan.io",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "Dukaan empowers local merchants, direct-to-consumer brands, and retailers in India "
                    "to launch an online ecommerce storefront in 30 seconds."
                ),
            },
            {
                "url": "https://mydukaan.io/pricing",
                "page_type": "PRICING",
                "raw_text_snippet": (
                    "Entrepreneur Plan: ₹699/month. Includes custom domain, payment gateway integration, "
                    "and automated shipping partner tie-ups."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Serves local retail merchants and budding Indian D2C brands.",
                "exact_quote": "Dukaan empowers local merchants, direct-to-consumer brands, and retailers in India",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "INR_PRICING",
                "claim_text": "Local monthly pricing in INR.",
                "exact_quote": "Entrepreneur Plan: ₹699/month.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Hosted cloud ecommerce store platform.",
                "exact_quote": "launch an online ecommerce storefront in 30 seconds.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
        ],
    },
    "vyaparapp.in": {
        "company_name": "Vyapar",
        "hq_location": "Bengaluru, Karnataka, India",
        "employee_range": "100-250",
        "sources": [
            {
                "url": "https://vyaparapp.in",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "Vyapar is a simple business accounting and GST billing software for Indian MSMEs. "
                    "Track inventory, receive payments via UPI, and manage Vyapar on Android or Windows."
                ),
            },
            {
                "url": "https://vyaparapp.in/pricing",
                "page_type": "PRICING",
                "raw_text_snippet": (
                    "Desktop Basic: ₹2,399 for 1 year. Mobile + Desktop Combo: ₹2,999/year. "
                    "Zero hidden charges with full GST filing capability."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Direct focus on Indian micro and small business accounting.",
                "exact_quote": "simple business accounting and GST billing software for Indian MSMEs.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "INR_PRICING",
                "claim_text": "Transparent annual pricing in INR.",
                "exact_quote": "Desktop Basic: ₹2,399 for 1 year.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MOBILE_WHATSAPP_ONBOARDING",
                "claim_text": "Provides UPI payment collection and mobile Android apps.",
                "exact_quote": "receive payments via UPI, and manage Vyapar on Android or Windows.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "TRANSPARENT_TIER_PRICING",
                "claim_text": "Clear self-serve pricing tiers.",
                "exact_quote": "Mobile + Desktop Combo: ₹2,999/year.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
        ],
    },
    "shiprocket.in": {
        "company_name": "Shiprocket",
        "hq_location": "New Delhi / Gurugram, India",
        "employee_range": "500-1000",
        "sources": [
            {
                "url": "https://shiprocket.in",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "Shiprocket is India's leading eCommerce shipping solution aggregator for direct sellers, "
                    "SMBs, and online retailers. Connect with 25+ courier partners with automated tracking."
                ),
            },
            {
                "url": "https://shiprocket.in/pricing",
                "page_type": "PRICING",
                "raw_text_snippet": (
                    "Lite Plan: Free with ₹20/500gm flat courier charges. "
                    "Advanced Plan: ₹1,000/month with discounted shipping rates and automated COD verification."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Focuses on Indian small e-commerce merchants and direct sellers.",
                "exact_quote": "eCommerce shipping solution aggregator for direct sellers, SMBs, and online retailers.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "INR_PRICING",
                "claim_text": "Usage and subscription billing calculated in Indian currency.",
                "exact_quote": "Lite Plan: Free with ₹20/500gm flat courier charges.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Cloud-based API aggregation platform.",
                "exact_quote": "Connect with 25+ courier partners with automated tracking.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
        ],
    },
    "classplus.co": {
        "company_name": "Classplus",
        "hq_location": "Noida, Uttar Pradesh, India",
        "employee_range": "500-1000",
        "sources": [
            {
                "url": "https://classplus.co",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "Classplus empowers individual educators, coaching institutes, and creators across India "
                    "to launch their branded teaching app, sell video courses, and accept student fees via UPI."
                ),
            },
            {
                "url": "https://classplus.co/features",
                "page_type": "PRODUCT",
                "raw_text_snippet": (
                    "White-label mobile app with built-in student attendance, live classes, and WhatsApp attendance alerts."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Tailored for standalone tutors and small coaching centers in India.",
                "exact_quote": "empowers individual educators, coaching institutes, and creators across India",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MOBILE_WHATSAPP_ONBOARDING",
                "claim_text": "Features native mobile app and WhatsApp alerts for student communication.",
                "exact_quote": "White-label mobile app with built-in student attendance, live classes, and WhatsApp attendance alerts.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 1,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "SaaS platform delivering customized apps and cloud hosting.",
                "exact_quote": "launch their branded teaching app, sell video courses, and accept student fees via UPI.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
        ],
    },
    "restroworks.com": {
        "company_name": "Restroworks (POSist)",
        "hq_location": "New Delhi, India",
        "employee_range": "250-500",
        "sources": [
            {
                "url": "https://restroworks.com",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "Restroworks (formerly POSist) provides cloud restaurant POS, inventory management, "
                    "and kitchen display systems for single cafes and multi-chain restaurants in India and globally."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Serves single-location food outlets, cafes, and restaurant operators.",
                "exact_quote": "systems for single cafes and multi-chain restaurants in India",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Cloud-based food service management SaaS.",
                "exact_quote": "provides cloud restaurant POS, inventory management",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
        ],
    },
    "exotel.com": {
        "company_name": "Exotel",
        "hq_location": "Bengaluru, Karnataka, India",
        "employee_range": "500-1000",
        "sources": [
            {
                "url": "https://exotel.com",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": (
                    "Exotel is an emerging market full-stack customer engagement platform providing cloud telephony, "
                    "virtual numbers, IVR, and WhatsApp business API for growing startups and Indian businesses."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MOBILE_WHATSAPP_ONBOARDING",
                "claim_text": "Cloud customer communication via WhatsApp Business API and telephony.",
                "exact_quote": "cloud telephony, virtual numbers, IVR, and WhatsApp business API",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Cloud customer engagement platform.",
                "exact_quote": "emerging market full-stack customer engagement platform providing cloud telephony",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
        ],
    },
    "zoho.com": {
        "company_name": "Zoho",
        "hq_location": "Chennai, Tamil Nadu, India",
        "employee_range": "10000+",
        "sources": [
            {
                "url": "https://zoho.com/books",
                "page_type": "PRODUCT",
                "raw_text_snippet": (
                    "Zoho Books is GST-compliant cloud accounting software crafted specifically for Indian businesses. "
                    "Standard plan starts at ₹749/month with automated invoicing and GST filing."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "MSME_EXPLICIT_FOCUS",
                "claim_text": "Provides localized GST compliance software for Indian businesses.",
                "exact_quote": "GST-compliant cloud accounting software crafted specifically for Indian businesses.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SMB_FOCUS",
                "rubric_criterion": "INR_PRICING",
                "claim_text": "Subscription pricing in INR.",
                "exact_quote": "Standard plan starts at ₹749/month with automated invoicing and GST filing.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Comprehensive cloud software suite.",
                "exact_quote": "Zoho Books is GST-compliant cloud accounting software",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
        ],
    },
    "freshworks.com": {
        "company_name": "Freshworks",
        "hq_location": "Chennai, Tamil Nadu, India",
        "employee_range": "4000-5000",
        "sources": [
            {
                "url": "https://freshworks.com/freshdesk",
                "page_type": "PRODUCT",
                "raw_text_snippet": (
                    "Freshdesk by Freshworks is cloud-hosted customer support software designed for fast-growing companies. "
                    "Includes self-serve knowledge base, ticketing automation, and transparent monthly subscriptions."
                ),
            },
        ],
        "evidence_items": [
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                "claim_text": "Cloud-hosted customer support SaaS with self-serve ticketing.",
                "exact_quote": "Freshdesk by Freshworks is cloud-hosted customer support software designed for fast-growing companies.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
            {
                "category": "SAAS_MODEL",
                "rubric_criterion": "TRANSPARENT_TIER_PRICING",
                "claim_text": "Transparent self-serve monthly subscriptions.",
                "exact_quote": "ticketing automation, and transparent monthly subscriptions.",
                "epistemic_status": "FACT",
                "confidence_score": 1.0,
                "gemini_reasoning": None,
                "source_index": 0,
            },
        ],
    },
}
