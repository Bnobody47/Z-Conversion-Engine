from __future__ import annotations


def lookup_company(company_name: str) -> dict:
    """
    Placeholder for Crunchbase ODM lookup logic.
    """
    return {"company_name": company_name, "crunchbase_id": f"cb_{abs(hash(company_name)) % 100000}"}
