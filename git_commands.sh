# Initialize git if not already done
git init

# Remove existing remote if it exists and add the new one
git remote remove origin
git remote add origin https://github.com/Nealjain/Beyoundhunger.git

# First fetch and merge remote changes
git fetch origin
git pull origin main --allow-unrelated-histories

# Add all files to staging
git add .

# Create commit
git commit -m "Initial commit"

# Push to main branch
git push -u origin main
