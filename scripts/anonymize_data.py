"""
Anonymize data/issues.json to remove employee names and customer references.
Creates a backup before modifying.
"""
import json
import re
from pathlib import Path

# Customer names to anonymize
CUSTOMERS = [
    'StarHub', 'Etisalat', 'Telefonica', 'Vodafone', 'T-Mobile', 'TMO',
    'Orange', 'AT&T', 'Verizon', 'Sprint', 'Deutsche Telekom', 'DT',
    'Telenor', 'Telia', 'KPN', 'BT', 'EE', 'O2', 'Three', 'UAE', 'UK',
    'Airtel', 'Jio', 'BSNL', 'MTN', 'STC', 'Mobily', 'Zain', 'Du',
    'SingTel', 'Globe', 'PLDT', 'Telstra', 'Optus', 'Rogers', 'Bell'
]

# Project/Product codenames that might reveal customer info
SENSITIVE_PATTERNS = [
    r'R\d{4}XX-[\w-]+',  # Release patterns like R2603XX-Etisalat-UAE
    r'-[A-Z]{2,5}$',     # Country codes at end
]

def anonymize_issues(input_file: Path, output_file: Path):
    """Anonymize employee names and customer references."""
    
    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        issues = json.load(f)
    
    # Build name mapping
    unique_names = sorted(set(issue['assignee'] for issue in issues))
    name_mapping = {}
    engineer_counter = 1
    
    for name in unique_names:
        if name == 'Unassigned':
            name_mapping[name] = 'Unassigned'
        else:
            name_mapping[name] = f'Engineer {chr(64 + engineer_counter)}'  # A, B, C...
            engineer_counter += 1
            if engineer_counter > 26:  # After Z, use AA, AB, etc.
                engineer_counter = 1
    
    # Build customer mapping
    customer_mapping = {}
    for idx, customer in enumerate(sorted(set(CUSTOMERS)), start=1):
        customer_mapping[customer] = f'Customer{idx}'
    
    # Anonymize each issue
    for issue in issues:
        # Anonymize assignee
        issue['assignee'] = name_mapping.get(issue['assignee'], issue['assignee'])
        
        # Anonymize title
        title = issue['title']
        
        # Replace customer names
        for customer, replacement in customer_mapping.items():
            title = re.sub(rf'\b{customer}\b', replacement, title, flags=re.IGNORECASE)
        
        # Replace sensitive version patterns
        title = re.sub(r'R\d{4}XX-[\w-]+', 'Release-X.X', title)
        title = re.sub(r'-[A-Z]{2,5}(?=\s|$)', '-XX', title)
        
        issue['title'] = title
        
        # Anonymize fix_version
        fix_version = issue['fix_version']
        for customer, replacement in customer_mapping.items():
            fix_version = re.sub(rf'\b{customer}\b', replacement, fix_version, flags=re.IGNORECASE)
        fix_version = re.sub(r'R\d{4}XX-[\w-]+', 'Release-X.X', fix_version)
        fix_version = re.sub(r'-[A-Z]{2,5}(?=\s|$)', '-XX', fix_version)
        issue['fix_version'] = fix_version
    
    # Save anonymized data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Anonymized {len(issues)} issues")
    print(f"   - {len(name_mapping)} assignee names mapped")
    print(f"   - {len(customer_mapping)} customer names replaced")
    print(f"   - Output: {output_file}")

if __name__ == '__main__':
    base_path = Path(__file__).parent.parent
    input_file = base_path / 'data' / 'issues.json'
    backup_file = base_path / 'data' / 'issues.json.backup'
    
    # Create backup
    if not backup_file.exists():
        import shutil
        shutil.copy(input_file, backup_file)
        print(f"📦 Backup created: {backup_file}")
    
    # Anonymize
    anonymize_issues(input_file, input_file)
    print("✅ Done! Original backed up to issues.json.backup")
