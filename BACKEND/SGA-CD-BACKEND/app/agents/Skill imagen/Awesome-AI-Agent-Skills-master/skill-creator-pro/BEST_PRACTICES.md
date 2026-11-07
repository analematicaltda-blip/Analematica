# Skill Creator Pro - Best Practices & Lessons Learned

This file contains accumulated wisdom about creating good skills. Use this to improve your own skill creation process.

---

## 🎯 Core principles

### 1. A skill is an operating procedure, not advice

**❌ Bad (advice):**
```md
## Workflow
1. Think about what the user wants
2. Consider the best approach
3. Write a good response
4. Make sure it's helpful
```

**✅ Good (operational):**
```md
## Workflow
1. Read the user's request and identify: goal, tools available, constraints
2. Look for [specific pattern] in their description
3. Ask clarifying questions IF [condition]
4. Follow the [specific template] structure
5. Verify [specific quality gates]
```

**Why?** A skill must be actionable for an AI agent. Steps must be specific enough to execute, not just thoughtful.

---

### 2. Trigger descriptions control when the skill activates

**❌ Too vague:**
```yaml
description: Helper for general business tasks
```

Result: Activates for everything, actually helps nothing.

**✅ Specific:**
```yaml
description: Create SEO audit reports for websites. Use when user asks to audit a site, find SEO issues, or generate an audit report. Produces formatted report with on-page, technical, and content analysis.
```

Result: Activates only for SEO audits, does SEO audits well.

**Rule:** Your description is a contract. It tells agents when to load you. Make it specific enough to be useful, broad enough to catch related requests.

---

### 3. Output format is not advice, it's a template

**❌ Bad:**
```md
## Output format
Create a well-structured report with findings and recommendations.
```

**✅ Good:**
```md
## Output format

# [Report Title]

**Summary:** [1-2 sentences of findings]

**Top Issues**
1. [Issue with explanation]
2. [Issue with explanation]
3. [Issue with explanation]

**Recommendations**
1. [Action + expected benefit]
2. [Action + expected benefit]
3. [Action + expected benefit]

**Next Steps**
- [Immediate action]
- [Follow-up action]
```

**Rule:** Show the actual structure. Include examples. An AI should be able to fill in the blanks.

---

### 4. Quality checklist = "done" definition

**❌ No checklist:**
```md
Deliver the report.
(When is it actually done? No one knows.)
```

**✅ With checklist:**
```md
## Quality checklist

Before delivery:
- [ ] All 3 sections present (Summary, Issues, Recommendations)
- [ ] At least 5 specific, actionable recommendations
- [ ] Each recommendation includes expected benefit
- [ ] No generic advice ("improve your SEO")
- [ ] Format matches template exactly
- [ ] Deliverable is under 1000 words
- [ ] Tone is professional and specific
```

**Rule:** Your checklist is the AI's "done" criteria. Agents should check this before delivering.

---

### 5. Rules are what to ALWAYS do

**❌ Weak:**
```md
## Rules
Be helpful and clear.
```

**✅ Strong:**
```md
## Rules

- Always analyze the actual template FIRST before designing
- Always include specific metrics (not "improve engagement")
- Always verify recommendations are implementable
- Always show expected impact/benefit of each action
- Never invent features unsupported by the target tool
- Never include generic best practices without context
```

**Rule:** Rules are specific behaviors that protect quality. They're not gentle suggestions, they're requirements.

---

### 6. Avoid section prevents recurring mistakes

**❌ Vague:**
```md
## Avoid
Don't make mistakes.
```

**✅ Specific:**
```md
## Avoid

- Don't create generic designs that ignore the actual template
- Don't recommend features the platform doesn't support
- Don't suggest changes without explaining SEO impact
- Don't copy-paste generic template designs
- Don't output recommendations without implementation steps
- Don't forget to show before/after or expected results
```

**Rule:** Learn from real failures. When a skill produces bad output, convert that into an "Avoid" item.

---

## 🔄 The improvement cycle

When a skill fails in real use:

1. **Don't just fix the output** — That's temporary
2. **Add a rule to prevent it** — That's permanent
3. **Add an avoid item** — So it's clear what not to do
4. **Add/update a test prompt** — So you catch it next time
5. **Document the lesson** — For future skills

**Example:**

User says: "The texture skill made a beautiful design but didn't respect the VRoid template zones."

**Don't do:**
```md
[Fix just that one output]
```

**Do this:**
```md
## New rule added:
- Always analyze the actual VRoid template zones before designing

## New avoid item added:
- Don't create generic square layouts if the template has specific zones

## New test prompt added:
- Test 4: Verify template zone compatibility
  Provide a reference image with unusual template zones,
  verify the design respects actual zones

## Updated workflow:
[Move template analysis to FIRST step, not last]
```

