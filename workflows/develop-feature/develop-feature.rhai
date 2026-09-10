let meta = #{
    name: "develop-feature",
    description: "Implement an ordered list of child tickets onto one parent feature branch, strictly one child at a time, and stop at human QA",
    when_to_use: "Develop a parent spec after it has been split into child tickets. /develop-feature, implement this ticket, sequential child tickets, feature branch ready for QA.",
    phases: [
        #{ title: "Discover", detail: "parent spec, ordered children, project verification" },
        #{ title: "Prepare", detail: "parent feature branch from the base branch" },
        #{ title: "Child", detail: "implement, verify, review, integrate — one child at a time" },
        #{ title: "Final", detail: "integration verification and parent-spec review" },
    ],
};

const MAX_VERIFY_RETRIES = 2;
const MAX_REVIEW_ROUNDS = 2;

fn trimmed(s) {
    if type_of(s) == "string" {
        s.trim();
        s
    } else if type_of(s) == "i64" {
        s.to_string()
    } else {
        ""
    }
}

fn as_str(v) {
    if v == () {
        ""
    } else if type_of(v) == "string" {
        trimmed(v)
    } else if type_of(v) == "i64" {
        v.to_string()
    } else if type_of(v) == "bool" {
        if v {
            "true"
        } else {
            "false"
        }
    } else {
        ""
    }
}

fn arg_field(a, key) {
    if a == () {
        ""
    } else if type_of(a) == "string" {
        if key == "ticket" { a } else { "" }
    } else if type_of(a) == "i64" {
        if key == "ticket" { a.to_string() } else { "" }
    } else {
        let v = ();
        if key == "ticket" {
            v = a.ticket;
            if v == () { v = a.parent; }
            if v == () { v = a.query; }
            if v == () { v = a.objective; }
        } else if key == "mode" {
            v = a.mode;
        } else if key == "helper_path" {
            v = a.helper_path;
        }
        as_str(v)
    }
}

fn is_success(s) {
    let t = trimmed(s);
    t == "ok" || t == "pass" || t == "passed" || t == "success"
}

fn is_stop(s) {
    let t = trimmed(s);
    t == "stop" || t == "stopped" || t == "ambiguous" || t == "blocked"
}

fn is_fail(s) {
    let t = trimmed(s);
    t == "fail" || t == "failed" || t == "blocking" || t == "error"
}

fn is_plan_mode(s) {
    s == "plan" || s == "dry-run" || s == "dry_run" || s == "dryrun"
}

fn is_smoke_mode(s) {
    s == "smoke" || s == "SMOKE"
}

fn worker_rules() {
    let s = "You are a worker, not an orchestrator. Do this task yourself. ";
    s += "Do not spawn subagents. Do not start extra implementation or review agents. ";
    s += "Do not merge into main, master, develop, trunk, production, or the repo base branch. ";
    s += "Do not open a pull request. Do not push unless a test cannot run without it. ";
    s += "Do not deploy or release. ";
    s += "If an acceptance criterion needs a product guess, set status to stop and explain. ";
    s
}

fn helper_lookup() {
    let s = "Find the git helper (python3) in this order and use the first file that exists: ";
    s += "1) .grok/lib/develop-feature/git_state.py ";
    s += "2) $HOME/.grok/lib/develop-feature/git_state.py ";
    s += "3) workflows/develop-feature/scripts/git_state.py. ";
    s += "If none exist, run the equivalent git commands yourself, still refusing merges into the base branch. ";
    s
}

fn agent_ok(r) {
    r != () && r.success && r.output != ()
}

fn status_of(r) {
    if !agent_ok(r) {
        "fail"
    } else {
        as_str(r.output.status)
    }
}

fn summary_of(r) {
    if !agent_ok(r) {
        "agent failed or returned no output"
    } else {
        as_str(r.output.summary)
    }
}

fn stop_reason_of(r) {
    if !agent_ok(r) {
        summary_of(r)
    } else {
        let s = as_str(r.output.stop_reason);
        if s == "" { summary_of(r) } else { s }
    }
}

fn is_blocking(r) {
    let st = status_of(r);
    is_fail(st) || st == "blocking"
}

fn is_already_done(s) {
    let t = trimmed(s);
    t == "integrated" || t == "skipped" || t == "done" || t == "closed" || t == "resolved" || t == "completed"
}

fn finish(status, reason, report) {
    log(status + ": " + reason);
    let p = write_scratch_file("report.md", report);
    complete(#{ status: status, reason: reason, path: p, report: report });
}

let work_schema = #{
    "type": "object",
    "required": ["status", "summary"],
    "properties": #{
        "status": #{ "type": "string", "description": "ok, fail, or stop" },
        "summary": #{ "type": "string" },
        "stop_reason": #{ "type": "string" },
        "branch": #{ "type": "string" },
        "sha": #{ "type": "string" },
        "files_changed": #{ "type": "array", "items": #{ "type": "string" } },
    },
};

