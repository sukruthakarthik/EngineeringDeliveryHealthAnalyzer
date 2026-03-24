---
applyTo: "backend/utils/project_mapping.py"
description: "This provides project name to ID mapping, this is needed for frontend to backeng communication."
---

## API Parameter Rules
- Currently, some APIs are using Spaces for query parameter. Instead, it should use the project IDs. We need to create a mapping between the project names and their corresponding IDs, and update the API endpoints to accept project IDs as query parameters. This will ensure consistency and improve the reliability of the API. Refer the instrction file for project name to ID mapping below.

### Project Name to ID Mapping
Create a mapping in `backend/utils/project_mapping.py`:
```python   
PROJECT_NAME_TO_ID = {
    "TSA-SITE": "TSITE",
    "Voice Policy Engine 2.0": "VPE2",
    "RCEM 3.1": "RCEM31",
    "RCEM 3.0": "RCEM3",
    "Steering 9.0": "NTR9"
}
```

### Project Contributors
Each project has a defined set of contributor display names (must match the `assignee` field in JIRA issues).
Only these names should be shown in the landing page contributor chips.

```python
PROJECT_CONTRIBUTORS = {
    "TSA-SITE": ["Sukrutha Karthik"],
    "Voice Policy Engine 2.0": ["Roja Rameti"],
    "RCEM 3.0": ["Sumit Kumar"],
    "AIPRS": ["Bruno Alves Ferraz"],
    "Steering 9.0": ["Chandramouli B"],
}
```

In `frontend/src/utils/projectMapping.ts` mirror this as `PROJECT_CONTRIBUTORS`:
```typescript
export const PROJECT_CONTRIBUTORS: Record<string, string[]> = {
  'TSA-SITE': ['Sukrutha Karthik'],
  'Voice Policy Engine 2.0': ['Roja Rameti'],
  'RCEM 3.0': ['Sumit Kumar'],
  'AIPRS': ['Bruno Ferraz'],
  'Steering 9.0': ['Chandramouli B'],
}
```
