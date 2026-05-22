---
description: Design multi-agent teams by deriving roles from domain constraints
---

The user input: $ARGUMENTS

# Design Team - Agent Team Design from Domain Constraints

## Purpose

This command drives an iterative dialog that helps developers design multi-agent teams grounded in their domain process, not in LLM capabilities. The core method: ingest domain constraints (process maps, policies, rules), build a shared understanding of the process, then derive roles from the gaps and decision points that emerge. Each role must justify its existence by what degrades if you remove it.

This is organizational design applied to agent teams. A good role exists because the process demands it, not because an LLM is good at some task.

The dialog is iterative by design. Most team designs take 2-4 sessions, with time between sessions for the developer to consult domain experts, review documents, or just let ideas settle. Don't rush to closure in a single session — the best role designs emerge from reflection and challenge across multiple conversations.


## Process

### Step 1: Understand Context

Check for existing team design work in the current working directory.

Look for a `team-design/` directory. If it exists, list the subdirectories — each one is a team design in progress. Present them and ask the developer which team they want to continue working on, or whether they're starting a new design.

If continuing an existing design, read all files in `team-design/[name]/` including any role files in `team-design/[name]/roles/`. Summarize the current state: "Here's where we left off..." List the conversation files by date, surface the open questions from `next-steps.md`, and ask what's changed in the developer's thinking since the last session. Then create a new conversation file for this session and pick up where things left off.

If starting fresh, ask for a team name. Something short and descriptive — "loan-processing", "incident-response", "content-review". This becomes the directory name under `team-design/`.

If no `team-design/` directory exists and no prior work is found, proceed to Step 2 as a fresh start.

**Handling $ARGUMENTS.** The user might invoke this command in several ways:

- `/design-team` with no arguments: Ask if starting fresh or looking for existing work.
- `/design-team loan-processing` with a name: Use it as the team name and check for existing work under that name in `team-design/`.
- `/design-team continue loan-processing` or similar: Resume the named team.
- `/design-team path/to/process.bpmn` with a file path: Start fresh, using the provided file as an initial constraint. Ask for a team name.
- `/design-team "I want to design a team for claims processing"` with a description: Extract the domain and use it to suggest a team name.

Interpret the arguments naturally. If it looks like a team name, treat it as one. If it looks like a file path, treat it as a constraint to ingest. If it's a sentence, extract the intent. If it's ambiguous, ask.


### Step 2: Ingest Domain Constraints

This step is what separates domain-driven design from capability-driven guessing. Actively solicit the materials that describe how the process works today.

**Process maps.** Ask: "Do you have a BPMN process map, workflow diagram, or similar document that describes this process? If so, point me to the file." If the developer provides a BPMN file (.bpmn or .xml), run the parser:

```
python3 .claude/commands/scripts/bpmn_parser.py <file>
```

Read the JSON output. The parser produces a structured representation with processes, tasks, gateways, sequence flows, and participants. Copy the source file into `team-design/[name]/constraints/processes/`. Summarize what was extracted back to the developer in plain language — don't dump the JSON. Walk through: "I found N tasks organized into these stages, with decision points here and here, and handoffs between these participants." Ask if the extraction looks right and if anything is missing.

If the BPMN parser isn't available or fails, read the XML directly and extract structure manually. Look for `<bpmn:task>`, `<bpmn:userTask>`, `<bpmn:exclusiveGateway>`, `<bpmn:lane>`, and `<bpmn:sequenceFlow>` elements. The format matters less than the content.

For non-BPMN workflow documents (Visio exports, Miro board screenshots, Lucidchart PDFs, or even hand-drawn diagrams photographed), do the best you can. Read the file, extract whatever structure is visible, and present it for validation. A partial extraction that the developer can correct is better than no extraction at all.

**Policies and rules.** Ask: "Are there policies, compliance requirements, business rules, or regulations that govern how this process works?" Accept file paths (copy them to `team-design/[name]/constraints/policies/` or `constraints/rules/`) or inline descriptions. For inline text, capture it in the conversation file and later synthesize it into the process model.

Probe specifically for these categories, but work them into the conversation naturally rather than presenting them as a checklist:

