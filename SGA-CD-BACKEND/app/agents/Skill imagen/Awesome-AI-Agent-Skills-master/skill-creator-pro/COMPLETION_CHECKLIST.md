# Skill Completion Checklist

Use this checklist when you've finished creating a skill to ensure it's ready for installation and use.

---

## ✅ Pre-launch checklist

### YAML Frontmatter
- [ ] Name is present and valid (lowercase, hyphens, no spaces)
- [ ] Description is present and specific
- [ ] Description includes what the skill does
- [ ] Description includes when to use it (trigger phrases)
- [ ] Description includes what it produces
- [ ] YAML is valid (no syntax errors)

**Example of good frontmatter:**
```yaml
---
name: seo-audit-basic
description: Create SEO audit reports for websites. Use when the user asks to audit a site, find SEO issues, or generate an audit report. Produces formatted report with on-page analysis, technical issues, and 5 actionable recommendations.
---
```

---

### Content sections
- [ ] Purpose section is present (1-2 sentences)
- [ ] "When to use this skill" section lists 3+ trigger situations
- [ ] "Inputs needed" section is clear about what user provides
- [ ] Workflow section has numbered steps (3-10 steps)
- [ ] Each workflow step is operational (actionable, not advice)
- [ ] Output format shows actual structure, not just description
- [ ] Output format includes an example
- [ ] Rules section lists 3+ specific rules
- [ ] Avoid section lists 3+ specific mistakes
- [ ] Quality checklist exists with 5+ checkboxes
- [ ] Test prompts section has 3-7 test cases
- [ ] Each test has: prompt, expected result

---

### Workflow quality
- [ ] Every step is specific (not "think about X", but "check Y specifically")
- [ ] Every step is actionable (an AI could execute it)
- [ ] Steps flow logically (one leads to the next)
- [ ] Success criteria are clear for each step
- [ ] No step is just generic advice
- [ ] No step is vague ("create good output")

**Bad step:**
```
1. Analyze the content
```

**Good step:**
```
1. Read the title tag and check:
   - Length (50-60 characters)
   - Keyword presence (does it include the target keyword?)
   - Clarity (would someone click on this?)
```

---

### Output format quality
- [ ] Output format shows actual structure (sections, formatting)
- [ ] Output format includes an example
- [ ] Output format is specific enough to replicate
- [ ] All output sections are listed
- [ ] Output includes required elements (title, sections, etc.)
- [ ] Output is copy-ready (no placeholders for section names)

**Bad output format:**
```
Write a good report with findings and recommendations.
```

**Good output format:**
```
# [Company Name] - SEO Audit Report

**Overall Score:** [0-100]

**Key Findings**
- [Finding 1]: [Explanation]
- [Finding 2]: [Explanation]

**Top 5 Recommendations**
1. [Action]: [Expected benefit]
2. [Action]: [Expected benefit]
...
```

---

### Rules quality
- [ ] Rules are specific behaviors (not generic advice)
- [ ] Rules state what MUST happen
- [ ] Rules are enforceable (an AI can check them)
- [ ] No rule is vague ("be helpful")
- [ ] Rules protect the skill's quality

**Bad rule:**
```
Always be accurate and helpful.
```

**Good rule:**
```
Always verify template compatibility before suggesting design changes.
Never recommend features unsupported by VRoid 3.0.
Always include specific metrics, not generic statements like "improve SEO".
```

---

### Avoid section quality
- [ ] Avoid items are specific mistakes
- [ ] Avoid items are learnable from real failures
- [ ] Avoid items are enforceable
- [ ] No avoid item is generic ("don't be bad")
- [ ] Avoid items prevent recurring problems

**Bad avoid:**
```
Don't make mistakes.
```

**Good avoid:**
```
Don't ignore the template zones when designing.
Don't recommend features the platform doesn't support.
Don't skip the verification step just to speed up.
```

---

### Quality checklist
- [ ] Checklist has 5-8 items
- [ ] All items are specific and checkable
- [ ] Checklist verifies quality (not just "did we run the skill?")
- [ ] Items match the skill's rules and avoid section
- [ ] Agent knows what "done" looks like

**Bad checklist:**
```
- [ ] Task completed
```

**Good checklist:**
```
- [ ] All sections of output format present
- [ ] At least 5 specific recommendations
- [ ] Each recommendation includes expected benefit
- [ ] No generic advice (like "improve SEO")
- [ ] Score is justified by findings
- [ ] Tone is professional and specific
```

---

### Test prompts quality
- [ ] At least 3 test prompts (5+ for complex skills)
- [ ] Test 1: Normal case (straightforward use)
- [ ] Test 2: Edge case (unusual constraint)
- [ ] Test 3: Missing info case
- [ ] Test 4+: Reference case, failure prevention, etc.
- [ ] Each test has clear expected result
- [ ] Expected results match skill's output format
- [ ] Tests cover important workflows
- [ ] Tests would catch major failures

