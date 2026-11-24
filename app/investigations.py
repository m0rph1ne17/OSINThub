import re
import socket
from urllib.parse import quote_plus

def valid_domain(value):
    value = value.strip().lower().rstrip(".")
    pattern = r"(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(\.([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))+"
    if not re.fullmatch(pattern, value) or "://" in value:
        raise ValueError("Enter a hostname only, such as example.org.")
    return value

def dns_lookup(domain):
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.timeout, resolver.lifetime = 3, 5
        result = {}
        for kind in ("A", "AAAA", "MX", "NS", "TXT"):
            try:
                result[kind] = [str(x) for x in resolver.resolve(domain, kind)][:20]
            except Exception:
                result[kind] = []
        return result
    except ImportError:
        try:
            return {"A": sorted({x[4][0] for x in socket.getaddrinfo(domain, None)}),
                    "note": "Install dnspython for additional record types."}
        except Exception:
            return {"error": "DNS lookup failed or no records were returned."}

def investigate(kind, target):
    target = target.strip()
    if not target:
        raise ValueError("Enter a target.")
    if kind == "username":
        name = target.lstrip("@")
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", name):
            raise ValueError("Username contains unsupported characters.")
        q = quote_plus('"' + name + '"')
        findings = [
            {"label": "Google search", "value": "https://www.google.com/search?q=" + q},
            {"label": "Bing search", "value": "https://www.bing.com/search?q=" + q},
            {"label": "GitHub users", "value": "https://github.com/search?q=" + quote_plus(name) + "&type=users"},
            {"label": "Reddit search", "value": "https://www.reddit.com/search/?q=" + quote_plus(name)}
        ]
        return {"summary": "Prepared public search links. No accounts were accessed or verified.",
                "findings": findings,
                "limitations": ["Results may be incomplete or unrelated.", "A username match does not prove identity."]}
    if kind == "email":
        if len(target) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", target):
            raise ValueError("Enter an email address in a valid basic format.")
        domain = valid_domain(target.rsplit("@", 1)[1])
        return {"summary": "Checked basic syntax and public DNS for the email domain.",
                "findings": [{"label": "Syntax", "value": "Basic format accepted"},
                             {"label": "Domain", "value": domain},
                             {"label": "DNS records", "value": dns_lookup(domain)}],
                "limitations": ["DNS cannot prove a mailbox exists or identify its owner."]}
    if kind == "phone":
        try:
            import phonenumbers
            number = phonenumbers.parse(target, None if target.startswith("+") else "US")
            value = {"E.164": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164),
                     "International": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                     "Possible": phonenumbers.is_possible_number(number),
                     "Valid numbering pattern": phonenumbers.is_valid_number(number),
                     "Region": phonenumbers.region_code_for_number(number)}
            return {"summary": "Parsed public numbering-plan metadata.",
                    "findings": [{"label": "Number metadata", "value": value}],
                    "limitations": ["No subscriber, owner, live-device, or carrier lookup is performed."]}
        except ImportError:
            return {"summary": "Optional phonenumbers package is not installed.",
                    "findings": [{"label": "Input", "value": "Stored as supplied"}],
                    "limitations": ["Install requirements to enable numbering-plan parsing.", "No subscriber lookup is provided."]}
        except Exception:
            raise ValueError("Could not parse the number. Try international format, e.g. +14155550123.")
    if kind == "domain":
        domain = valid_domain(target)
        return {"summary": "Collected basic DNS records and prepared public registration/certificate lookup links.",
                "findings": [{"label": "Hostname", "value": domain},
                             {"label": "DNS records", "value": dns_lookup(domain)},
                             {"label": "RDAP lookup", "value": "https://rdap.org/domain/" + quote_plus(domain)},
                             {"label": "Certificate transparency", "value": "https://crt.sh/?q=%25." + quote_plus(domain)}],
                "limitations": ["RDAP and certificate links open external services; they are not fetched by this MVP.",
                                "Only assess domains you own or are authorized to assess."]}
    raise ValueError("Unsupported investigation type.")
