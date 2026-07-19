# Time-Freeze Scene — Research & Brainstorm

**Created:** 2026-06-25
**Purpose:** Learn what works for time-freeze effects in Seedance 2.0, identify gaps vs Omni Flash, find workarounds to adapt best practices.

---

## 1. WHAT WORKS BEST FOR TIME-FREEZE IN SEEDANCE 2.0

### The Winning Formula (from viral creators)

**Structure that consistently goes viral:**

```
HOOK (0-2s)    → Snap/clap/trigger action + shockwave visual
FREEZE (2-5s)  → Camera moves through frozen world, character is the ONLY moving thing
EXPLORE (5-8s) → Character interacts with frozen elements (playful, not destructive)
UNFREEZE (8-10s) → Reverse snap, everything resumes, wide pull-back reveal
```

### Key Insights from Research

**1. "Only the camera moves" is the magic phrase**
- The highest-performing time-freeze prompts use: *"Only the camera is moving, everything else is absolute zero motion"*
- This tells Seedance to lock everything except camera — the model treats camera as a separate variable from scene physics
- When the CHARACTER is also moving, you need to explicitly say: *"The character is the only living thing moving in this frozen world"*

**2. Frozen elements sell the effect**
- Specificity matters: not "everything freezes" but *"pedestrians frozen mid-stride, coffee suspended mid-spill, pigeons frozen mid-flight, confetti halted mid-fall"*
- The more diverse the frozen elements (people, objects, particles, animals), the more visually impressive the freeze reads
- Liquid droplets, steam, smoke, dust — these are the "wow" particles that make the freeze feel real

**3. Shockwave description is critical**
- Vague: "a shockwave bursts from his hand"
- Specific: *"A bright spherical shockwave erupts from his hand with visible air distortion, refracted light, and expanding ripples that lock everything in place"*
- The shockwave is the transition moment — it needs its own 1-2 seconds of visual real estate

**4. Camera movement during freeze = engagement**
- Orbiting shots (camera circles the frozen scene) perform best
- Weaving between frozen objects creates depth and immersion
- Low-to-high angle sweeps add drama
- Dolly zoom through frozen crowd is a viral staple

---

## 2. SEEDANCE 2.0 vs OMNI FLASH — KEY DIFFERENCES

### What Seedance 2.0 Does Better

| Feature | Seedance 2.0 | Omni Flash |
|---|---|---|
| **Native 4K** | Yes (3840×2160) | No (720p/1080p) |
| **Multimodal inputs** | Up to 9 images + 3 videos + 3 audio | Up to 5 images (reference only) |
| **@ mention system** | Tag specific images with roles (@image1 = character, @image2 = background) | No tagging — just "use the reference image" |
| **Elements/Soul ID** | Upload 20-70 photos to train persistent character identity | Upload 1-5 reference photos per generation |
| **Physics simulation** | Superior fluid, cloth, hair, collision physics | Good but less precise |
| **Temporal consistency** | Stronger object/character stability across frames | Can drift, especially across morphs |
| **Director Mode** | Storyboard-level control over shots | Conversational multi-turn editing |
| **Audio sync** | Native synchronized audio in same pass | Auto-generated ambient audio |
| **Max clip length** | 10-15s per clip | 8s per generation (can chain) |

### What Omni Flash Does Better

| Feature | Seedance 2.0 | Omni Flash |
|---|---|---|
| **Conversational editing** | Limited — modify/extend existing video | Multi-turn: "change the hat to black, keep everything else" |
| **World knowledge** | Less contextual reasoning | Understands physics, history, culture, geography |
| **Multi-shot chaining** | Storyboard mode but limited turns | Natural conversation flow across multiple edits |
| **NZ knowledge** | Minimal — needs explicit location details | Knows Queenstown, Auckland, landmarks by name |
| **Speed** | Slower (4-8 min for 4K 5s clip) | Faster generation for shorter clips |
| **Cost** | More expensive at 4K | Free tier available, Flash = budget option |