let verify_schema = #{
    "type": "object",
    "required": ["status", "summary"],
    "properties": #{
        "status": #{ "type": "string", "description": "pass, fail, or stop" },
        "summary": #{ "type": "string" },
        "stop_reason": #{ "type": "string" },
        "failed_commands": #{ "type": "array", "items": #{ "type": "string" } },
    },
};

let review_schema = #{
    "type": "object",
    "required": ["status", "summary", "blocking_count"],
    "properties": #{
        "status": #{ "type": "string", "description": "pass, blocking, or stop" },
        "summary": #{ "type": "string" },
        "stop_reason": #{ "type": "string" },
        "blocking_count": #{ "type": "integer" },
        "blocking_issues": #{
            "type": "array",
            "items": #{
                "type": "object",
                "properties": #{
                    "file": #{ "type": "string" },
                    "issue": #{ "type": "string" },
                },
            },
        },
    },
};

let discovery_schema = #{
    "type": "object",
    "required": ["status", "parent_id", "parent_title", "parent_ref", "base_branch", "parent_branch", "children"],
    "properties": #{
        "status": #{ "type": "string", "description": "ok or stop" },
        "stop_reason": #{ "type": "string" },
        "parent_id": #{ "type": "string" },
        "parent_title": #{ "type": "string" },
        "parent_ref": #{ "type": "string", "description": "issue number, URL, or file path" },
        "base_branch": #{ "type": "string" },
        "parent_branch": #{ "type": "string" },
        "helper_path": #{ "type": "string" },
        "config_notes": #{ "type": "string" },
        "verify_commands": #{ "type": "array", "items": #{ "type": "string" } },
        "integration_verify_commands": #{ "type": "array", "items": #{ "type": "string" } },
        "children": #{
            "type": "array",
            "items": #{
                "type": "object",
                "required": ["id", "title", "ref"],
                "properties": #{
                    "id": #{ "type": "string" },
                    "title": #{ "type": "string" },
                    "ref": #{ "type": "string" },
                    "status": #{ "type": "string" },
                    "blocked_by": #{ "type": "array", "items": #{ "type": "string" } },
                },
            },
        },
    },
};

if args == () {
    pause("verification", "Pass a parent spec ticket. Example: /develop-feature {\"ticket\":\"172\"} or /workflow develop-feature {\"ticket\":\"workflows/develop-feature/examples/parent-spec.md\",\"mode\":\"plan\"}");
}

let ticket = arg_field(args, "ticket");
let mode = arg_field(args, "mode");
if mode == "" { mode = "develop"; }
let helper_override = arg_field(args, "helper_path");

if ticket == "" && !is_smoke_mode(mode) {
    pause("verification", "Pass args.ticket — parent spec issue number, URL, or file path.");
}

