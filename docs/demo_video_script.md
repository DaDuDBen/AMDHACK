# Demo Video Script (Submission Ready)

Use this script for a **3–5 minute hackathon video demo**.

---

## 0) Opening (0:00–0:25)

**On-screen:** App home page + project title slide.

**Narration:**

"Hi, we are presenting **Prayog-Shala**, an AI-powered virtual chemistry lab built for students who do not have access to real laboratories. Our goal is to bridge the digital divide by making practical science education available with offline-capable architecture."

---

## 1) Problem and Vision (0:25–0:50)

**On-screen:** One slide with problem statement.

**Narration:**

"Many students in Tier-2, Tier-3, and rural schools learn chemistry only from textbooks. Prayog-Shala allows them to type experiments in natural language and observe reaction outcomes, safety guidance, and conceptual explanations instantly."

---

## 2) Architecture Quick Walkthrough (0:50–1:25)

**On-screen:** Architecture diagram / code folders.

**Narration:**

"Our frontend is built in React, and backend in FastAPI. The request pipeline is safety-first: Safety Filter runs first, then NLP parsing, then simulation from a local reaction database, then visualization mapping and explanation generation. Critical chemistry logic is local and deterministic, so the platform remains reliable even with poor connectivity."

---

## 3) Live Product Demo — Main Flow (1:25–2:30)

### Step A: Normal experiment

**Type in app:**

`Add magnesium ribbon to dilute hydrochloric acid`

**Narration:**

"The system detects a known reaction, displays the balanced equation, predicted products, and observation cues like gas bubbles and exothermic behavior."

### Step B: Follow-up conceptual question

**Type in app:**

`Why does the test tube feel warm?`

**Narration:**

"Now we ask a conceptual follow-up. The explanation layer responds in a Socratic teaching style, helping students reason instead of memorizing."

---

## 4) Responsible AI / Safety Demo (2:30–3:05)

**Type in app:**

`Mix potassium with water`

**Narration:**

"The safety layer intercepts this dangerous instruction before simulation and returns an educational warning. This demonstrates responsible AI behavior and classroom-safe usage."

---

## 5) Graceful Degradation Demo (3:05–3:30)

**Type in app:**

`Dissolve copper in ethanol`

**Narration:**

"For unsupported reactions, we gracefully return ‘not in database yet’ along with partial learning info, instead of hallucinating unsafe or incorrect chemistry."

---

## 6) Offline Capability (3:30–4:05)

**On-screen:** Show `.env` with `LLM_MODE=offline`, then app still handling a known reaction.

**Narration:**

"Switching to offline mode still preserves core functionality because reaction simulation and safety checks are fully local. This is essential for low-connectivity educational environments."

---

## 7) Closing (4:05–4:30)

**On-screen:** Team slide + key outcomes.

**Narration:**

"Prayog-Shala turns theoretical chemistry into interactive learning for every student, regardless of geography, internet quality, or lab infrastructure. Thank you."

---

## Recording Tips

- Keep browser zoom at 110–125% for readability.
- Use large terminal font when showing backend logs or `.env` toggle.
- Add subtitles for clarity.
- Keep each typed prompt pre-copied for a smooth demo.
- Ensure no secret keys are visible while recording.
