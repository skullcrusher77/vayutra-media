# Vayutra daily Instagram playbook

This repository holds the brand assets, the renderer and every day's media for the Instagram account **@vayutra.in**.
Scheduled tasks follow this playbook three times a day to publish **3 reels, 1 feed post and 3 stories**, all about the
**Odisha Experience**. Files in `media/` are public, because Instagram downloads them from raw.githubusercontent.com.

## Brand facts (only use these; never invent anything else)

Vayutra (vayutra.in, tagline "Explore. Engage. Evolve.") is a Bhubaneswar youth initiative running student expeditions,
outdoor learning programs and student events, working with schools, colleges and student bodies.

**The Odisha Experience** (vayutra.in/odisha-experience). The website calls it the only program with direct booking.
- 6 days / 5 nights, age 10+. Places: Bhubaneswar, Konark, Puri, Chilika Lake, the Konark coastal adventure zone.
- Day 1, Bhubaneswar: arrival, orientation, heritage walk, team activities.
- Day 2, Old Town Bhubaneswar: guided heritage cycle ride, temple architecture, reflection session.
- Day 3, Konark to Puri: Konark Sun Temple, coastal exploration, beach activities.
- Day 4, Konark Coastal Adventure Day (NEW): surfing with instructors, stand-up paddle (SUP), ocean safety briefing,
  coastal forest hike near the Sun Temple zone, sunset reflection circle.
- Day 5, Chilika Lake: ecosystem learning, seasonal boat ride, teamwork challenges.
- Day 6, wrap-up: reflection, feedback, departure.
- Also: beach sunrise sessions with reflection journaling, leadership and teamwork challenges, group discussions.
- Included: accommodation, all meals, certified instructors and supervisors, surfing and SUP equipment, safety gear,
  local transport, learning materials and structured sessions.
- Pre-departure: detailed itinerary, packing list, fitness guidelines, safety briefing, parent orientation.
- Safety: 24x7 supervision, verified stays and locations, emergency contact access, regular updates to parents.
- Outcomes: confidence, balance, environmental awareness, leadership, teamwork, cultural awareness, personal growth.
- Contact: DM on Instagram, vayutra.in/contact, phone/WhatsApp 9090011077.

**Never state** prices, batch dates, discounts, seat counts, student names, testimonials, quotes, statistics or awards.
Price and date questions go to "DM us". Do not mention other companies or schools by name.

## Theme rotation

**Use `content/calendar.md` first:** its row for today gives the theme and the music style for the reel and each story.
Outside the calendar's dates, pick the next theme not used in the last 10 days of `posted.log`, and music styles
(tools/music.py lists 8) that were not used the previous day.

1. Full 6-day overview   2. Day 4 Konark surf and SUP   3. Chilika Lake   4. Old Town heritage cycle ride
5. Sun Temple, Konark to Puri   6. Safety, for parents   7. What's included and how to book
8. Leadership and teamwork outcomes   9. Relatable student humour (exams, holidays, boring trips vs Odisha)
10. Who it's for: age 10+, schools and student groups, direct booking   11. Sunrise journaling and reflection
12. Pre-departure support and packing   13. FAQ (duration, age, where it starts)   14. Schools: plan your class trip

Festival days override the theme with a greeting that still ties back to the program: Dussehra 20 Oct 2026,
Diwali 8 Nov 2026, Children's Day 14 Nov 2026, Christmas 25 Dec, New Year 1 Jan, Republic Day 26 Jan.

## Daily schedule: three slots

Each day has three runs, and each run is one **slot**:

| Slot | Time (IST) | Publishes |
|---|---|---|
| morning | about 8:55 am | 1 reel + 1 story |
| afternoon | about 12:55 pm | 1 reel + 1 story |
| evening | about 6:47 pm | 1 reel + 1 feed post + 1 story |

All three slots share the day's theme from `content/calendar.md`, but each reel takes a different angle:
- **morning:** the hook, a bold question or a "did you know" about the theme
- **afternoon:** the experience, what students actually do and see (day-by-day details)
- **evening:** the call to action, why join, who it's for, DM or website

Music: the three reels use three different styles (morning = calendar "Reel music", afternoon = "Story 1",
evening = "Story 2"), and the slot's story uses "Story 3" in the morning, then any style not used by that slot's reel.
Every asset gets its own seed (`"seed": "D-<slot>"`), so no track is ever repeated.