---

## 3. WORKAROUNDS: ADAPTING SEEDANCE 2.0 TECHNIQUES TO OMNI FLASH

### Problem 1: No @ mention system
**Seedance way:** @image1 = character, @image2 = background
**Omni Flash workaround:** Use a "Fixed Identity Block" at the start of every prompt:

```
IDENTITY BLOCK (copy-paste this exactly every time):
"Use the attached reference image as the main character. Maintain identical facial 
features, hairstyle, beard, body proportions, and outfit throughout. The character 
is Michael, aged 48, Indian origin (Kerala), living in Christchurch, New Zealand. 
He wears a cap suited to the scene and glasses/spectacles throughout. He is a real 
person, not a model. Keep face geometry locked."
```

**Critical:** Copy-paste this EXACT string every time. Even slight wording changes cause the model to interpret it as a new character.

### Problem 2: No Elements/Soul ID for persistent identity
**Seedance way:** Train on 20-70 photos, persistent identity across all generations
**Omni Flash workaround:**
- Upload 3-5 high-quality reference photos per generation (front-facing, well-lit)
- Include variety: front, 3/4 angle, with cap, without cap
- Use the same photos every time for the same character
- After first generation, use "the same character as in the previous shot" to chain

### Problem 3: Frozen physics precision
**Seedance way:** "Absolute zero motion from any human, vehicle, flame, smoke or particle"
**Omni Flash workaround:**
- Be more descriptive about WHAT is frozen: list specific elements (pedestrians, vehicles, smoke, droplets)
- Use "frozen mid-action" phrasing: "pedestrians frozen mid-stride" not just "pedestrians frozen"
- Specify camera movement separately: "Camera tracks through the frozen scene while everything remains perfectly still"
- Omni Flash responds better to natural language descriptions of physics than technical commands

### Problem 4: Camera control
**Seedance way:** "Dramatic orbiting shot, weaving between suspended objects, low-to-high angle sweep"
**Omni Flash workaround:**
- Use specific cinematography terms: "tracking shot," "dolly zoom," "whip-pan," "drone pull-back"
- Describe camera movement in relation to the subject: "Camera tracks backward as Michael walks forward"
- Omni Flash responds well to standard film vocabulary — be precise about shot type and direction
- Avoid abstract camera moves ("impossible AI camera moves") — stick to real-world techniques

### Problem 5: Shockwave visual quality
**Seedance way:** "Spherical shockwave with air distortion, light refraction, expanding ripples"
**Omni Flash workaround:**
- Describe the shockwave as a physical event: "golden-white energy burst expands outward from his fingertips, distorting the air and bending light"
- Add physics cues: "visible air ripples, light refracting through the shockwave edge"
- Omni Flash's strength is physical realism — lean into that: describe the shockwave as something with weight and force, not just a visual effect
- Use "slow-motion" to give the model time to render the shockwave detail: "The shockwave expands in slow-motion as time freezes"