// --------------------------------------------------------------------------- smoke
if is_smoke_mode(mode) {
    phase("Discover");
    log("DEVELOP FEATURE: SMOKE-1");
    log("smoke path: two synthetic children, sequential agents, no git, no file edits");
    phase("Prepare");
    let smoke_opts = #{ label: "smoke-prepare", capability_mode: "read-only" };
    let sp = agent("Smoke test. Reply with OK. Do not use tools. Do not edit files.", smoke_opts);
    if sp == () || !sp.success {
        finish("STOPPED", "smoke prepare agent failed", "STOPPED\nsmoke prepare failed\n");
    }
    log("Parent prepared (smoke)");
    phase("Child");
    let smoke_ids = ["SMOKE-1-1", "SMOKE-1-2"];
    let si = 0;
    while si < smoke_ids.len() {
        let sid = smoke_ids[si];
        let n = (si + 1).to_string();
        let total = smoke_ids.len().to_string();
        log("[" + n + "/" + total + "] " + sid);
        let impl = agent("Smoke test child " + sid + " implement. Reply with OK. Do not use tools. Do not edit files.", #{ label: "smoke-impl-" + sid, capability_mode: "read-only" });
        if impl == () || !impl.success { finish("STOPPED", "smoke implement failed for " + sid, "STOPPED\n"); }
        log("  implemented");
        let ver = agent("Smoke test child " + sid + " verify. Reply with OK. Do not use tools.", #{ label: "smoke-verify-" + sid, capability_mode: "read-only" });
        if ver == () || !ver.success { finish("STOPPED", "smoke verify failed for " + sid, "STOPPED\n"); }
        log("  verified");
        let rev = agent("Smoke test child " + sid + " review. Reply with OK. Do not use tools.", #{ label: "smoke-review-" + sid, capability_mode: "read-only" });
        if rev == () || !rev.success { finish("STOPPED", "smoke review failed for " + sid, "STOPPED\n"); }
        log("  reviewed");
        log("  integrated");
        si += 1;
    }
    phase("Final");
    let fin = agent("Smoke test final review. Reply with OK. Do not use tools.", #{ label: "smoke-final", capability_mode: "read-only" });
    if fin == () || !fin.success { finish("STOPPED", "smoke final agent failed", "STOPPED\n"); }
    let report = "";
    report += "READY FOR HUMAN QA\n\n";
    report += "Parent: SMOKE-1\n";
    report += "Branch: (smoke — no git)\n";
    report += "Mode: smoke\n\n";
    report += "Children:\n";
    report += "  SMOKE-1-1\n";
    report += "  SMOKE-1-2\n\n";
    report += "This was a sequential-orchestration smoke test. No product code was changed.\n";
    finish("READY FOR HUMAN QA", "smoke sequential path passed", report);
}

// --------------------------------------------------------------------------- discover
phase("Discover");
log("DEVELOP FEATURE: " + ticket);

let discover_prompt = worker_rules();
discover_prompt += "Discover everything needed to implement parent ticket ";
discover_prompt += json_encode(ticket);
discover_prompt += " as a sequential child-ticket feature. Use tools. Read the tracker and the repo. Do not edit files, except you may run the git helper's info and state-read (those are read-only).\n\n";
discover_prompt += "Ticket formats you must recognize:\n";
discover_prompt += "- Parent spec (to-spec): Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope.\n";
discover_prompt += "- Child ticket (to-tickets): Parent, What to build, Acceptance criteria, Blocked by.\n";
discover_prompt += "- GitHub/GitLab: gh/glab issue view; children often have `## Parent` pointing at the parent, native sub-issues, or a task list in the parent body. Blocked by is `## Blocked by` and/or native dependencies.\n";
discover_prompt += "- Local markdown: docs/agents/issue-tracker.md, then typically .scratch/<feature>/spec.md and .scratch/<feature>/issues/<NN>-<slug>.md.\n";
discover_prompt += "- A path argument may be the parent spec file itself.\n\n";
discover_prompt += "Read if present: .grok/develop-feature.toml, docs/agents/issue-tracker.md, AGENTS.md, CLAUDE.md, CONTRIBUTING.md, CONTEXT.md, package.json/Makefile/justfile/pyproject.toml/Cargo.toml/go.mod, and CI workflows.\n";
discover_prompt += helper_lookup();
if helper_override != "" {
    discover_prompt += "Preferred helper_path from args: " + json_encode(helper_override) + ".\n";
}
discover_prompt += "Run python3 <helper> info and python3 <helper> state-read --parent <id> when the helper exists.\n\n";
discover_prompt += "Ordering: topological by Blocked by, then numeric/lexical id. Return a fully linearized list. Later children must assume earlier children are already on the parent branch. Never recommend parallel implementation.\n";
discover_prompt += "If the parent has no children, return one child that is the parent itself.\n";
discover_prompt += "Resume / ongoing spec: keep EVERY child in the list. Mark already-finished children status=integrated so the orchestrator skips them and continues at the first unfinished child. A child is finished if ANY of these is true:\n";
discover_prompt += "1) The run-state file lists it as integrated.\n";
discover_prompt += "2) The tracker issue is closed (GitHub/GitLab), or the local ticket Status is resolved/completed/done/closed (not ready-for-agent, claimed, or in progress).\n";
discover_prompt += "3) The parent feature branch already exists and clearly contains that child's work (merge commit, commit message with the child id, or the child's branch already merged). Check out git log on the parent branch vs the base; do not re-implement work that is already there.\n";
discover_prompt += "If a child is still open/ready-for-agent and there is no evidence on the parent branch, status is pending (omit status or use pending).\n";
discover_prompt += "If it is unclear whether a child is done (ticket still open but the parent branch has overlapping unrelated commits), set the discovery status=stop and name the ambiguous children. Do not guess and do not redo finished work.\n";
discover_prompt += "Reuse an existing parent feature branch when it already exists; do not recreate it from the original base.\n";
discover_prompt += "Branch names: use .grok/develop-feature.toml templates when set, else feat/{id} and feat/{parent-id}-{child-id}, else the repo's documented convention (conventional-git, AGENTS.md). The parent branch must not be the base branch.\n";
discover_prompt += "Verification: do not assume npm, pnpm, bun, cargo, or any stack. Prefer (1) ticket acceptance criteria, (2) .grok/develop-feature.toml, (3) AGENTS.md/CLAUDE.md, (4) repo scripts, (5) CI. Put cheap commands in verify_commands and full/e2e/automation commands in integration_verify_commands.\n";
discover_prompt += "Set status=stop if the parent is missing, children cannot be ordered, the ticket is too ambiguous to implement, or required environment is unavailable.\n";
discover_prompt += "Do not implement code.\n";

let discovered = ();
try {
    discovered = agent(discover_prompt, #{
        label: "discover",
        capability_mode: "all",
        output_schema: discovery_schema,
    });
} catch (e) {
    finish("STOPPED", "discover agent threw: " + e, "STOPPED\ndiscover failed\n" + e + "\n");
}

if !agent_ok(discovered) {
    finish("STOPPED", "discover agent failed", "STOPPED\ndiscover failed\n" + summary_of(discovered) + "\n");
}

if is_stop(status_of(discovered)) {
    finish("STOPPED", stop_reason_of(discovered), "STOPPED\n" + stop_reason_of(discovered) + "\n");
}

let parent_id = as_str(discovered.output.parent_id);
let parent_title = as_str(discovered.output.parent_title);
let parent_ref = as_str(discovered.output.parent_ref);
let base_branch = as_str(discovered.output.base_branch);
let parent_branch = as_str(discovered.output.parent_branch);
let helper_path = as_str(discovered.output.helper_path);
if helper_path == "" { helper_path = helper_override; }
let config_notes = as_str(discovered.output.config_notes);
let verify_commands = discovered.output.verify_commands;
let integration_verify_commands = discovered.output.integration_verify_commands;
let children = discovered.output.children;

if parent_id == "" || parent_branch == "" || base_branch == "" {
    finish("STOPPED", "discover did not return parent_id, parent_branch, and base_branch", "STOPPED\nincomplete discovery\n");
}
if parent_branch == base_branch {
    finish("STOPPED", "parent branch must not equal base branch " + base_branch, "STOPPED\n");
}
if children == () || type_of(children) != "array" || children.len() == 0 {
    finish("STOPPED", "discover returned no children", "STOPPED\nno child tickets\n");
}

let child_count = children.len();
let done_count = 0;
let ci = 0;
while ci < children.len() {
    if is_already_done(as_str(children[ci].status)) { done_count += 1; }
    ci += 1;
}
log("Parent " + parent_id + " — " + parent_title);
log("Base " + base_branch + " -> parent branch " + parent_branch);
log(child_count.to_string() + " child ticket(s), sequential; " + done_count.to_string() + " already done, " + (child_count - done_count).to_string() + " remaining");

if is_plan_mode(mode) {
    phase("Prepare");
    log("plan mode: no git mutation, no implementation");
    let report = "";
    report += "PLAN ONLY — no implementation\n\n";
    report += "Parent: " + parent_id + " — " + parent_title + "\n";
    report += "Ref: " + parent_ref + "\n";
    report += "Base: " + base_branch + "\n";
    report += "Branch: " + parent_branch + "\n";
    if helper_path != "" { report += "Helper: " + helper_path + "\n"; }
    if config_notes != "" { report += "Config: " + config_notes + "\n"; }
    report += "\nChildren (strict sequence):\n";
    let pi = 0;
    while pi < children.len() {
        let ch = children[pi];
        let cid = as_str(ch.id);
        let ctitle = as_str(ch.title);
        let cst = as_str(ch.status);
        report += "  " + (pi + 1).to_string() + ". " + cid + " — " + ctitle;
        if cst != "" { report += " [" + cst + "]"; }
        report += "\n";
        pi += 1;
    }
    report += "\nTo implement: /develop-feature {\"ticket\":" + json_encode(ticket) + "}\n";
    finish("PLAN", "discovery only; no implementation", report);
}

// --------------------------------------------------------------------------- prepare
phase("Prepare");
let prepare_prompt = worker_rules();
prepare_prompt += helper_lookup();
prepare_prompt += "Prepare the parent feature branch. Context (JSON):\n";
prepare_prompt += json_encode(#{
    parent_id: parent_id,
    parent_branch: parent_branch,
    base_branch: base_branch,
    helper_path: helper_path,
});
prepare_prompt += "\nIf the helper exists, run:\n";
prepare_prompt += "python3 <helper> assert-not-base --branch <parent_branch> --base <base_branch>\n";
prepare_prompt += "python3 <helper> prepare-parent --parent <parent_id> --branch <parent_branch> --base <base_branch>\n";
prepare_prompt += "If the parent branch already exists, check it out and keep its commits. Do not reset it to the original base. Later children must start from the current parent tip.\n";
prepare_prompt += "Do not implement product code. Do not merge to the base branch. Do not create a PR.\n";
prepare_prompt += "status=ok when the parent branch exists and is checked out from the base (or already existed). status=stop on dirty unexpected state or protected-branch refusal.\n";

let prepared = ();
try {
    prepared = agent(prepare_prompt, #{
        label: "prepare",
        capability_mode: "all",
        output_schema: work_schema,
    });
} catch (e) {
    finish("STOPPED", "prepare agent threw: " + e, "STOPPED\nprepare failed\n" + e + "\n");
}
if !agent_ok(prepared) || is_stop(status_of(prepared)) || is_fail(status_of(prepared)) {
    finish("STOPPED", "prepare failed: " + stop_reason_of(prepared), "STOPPED\nprepare failed\n" + stop_reason_of(prepared) + "\n");
}
log("Parent prepared");

let report = "";
report += "DEVELOP FEATURE: " + parent_id + "\n\n";
report += "Parent prepared: " + parent_branch + " from " + base_branch + "\n\n";

let impl_ids = [];
let child_results = [];

// --------------------------------------------------------------------------- children (STRICTLY SEQUENTIAL — never parallel)
phase("Child");
let idx = 0;
while idx < children.len() {
    let child = children[idx];
    let child_id = as_str(child.id);
    let child_title = as_str(child.title);
    let child_ref = as_str(child.ref);
    let child_status = as_str(child.status);
    let pos = (idx + 1).to_string() + "/" + children.len().to_string();
    log("[" + pos + "] " + child_id + " — " + child_title);

    if is_already_done(child_status) {
        log("  skipped (already done: " + child_status + ")");
        report += "[" + pos + "] " + child_id + " skipped (already done)\n";
        child_results.push(#{ id: child_id, status: "skipped" });
        idx += 1;
        continue;
    }

    let child_branch = parent_branch + "-" + child_id;
    if child.branch != () { child_branch = as_str(child.branch); }

    let ctx = json_encode(#{
        parent_id: parent_id,
        parent_title: parent_title,
        parent_ref: parent_ref,
        parent_branch: parent_branch,
        base_branch: base_branch,
        helper_path: helper_path,
        verify_commands: verify_commands,
        child_id: child_id,
        child_title: child_title,
        child_ref: child_ref,
        child_branch: child_branch,
        position: pos,
        config_notes: config_notes,
    });

    let impl_prompt = worker_rules();
    impl_prompt += helper_lookup();
    impl_prompt += "Implement ONE child ticket. Stay inside that child's scope unless a supporting change is required for it to land.\n";
    impl_prompt += "Context JSON:\n" + ctx + "\n";
    impl_prompt += "Read the parent spec, this child ticket, AGENTS.md/CLAUDE.md, CONTEXT.md, docs/agents/*, and the current code.\n";
    impl_prompt += "If skills tdd, implement, or conventional-git are available, follow them. Do not invoke /implement or /execute-plan (those are outer orchestrators).\n";
    impl_prompt += "Start from the CURRENT parent branch (it already contains earlier children). ";
    impl_prompt += "If using child branches, run: python3 <helper> start-child --branch <child_branch> --parent-branch <parent_branch> --parent <parent_id> --child <child_id>\n";
    impl_prompt += "Commit on the child branch (or on the parent if the project config sets child_branches=false).\n";
    impl_prompt += "Run the ticket's verification plus project verify_commands you can run safely.\n";
    impl_prompt += "Do not merge into the parent or base. Do not start the next child.\n";
    impl_prompt += "status=ok when the child is implemented and committed. status=stop when you would have to guess product behavior, a dependency is missing, or tests need a human.\n";

    let impl = ();
    try {
        impl = agent(impl_prompt, #{
            label: "impl:" + child_id,
            capability_mode: "all",
            output_schema: work_schema,
        });
    } catch (e) {
        finish("STOPPED", "implement threw for " + child_id + ": " + e, report + "STOPPED on " + child_id + "\n" + e + "\n");
    }
    if !agent_ok(impl) || is_stop(status_of(impl)) || is_fail(status_of(impl)) {
        finish("STOPPED", "implement failed for " + child_id + ": " + stop_reason_of(impl), report + "STOPPED on " + child_id + "\n" + stop_reason_of(impl) + "\n");
    }
    log("  implemented");
    let impl_id = impl.agent_id;

    let verify_prompt = worker_rules();
    verify_prompt += "Verify the current child implementation. Use tools. Run the commands; do not claim pass from memory.\n";
    verify_prompt += "Context JSON:\n" + ctx + "\n";
    verify_prompt += "Prefer the child's acceptance criteria, then project verify_commands, then repo scripts/CI. Do not assume a package manager.\n";
    verify_prompt += "If a command needs a human (device tap, paid credential, interactive simulator), status=stop.\n";
    verify_prompt += "status=pass only with evidence you ran (or a documented reason that no automated command exists and you inspected the diff against the criteria).\n";

    let verify = ();
    try {
        verify = agent(verify_prompt, #{
            label: "verify:" + child_id,
            capability_mode: "all",
            output_schema: verify_schema,
        });
    } catch (e) {
        finish("STOPPED", "verify threw for " + child_id + ": " + e, report + "STOPPED on " + child_id + "\n" + e + "\n");
    }

    let vtries = 0;
    while !is_success(status_of(verify)) && vtries < MAX_VERIFY_RETRIES {
        if is_stop(status_of(verify)) {
            finish("STOPPED", "verify stopped for " + child_id + ": " + stop_reason_of(verify), report + "STOPPED on " + child_id + "\n" + stop_reason_of(verify) + "\n");
        }
        vtries += 1;
        log("  verify failed; repair " + vtries.to_string() + "/" + MAX_VERIFY_RETRIES.to_string());
        let repair_prompt = worker_rules();
        repair_prompt += "Repair the implementation so verification passes. Previous verify summary: ";
        repair_prompt += json_encode(summary_of(verify));
        repair_prompt += "\nContext JSON:\n" + ctx + "\n";
        repair_prompt += "Commit the fix. Do not merge to parent/base. Do not start the next child.\n";
        try {
            impl = agent(repair_prompt, #{
                label: "repair:" + child_id,
                capability_mode: "all",
                output_schema: work_schema,
                resume_from: impl_id,
            });
        } catch (e) {
            impl = agent(repair_prompt, #{
                label: "repair-fresh:" + child_id,
                capability_mode: "all",
                output_schema: work_schema,
            });
        }
        if agent_ok(impl) { impl_id = impl.agent_id; }
        if !agent_ok(impl) || is_stop(status_of(impl)) {
            finish("STOPPED", "repair failed for " + child_id + ": " + stop_reason_of(impl), report + "STOPPED on " + child_id + "\n");
        }
        verify = agent(verify_prompt, #{
            label: "reverify:" + child_id,
            capability_mode: "all",
            output_schema: verify_schema,
        });
    }
    if !is_success(status_of(verify)) {
        await_user("verification", "Child " + child_id + " verification failed after retries: " + summary_of(verify) + ". Fix the environment or code, then resume this workflow.");
        verify = agent(verify_prompt, #{
            label: "reverify-resume:" + child_id,
            capability_mode: "all",
            output_schema: verify_schema,
        });
        if !is_success(status_of(verify)) {
            finish("STOPPED", "verify still failing for " + child_id + ": " + summary_of(verify), report + "STOPPED on " + child_id + "\n" + summary_of(verify) + "\n");
        }
    }
    log("  verified");

    let review_prompt = worker_rules();
    review_prompt += "Fresh review of this child only. Read the child ticket, parent spec where relevant, the diff against the parent branch before this child, and the surrounding code.\n";
    review_prompt += "Context JSON:\n" + ctx + "\n";
    review_prompt += "If a code-review skill exists, apply its two axes (standards and spec) yourself — do not spawn reviewers.\n";
    review_prompt += "Blocking issues: correctness, missed acceptance criteria, regressions, required tests missing, unsafe scope expansion.\n";
    review_prompt += "Do not block on style nits or optional refactors. Put those in summary only.\n";
    review_prompt += "status=pass when blocking_count is 0. status=blocking when something must be fixed before integrate. status=stop if you cannot review (empty diff, missing ticket).\n";

    let review = ();
    try {
        review = agent(review_prompt, #{
            label: "review:" + child_id,
            capability_mode: "all",
            output_schema: review_schema,
        });
    } catch (e) {
        finish("STOPPED", "review threw for " + child_id + ": " + e, report + "STOPPED on " + child_id + "\n" + e + "\n");
    }

    let rrounds = 0;
    while is_blocking(review) && rrounds < MAX_REVIEW_ROUNDS {
        rrounds += 1;
        log("  review blocking; fix round " + rrounds.to_string() + "/" + MAX_REVIEW_ROUNDS.to_string());
        let fix_prompt = worker_rules();
        fix_prompt += "Address blocking review findings. Review summary: ";
        fix_prompt += json_encode(summary_of(review));
        if agent_ok(review) && review.output.blocking_issues != () {
            fix_prompt += "\nFindings JSON: " + json_encode(review.output.blocking_issues);
        }
        fix_prompt += "\nContext JSON:\n" + ctx + "\n";
        fix_prompt += "Fix blocking issues. You may wontfix a finding only with a technical reason. Commit. Then we will re-verify.\n";
        try {
            impl = agent(fix_prompt, #{
                label: "fix:" + child_id,
                capability_mode: "all",
                output_schema: work_schema,
                resume_from: impl_id,
            });
        } catch (e) {
            impl = agent(fix_prompt, #{
                label: "fix-fresh:" + child_id,
                capability_mode: "all",
                output_schema: work_schema,
            });
        }
        if agent_ok(impl) { impl_id = impl.agent_id; }
        if !agent_ok(impl) || is_stop(status_of(impl)) {
            finish("STOPPED", "review fix failed for " + child_id + ": " + stop_reason_of(impl), report + "STOPPED on " + child_id + "\n");
        }
        verify = agent(verify_prompt, #{
            label: "reverify-review:" + child_id,
            capability_mode: "all",
            output_schema: verify_schema,
        });
        if !is_success(status_of(verify)) {
            finish("STOPPED", "verify failed after review fix for " + child_id + ": " + summary_of(verify), report + "STOPPED on " + child_id + "\n");
        }
        review = agent(review_prompt, #{
            label: "rereview:" + child_id,
            capability_mode: "all",
            output_schema: review_schema,
        });
    }
    if is_stop(status_of(review)) {
        finish("STOPPED", "review stopped for " + child_id + ": " + stop_reason_of(review), report + "STOPPED on " + child_id + "\n");
    }
    if is_blocking(review) {
        await_user("verification", "Child " + child_id + " still has blocking review findings: " + summary_of(review) + ". Inspect, then resume to retry once.");
        review = agent(review_prompt, #{
            label: "rereview-resume:" + child_id,
            capability_mode: "all",
            output_schema: review_schema,
        });
        if is_blocking(review) || is_stop(status_of(review)) {
            finish("STOPPED", "review still blocking for " + child_id + ": " + summary_of(review), report + "STOPPED on " + child_id + "\n");
        }
    }
    log("  reviewed");

    let integ_prompt = worker_rules();
    integ_prompt += helper_lookup();
    integ_prompt += "Integrate this completed child into the parent feature branch. Context JSON:\n" + ctx + "\n";
    integ_prompt += "If a child branch was used: python3 <helper> integrate-child --branch <child_branch> --parent-branch <parent_branch> --parent <parent_id> --child <child_id> --delete-child\n";
    integ_prompt += "If work was already on the parent branch: python3 <helper> state-mark --parent <parent_id> --child <child_id> --status integrated\n";
    integ_prompt += "Do not merge to the base branch. Do not create a PR. Do not start the next child.\n";
    integ_prompt += "status=ok when the parent branch contains this child and the working tree is clean.\n";

    let integ = ();
    try {
        integ = agent(integ_prompt, #{
            label: "integrate:" + child_id,
            capability_mode: "all",
            output_schema: work_schema,
        });
    } catch (e) {
        finish("STOPPED", "integrate threw for " + child_id + ": " + e, report + "STOPPED on " + child_id + "\n" + e + "\n");
    }
    if !agent_ok(integ) || !is_success(status_of(integ)) {
        finish("STOPPED", "integrate failed for " + child_id + ": " + stop_reason_of(integ), report + "STOPPED on " + child_id + "\n" + stop_reason_of(integ) + "\n");
    }
    log("  integrated");
    report += "[" + pos + "] " + child_id + " implemented, verified, reviewed, integrated\n";
    child_results.push(#{ id: child_id, status: "integrated" });
    impl_ids.push(impl_id);

    idx += 1;
}

