# Contribute or review

Anyone with a GitHub account can propose a contribution to this public repository through a fork and pull request. You do not need the owner's credentials or a 99 Tokens account. Research and reviewing existing pull requests are both useful; choose work that fits your access and available time.

Read [the project brief](99TOKENS.md), [the source register](research/SOURCES.md), existing issues, and open pull requests before choosing work. Check for overlapping contributions and build on existing evidence.

## Account for local agents

All agents and subagents working on this project for this user must authenticate as `tobrien6` for GitHub submissions, pushes, issues, comments, and reviews. Verify the selected identity with `gh api user --jq .login` before acting. Pass this requirement to delegated agents and separate checkouts.

When the user explicitly requests cleanup of earlier `tim-repligen` activity, preserve and resubmit those contributions as `tobrien6` before removing authorized originals wherever GitHub supports deletion. Close superseded PRs and report records that remain. A merged contribution is already part of the repository; a follow-up PR can update its guidance, but it cannot change the original PR author. Submitted reviews cannot be deleted. If cleanup requires a former account's credentials, obtain explicit authorization for that account and the specific item before using them. Keep `tobrien6` selected for normal work.

## Establish your role

Verify your user-authorized GitHub identity, the upstream repository owner, current permissions, and assigned scope. Record **owner/maintainer**, **contributor**, or **unverified**, with the evidence. An owner/maintainer acts for the project owner or an explicitly assigned maintainer with the permissions needed for the action. Write access alone, a fork, or a verified directory listing does not establish this role. If unclear, continue contribution work while resolving it.

An owned project assigned to an agent includes routine PR management within the user's scope: merge validated work, adopt selected changes, request changes, or reject and close with reasons. These decisions need no repeated permission when already covered by the assignment. Contributors propose changes and leave merge and closure decisions to the assigned owner/maintainer. All actions must satisfy repository protections and required approvals.

For partial adoption, use a dedicated branch and linked follow-up PR, preserve attribution and dependencies, and identify included and omitted changes. Validate the combined result and verify the replacement before closing the original as partially adopted or superseded.

Document every decision in the PR discussion or existing repository decision log: PR link, reviewed commit, role and authority, disposition, included and omitted changes, rationale and evidence, validation and limitations, and resulting PR or merge commit. Inspect the current diff, discussion, reviews, and checks; confirm the head before acting. Preserve the role, scope, pending PRs, and records in handoffs, then recheck identity and permissions.

## Submit research through a pull request

1. Confirm your authenticated GitHub login. Use your own account or the specific identity already authorized by your user; do not switch to the repository owner's credentials to obtain write access.
2. Fork `tobrien6/voynich-manuscript-research` to your GitHub account and clone your fork into a separate directory. Agents running concurrently should each have an isolated checkout or worktree.
3. Add the original repository as `upstream`, fetch its default branch, and create a dedicated branch from `upstream/main`.
4. Make a focused contribution and run the checks relevant to it. Keep source statements, direct observations, interpretations, and uncertainty distinct.
5. Commit and push your branch to your fork. Open a pull request targeting `tobrien6/voynich-manuscript-research:main`. If you already have upstream write access, you may push a topic branch there and open a PR from it.
6. Respond to review feedback. Leave merging to the explicitly authorized maintainer workflow; do not push contributions directly to `main`.

With GitHub CLI, fork and clone using `gh repo fork tobrien6/voynich-manuscript-research --clone`. Check `git remote -v` before pushing: `origin` should be your fork, and `upstream` should be the original repository. Open the PR with `gh pr create --repo tobrien6/voynich-manuscript-research --base main --head YOUR_GITHUB_LOGIN:YOUR_BRANCH`, replacing the placeholders with your own login and branch.

Each PR should state:

- The question and how the work advances the project's research goal.
- Sources, folio identifiers, dataset editions, and preprocessing choices.
- The method, observations or results, and relevant validation.
- Limitations, contradictory evidence, and the next test.

Link to images and transcriptions until reuse rights are established. Keep credentials out of repository files, logs, and PR descriptions. Authentication to 99 Tokens grants no GitHub permissions.

## Review a pull request

If your user has authorized GitHub reviews and your credential supports them, you may choose an open PR that needs review instead of starting new research. Inspect its current diff, description, discussion, previous reviews, and checks. Assess source support, reproducibility, folio and dataset identifiers, uncertainty, and fit with repository conventions. Inspect changed scripts before running them.

Submit actionable comments or request changes when you find substantive problems. Approve when the evidence and validation support the change. Record what you checked and any limits. Confirm that the PR's head commit has not changed before submitting; reassess if it has. Avoid repeating a completed review of the same commit unless new evidence requires it.

GitHub does not allow an account to approve its own PR. Two agents authenticated as the same GitHub user are the same author/reviewer identity. A PR authored by `tobrien6` needs a different independently authorized account for approval; an outside contributor's PR can be reviewed by an authorized agent using `tobrien6`. Reviews that count toward required approvals must satisfy GitHub's repository rules and reviewer permissions.

Review permission alone does not assign owner/maintainer authority. Owners and assigned maintainers follow the documented decision workflow above and satisfy the repository's requirements, including any required independent approval.

