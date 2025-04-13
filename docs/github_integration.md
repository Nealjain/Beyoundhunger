# GitHub Integration Guide for Beyond Hunger

This guide explains how to set up automated GitHub integration so your Beyond Hunger project is automatically updated on GitHub when you make changes.

## Initial GitHub Setup

1. Create a new repository on GitHub:
   - Go to [GitHub](https://github.com) and sign in
   - Click the "+" icon in the upper right corner and select "New repository"
   - Name your repository (e.g., "beyond-hunger")
   - Choose if you want it to be public or private
   - Do not initialize with README, .gitignore, or license as we already have these files
   - Click "Create repository"

2. Connect your local repository to GitHub:
   ```bash
   git remote add origin https://github.com/yourusername/beyond-hunger.git
   git branch -M main
   git push -u origin main
   ```

## Automatic GitHub Updates

We've provided a script called `auto_git_push.py` that will automatically detect changes in your project and push them to GitHub.

### Setup:

1. Make sure your GitHub credentials are configured:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. Create a Personal Access Token on GitHub:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Click "Generate new token"
   - Give it a name (e.g., "Beyond Hunger Auto Push")
   - Select the "repo" scope
   - Click "Generate token"
   - Copy the token and store it securely

3. Store your credentials (this will avoid repeated password prompts):
   ```bash
   git config --global credential.helper store
   ```
   
   Then perform a git operation that requires authentication (like a push), 
   where you'll enter your GitHub username and personal access token.

### Using the Auto Git Push Script:

Run the script to automatically watch for file changes and push them to GitHub:

```bash
python auto_git_push.py
```

Options:
- `--watch_dir DIRECTORY`: Directory to watch for changes (default: current directory)
- `--interval SECONDS`: Check interval in seconds (default: 60)
- `--message MESSAGE`: Custom commit message (default: "Auto update: {timestamp}")

For example, to check every 30 seconds with a custom message:
```bash
python auto_git_push.py --interval 30 --message "Update: {timestamp}"
```

## Automatic Deployment with GitHub Actions

We've also set up GitHub Actions to automatically deploy your app to PythonAnywhere whenever you push changes to GitHub.

### Setup:

1. Get a PythonAnywhere API token:
   - Go to [PythonAnywhere Account](https://www.pythonanywhere.com/user/yourusername/account/)
   - Go to the "API token" section and create a token

2. Add secrets to your GitHub repository:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add two new repository secrets:
     - `PYTHONANYWHERE_USERNAME`: Your PythonAnywhere username
     - `PYTHONANYWHERE_API_TOKEN`: Your PythonAnywhere API token

Now when you push changes to GitHub (either manually or using the auto_git_push.py script), GitHub Actions will automatically deploy those changes to PythonAnywhere!

## Workflow

With this setup, your workflow becomes very simple:

1. Make changes to your Beyond Hunger project
2. Run `auto_git_push.py` (or let it run in the background)
3. Your changes are automatically:
   - Committed to Git
   - Pushed to GitHub
   - Deployed to PythonAnywhere

This means you can focus on developing your application without worrying about manual deployments! 