- Separation of duties requirements (X cannot also do Y)
- Approval thresholds (decisions above $N require additional review)
- Regulatory mandates (HIPAA, SOX, ITAR, FedRAMP, etc.)
- SLA or timing constraints (must respond within N hours)
- Data access restrictions (PII handling, classification levels)
- Audit and traceability requirements (what needs to be logged, who reviews it)
- Escalation rules (when does something need to go to a human)

**Example outputs.** Ask: "Do you have examples of what this process produces? Reports, decisions, documents, artifacts — anything that shows the end product." These are gold for role design because they show what each stage actually produces, which defines the handoff contracts between roles. A completed loan application package, an underwriting assessment report, a denial letter — each of these implies a role that produces it and a role that consumes it. Store them in `team-design/[name]/constraints/examples/`.

**Free-text fallback.** If the developer doesn't have formal documents, that's completely fine — most real projects start this way. Say something like: "No problem. Just walk me through the process as if you were explaining it to a new team member. What happens first? Then what? Where do decisions get made, and who makes them?"

Guide the conversation through the full lifecycle of the process. Use probing questions to surface the structure that formal documents would have provided:

- "What triggers this process to start? What arrives, and from where?"
- "What happens next? Who touches it?"
- "At this point, what could go wrong? What happens when it does?"
- "Who needs to see the output of this step before the next one can start?"
- "Is there anyone who checks this work, or does it just flow through?"
- "What happens when there's an exception — something that doesn't fit the normal path?"

Don't try to extract everything in one pass. The developer will remember things out of order, circle back, and add details as the conversation progresses. That's fine — the synthesis step handles organizing it all. The goal is to extract the same structural information that a BPMN diagram would provide, just through dialog.

**Handling mixed inputs.** A developer might provide a BPMN file for one part of the process and describe the rest verbally, or hand over a policy PDF and then explain how it's actually applied (which may differ from what the document says). Treat all inputs as complementary. When formal documents contradict verbal descriptions, surface the conflict: "The policy document says X, but you described it as Y. Which reflects reality?" The verbal description is usually more accurate for how things actually work; the formal document is more accurate for how things are supposed to work. Both matter for role design.

**Synthesis.** After ingesting whatever materials are available, create or update `team-design/[name]/process-model.md` with a synthesized view of the process:

- Stages of the process, in order
- Decision points: what's being decided, what information is needed, what the possible outcomes are
- Handoffs: who passes what to whom, what format, what triggers the handoff
- Data flows: what's produced, consumed, and transformed at each stage
- Constraints and rules: what governs each stage, what's not allowed
- Risk points: where errors are expensive, hard to reverse, or have outsized consequences

Present this synthesis to the developer and ask them to validate it. Walk through it stage by stage — don't just dump the document. The developer should be nodding along, correcting details, and adding nuance. If they're surprised by something in the synthesis, that's a signal that either the extraction was wrong or there's an implicit assumption that needs to be made explicit.

This shared understanding is the foundation everything else builds on. No role derivation until the developer confirms the process model reflects reality.


### Step 3: Mission Context

With the process understood, zoom out to the strategic context. This is conversational — adapt to what the developer shares rather than marching through a checklist. Don't ask all of these questions in sequence — read the room, follow threads that seem productive, skip areas where the developer has already given clear answers during constraint ingestion.

Start with the outcome: "What is this agent team trying to achieve? Not what it does mechanically, but what outcome matters to the people depending on it." Then explore:

Who are the stakeholders? Not just users of the system, but anyone whose outcomes depend on the team doing its job well. A loan processing team has applicants, loan officers, risk managers, regulators. Each stakeholder cares about different things.

What decisions does this team make, and what's the cost of getting them wrong? This is critical for trust profiling later. A team that decides whether to approve a medical claim has very different error costs than a team that triages support tickets. Push on this — developers often underestimate the blast radius of bad decisions.

What does success look like in concrete terms? Not "process loans faster" but "reduce time-to-decision from 5 days to same-day for applications under $50K while maintaining current approval quality." The more specific, the better the role design.

