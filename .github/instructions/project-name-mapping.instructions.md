---
applyTo: "backend/utils/project_mapping.py"
description: "This provides project name to ID mapping, this is needed for frontend to backeng communication."
---

## API Parameter Rules
- Currently, some APIs are using Spaces for query parameter. Instead, it should use the project IDs. We need to create a mapping between the project names and their corresponding IDs, and update the API endpoints to accept project IDs as query parameters. This will ensure consistency and improve the reliability of the API. Refer the instrction file for project name to ID mapping below.

## Project Configuration

All project and space name mappings are configured in a single file: **`config/projects.json`**

### How to Add Your Projects

Edit `config/projects.json`:

```json
{
  "projects": {
    "Your Space Name": "PROJECTKEY",
    "Another Space 2.0": "PROJ2"
  },
  "contributors": {
    "Your Space Name": ["Developer Name 1", "Developer Name 2"],
    "Another Space 2.0": ["Developer Name 3"]
  }
}
```

**That's it!** Both backend and frontend will automatically use these mappings.

### Rules
- **Space Name**: The display name shown in the UI (key in `projects` object)
- **Project Key**: The JIRA project key/ID (value in `projects` object)  
- **Contributors**: Optional - list of assignee names for each space
