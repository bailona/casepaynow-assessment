from copy import deepcopy

from lead_update import update_lead


def make_leads():
    return {
        101: {
            "id": 101,
            "tenant_id": "T-A",
            "assigned_to": "U-A",
            "status": "contact_lawyer",
            "version": 1,
        },
        102: {
            "id": 102,
            "tenant_id": "T-A",
            "assigned_to": "U-B",
            "status": "contact_lawyer",
            "version": 1,
        },
        201: {
            "id": 201,
            "tenant_id": "T-B",
            "assigned_to": "U-X",
            "status": "contact_lawyer",
            "version": 1,
        },
    }


AGENT_UA = {
    "user_id": "U-A",
    "tenant_id": "T-A",
    "role": "agent",
}

MANAGER_TA = {
    "user_id": "U-M",
    "tenant_id": "T-A",
    "role": "manager",
}


def test_1_unauthenticated_update_is_rejected():
    leads = make_leads()
    before = deepcopy(leads)

    response = update_lead(
        None,
        {"id": 101, "status": "sent_to_funder", "version": 1},
        leads,
    )

    assert response["status"] == 401
    assert leads == before


def test_2_assigned_agent_can_update_lead():
    leads = make_leads()

    response = update_lead(
        AGENT_UA,
        {"id": 101, "status": "sent_to_funder", "version": 1},
        leads,
    )

    assert response["status"] == 200
    assert response["data"] == {
        "id": 101,
        "status": "sent_to_funder",
        "version": 2,
    }
    assert leads[101]["status"] == "sent_to_funder"
    assert leads[101]["version"] == 2


def test_3_agent_cannot_update_lead_assigned_to_another_agent():
    leads = make_leads()
    before = deepcopy(leads)

    response = update_lead(
        AGENT_UA,
        {"id": 102, "status": "sent_to_funder", "version": 1},
        leads,
    )

    assert response["status"] == 404
    assert leads == before


def test_4_manager_cannot_update_cross_tenant_lead():
    leads = make_leads()
    before = deepcopy(leads)

    response = update_lead(
        MANAGER_TA,
        {"id": 201, "status": "sent_to_funder", "version": 1},
        leads,
    )

    assert response["status"] == 404
    assert leads == before


def test_5_manager_can_update_lead_in_same_tenant():
    leads = make_leads()

    response = update_lead(
        MANAGER_TA,
        {"id": 102, "status": "cannot_fund", "version": 1},
        leads,
    )

    assert response["status"] == 200
    assert response["data"] == {
        "id": 102,
        "status": "cannot_fund",
        "version": 2,
    }
    assert leads[102]["status"] == "cannot_fund"
    assert leads[102]["version"] == 2


def test_6_unknown_target_status_is_rejected():
    leads = make_leads()
    before = deepcopy(leads)

    response = update_lead(
        AGENT_UA,
        {"id": 101, "status": "approved", "version": 1},
        leads,
    )

    assert response["status"] == 422
    assert leads == before


def test_7_replaying_original_version_does_not_write_twice():
    leads = make_leads()

    first_response = update_lead(
        AGENT_UA,
        {"id": 101, "status": "sent_to_funder", "version": 1},
        leads,
    )

    assert first_response["status"] == 200

    state_after_first_update = deepcopy(leads)

    replay_response = update_lead(
        AGENT_UA,
        {"id": 101, "status": "sent_to_funder", "version": 1},
        leads,
    )

    assert replay_response["status"] == 409
    assert leads == state_after_first_update


def test_8_unknown_role_and_body_fields_cannot_elevate_privileges():
    leads = make_leads()
    before = deepcopy(leads)

    unknown_role = {
        "user_id": "U-X",
        "tenant_id": "T-A",
        "role": "intern",
    }

    response = update_lead(
        unknown_role,
        {"id": 101, "status": "sent_to_funder", "version": 1},
        leads,
    )

    assert response["status"] == 403
    assert leads == before

    response = update_lead(
        AGENT_UA,
        {
            "id": 102,
            "status": "sent_to_funder",
            "version": 1,
            "role": "manager",
            "tenant_id": "T-B",
        },
        leads,
    )

    assert response["status"] == 422
    assert leads == before


def run_tests():
    tests = [
        test_1_unauthenticated_update_is_rejected,
        test_2_assigned_agent_can_update_lead,
        test_3_agent_cannot_update_lead_assigned_to_another_agent,
        test_4_manager_cannot_update_cross_tenant_lead,
        test_5_manager_can_update_lead_in_same_tenant,
        test_6_unknown_target_status_is_rejected,
        test_7_replaying_original_version_does_not_write_twice,
        test_8_unknown_role_and_body_fields_cannot_elevate_privileges,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\n{len(tests)} tests passed.")


if __name__ == "__main__":
    run_tests()
