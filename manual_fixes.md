# Manual Fixes for Syntax Errors

If you encounter syntax errors with backslashes, follow these steps:

## Fix the Syntax Error in views.py (Line 466)

The error in your views.py file is on line 466:
```
items = MarketplaceItem.objects.filter(status='available')\\
```

The problem is the double backslash at the end of the line. In Python, a single backslash is used for line continuation, but two backslashes is invalid.

### Option 1: Edit the file with a text editor

```bash
# Open the file in nano editor
nano food_donation/views.py
```

Then go to line 466 (you can use Ctrl+_ and then type 466 to jump to line 466 in nano).

Change:
```
items = MarketplaceItem.objects.filter(status='available')\\
```

To:
```
items = MarketplaceItem.objects.filter(status='available')
```

Save the file with Ctrl+O, then press Enter, and exit with Ctrl+X.

### Option 2: Use sed to fix it directly

```bash
# Use sed to replace the incorrect line
sed -i '466s/\\\\$//' food_donation/views.py
```

### Option 3: Run the fix_backslash_syntax.py script

```bash
# Create the script
cat > fix_backslash_syntax.py << 'EOL'
#!/usr/bin/env python3
import os
import re

def fix_file(file_path):
    """Fix specific backslash errors in a file"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Fix backslash at end of line
    new_content = re.sub(r'(.*?)\\\\(\s*\n)', r'\1\2', content)
    
    if new_content != content:
        print(f"Fixing backslash errors in {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# Fix the views.py file
if os.path.exists("food_donation/views.py"):
    fix_file("food_donation/views.py")
    print("Fixed backslash errors in food_donation/views.py")
EOL

# Make it executable and run it
chmod +x fix_backslash_syntax.py
python fix_backslash_syntax.py
```

## After Fixing the Error

Once the syntax error is fixed, try running the commands again:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

This should allow you to continue with the deployment process. 