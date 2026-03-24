# Project Configuration Guide

## Overview

The application uses a single configuration file to map your space names to JIRA project keys.

**File:** `config/projects.json`

## Configuration Format

```json
{
  "projects": {
    "Space Display Name": "PROJECT_KEY"
  },
  "contributors": {
    "Space Display Name": ["Assignee Name 1", "Assignee Name 2"]
  }
}
```

## Fields Explained

### `projects` (Required)

Maps space display names to JIRA project keys.

- **Key** (Space Display Name): The friendly name shown in the UI
  - This appears in dropdowns, filters, and the dashboard
  - Can contain spaces, numbers, special characters
  - Examples: "TSA-SITE", "Voice Policy Engine 2.0", "RCEM 3.0"
  
- **Value** (JIRA Project Key): Your actual JIRA project identifier
  - Must match your JIRA project key exactly
  - Usually uppercase, no spaces
  - Examples: "TSITE", "VPE2", "RCEM3"

### `contributors` (Optional)

Maps space names to lists of team member names.

- **Key**: Must match a space name from the `projects` section
- **Value**: Array of assignee display names
  - These names must match the `assignee` field in JIRA issues exactly
  - Used for filtering and contributor chips in the UI
  - Case-sensitive

## Example Configuration

```json
{
  "projects": {
    "TSA-SITE": "TSITE",
    "Voice Policy Engine 2.0": "VPE2",
    "RCEM 3.0": "RCEM3",
    "AIP Risk Support": "AIPRS",
    "Steering 9.0": "NTR9"
  },
  "contributors": {
    "TSA-SITE": ["John Doe", "Jane Smith"],
    "Voice Policy Engine 2.0": ["Alice Johnson"],
    "RCEM 3.0": ["Bob Williams", "Carol Davis"],
    "AIP Risk Support": ["David Brown"],
    "Steering 9.0": ["Eve Martinez"]
  }
}
```

## How to Find Your JIRA Project Key

1. Log in to your JIRA instance
2. Navigate to any project
3. Look at the URL: `https://your-jira.atlassian.net/projects/PROJKEY/`
4. Or check the project abbreviation in issue IDs like `PROJKEY-123`

## How It Works

### Backend (`backend/utils/project_mapping.py`)
- Loads `config/projects.json` at startup
- Creates bidirectional mapping (name ↔ key)
- Used by JIRA sync endpoints to filter by space

### Frontend (`frontend/src/utils/projectMapping.ts`)
- Imports `config/projects.json` 
- Provides UI dropdowns and filters
- Maps user selections to API parameters

## Best Practices

### ✅ Do:
- Use descriptive space names that match your team's vocabulary
- Keep JIRA keys in ALL CAPS
- Match contributor names exactly as they appear in JIRA
- Commit the config file if project names aren't sensitive
- Create a backup (`.backup`) before anonymizing for public repos

### ❌ Don't:
- Use spaces in JIRA project keys
- Mismatch space names between backend and frontend
- Hardcode project names in other code files
- Forget to restart backend after config changes

## Security Considerations

If your project names or contributor names are sensitive:

1. Keep real data in `config/projects.json.backup` (already in `.gitignore`)
2. Use generic names in `config/projects.json` for commits
3. Or uncomment this line in `.gitignore`:
   ```
   config/projects.json
   ```

## Troubleshooting

### "Space not found" errors
- Check that space name in config matches exactly what you're filtering by
- Space names are case-sensitive

### No issues showing for a space
- Verify JIRA project key is correct
- Check your JIRA credentials have access to that project
- Ensure `.env` has correct JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

### Changes not reflected
- Restart backend server: `Ctrl+C` then `uvicorn main:app --reload --port 8000`
- For frontend: Changes are hot-reloaded automatically

## Adding a New Project

1. Edit `config/projects.json`
2. Add new entry to `projects` section
3. Optionally add to `contributors` section
4. Restart backend server
5. Refresh frontend - new project appears in dropdowns automatically!

**Example:**
```json
{
  "projects": {
    "Existing Project": "EXIST",
    "New Project Name": "NEWPROJ"  // ← Add this
  },
  "contributors": {
    "New Project Name": ["Team Lead", "Developer 1"]  // ← Add this
  }
}
```

## See Also

- [README.md](../README.md) - Full setup guide
- [API_REFERENCE.md](API_REFERENCE.md) - API endpoint documentation
- [DEPLOYMENT.md](DEPLOYMENT_NGINX.md) - Production deployment