Now the skill is better forever, not just for that one case.

---

## 📝 Writing good test prompts

### Test 1: Normal case (straightforward use)
```
Prompt: [Typical user request with all info]
Expected: [Ideal output with all required sections]
```

**Why:** Verify the skill works in the happy path.

### Test 2: Edge case (unusual constraint)
```
Prompt: [Request with specific constraint or unusual detail]
Expected: [How skill adapts to constraint]
```

**Why:** Show skill handles variations, doesn't just work for one scenario.

### Test 3: Missing info case
```
Prompt: [Request with incomplete information]
Expected: [Skill proceeds with placeholders, asks only critical questions]
```

**Why:** Skill shouldn't block progress on missing non-critical info.

### Test 4: Reference case (follow an example)
```
Prompt: [Request with example/reference to follow]
Expected: [Skill respects the reference, doesn't invent]
```

**Why:** Skill should copy-from-reference, not create generically.

### Test 5: Failure prevention case
```
Prompt: [Scenario that previously caused problems]
Expected: [Skill prevents the problem with new rule]
```

**Why:** Verify improvements actually work.

---

## ⚠️ Common skill problems & how to fix them

### Problem 1: Skill is too broad

**Symptom:** Skill tries to do everything, does nothing well.

**Example:**
```yaml
name: general-business-helper
description: Help with business tasks
```

**Fix:** Narrow the scope hard.

**Before:**
```md
Create website content, email templates, social media posts, and reports.
```

**After:**
```md
Create SEO audit reports for websites. Period. If user wants email templates, 
that's a different skill.
```

---

### Problem 2: Output format is vague

**Symptom:** Each time skill runs, output looks different.

**Example:**
```md
## Output format
Write a good report
```

**Fix:** Show the actual structure.

**Before:**
```md
Create a report about the website.
```

**After:**
```md
# Audit Report: [Site Name]

**Score:** [0-100]

**Top 3 Issues**
1. [Issue]: [Why it matters]

**Top 5 Recommendations**
1. [Action]: [Impact]
```

---

### Problem 3: Workflow steps are advice, not operations

**Symptom:** Steps are too vague for an AI to execute.

**Example:**
```md
1. Analyze the content
2. Think about improvement
3. Create the output
```

**Fix:** Make each step specific and operational.

**Before:**
```md
1. Look at the website
2. Find problems
3. Write recommendations
```

**After:**
```md
1. Access the homepage and read all visible text
2. Check the title tag (length, keywords, clarity)
3. Check H1 tag (present, matches title, includes keyword)
4. Check meta description (160 chars, includes keyword, has CTA)
5. Analyze H2/H3 hierarchy (logical? keyword relevant?)
6. List all findings in the Issues section
```

---

### Problem 4: No checklist = no "done" criteria

**Symptom:** Skill keeps improving output but never feels done.

**Example:**
```md
Deliver the report.
(What makes it good?)
```

**Fix:** Define "done" explicitly.

**Before:**
```md
Output the audit report.
```

**After:**
```md
## Quality checklist

Before delivery:
- [ ] Report includes all 4 sections
- [ ] At least 5 specific recommendations
- [ ] Each recommendation includes expected impact
- [ ] Score is justified by findings
- [ ] No generic advice included
- [ ] Tone is professional
- [ ] Report is under 1500 words
```

---

### Problem 5: Trigger is too generic

**Symptom:** Skill activates for unrelated requests.

**Example:**
```yaml
description: Help with tasks
```

Result: Activates for everything.

**Fix:** Make trigger specific.

**Before:**
```yaml
description: Business assistant
```

**After:**
```yaml
description: Create SEO audit reports for websites. Use when user asks to 
audit a site, find SEO issues, or generate an audit report. Produces formatted 
report with on-page analysis, technical issues, and recommendations.
```

---

## 💪 Patterns of strong skills

### Pattern 1: Specific input requirement
```md
## Inputs needed
- Website URL (required)
- Focus area: [on-page / technical / content] (optional)

[Does NOT accept vague inputs like "help me"]
```

### Pattern 2: Template-based output
```md
## Output format

[Show EXACT structure with sections and format]

Example:
[Actual example output]
```

### Pattern 3: Numbered, operational workflow
```md
## Workflow

1. [Specific action] — [Why this matters or what success looks like]
2. [Specific action] — [Verification step or expected result]
3. [Specific action] — [How you know it's done]
```

### Pattern 4: Clear rules and avoid items
```md
## Rules
- [Specific behavior that must happen]
- [Constraint that must be respected]

## Avoid
- [Specific mistake to prevent]
- [Bad output pattern to never repeat]
```

