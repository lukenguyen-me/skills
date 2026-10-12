# Sync

Run as `$luke-mode sync` in Codex or `/luke-mode sync` in Cursor Cloud and
Claude Code. Sync updates the skills listed in
[dependencies](../references/dependencies.md), and nothing else. Other skills
from the same sources stay at their installed version; name them in the report
so the user can update them separately. Per-repository configuration belongs to
[setup](setup.md).

## Resolve the target

Read [harness selection](../references/harnesses.md), the matching adapter,
[composition](../references/composition.md), and
[dependencies](../references/dependencies.md). Read applicable project
instructions. Inspect the project's skill roots and `skills-lock.json` to
establish each dependency's agents, locked ref, and provenance. Preserve
unrelated skills, Luke's model profile, repository guidance, and tracker
settings.

Matt's target tag is the one the user names, otherwise the latest release tag:

```sh
git ls-remote --tags --refs --sort=-v:refname https://github.com/mattpocock/skills 'v*' | head -1
```

List the target's skills with
`npx skills@latest add 'mattpocock/skills#<tag>' --list`. Every Matt dependency
must appear there. A renamed or removed dependency stops the Matt refresh until
the dependency list is updated; report it. PStack has no tags, so its target is
the default branch.

## Refresh

Apply the safeguards for [entries the CLI did not make](../references/dependencies.md#entries-the-cli-did-not-make)
before writing. Then run one `add` per source, naming every dependency of that
source, with the target ref and the full agent list. A dependency missing from
the project is installed by the same `add`.

In Cursor Cloud, run sync inside the run's checkout; a laptop installation does
not update a Cloud run.

## Verify and report

Run the dependency checks for every dependency. Read back each refreshed
`SKILL.md` for its name, description, and invocation policy. Distinguish
installed files from skills loaded into an already running session.

Report the source, the old and new refs, the agents, updated skills, other
skills from these sources left at their old ref, preserved customizations, and
any pending conflict or discovery refresh. When the new tag differs from the
tested tag in the dependency list, say so. Claim a complete sync only after
every dependency passes the checks. Network failures and unverified entries
remain pending. Installation alone does not run Matt's user-only setup workflow
or establish repository readiness. When setup is requested too, sync first,
then run [setup](setup.md) against the refreshed installed requirements.
