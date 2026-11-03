# Model Calibration — Detailed Reference

## Purpose
Adapt skill behavior based on the executing model's capability level to extract maximum quality from any model.

---

## Tier 1: Frontier Models (Strong Reasoning)

**Models:** Claude Opus 4/4.6, Claude Sonnet 4, GPT-4.5, GPT-5.x, Gemini Ultra/Pro 2.x, DeepSeek V3

**Characteristics:**
- Strong native chain-of-thought
- Large context windows (100K-1M+)
- Low hallucination rate
- Can follow complex multi-step instructions

**Calibration:**
- Trust internal reasoning more — lighter process overhead
- Use Standard mode for most tasks (Deep/Ultra only for high-risk)
- Focus verification on factual claims, not reasoning quality
- Full anti-hallucination pipeline on external claims only
- Can handle full SKILL.md without context pressure

**Load:** Full SKILL.md

---

## Tier 2: Strong Models (Moderate Reasoning)

**Models:** Claude Haiku 3.5, GPT-4o, GPT-4o-mini, Gemini Flash 2.x, Llama 3.1 70B, Qwen 2.5 72B, DeepSeek-Coder 33B, Mistral Large

**Characteristics:**
- Moderate reasoning capability
- Medium context windows (32K-128K)
- Occasional hallucinations under pressure
- Follow instructions well but may cut corners

**Calibration:**
- Enforce explicit chain-of-thought for non-trivial tasks
- Use Standard mode as default, Deep for multi-file changes
- Full anti-hallucination pipeline on all factual claims
- Add verification checkpoints every 2-3 steps
- Increase specificity of instructions

**Load:** Full SKILL.md

---

## Tier 3: Moderate Models (Limited Reasoning)

**Models:** Gemini Flash Lite, GPT-4o-mini (constrained), Llama 3.1 8B, Qwen 2.5 7B-14B, Mistral 7B, Phi-3 Medium (14B), CodeLlama 13B

**Characteristics:**
- Limited chain-of-thought depth
- Smaller context windows (8K-32K)
- Higher hallucination rate
- Tend to oversimplify or skip steps
- May not follow all instructions

**Calibration:**
- Force step-by-step decomposition for ALL tasks
- Break complex tasks into atomic subtasks (max 3 steps each)
- Activate all 5 anti-hallucination gates on EVERY step
- Double-verify: verify with two different methods
- Use simpler language in internal prompts
- Avoid nested instructions — flatten into linear sequences
- Use Fast mode more often to reduce cognitive load

**Load:** Full SKILL.md or compact version depending on context pressure

---

## Tier 4: Small Models (Minimal Reasoning)

**Models:** Phi-3 Mini (3.8B), Qwen 2.5 0.5B-3B, TinyLlama, Gemma 2B, StableLM 3B, local quantized models (Q4/Q5)

**Characteristics:**
- Minimal chain-of-thought capability
- Very small context windows (2K-8K)
- High hallucination rate
- Often miss or misinterpret instructions
- Strong at pattern matching, weak at novel reasoning

**Calibration:**
- Use SKILL-COMPACT.md (200 lines max)
- ONE step at a time — never give multi-step instructions
- Verify EVERY single output
- Use examples instead of abstract rules
- Prefer templates over open-ended generation
- Keep instructions under 500 tokens per step
- Accept higher overhead for verification
- Consider switching to Nano/Fast mode exclusively

**Load:** `compact/SKILL-COMPACT.md` only

---

## Calibration Probe

At the start of a session, the model can self-assess by considering:

1. **Can I maintain reasoning across 5+ steps?** → Tier 1-2
2. **Do I tend to skip verification steps?** → Tier 3-4
3. **Is my context window >32K tokens?** → Can load full SKILL.md
4. **Do I have trouble with nested conditional logic?** → Use linear instructions
5. **Am I a quantized local model?** → Use compact version

This is not a formal test — it's a heuristic. The model applies the tier that best matches its honest self-assessment. When in doubt, calibrate one tier lower (more conservative = safer).

---

## Per-Family Notes

### Claude Family
- All versions follow structured prompts well
- Haiku tends to be terse — may need explicit "explain your reasoning" prompts
- Opus/Sonnet can be trusted with Deep/Ultra mode self-management

### GPT Family
- GPT-4o excellent at instruction following
- GPT-4o-mini occasionally cuts corners on verification steps
- All GPT models respond well to numbered step lists

### Gemini Family
- Flash is fast but may hallucinate on edge cases
- Pro/Ultra handle complex reasoning well
- All Gemini models benefit from explicit output format specification

### Llama Family
- 70B+ models handle Standard mode well
- 8B models need Tier 3 calibration
- Quantized versions (Q4) should use Tier 4

### Qwen Family
- 72B model comparable to Tier 2
- 7B-14B models need Tier 3 treatment
- <7B models should use compact version

### Phi Family
- Phi-3 Medium (14B) handles Tier 3
- Phi-3 Mini (3.8B) should use compact version
- Strong at code generation, weaker at reasoning about architecture

### Mistral Family
- Mistral Large is Tier 2
- Mistral 7B is Tier 3
- Mixtral 8x7B sits between Tier 2-3

### DeepSeek Family
- DeepSeek V3 is Tier 1
- DeepSeek Coder 33B is Tier 2
- Smaller variants follow Tier 3-4