// --------------------------------------------------------------------------- final
phase("Final");
log("All children integrated. Running final integration verification");

let final_ctx = json_encode(#{
    parent_id: parent_id,
    parent_title: parent_title,
    parent_ref: parent_ref,
    parent_branch: parent_branch,
    base_branch: base_branch,
    helper_path: helper_path,
    verify_commands: verify_commands,
    integration_verify_commands: integration_verify_commands,
    children: children,
});

let final_verify_prompt = worker_rules();
final_verify_prompt += "The parent feature branch now contains every child. Inspect the full diff against the base branch and run integration verification.\n";
final_verify_prompt += "Context JSON:\n" + final_ctx + "\n";
final_verify_prompt += "Run integration_verify_commands when present (including e2e/automation if the project defines them and they can run without a human). Also run verify_commands if they were not a full-suite run.\n";
final_verify_prompt += "Do not merge to base. Do not create a PR.\n";
final_verify_prompt += "status=pass with evidence. status=stop if a required human-operated test is the only remaining check — list it for the human QA step rather than failing closed on that alone, unless the ticket demanded it as an automated gate.\n";

let final_verify = ();
try {
    final_verify = agent(final_verify_prompt, #{
        label: "final-verify",
        capability_mode: "all",
        output_schema: verify_schema,
    });
} catch (e) {
    finish("STOPPED", "final verify threw: " + e, report + "STOPPED at final verify\n" + e + "\n");
}