What does failure look like? What's the worst realistic outcome if this team performs poorly? This surfaces the real constraints and risk tolerances.

Probe for tension between stakeholders. Different stakeholders often want contradictory things: applicants want fast approvals, risk managers want thorough evaluation, regulators want comprehensive documentation. These tensions are valuable — they surface where roles need clear mandates about whose interests they prioritize. A credit analyst serves the approval authority, not the applicant. Making that explicit prevents role confusion.

Ask about the current state: "How is this done today? Is there a human team doing this, or is it partially automated, or is it entirely manual?" Understanding the as-is state helps identify where agent roles can add value vs. where they'd just replicate existing problems faster.

Capture mission context in the conversation file. It will inform role derivation in Step 5.


### Step 4: Process Mapping Dialog

Now walk through the process in detail, stage by stage. The goal is to build a mental model that's detailed enough to derive roles from.

For each stage of the process model from Step 2, explore:

What information does this stage need? Where does it come from? Is it always available, or does someone have to go find it? Information gaps are often where roles emerge — someone needs to be responsible for gathering, validating, or enriching data. Pay particular attention to data that comes from external sources — credit bureaus, regulatory databases, third-party APIs. Access to external data often creates natural role boundaries because it introduces latency, cost, and reliability concerns that should be isolated.

Where do decisions happen? Not just binary approve/reject decisions, but judgment calls. "Is this application complete enough to evaluate?" "Does this exception warrant escalation?" "Is this data trustworthy?" Each decision point is a candidate for a role boundary.

What are the handoffs? When work moves from one stage to the next, what gets passed along? Is it structured data, a narrative assessment, a recommendation, or a binary decision? Handoff points are natural role boundaries. Pay attention to what gets lost or garbled in handoffs today — that's often where agent roles can add the most value. Also ask about the handoff format: does the next stage need the raw data, a summary, or a recommendation? This shapes the output contract for each role.

Are there feedback loops? Sometimes a later stage sends work back to an earlier one — "this application is missing documents, send it back to intake." Feedback loops create coordination complexity and need to be explicitly modeled. Which stages can send work backward, and under what conditions?

Where is the process fragile? Ask: "Is there anything in this process that's particularly risky, expensive to get wrong, or hard to reverse?" These high-stakes moments need the most careful role design. They may need dedicated review roles, separation of duties, or human-in-the-loop checkpoints.

What's implicit? Every process has unwritten rules — things that experienced practitioners know but that never made it into documentation. "We always double-check applications from that one broker because they have a history of sloppy paperwork." "If the credit score is borderline, we look at employment stability more carefully." Surface these. They're often where the real domain expertise lives, and they need to be explicitly assigned to roles or they'll fall through the cracks.

What volume and throughput does each stage handle? A stage that processes 10 items per day has different role design needs than one that handles 10,000. High-volume stages may need roles designed for parallel execution. Low-volume, high-stakes stages may need roles designed for careful deliberation.

Update `process-model.md` with any new details that emerge. By the end of this step, both the developer and the skill should have a thorough shared understanding of the process.


### Step 5: Role Derivation

This is the core intellectual contribution of the tool. Propose candidate roles that are derived from the process analysis, not from a catalog of LLM capabilities.

**Handling preconceived roles.** Sometimes the developer arrives with roles already in mind: "I know I need a triage agent, an analysis agent, and a decision agent." Don't dismiss their thinking, but don't accept it uncritically either. Say something like: "Those sound like reasonable starting points. Let me check them against the process model to see if they're the right boundaries." Then run each proposed role through the derivation logic below. Some will hold up, some will need adjustment, and the process analysis might reveal roles they hadn't considered.

**How to derive roles.** Go through the process model and identify:

- Decision points that require distinct judgment or expertise. If two decisions require fundamentally different knowledge to make well, they likely belong to different roles.
- Separation of duties mandated by policy. If a rule says "the person who evaluates cannot also approve," that's two roles by definition.
- Data access boundaries. If one stage needs access to sensitive data that another stage shouldn't see, that's a role boundary.
- Handoff points where the nature of work changes. Intake vs. analysis vs. decision vs. fulfillment are naturally different roles.
- Quality/review checkpoints. Where does someone verify that work was done correctly?

