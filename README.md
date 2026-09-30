# CasePayNow Assessment

## Lead Update API

Local Python implementation for the lead status update workflow.

## Run tests

    python test_lead_update.py

## Test scenarios

1. Unauthenticated request
2. Authorized assigned agent
3. Agent accessing another agent's lead
4. Cross-tenant access
5. Manager access within the same tenant
6. Invalid target status
7. Replay using an old version
8. Unknown role and privilege escalation through request fields

## Production concurrency

The production database update should be atomic and use the expected version to prevent concurrent updates.

## Data safety

Only local fake data was used. No production systems, real customer data, credentials, or live third-party services were accessed.
