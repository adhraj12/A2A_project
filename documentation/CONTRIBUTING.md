# Contributing to Protocol Zero

This guide explains how to contribute to Protocol Zero. We welcome contributions from everyone!

---

## How to Contribute (Step by Step)

### Step 1: Fork the Repository

1. Go to the main repository: https://github.com/adhraj12/A2A_project

2. In the top-right corner of the page, click the **Fork** button

3. GitHub will ask you where to create the fork. Select your own account.

4. Wait a few seconds. GitHub will create a copy of the repository under your account. You'll be redirected to `github.com/YOUR_USERNAME/A2A_project`

You now have your own copy of the project that you can modify freely.

---

### Step 2: Clone Your Fork to Your Computer

Open a terminal and run:

```
git clone https://github.com/YOUR_USERNAME/A2A_project.git
```

Replace `YOUR_USERNAME` with your actual GitHub username.

Then navigate into the folder:

```
cd A2A_project
```

---

### Step 3: Set Up the Upstream Remote

This connects your local copy to the original repository so you can pull updates later.

```
git remote add upstream https://github.com/adhraj12/A2A_project.git
```

Verify your remotes are set up correctly:

```
git remote -v
```

You should see:
```
origin    https://github.com/YOUR_USERNAME/A2A_project.git (fetch)
origin    https://github.com/YOUR_USERNAME/A2A_project.git (push)
upstream  https://github.com/adhraj12/A2A_project.git (fetch)
upstream  https://github.com/adhraj12/A2A_project.git (push)
```

---

### Step 4: Create a New Branch for Your Changes

Never work directly on the `main` branch. Always create a new branch for your feature or fix.

```
git checkout -b feature/your-feature-name
```

Examples of good branch names:
- `feature/add-grocery-agent`
- `fix/order-validation-bug`
- `docs/update-readme`
- `refactor/clean-up-tools`

---

### Step 5: Make Your Changes

Now you can edit files, add new features, fix bugs, etc.

Refer to `SETUP_GUIDE.md` to run the project locally and test your changes.

---

### Step 6: Test Your Changes

Before committing, make sure everything still works:

1. Start all services (see SETUP_GUIDE.md)
2. Run a test query to verify the system works
3. Check that your specific changes work as expected

---

### Step 7: Commit Your Changes

First, see what files you changed:

```
git status
```

Add the files you want to commit:

```
git add .
```

Or add specific files:

```
git add buyer_agent/tools.py
git add documentation/NEW_FILE.md
```

Now commit with a descriptive message:

```
git commit -m "Add grocery store agent template"
```

Good commit message examples:
- "Fix stock not decrementing after order"
- "Add delivery time estimation to seller response"
- "Update documentation with troubleshooting section"

Bad commit message examples:
- "fix"
- "updated stuff"
- "changes"

---

### Step 8: Push Your Branch to Your Fork

```
git push origin feature/your-feature-name
```

If this is your first push to this branch, Git will show you the URL to create a pull request.

---

### Step 9: Create a Pull Request

1. Go to your fork on GitHub: `https://github.com/YOUR_USERNAME/A2A_project`

2. You should see a yellow banner saying "your-branch-name had recent pushes" with a **Compare & pull request** button. Click it.

   If you don't see this banner, click on **Pull requests** tab, then **New pull request**.

3. Make sure the base repository is `adhraj12/A2A_project` and the base branch is `main`

4. Make sure the head repository is `YOUR_USERNAME/A2A_project` and the compare branch is your feature branch

5. Fill in the pull request details:

   **Title:** A clear, short description of what you did
   
   **Description:** Explain:
   - What does this PR do?
   - Why is this change needed?
   - How did you test it?
   - Any special notes for reviewers?

6. Click **Create pull request**

---

### Step 10: Wait for Review

A maintainer will review your pull request. They may:

- **Approve and merge** - Your changes are accepted!
- **Request changes** - They'll leave comments explaining what needs to be fixed
- **Ask questions** - They may need clarification about your changes

If changes are requested, make the fixes locally, commit, and push again:

```
git add .
git commit -m "Address review feedback: fix X"
git push origin feature/your-feature-name
```

The pull request will automatically update with your new commits.

---

## Keeping Your Fork Updated

Over time, the main repository will get new commits. To keep your fork updated:

### Fetch the latest changes from upstream

```
git fetch upstream
```

### Switch to your main branch

```
git checkout main
```

### Merge the upstream changes

```
git merge upstream/main
```

### Push the updates to your fork

```
git push origin main
```

Now your fork is up to date with the main repository.

---

## Code Style Guidelines

When contributing code, please follow these guidelines:

**Python (buyer_agent, seller_agent):**
- Use 4 spaces for indentation (not tabs)
- Add docstrings to functions
- Use type hints where possible
- Keep functions focused and small

**TypeScript/JavaScript (marketplace):**
- Use 2 spaces for indentation
- Use meaningful variable names
- Add comments for complex logic

**Documentation:**
- Write in clear, simple English
- Include examples where helpful
- Keep explanations concise

---

## What to Contribute

Here are some ideas if you want to help but don't know where to start:

**Easy (Good for first-timers):**
- Fix typos in documentation
- Improve error messages
- Add more comments to code

**Medium:**
- Add a new seller agent template (grocery, hardware, clothing)
- Improve the marketplace search functionality
- Add input validation

**Advanced:**
- Add authentication to the marketplace API
- Implement Vector Search for semantic agent discovery
- Add WebSocket support for real-time updates

---

## Questions?

If you have questions about contributing, open an issue on the repository or reach out to the maintainers.

Thank you for contributing to Protocol Zero!