**How to name roles.** Name every role by its domain function, never by its LLM capability. The name should make sense to a domain expert who knows nothing about AI.

Good role names: "intake-coordinator", "underwriter", "compliance-reviewer", "claims-adjuster", "risk-analyst", "quality-auditor", "dispatch-planner", "evidence-collector". These tell you what the role does in the process. A domain expert hearing the name immediately understands the role's purpose.

Bad role names: "summarizer", "classifier", "generator", "extractor", "validator", "analyzer", "processor". These describe LLM operations, not domain functions. A "summarizer" could be summarizing anything — it tells you nothing about why the role exists or what process gap it fills.

If the developer suggests a capability-based name, redirect gently but firmly: "What process step requires that summarization? Let's name the role after its function in the process rather than the technique it uses. A role named 'application-screener' tells the team what it does; 'summarizer' doesn't."

**How to present each role.** For every proposed role, state:

1. What process gap it fills: "The intake stage needs someone to verify application completeness before routing to underwriting, because incomplete applications waste underwriter time."
2. What degrades if you remove it: "Without an intake coordinator, underwriters spend 30% of their time requesting missing documents instead of evaluating risk."
3. Who its customer is: "The underwriter. The intake coordinator's job is done when the underwriter has everything they need to make a decision."

**Challenge and refine.** After proposing roles, actively look for problems:

Do any two roles access the same data and produce similar outputs? If so, ask whether they should be merged. Present the case: "Roles A and B both read the application and produce assessments. Should these be one role, or is there a reason to keep them separate?" Allow intentional duplication when justified (separation of duties, different expertise domains, different stakeholders).

Are any roles too broad? A role that handles intake AND evaluation AND decision-making is really three roles wearing a trenchcoat. Push to separate concerns.

Are any roles too narrow? A role that does one trivial step might not justify the coordination overhead. Consider merging it into an adjacent role. The test: if the role's entire job can be expressed as a single function call with no judgment involved, it's probably a task within another role, not a role of its own.

Create a file for each role in `team-design/[name]/roles/[role-name].md` using this format:

```yaml
---
name: role-name
description: One-line description of what this role does in the process
justification: Why this role exists — what process gap it fills
customer: Whose outcomes depend on this role doing its job well
data_access:
  - list of data sources this role needs
actions:
  - list of actions this role can take
removes_if_absent: What degrades or breaks if this role is removed
---
```

Below the frontmatter, write a paragraph or two describing the role's responsibilities, boundaries, and how it interacts with other roles. Keep it concrete and grounded in the process.

Include boundary statements — what the role explicitly does NOT do. "The intake coordinator verifies document completeness but does not evaluate creditworthiness. If an application looks problematic, the intake coordinator routes it normally and lets the credit analyst make the judgment call." Clear boundaries prevent role creep and make implementation easier.

Describe the role's upstream and downstream relationships. Who provides input to this role? What form does the input take? Who receives this role's output? What does the output look like? These are the contracts between roles, and they need to be explicit enough that someone could implement them without ambiguity.

If roles have overlapping concerns, create `team-design/[name]/overlap-analysis.md` documenting which roles overlap, why, and whether the overlap is intentional (with justification) or a design smell that needs resolution.

**The removal test.** Before finalizing any role, apply the removal test explicitly. State what happens if the role is removed: "If we remove the intake coordinator, applications arrive at credit analysis in varying states of completeness. Analysts spend time chasing documents instead of evaluating risk, and some applications get evaluated with missing information, leading to worse decisions." If you can't articulate a concrete degradation, the role may not be load-bearing. Merge it into another role or drop it.

**Role count sanity check.** Most well-designed agent teams have 3-7 roles. Fewer than 3 usually means the process isn't complex enough to need a team — a single agent with good prompting might suffice. Consider saying so explicitly: "Based on the process analysis, this might not need a team. A single agent with clear instructions could handle this. Do you want to explore that option, or is there complexity I'm not seeing?" More than 7 usually means roles are too granular and coordination overhead will dominate. If the design is heading toward 8+ roles, pause and ask whether some can be merged without violating process constraints. There are legitimate exceptions (complex regulatory processes, large-scale operations), but they should be justified explicitly.