if is_fail(status_of(final_verify)) {
    log("final verify failed; one repair cycle");
    let integ_fix = worker_rules();
    integ_fix += "Fix blocking integration verification failures on the parent branch. Summary: ";
    integ_fix += json_encode(summary_of(final_verify));
    integ_fix += "\nContext JSON:\n" + final_ctx + "\n";
    integ_fix += "Commit on the parent branch. Do not merge to base.\n";
    let fixer = agent(integ_fix, #{
        label: "final-repair",
        capability_mode: "all",
        output_schema: work_schema,
    });
    if !agent_ok(fixer) || is_stop(status_of(fixer)) {
        finish("STOPPED", "final repair failed: " + stop_reason_of(fixer), report + "STOPPED at final repair\n");
    }
    final_verify = agent(final_verify_prompt, #{
        label: "final-reverify",
        capability_mode: "all",
        output_schema: verify_schema,
    });
}
if !is_success(status_of(final_verify)) && !is_stop(status_of(final_verify)) {
    await_user("verification", "Final integration verification failed: " + summary_of(final_verify) + ". Fix, then resume.");
    final_verify = agent(final_verify_prompt, #{
        label: "final-reverify-resume",
        capability_mode: "all",
        output_schema: verify_schema,
    });
    if !is_success(status_of(final_verify)) && !is_stop(status_of(final_verify)) {
        finish("STOPPED", "final verify still failing: " + summary_of(final_verify), report + "STOPPED at final verify\n");
    }
}
log("Final verification: " + status_of(final_verify) + " — " + summary_of(final_verify));