## Procedure for one slot (D = today's IST date, S = slot)

1. `cd` into the clone and `git pull`. If `posted.log` already has a line starting `D S |`, or the account already
   shows this slot's reel (check `instagram_get_ig_user_media` for a reel published today in this slot's time window),
   stop and only report.
2. Write `specs/D-S.json` in the format documented at the top of `tools/render.py`:
   - reel: 4–7 scenes with short punchy lines (max ~4 words per big line), plus the end card with a DM keyword CTA
   - post: ONLY in the evening slot (kicker, a 1–2 line title, subtitle, 3–6 items); leave it out otherwise
   - stories: exactly 1 (a question or poll-style hook in the morning, a fact in the afternoon, a CTA in the evening)
   - `"music": {"seed": "D-S", "reel": <style>, "stories": [<style>]}` chosen as described above.
   - Use only Poppins-safe characters: no arrows or rare symbols ("to" instead of "→"). Keep every line short.
   - Real footage: list `library/photos/` and `library/clips/`. If files exist, use the ones whose file names match
     today's theme: a `clip` on 1–3 reel scenes (with `clip_start` a few seconds in), a `bg` photo on the post or story.
     Prefer files not used in the last 7 days of `posted.log`. With no matching files, use the illustrated scenes.
     Never download images or videos from the web; only use what is in `library/`.
   - Illustrated scenes (always available): set `"scene"` on the post, the story and most reel scenes, matching the
     theme: surf/SUP -> surf, beach; Chilika -> lake; Old Town -> oldtown, cycle; Sun Temple -> temple, wheel;
     reflection or sunrise -> sunrise, beach; leadership or teamwork -> campfire, cycle; safety or FAQ -> beach, lake;
     festivals -> night, campfire, temple. Use different scenes from the day's earlier slots (see their specs).
3. Render: `python3 tools/render.py specs/D-S.json media/D/S`. Open `post.jpg` (evening), `story1.jpg` and a frame of
   `reel.mp4` (`ffmpeg -ss 3 -i media/D/S/reel.mp4 -frames:v 1 /tmp/f.jpg`) with the Read tool; check that no text
   overflows or overlaps and that the logo shows. Fix the spec and re-render if needed.
4. Commit and push `specs/D-S.json` and `media/D/S/` to `main`.
5. Media URL base: `https://raw.githubusercontent.com/skullcrusher77/vayutra-media/main/media/D/S/`.
   Wait about 30 seconds after the push, then publish with the instgram connector (ig_user_id "me"):
   - Reel: `instagram_post_ig_user_media` with media_type REELS, video_url `.../reel.mp4`, cover_url `.../reel_cover.jpg`,
     share_to_feed true, caption; then `instagram_post_ig_user_media_publish` (max_wait_seconds 180).
   - Feed post (evening only): image_url `.../post.jpg` + caption, then publish.
   - Story: media_type STORIES, video_url `.../story1.mp4` (8 s with music), then publish with max_wait_seconds 120.
     If the story video fails twice, fall back to image_url `.../story1.jpg`.
   - **If a publish call returns an error, check `instagram_get_ig_user_media` (and stories) before retrying.**
     Publishes often succeed despite a "temporarily unavailable" error. Never publish the same item twice.
6. Captions: hook line first; 3–6 short lines; max 3 emoji; end with one action (comment a keyword / DM us /
   link in bio); then 8–12 hashtags, each starting with #, from:
   `#Vayutra #OdishaExperience #Odisha #Konark #Chilika #Puri #Bhubaneswar #OdishaTourism #ExploreOdisha
   #StudentTravel #EducationalTrip #ExperientialLearning #OutdoorLearning #StudentLeadership #SurfingIndia
   #LearnToSurf #ExploreEngageEvolve #ParentsOfIndia #LearnBeyondClassroom`
   - Growth: at least every other caption also points to the website ("Full itinerary at vayutra.in/odisha-experience").
     Stories end with "Link in bio" or a DM keyword. Ask viewers to share or tag a friend in the reel caption.
7. Append one line to `posted.log`: `D S | theme | reel <media id> | post <media id or -> | story <media id> | music <reel>/<story> | files <library files used>`,
   commit, push.
8. Report to the owner in under 80 words: what was published, with permalinks, and anything that failed.

Do not follow, unfollow, like or DM other accounts.