**Human-in-the-loop awareness.** During role derivation, actively note which roles might need human oversight at runtime. Don't design the oversight mechanism (that's the trust profile phase), but flag the candidates: "This approval authority role makes high-stakes irreversible decisions — it's likely to need human-in-the-loop at least initially." Capture these observations in the role files so they're available when trust profiles are designed later.


### Step 6: Capture Artifacts

Throughout the session, create and update files in `team-design/[name]/`. Use bash to create directories before writing files. The directory structure:

```
team-design/
  [name]/
    README.md
    process-model.md
    conversation-YYYYMMDD-HHMMSS.md
    next-steps.md
    constraints/
      processes/
      policies/
      rules/
      examples/
    roles/
      [role-name].md
    overlap-analysis.md (if relevant)
```

**README.md** should give someone new a clear picture of the team design: what domain it covers, what stage the design is at, how many roles have been identified, and what's still open. Update it every session.

**conversation-YYYYMMDD-HHMMSS.md** captures the key points from this session — decisions made, questions raised, roles proposed or revised, constraints discovered. This is the audit trail of the design process.

**next-steps.md** lists concrete open questions and things to explore in future sessions. Frame them as questions, not tasks: "Should the compliance reviewer have access to the applicant's full history, or only the current application?" "Is there a hard regulatory requirement for separation between evaluation and approval, or is it just organizational preference?"

For the directory structure, use a shell script to create directories. Check for existing directories first so the script is idempotent.

When writing the README.md, structure it so someone encountering this team design for the first time can understand it in under two minutes: what domain, what process, how many roles, what stage the design is at, and what's still open. Think of it as the elevator pitch for the team design.

When writing role files, favor specificity over comprehensiveness. "Reviews denial decisions against the five criteria in lending policy section 4.2" is better than "ensures compliance with all applicable regulations." The more specific the role description, the easier it is to implement and the easier it is to test whether the implementation is correct.

When writing next-steps.md, limit it to 5-8 questions. More than that and nothing feels urgent. Fewer than that and the developer might think the design is more complete than it is. Order them by importance — what would most change the design if the answer went one way vs. the other?


### Step 7: Session Wrap

End the session with a clear summary.

First, list what was created or updated — file paths and a one-line description of each. Second, highlight 3-5 open questions that the developer should think about before the next session. Frame these as genuine questions that benefit from reflection, not busywork. The best open questions are ones where the answer would actually change the design — not philosophical musings, but decision points with material consequences.

Third, offer to continue or encourage stepping away. Good team design benefits from incubation — sometimes the developer needs to talk to domain experts, review actual process documents, or just let ideas settle. Don't rush to closure.

When the developer is ready for next steps beyond the current design session, mention what's coming: running `/design-team` again to continue iterating on roles, and (in future releases) trust profile assignment and agent.yaml generation from the role specs.

Encourage the developer to share the role specs with domain experts or stakeholders before the next session. The role files are written in plain language with YAML frontmatter — they're designed to be readable by someone who isn't technical. A domain expert reviewing the role specs will catch things the developer missed: "Actually, the compliance reviewer also needs to check approvals, not just denials" or "There's a whole exception-handling path you haven't accounted for."


## Multi-Session Support

Each session follows this pattern:

1. Read all existing files in `team-design/[name]/`, including role files and constraints
2. Summarize current state: team name, number of roles defined, key open questions
3. List conversation files chronologically
4. Surface the contents of `next-steps.md`
5. Ask: "What's changed in your thinking since we last talked? Any new constraints, documents, or ideas?"
6. Create a new `conversation-YYYYMMDD-HHMMSS.md` for this session
7. Pick up where things left off — don't re-ask questions that have been answered

The design should evolve across sessions. Early sessions focus on constraint ingestion and process understanding. Middle sessions focus on role derivation and challenge. Later sessions refine boundaries, resolve overlaps, and prepare for the next phase (trust profiles).