let final_review_prompt = worker_rules();
final_review_prompt += "Fresh final review against the ORIGINAL PARENT SPEC, not only the child tickets. Individually green children can still miss the parent feature.\n";
final_review_prompt += "Context JSON:\n" + final_ctx + "\n";
final_review_prompt += "Read the parent spec in full. Inspect the complete diff of the parent branch against the base branch.\n";
final_review_prompt += "Look for: gaps versus the parent spec, contradictory child implementations, missing tests for the overall feature, regressions, unsafe extra scope.\n";
final_review_prompt += "Do not block on style nits. status=pass when the parent spec is satisfied enough for human QA. status=blocking for gaps that must be fixed first.\n";
final_review_prompt += "Do not create a PR. Do not merge to base.\n";

let final_review = ();
try {
    final_review = agent(final_review_prompt, #{
        label: "final-review",
        capability_mode: "all",
        output_schema: review_schema,
    });
} catch (e) {
    finish("STOPPED", "final review threw: " + e, report + "STOPPED at final review\n" + e + "\n");
}

if is_blocking(final_review) {
    log("final review blocking; one fix cycle");
    let ffix = worker_rules();
    ffix += "Fix blocking gaps versus the original parent spec. Review summary: ";
    ffix += json_encode(summary_of(final_review));
    ffix += "\nContext JSON:\n" + final_ctx + "\n";
    ffix += "Commit on the parent branch. Do not merge to base.\n";
    let ffixer = agent(ffix, #{
        label: "final-spec-fix",
        capability_mode: "all",
        output_schema: work_schema,
    });
    if !agent_ok(ffixer) || is_stop(status_of(ffixer)) {
        finish("STOPPED", "final spec fix failed: " + stop_reason_of(ffixer), report + "STOPPED at final spec fix\n");
    }
    final_verify = agent(final_verify_prompt, #{
        label: "final-reverify-spec",
        capability_mode: "all",
        output_schema: verify_schema,
    });
    if !is_success(status_of(final_verify)) && !is_stop(status_of(final_verify)) {
        finish("STOPPED", "verify failed after final spec fix: " + summary_of(final_verify), report + "STOPPED at final verify\n");
    }
    final_review = agent(final_review_prompt, #{
        label: "final-rereview",
        capability_mode: "all",
        output_schema: review_schema,
    });
    if is_blocking(final_review) {
        finish("STOPPED", "final review still blocking: " + summary_of(final_review), report + "STOPPED at final review\n" + summary_of(final_review) + "\n");
    }
}

report += "\nREADY FOR HUMAN QA\n\n";
report += "Parent: " + parent_id + " — " + parent_title + "\n";
report += "Ref: " + parent_ref + "\n";
report += "Branch: " + parent_branch + "\n";
report += "Base: " + base_branch + "\n";
if helper_path != "" { report += "Helper: " + helper_path + "\n"; }
report += "\nChildren:\n";
let ri = 0;
while ri < child_results.len() {
    let cr = child_results[ri];
    report += "  " + as_str(cr.status) + "  " + as_str(cr.id) + "\n";
    ri += 1;
}
report += "\nVerification: " + status_of(final_verify) + " — " + summary_of(final_verify) + "\n";
report += "Final review: " + status_of(final_review) + " — " + summary_of(final_review) + "\n";
report += "\nManual QA required before merging to " + base_branch + ".\n";
report += "This workflow did not create a PR and did not merge to the base branch.\n";

finish("READY FOR HUMAN QA", "parent branch " + parent_branch + " is ready for manual QA", report);
