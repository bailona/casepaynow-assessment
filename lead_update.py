def update_lead(auth, body, leads):
    if auth is None:
        return {"status": 401, "error": "Authentication required"}

    if auth.get("role") not in {"agent", "manager"}:
        return {"status": 403, "error": "Forbidden"}

    if not isinstance(body, dict):
        return {"status": 422, "error": "Invalid request body"}

    required_fields = {"id", "status", "version"}

    if not required_fields.issubset(body):
        return {"status": 422, "error": "Missing required field"}

    lead_id = body["id"]
    status = body["status"]
    version = body["version"]

    if (
        isinstance(lead_id, bool)
        or not isinstance(lead_id, int)
        or lead_id <= 0
    ):
        return {"status": 422, "error": "Invalid id"}

    if (
        isinstance(version, bool)
        or not isinstance(version, int)
        or version <= 0
    ):
        return {"status": 422, "error": "Invalid version"}

    if status not in {"sent_to_funder", "cannot_fund"}:
        return {"status": 422, "error": "Invalid status"}

    unexpected_fields = set(body) - required_fields

    if unexpected_fields:
        return {"status": 422, "error": "Unexpected field"}

    lead = leads.get(lead_id)

    if lead is None:
        return {"status": 404, "error": "Lead not found"}

    if lead["tenant_id"] != auth["tenant_id"]:
        return {"status": 404, "error": "Lead not found"}

    if auth["role"] == "agent":
        if lead["assigned_to"] != auth["user_id"]:
            return {"status": 404, "error": "Lead not found"}

    if version != lead["version"]:
        return {"status": 409, "error": "Version conflict"}

    if lead["status"] != "contact_lawyer":
        return {"status": 422, "error": "Invalid state transition"}

    lead["status"] = status
    lead["version"] += 1

    return {
        "status": 200,
        "data": {
            "id": lead["id"],
            "status": lead["status"],
            "version": lead["version"],
        },
    }