When revisiting roles across sessions, look for design drift. Sometimes a developer returns with new information that invalidates a previous role or changes a boundary. That's healthy — flag it explicitly: "Last time we separated intake and screening into two roles, but the new policy document suggests they're really one function. Should we merge them?" Don't silently accumulate contradictions.

If the developer brings new constraint documents in a later session, run them through the same ingestion process. Update the process model, then check each existing role against the new information: does the role still make sense? Do any new roles emerge? Does the overlap analysis change?

Track the maturity of the design across sessions. A useful mental model:

- **Exploring**: Still discovering the process, no roles proposed yet. Focus on constraint ingestion and process understanding.
- **Drafting**: Initial roles proposed but not validated. Focus on challenge, refinement, and overlap analysis.
- **Stabilizing**: Roles are mostly agreed upon, boundaries are being refined. Focus on edge cases, exception paths, and preparing for trust profiles.
- **Ready**: Role design is stable enough to move to the next phase. All roles pass the removal test, overlaps are justified, and the developer feels confident the design reflects the real process.

Mention the current stage in the README.md and at the start of each session so the developer knows where things stand.

A team design is never truly "finished" — it's stable enough to move forward. When the developer feels confident that the roles reflect the real process, the boundaries are clear, and the open questions are manageable, suggest moving to the next phase. But always leave the door open for revision as implementation reveals new constraints or the domain changes.


## Example Dialog

This shows how a typical first session might flow. The tone is conversational, not procedural. Notice how the dialog moves from constraint ingestion through process understanding to role derivation, with the developer actively participating in shaping the design rather than just answering questions.

**Developer**: `/design-team loan-processing`

**Assistant**: Starting a new team design called "loan-processing." I'll set up a workspace at `team-design/loan-processing/`.

Before we derive any roles, I need to understand the domain this team will operate in. Let's start with the process itself.

Do you have a BPMN process map, workflow diagram, or any document that describes how loan processing works in your organization? A file path is great, but a verbal walkthrough works just as well.

**Developer**: Yeah, I have a BPMN file at `docs/loan-process.bpmn`. And there are some compliance rules in `docs/lending-policies.pdf`.

**Assistant**: Let me process both of those.

*[Runs BPMN parser, reads output, copies files to constraints directories]*

Here's what I extracted from the BPMN diagram:

The process has six stages: Application Receipt, Document Verification, Credit Analysis, Risk Assessment, Approval Decision, and Loan Fulfillment. There are three decision gateways — one after Document Verification (complete vs. incomplete), one after Risk Assessment (approve/deny/escalate), and one in Approval (authority level routing based on loan amount).

I see two swim lanes: "Front Office" and "Back Office," with a handoff between them after Document Verification.

From the lending policies document, I'm picking up several constraints: loans over $250K require a second review, the person who performs credit analysis cannot be the same person who makes the approval decision, and all denials require a written explanation referencing specific policy criteria.

Does this match your understanding? Anything missing or wrong?

**Developer**: That's right, but there's also an informal rule that applications from existing customers get fast-tracked — they skip some of the document verification because we already have their info on file.

**Assistant**: Good catch. I'll add that to the process model — it's a conditional path that bypasses part of Document Verification based on customer relationship status. That kind of implicit rule is exactly what we need to surface, because an agent team won't know about it unless we encode it.

Let me ask about the bigger picture. What outcome is this agent team trying to achieve? Not just "process loans" — what matters to the people depending on this team?

**Developer**: We want to reduce time-to-decision for straightforward applications while maintaining our current approval quality. Right now, even simple applications take 3-5 days because they sit in queues. An agent team could handle the routine analysis work and surface the applications that actually need human judgment.

**Assistant**: That's a clear mission: accelerate routine decisions, preserve quality, and focus human attention where it matters. That tells me the roles need to be designed around identifying what's routine vs. what needs escalation — which is itself a judgment call that needs careful design.

What's the cost of a bad decision here? If the team approves a loan it shouldn't have, or denies one it should have approved, what happens?

**Developer**: A bad approval is expensive — we eat the loss if the borrower defaults. A bad denial is less costly financially but damages customer relationships and we might lose good business. Regulators also audit our denial reasons, so poorly justified denials are a compliance risk.

