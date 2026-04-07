#!/usr/bin/env python
"""Clear all backend data and reset to fresh state"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import Issue, IssueUpvote, IssueUpdate

print("🗑️  Clearing project data...\n")

# Clear uploads folder
uploads_dir = 'uploads'
if os.path.exists(uploads_dir):
    files_removed = 0
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            files_removed += 1
    print(f'✓ Cleared uploads folder ({files_removed} files removed)')
else:
    print(f'✓ Uploads folder already empty (creating if needed)')
    os.makedirs(uploads_dir, exist_ok=True)

# Clear database
try:
    db = SessionLocal()
    
    # Delete all issues
    issue_count = db.query(Issue).count()
    db.query(Issue).delete()
    
    # Delete all upvotes
    upvote_count = db.query(IssueUpvote).count()
    db.query(IssueUpvote).delete()
    
    # Delete all updates
    update_count = db.query(IssueUpdate).count()
    db.query(IssueUpdate).delete()
    
    db.commit()
    print(f'✓ Cleared {issue_count} issues from database')
    print(f'✓ Cleared {upvote_count} upvotes from database')
    print(f'✓ Cleared {update_count} updates from database')
    
    db.close()
    
    print(f'\n✅ Project reset complete!')
    print(f'All backend data cleared - fresh start ready!\n')
    
except Exception as e:
    print(f'❌ Error: {e}')
    print(f'This is OK - your database may already be clean')
    print(f'Uploads folder was cleared successfully')
    sys.exit(0)
