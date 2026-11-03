# Skill Structure Template

Use this as a template when creating new skills. Copy and fill in the blanks.

```md
---
name: [skill-name-in-lowercase-with-hyphens]
description: [What it does]. Use when the user asks to [main task], [related task], or [common phrase]. Produces [output format] with [important constraints].
---

# [Skill Name]

## Purpose

[1-2 sentences: What does this skill do?]

## When to use this skill

[List 3-5 situations where this skill should activate]

Examples of user phrases:
- "..."
- "..."
- "..."

## Inputs needed

[List what the user should provide]

Example:
- [input 1]
- [input 2]
- [input 3]

## Workflow

[Numbered, operational steps. Each step should be actionable, not just advice.]

1. [Step 1 - what to do and why]
2. [Step 2 - specific action]
3. [Step 3 - verify success]
4. [Continue as needed]

## Output format

[Describe the exact deliverable. Show structure.]

Example:

```
[Show example output here]
```

## Rules

[Key behaviors to follow]

- Rule 1: [What to always do]
- Rule 2: [What to always consider]
- Rule 3: [Constraint or requirement]

## Avoid

[Mistakes to prevent]

- Don't [mistake 1]
- Don't [mistake 2]
- Don't [mistake 3]

## Quality checklist

Before final delivery:

- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]
- [ ] [Check 4]

## Test prompts

### Test 1: Normal case
**Prompt:** [Example user request]

**Expected result:** [What a good output looks like]

---

### Test 2: Edge case
**Prompt:** [Example with constraints or unusual input]

**Expected result:** [What should happen]

---

### Test 3: Missing info case
**Prompt:** [Example with incomplete information]

**Expected result:** [How to proceed with placeholders]

---

[Add more test prompts as needed]

---

**Version:** 1.0  
**Platform compatible:** [Claude / OpenCode / Agent Skills / All]
```

---

## How to use this template

1. **Copy the template above**
2. **Replace all `[bracketed]` items** with your specific skill content
3. **Keep the structure** — don't rearrange sections
4. **Fill in thoughtfully** — be specific, not generic
5. **Test it** — use the test prompts section to verify it works

## Tips

- **Name:** Use lowercase with hyphens: `skill-name-here`
- **Description:** This tells AI agents WHEN to use your skill. Make it specific and include user phrases.
- **Workflow:** Make steps operational. "Analyze the document" → "Read the first page, identify the main topic, note any unusual language"
- **Output format:** Don't just say "write a report." Show the actual structure with sections, formatting, etc.
- **Rules:** What MUST always happen
- **Avoid:** What MUST never happen
- **Test prompts:** Cover normal cases, edge cases, and failure prevention
- **Quality checklist:** What to verify before saying "done"

## Common mistakes

❌ **Too vague:** "Create content"  
✅ **Better:** "Create SEO-optimized blog posts with 1500+ words, H1/H2 structure, internal links, and meta descriptions"

❌ **No output example:** "Write a summary"  
✅ **Better:** Show the actual format, sections, and length

❌ **Missing checklist:** Just deliver the output  
✅ **Better:** Include checklist so agent knows when it's done

❌ **No test prompts:** "I assume it works"  
✅ **Better:** Include 3-5 test prompts with expected results

---

**Ready?** Fill in the template and you'll have a professional skill! 🚀