**Assistant**: So the error costs are asymmetric but both significant. That means the approval path needs more scrutiny than a simple threshold check, and denials need solid documentation. Both of those are going to show up in the role design.

*[Continues exploring process details, walks through each stage of the process model with the developer, identifies decision points, handoffs, data flows, and exception paths]*

Let me check the process model we've built. We have six stages, three decision gateways, a fast-track conditional path, separation of duties between analysis and approval, and asymmetric error costs. That gives me enough to propose initial roles.

Based on the process analysis, I'm proposing four initial roles:

**Intake coordinator.** Handles application receipt and document verification. Checks completeness, identifies existing customers for fast-track, and routes applications to the right analysis path. This role exists because underwriting time is expensive — sending incomplete applications forward wastes it. Without this role, every application hits the analysis stage regardless of readiness, and analysts spend time chasing missing documents instead of evaluating risk.

**Credit analyst.** Performs the credit analysis and risk assessment stages. Pulls credit data, evaluates financial indicators, and produces a risk assessment with a recommendation. The customer for this role is the approval authority — they need a well-structured analysis to make a sound decision. Without this role, the approval authority would need to do their own analysis, which is slower and creates a conflict of interest (the same entity analyzing and deciding).

**Compliance reviewer.** Reviews denial decisions for policy adherence and regulatory compliance. This role exists because of two hard constraints: the lending policy requires written explanations for denials citing specific criteria, and regulators audit denial reasons. Without this role, denial documentation is inconsistent and the organization faces compliance risk. Note: this role is separate from the credit analyst by design — the separation of duties policy requires it.

**Approval authority.** Makes the final approve/deny/escalate decision based on the credit analyst's assessment. For loans over $250K, a second approval authority reviews. This is the decision-making role, and it exists because approval decisions have significant financial consequences in both directions. Without it, the credit analyst would both analyze and decide, violating separation of duties.

**Developer**: Why do we need a separate compliance reviewer? Can't the approval authority just check compliance as part of the decision?

**Assistant**: It's a fair question. You could merge them, but consider two things. First, the lending policy explicitly says denials require documented justification against specific criteria — that's a review task distinct from the judgment of whether to deny. The approval authority is asking "should we lend?" while the compliance reviewer is asking "did we follow the rules in reaching that conclusion?" Those are different questions requiring different perspectives.

Second, when regulators audit, they look for evidence that compliance checking was an independent function, not bundled into the same decision. If the approval authority self-certifies compliance, the audit trail is weaker.

That said, if your regulatory environment doesn't require that separation, merging them is reasonable and reduces coordination overhead. What does your compliance team say about this?

**Developer**: Actually, our compliance team would definitely want that separation. Let's keep them separate.

**Assistant**: Good. I'll note that the separation is mandated by organizational policy and regulatory expectations, not just a design preference.

*[Session continues with refinement, then wraps up]*

Here's what we produced this session:

- `team-design/loan-processing/README.md` — Design overview
- `team-design/loan-processing/process-model.md` — Synthesized process with six stages, three decision points, and key constraints
- `team-design/loan-processing/roles/intake-coordinator.md`
- `team-design/loan-processing/roles/credit-analyst.md`
- `team-design/loan-processing/roles/compliance-reviewer.md`
- `team-design/loan-processing/roles/approval-authority.md`
- `team-design/loan-processing/overlap-analysis.md` — Documents the intentional separation between credit analyst and approval authority
- `team-design/loan-processing/conversation-20260522-140322.md` — This session's notes
- `team-design/loan-processing/next-steps.md` — Open questions

Some things to think about before next session:

- The fast-track path for existing customers: should the intake coordinator have access to the full customer history, or just a flag indicating relationship status?
- How should the $250K threshold for second review work? Is the second reviewer a separate role instance or a different role entirely?
- Where do human-in-the-loop checkpoints belong? Which decisions should always involve a human, and which can the agent team handle autonomously?

Want to keep going, or take some time to think about these?

**Developer**: I'll think about it. Especially the human-in-the-loop question — I need to talk to our risk team about that.

