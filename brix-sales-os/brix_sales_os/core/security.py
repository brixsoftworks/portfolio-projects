"""
brix_sales_os/core/security.py
=============================
Security, SSRF validation, and Prompt Injection defenses.
"""

import ipaddress
import re
import urllib.parse
from typing import Tuple

BLOCKED_SUBNETS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.169.254/32"),  # Cloud metadata
    ipaddress.ip_network("::1/128"),
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*prompt",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"output\s+the\s+above\s+instructions",
    r"disregard\s+all\s+prior",
]

def is_safe_external_url(url: str) -> Tuple[bool, str]:
    """
    Validates that a URL does not attempt SSRF against localhost, private IPs, or cloud metadata.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, "Invalid URL scheme; must be http or https"
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in URL"
            
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
            return False, "Forbidden local loopback host"

        try:
            ip = ipaddress.ip_address(hostname)
            for subnet in BLOCKED_SUBNETS:
                if ip in subnet:
                    return False, f"Target IP {ip} is within restricted private/internal subnet"
        except ValueError:
            # Domain name, not a raw IP address
            pass

        return True, "URL is safe"
    except Exception as e:
        return False, f"URL parse error: {str(e)}"

def sanitize_external_text(text: str, max_chars: int = 5000) -> str:
    """
    Sanitizes external scraped content or user input before passing into LLM prompts.
    Defends against prompt injection and bounds token length.
    """
    if not text:
        return ""
    
    # Bound length
    trimmed = text[:max_chars]
    
    # Strip null bytes and control chars
    cleaned = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", trimmed)
    
    # Neutralize injection attempts by flag/escaping
    for pattern in PROMPT_INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "[BLOCKED_INSTRUCTION_REMOVED]", cleaned, flags=re.IGNORECASE)
        
    return cleaned