**Bad test:**
```
Test: Create a report
Expected: A good report
```

**Good test:**
```
Test: Audit https://example.com/ for SEO
Expected: Report includes all 4 sections (Score, On-Page, Technical, Recommendations),
at least 5 specific recommendations, each with expected benefit, no generic advice,
and score of 60-80 is typical.
```

---

### Formatting & presentation
- [ ] File is valid Markdown
- [ ] No broken links
- [ ] No spelling or grammar errors
- [ ] Consistent formatting throughout
- [ ] Headers are used properly (H1 for title, H2 for sections)
- [ ] Code blocks are formatted correctly
- [ ] Lists are properly indented
- [ ] No TODO or placeholder text left
- [ ] All [BRACKETS] are either filled or clearly documented

---

## 🎯 Scope check

Before finalizing, verify the skill is the right size:

### ✅ Good scope examples
- "Create SEO audit reports" (one clear output)
- "Generate Instagram captions with hashtags" (one clear output)
- "Convert website analytics into weekly summary" (one clear output)

### ❌ Bad scope examples
- "General business helper" (too broad)
- "Create all kinds of content" (too broad)
- "Do whatever the user asks" (not a skill, that's just ChatGPT)

**Fix broad scope:**
If your skill does multiple unrelated things, split it into smaller skills:

**Before:**
```
skill: content-creator
does: blog posts, emails, social media, ads, reports
```

**After:**
```
skills:
- blog-post-writer (for blog posts)
- email-template-writer (for emails)
- social-caption-generator (for social media)
- ad-copywriter (for ads)
- report-generator (for reports)
```

Each skill is narrow and excellent at ONE thing.

---

## 🚀 Pre-deployment tests

Run these tests before sharing the skill:

### Test 1: Copy-paste test
- [ ] Copy the full SKILL.md
- [ ] Paste it into Claude, OpenCode, or your platform
- [ ] It loads without errors
- [ ] Frontmatter is recognized

### Test 2: Run all test prompts
- [ ] Run Test 1 (normal case) — does output match expected?
- [ ] Run Test 2 (edge case) — does skill handle constraint?
- [ ] Run Test 3+ (all other tests) — do they pass?
- [ ] Note any failures and fix them

### Test 3: Checklist test
- [ ] Run the quality checklist on your test outputs
- [ ] Does every checkbox item pass?
- [ ] If not, fix the workflow or output format

### Test 4: Real-world test
- [ ] Use the skill for an actual task (not just tests)
- [ ] Does it work as expected?
- [ ] Did anything surprise you?
- [ ] Would a beginner understand it?

---

## 📋 Installation & documentation

Before deploying, prepare:

- [ ] README or installation instructions
- [ ] Clear usage examples
- [ ] Folder structure defined
- [ ] Platform-specific notes included
- [ ] Support/troubleshooting section
- [ ] Version number documented
- [ ] Date documented
- [ ] Compatible platforms listed

**Minimum installation note:**

```
# Installation

1. Copy SKILL.md to ~/.claude/skills/[skill-name]/
2. Usage: /[skill-name] [your task]
3. Example: /seo-audit-basic Audit https://example.com/
```

---

## 🔄 Quality assurance summary

| Check | Status | Notes |
|-------|--------|-------|
| YAML valid | ✓ ☐ | |
| Name is specific | ✓ ☐ | |
| Description is clear | ✓ ☐ | |
| Scope is narrow | ✓ ☐ | |
| Workflow is operational | ✓ ☐ | |
| Output format is specific | ✓ ☐ | |
| Rules are clear | ✓ ☐ | |
| Avoid items are specific | ✓ ☐ | |
| Checklist exists | ✓ ☐ | |
| Test prompts are good | ✓ ☐ | |
| All tests pass | ✓ ☐ | |
| No grammar errors | ✓ ☐ | |
| Ready to share | ✓ ☐ | |

**✓ = Ready to deploy**

---

## 🎓 If tests fail

### Failure: Workflow steps are unclear

**Fix:**
- Make each step more specific
- Add "how do you know it's done" for each step
- Remove generic advice

### Failure: Output doesn't match format

**Fix:**
- Make output format more specific
- Add example output
- List all required sections

### Failure: Test expectations aren't met

**Fix:**
- Update workflow to match test expectations
- Update output format if needed
- Add rules to prevent the problem

### Failure: Scope is too broad

**Fix:**
- Narrow what the skill does
- Move unrelated tasks to separate skills
- Focus on ONE clear outcome

---

## ✨ Final sign-off

When everything above is done:

- [ ] Skill is narrow and focused
- [ ] All tests pass
- [ ] Checklist makes sense
- [ ] A beginner could use it
- [ ] Documentation is complete
- [ ] No spelling or formatting errors
- [ ] Version and date documented
- [ ] Ready to deploy

**Sign-off:** _________________ Date: _________

---

**You're ready to launch!** 🚀

Your skill is documented, tested, and ready for production use.