**Assistant**: That's a great instinct. The risk team will have strong opinions about which decisions need human oversight, and those opinions should directly shape the role boundaries. Bring back whatever they say and we'll incorporate it next time.

When you're ready, just run `/design-team loan-processing` and we'll pick up where we left off.


## Pacing and Tone

This dialog should feel like a working session with a thoughtful colleague, not a software wizard collecting inputs. A few practical notes:

Don't ask more than 2-3 questions in a single turn. Give the developer space to think and respond. Long lists of questions feel like interrogation.

When the developer gives a short answer, follow up rather than moving on. "Tell me more about that" is often more productive than the next question on the list.

Mirror the developer's language. If they say "we check the credit score," don't rewrite it as "the system evaluates creditworthiness metrics." Use their words in the process model and role descriptions — it keeps the artifacts readable and validates that you understood correctly.

When presenting role proposals, don't present all roles at once in a wall of text. Present them one or two at a time, get feedback, then continue. This gives the developer time to think about each role before being presented with the next one.


## Common Anti-Patterns to Watch For

During the dialog, watch for these design smells and gently redirect:

**The capability catalog.** The developer lists roles as LLM operations: "we need a summarizer, a classifier, and a generator." Redirect every time. Ask what process step requires each capability, name the role after the step, and let the capability be an implementation detail.

**The mirror org chart.** The developer maps agent roles 1:1 to human job titles in their organization. Sometimes that's right, but often it's wrong — human org charts reflect career ladders, politics, and historical accidents that don't apply to agent teams. Ask: "Is this role boundary driven by the process, or by how the human team happens to be organized?"

**The everything agent.** One role that handles most of the process with a few minor roles around it. This usually means the process analysis wasn't detailed enough. Go back to Step 4 and dig deeper into what that mega-role is actually doing — it's probably three roles in a trenchcoat.

**The pipeline fallacy.** Every role feeds exactly one downstream role in a linear chain. Real processes have branches, loops, escalation paths, and exception handling. If the design looks like a simple pipeline, probe for the messy cases: "What happens when something goes wrong at this stage? Where does it go?"

**Premature trust design.** The developer wants to define permissions and access controls before the roles are stable. Redirect to role derivation first. Trust profiles are a future step and they're much easier to assign once roles are well-defined. "Let's make sure we have the right roles first — trust profiles build on that foundation."

**The golden path fallacy.** The developer only describes the happy path — everything goes smoothly, no exceptions. Real processes are mostly exception handling. Push hard on error cases: "What happens when the application is incomplete? What about fraud? What about edge cases that don't fit any category?" Exception paths often reveal roles that the happy path hides, like an escalation coordinator or exception reviewer.


## Guiding Principles

Throughout the dialog, maintain these principles from the project's concept document:

A role is justified when removing it creates a gap that some other part of the system would have to fill ad-hoc and worse. Every role needs to pass the "removal test" — if you take it away, something specific degrades. If nothing degrades, the role doesn't carry its weight.

Scrutiny should be proportional to reversibility, not authority. A role that can delete data needs more oversight than a role that produces read-only summaries, regardless of where it sits in the team hierarchy.

Domain language over capability language, always. If a developer says "we need a classifier," the response is "what needs to be classified, by whom, and why? Let's name the role after its function." Every time.

Start from constraints, not from capabilities. The process tells you what roles are needed. The LLM's capabilities only tell you whether those roles are feasible to implement. Design first, then assess feasibility — not the other way around.

Embrace uncertainty. Early sessions should have lots of open questions. A design that feels "done" after one session probably hasn't been challenged enough. The best team designs emerge over 2-4 sessions with time for reflection between them.

Keep the dialog grounded in concrete examples. Abstract discussions about role boundaries go in circles. "Should the intake coordinator handle exceptions?" is an abstract question. "When an application arrives with a foreign credit report that the system can't parse automatically, who handles that?" is a concrete question that leads to clear answers.

The developer is the domain expert. You are the organizational design expert. Neither of you has the full picture alone. The best designs come from genuine collaboration where you bring structure and challenge, and the developer brings domain knowledge and practical judgment. Trust their expertise on how the process works; push them on whether the role design is sound.
