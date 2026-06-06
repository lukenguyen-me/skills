---
name: commit-message
description: Generate two conventional commit message options from staged changes and recent commit history.
---

# Generate a new commit message

Check my staged changes only and create a new commit message for it on that, don't add more changes, don't make new commit.

## Steps

Check all the staged changes, don't need to check unstaged changes, stop and alert me if there is:

- Expose of secret key, api key,... all the potential leak of credentials.
- Log inteded for debugging purposes, not for tracking errors.

Check recent commit history to understand the context of the project.

Create two commit message options based on the staged changes and recent commit history, following conventional commit format.

Option 1 should use the existing multi-line format.

Option 2 should be a one-line version that covers all main points shortly.

## Rules

Following conventional commit.

Keep commit message clean, use simple words.

Explain what and why, not how. Don't specify detail on each file, changes,... but group them into same topic.

For option 1, break new line for each topic to improve readability.

For option 2, keep everything on one line while still covering the main points briefly.

DO NOT include any Claude or AI information.

DO NOT execute git commit command, just generate the commit message.
