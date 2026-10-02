# VelaBuilt v3: "After hours"

**Idea:** one continuous shot of a real VelaBuilt build: the DreamBuilder garden. It runs from sunset to night to sunrise. While the owner is closed, a single glass object morphs through the whole enquiry: question, agent, qualification, WhatsApp follow-up, booking. By morning it is three ticked boxes, and those become the call to action.
**Style reference:** the single-shot product film the client shared (one camera, a time-of-day arc, one morphing UI object, a cursor, a clock, checklist pills).
**Format:** 1080×1920, 30fps, 24.0s. Rendered supersampled: the composition at 2× device pixels, downscaled with Lanczos, then a single encode at CRF 8.
**Identity kept:** ink `#151412` on cream/sky, champagne and amber accents, Archivo expanded display, Geist Mono labels, the VelaBuilt mark, and "The systems a business runs on."

## The plates are real

- **The scene:** the garden is DreamBuilder (velabuilt-dreambuilder.vercel.app), captured live in Chromium.
- **The light:** the sunset is DreamBuilder's own day → evening lighting model: the sun drops, the rooms and facade lamps come on, the sky goes to blue hour.
  - It was recorded on a virtual clock, so every plate is exactly 150 ms of scene time apart (`work/capture/timelapse2.cjs`).
  - The camera keeps the house in the lower half so the type has open sky.
- **The sunrise:** the same sequence played backwards (lamps off, sky lifting) under a warm grade.
- **Safety:** analytics are blocked and no forms are submitted.

## Second by second

| Time | Beat | On screen | Sound |
|---|---|---|---|
| 0.0–2.0 | Brand | Daylight garden, the sun starting to drop. The VelaBuilt mark, **VelaBuilt.** and *The systems a business runs on.* sharpen in over the sky. | Dmaj9 pad, Rhodes, shimmer |
| 2.0–2.7 | Delete | "VelaBuilt" backspaces to its full stop, which swells. | Real CC0 keystrokes |
| 2.7–3.5 | Portal | The full stop opens into the same garden at night: lamps on, blue hour, stars. | Air sweep and a sub hit |
| 3.55–6.5 | Set-up | **You close at six.** → **Your systems don't.** | Bm11, a soft plucked pulse and a heartbeat |
| 6.25–9.0 | Enquiry | The line becomes a glass pill, *Ask about your project*, with an 11:42 PM chip. Tendai's cursor types *Can you quote a pergola for our garden?* and sends. | Keystrokes, send tick |
| 9.0–10.2 | Thinking | Pill → bar → ring of orbiting dots. | Shimmer |
| 10.2–12.0 | Agent | **AI agent · 11:42 PM**: *Happy to. Roughly how big — and how soon?* / *About 4 × 6 m. Next month.* / **Qualified · added to CRM** | Blips, two bells |
| 12.0–14.2 | Follow-up | **WhatsApp · Tendai · Sent automatically**: *Hi Tendai, thanks for the pergola enquiry. Free site visit — which suits you?* Thu 10:00 / Fri 14:00. Tendai taps Thursday → **Site visit booked · Thu 10:00** | Air, tap, bells |
| 14.25–17.5 | While you sleep | **While you sleep.** The object becomes a clock: 11:58 PM runs to 6:42 AM as the arc fills, the stars fade and the garden plays back to morning. | Asus swell, dawn bells |
| 17.5–20.5 | Morning | The clock goes solid and splits into **Enquiry answered**, **Lead in your CRM** and **Site visit booked**, each ticked. | One bell per tick, Dadd9 |
| 20.5–24.0 | End | The three pills merge into one capsule, which becomes the URL pill: mark, **VELABUILT**, *The systems a business runs on.*, **velabuilt.com**. Fine print: *3D scene: DreamBuilder, a VelaBuilt build.* | Sub and bell chord, URL tick, ring-out |

*System demo · sample data* rides under the object from 6.9s to 17.4s. Every label sits inside the 9:16 safe area, clear of Reels/TikTok UI at the bottom.

## Honesty

- **Sample content:** the conversation, the customer, the times and the booking are sample data built for this video, and the screen labels them that way.
- **Real work:** the 3D garden and its lighting are real VelaBuilt work.
- **Nothing invented:** no metrics, testimonials, client logos or results.

## Files

- **Composition:** `composition-v3/index.html`. Every frame is a pure function of t; preview with `?t=12.7`.
- **Plates:** `composition-v3/assets/plates/` holds d00–d09 (sunset) plus `night.webp`.
- **Score:** `work/audio3.py`. The cue list comes from the composition, so every sound is frame-locked.
- **Delivery:** `work/finalize3.sh` → `after-hours-v3.mp4`, `after-hours-v3.jpg`.