### Problem 6: Character interaction with frozen elements
**Seedance way:** "He grabs popcorn," "adjusts fan's cap," "touches frozen pigeon"
**Omni Flash workaround:**
- Avoid actions that could read as theft/destruction (grabbing food, touching people's property)
- Use non-contact interactions: "blows on steam and watches it drift," "catches a water droplet on his finger," "tilts his head examining a frozen moment"
- Or use universally acceptable interactions: "walks calmly through the frozen world" (walking is always safe)
- Add a "wonder/exploration" tone: "He explores the frozen scene with quiet curiosity" — this frames the interaction as discovery, not manipulation

---

## 4. OPTIMIZED PROMPT STRUCTURE FOR OMNI FLASH

Based on all research, here's the ideal structure for our time-freeze prompt:

```
[IDENTITY BLOCK — copy-paste exact string]
[CAMERA/LENS/LIGHTING — technical setup]
[TIME-CODED BEATS — 4-6 second segments]
[FROZEN ELEMENTS — specific list]
[CAMERA MOVEMENT — what the camera does during freeze]
[QUALITY CONSTRAINTS — what to avoid]
```

### Template:

```
IDENTITY: [Fixed Identity Block — same every time]

STYLE: Cinematic [camera type], [lens]mm, [lighting description]. [Color palette].

0-[X]s: [Beat 1 — HOOK: trigger action + shockwave]
[X]-[X]s: [Beat 2 — FREEZE: camera reveals frozen world, specific frozen elements listed]
[X]-[X]s: [Beat 3 — EXPLORE: character moves through frozen scene, specific interaction]
[X]-[X]s: [Beat 4 — PAYOFF: unfreeze trigger, everything resumes]
[X]-[X]s: [Beat 5 — WIDE REVEAL: drone pull-back or panoramic shot]

STYLE NOTES: [Frozen physics description], [camera movement during freeze], 
[what NOT to include]. No text, no watermark, no AI artifacts.
```

---

## 5. WHAT WE SHOULD CHANGE IN OUR APPROACH

### ❌ Stop doing:
1. **Don't prescribe outfits** — let the model choose based on context (Queenstown prompt proved this works)
2. **Don't use vague freeze descriptions** — list every frozen element specifically
3. **Don't use abstract camera moves** — stick to real cinematography terms
4. **Don't describe the shockwave as a visual effect** — describe it as a physical event
5. **Don't let character interact with food/property** — frame interactions as wonder/exploration

### ✅ Start doing:
1. **Use a Fixed Identity Block** — same string, copy-paste every generation
2. **List 5+ specific frozen elements** — people, objects, particles, animals, vehicles
3. **Separate camera movement from scene description** — "Camera does X while everything remains frozen"
4. **Describe shockwave with physics** — air distortion, light refraction, expanding ripples
5. **Frame character as explorer** — "walks calmly," "observes with quiet wonder," "explores the frozen moment"
6. **Use "slow-motion" on the snap** — gives the model time to render shockwave detail
7. **Generate 3-5 times per beat** — expect to iterate, don't expect perfection on first try
8. **Use start/end frames if available** — lock the first and last frame for continuity

---

## 6. RECOMMENDED PRACTICE WORKFLOW

### Step 1: Generate a "master shot" (the freeze moment only)
- Focus on getting the shockwave + frozen world right
- This is the money shot — spend the most generations here
- Once you have a good freeze frame, save it as a reference

### Step 2: Generate the hook (pre-snap)
- Use the master shot as a style reference
- Focus on character walking toward the snap moment
- Keep it short: 2-3 seconds

### Step 3: Generate the unfreeze (post-snap)
- Use the master shot as a style reference
- Focus on the reverse shockwave + everything resuming
- Keep it short: 2-3 seconds

### Step 4: Chain them together
- Use Omni Flash's conversational editing to connect the shots
- "Now extend this clip — after the freeze, the character walks forward..."
- Maintain the same Identity Block across all edits

### Step 5: Add sound design in post
- Seedance 2.0 generates audio natively, but Omni Flash audio is less controllable
- Better to add trending audio/sound effects in CapCut or similar
- The snap → silence → snap back arc works best with custom sound design anyway

---

## 7. QUICK REFERENCE: PROMPT CHECKLIST

Before every generation, check:

- [ ] Fixed Identity Block included (exact same string)?
- [ ] Reference image attached (front-facing, well-lit)?
- [ ] Camera/lens/lighting specified?
- [ ] Each beat has specific actions (not vague)?
- [ ] Frozen elements listed individually (5+)?
- [ ] Camera movement described separately from scene?
- [ ] Character interaction is non-destructive?
- [ ] Shockwave described with physics (air distortion, light refraction)?
- [ ] Quality constraints included (no text, no watermark, no artifacts)?
- [ ] Time codes align with target duration?
