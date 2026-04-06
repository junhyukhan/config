Create a pull request for the current changes. Follow these steps:

0. Run `git fetch --prune origin` to sync remote tracking refs.
   Then check if the current branch's remote is gone:
   - Run `git branch -vv --list "$(git branch --show-current)"` and look for `: gone]`
   - If the remote is gone, switch to main/master and pull: `git checkout main && git pull`
   - Also clean up the stale local branch: `git branch -d <old-branch>`

1. Run `git status` and `git diff` (staged + unstaged) and `git log --oneline -5` to understand the changes and commit style.

2. If on main/master, create a new branch:
   - If an argument was provided ("$ARGUMENTS"), use it as the branch name
   - Otherwise, generate a descriptive branch name from the changes (e.g., `feat/add-user-auth`, `fix/null-pointer-dashboard`)
   - Run `git checkout -b <branch-name>`

3. Stage all relevant changed files (do NOT stage .env, credentials, or secrets). Use specific file paths, not `git add -A`.

4. Commit with a concise message following conventional commits style. End with:
   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

5. Push the branch: `git push -u origin <branch-name>`

6. Create the PR with `gh pr create`:
   - Title: short, under 70 characters
   - Body: include a ## Summary section with 1-3 bullet points, a ## Test plan section, and the Claude Code footer

Return the PR URL when done.