### Pattern 5: Detailed quality checklist
```md
## Quality checklist

- [ ] [Specific deliverable present]
- [ ] [Specific quality metric met]
- [ ] [Specific format followed]
```

---

## 🎓 Lessons from real skill failures

### Lesson 1: Always analyze before creating

**What happened:**
Texture skill made beautiful designs but ignored actual template zones.

**Root cause:**
Skipped template analysis, jumped straight to design.

**Fix:**
Add rule: "Analyze template FIRST, before any design work."
Reorder workflow: Template analysis moved to step 1.

---

### Lesson 2: Output format must be specific enough to copy

**What happened:**
Email templates came out wildly different each time.

**Root cause:**
Output format was vague ("write a professional email").

**Fix:**
Show exact sections: Subject line, opening, body paragraphs, CTA, closing.
Include example output.

---

### Lesson 3: Rules protect against shortcuts

**What happened:**
Skill skipped important verification steps.

**Root cause:**
No explicit rule saying "verify X before output."

**Fix:**
Add rule: "Always verify [critical thing] before final delivery."
Add to checklist: "Verify [critical thing] ✓"

---

### Lesson 4: Test prompts catch regressions

**What happened:**
Skill fixed one problem but broke something that used to work.

**Root cause:**
No test prompts, so old functionality wasn't verified after update.

**Fix:**
Include test prompts for all important paths.
When updating, run ALL test prompts, not just new ones.

---

### Lesson 5: Narrow scope beats broad flexibility

**What happened:**
General "content helper" skill did everything poorly.

**Root cause:**
Tried to handle blog posts, emails, social media, reports, ads...

**Fix:**
Split into specific skills:
- blog-post-writer
- email-template-writer
- social-media-caption-generator

Each skill is narrow, deep, and excellent at ONE thing.

---

## 🚀 Creating your best skill

### Step-by-step checklist

- [ ] **1. Narrow the scope hard**
  - What's ONE thing this skill does?
  - Cut everything else into separate skills

- [ ] **2. Write a specific trigger**
  - Include user phrases that should activate it
  - Make it specific enough to not trigger falsely

- [ ] **3. Make workflow operational**
  - Each step should be actionable, not thoughtful
  - Include "how do you know it's done" for each step

- [ ] **4. Show actual output structure**
  - Don't describe, show
  - Include an example
  - Show all sections and formatting

- [ ] **5. Write clear rules**
  - What MUST always happen
  - What MUST never happen
  - What constraints are non-negotiable

- [ ] **6. Include a detailed checklist**
  - "Done" should be unambiguous
  - Checklist should verify quality, not just existence

- [ ] **7. Create 5+ test prompts**
  - Normal case
  - Edge cases
  - Missing info case
  - Reference case
  - Failure prevention case

- [ ] **8. Test and improve**
  - Run every test prompt
  - Fix failures
  - Add rules based on failures
  - Re-test

---

## 📊 Skill quality scorecard

Use this to evaluate if your skill is ready:

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Scope is narrow** | /10 | Does ONE thing, not many |
| **Trigger is specific** | /10 | Won't activate wrongly |
| **Purpose is clear** | /10 | Anyone understands what it does |
| **Workflow is operational** | /10 | Steps are actionable, not advice |
| **Output format is specific** | /10 | Shows structure, not just description |
| **Rules are clear** | /10 | Specific behaviors to always follow |
| **Avoid items are specific** | /10 | Real mistakes to prevent |
| **Checklist is useful** | /10 | "Done" is unambiguous |
| **Test prompts are good** | /10 | Cover normal, edge, and failure cases |
| **Everything is copy-ready** | /10 | No broken links, valid YAML, etc. |

**Total: /100**

**Target:** 85+

**How to improve:**
- 70-84: Fix weak areas (usually output format or test prompts)
- 60-69: Major rework needed (usually scope or workflow)
- <60: Start over, too broad or unfocused

---

## 🎯 Final wisdom

1. **Specificity beats flexibility.** A skill that does one thing perfectly beats a skill that does everything okay.

2. **Output format matters.** Show, don't tell. Examples beat descriptions.

3. **Rules protect quality.** Clear rules prevent most failures.

4. **Test everything.** Test prompts catch problems before users do.

5. **Learn from failures.** When a skill fails, add a rule. Don't just fix the output.

6. **Narrow scope hard.** If a skill is doing more than one thing, split it.

7. **Make workflows operational.** "Think about this" is not a step. "Verify this specific thing" is.

8. **Include a checklist.** Agents need to know when they're done.

---

**Now you know how to create great skills.** Go make something useful! 🚀
