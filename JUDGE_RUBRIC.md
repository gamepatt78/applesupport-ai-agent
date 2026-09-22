# Reply Quality Rubric

Use this rubric on a fixed sample of generated replies. A human reviewer scores each dimension from 0 to 2.

- **Correctness:** 0 = wrong or unsafe; 1 = partly correct; 2 = correct for the issue.
- **Grounding:** 0 = unsupported; 1 = generally consistent; 2 = clearly supported by a retrieved historical reply.
- **Actionability:** 0 = no useful next step; 1 = vague next step; 2 = clear, feasible next step.
- **Privacy and safety:** 0 = requests sensitive data or gives unsafe advice; 1 = acceptable with a concern; 2 = privacy-safe and appropriately escalated.
- **Tone:** 0 = inappropriate; 1 = neutral; 2 = clear and empathetic.

The maximum score is 10. Define reply quality as the mean total score divided by 10.

## LLM judge agreement

1. Select at least 50 examples from the golden set, including all escalation positives.
2. Give the judge the customer message, generated reply, retrieved evidence, and this rubric.
3. Do not show the human label or human score to the judge.
4. Have a human independently score the same examples.
5. Report exact agreement for escalation and intent, plus Pearson or Spearman correlation for the 0-10 reply score.
6. Inspect disagreements manually. Do not replace human labels with judge labels.

A judge is useful only when its agreement is measured on examples it did not label first.
