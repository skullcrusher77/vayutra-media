# Vayutra daily Instagram playbook

This repository holds the brand assets, the renderer and every day's media for the Instagram account **@vayutra.in**.
A scheduled task follows this playbook once a day to publish **1 reel, 1 feed post and 2–3 stories**, all about the
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

## Theme rotation (pick the next theme not used in the last 10 days of `posted.log`)

1. Full 6-day overview   2. Day 4 Konark surf and SUP   3. Chilika Lake   4. Old Town heritage cycle ride
5. Sun Temple, Konark to Puri   6. Safety, for parents   7. What's included and how to book
8. Leadership and teamwork outcomes   9. Relatable student humour (exams, holidays, boring trips vs Odisha)
10. Who it's for: age 10+, schools and student groups, direct booking   11. Sunrise journaling and reflection
12. Pre-departure support and packing   13. FAQ (duration, age, where it starts)   14. Schools: plan your class trip

Festival days override the theme with a greeting that still ties back to the program: Dussehra 20 Oct 2026,
Diwali 8 Nov 2026, Children's Day 14 Nov 2026, Christmas 25 Dec, New Year 1 Jan, Republic Day 26 Jan.

## Daily procedure

1. `cd` into the clone and `git pull`. Today's date in IST = D (YYYY-MM-DD). If `posted.log` already has a line for
   D, or the account already has a feed post or reel with today's IST date, stop and only report.
2. Write `specs/D.json` in the format documented at the top of `tools/render.py`, for the chosen theme:
   - reel: 4–7 scenes with short punchy lines (max ~4 words per big line), plus the end card with a DM keyword CTA
   - post: kicker, a 1–2 line title, subtitle, 3–6 items
   - stories: 2 or 3 (question or poll-style hook, facts, or a CTA story)
   - Use only Poppins-safe characters: no arrows or rare symbols ("to" instead of "→"). Keep every line short.
3. Render: `python3 tools/render.py specs/D.json media/D`. Then open `post.jpg`, every `story*.jpg` and a frame of
   `reel.mp4` (`ffmpeg -ss 3 -i media/D/reel.mp4 -frames:v 1 /tmp/f.jpg`) with the Read tool and check that no text
   overflows or overlaps and that the logo shows. Fix the spec and re-render if needed.
4. Commit and push `specs/D.json` and `media/D/` to `main`.
5. Media URL base: `https://raw.githubusercontent.com/skullcrusher77/vayutra-media/main/media/D/`.
   Wait about 30 seconds after the push, then publish with the instgram connector (ig_user_id "me"):
   - Reel: `instagram_post_ig_user_media` with media_type REELS, video_url `.../reel.mp4`, cover_url `.../reel_cover.jpg`,
     share_to_feed true, caption; then `instagram_post_ig_user_media_publish` (max_wait_seconds 180).
   - Feed post: image_url `.../post.jpg` + caption, then publish.
   - Each story: media_type STORIES, image_url `.../storyN.jpg`, then publish (one call per story, not the bulk form).
   - **If a publish call returns an error, check `instagram_get_ig_user_media` (and stories) before retrying.**
     Publishes often succeed despite a "temporarily unavailable" error. Never publish the same item twice.
6. Captions: hook line first; 3–6 short lines; max 3 emoji; end with one action (comment a keyword / DM us /
   link in bio); then 8–12 hashtags, each starting with #, from:
   `#Vayutra #OdishaExperience #Odisha #Konark #Chilika #Puri #Bhubaneswar #OdishaTourism #ExploreOdisha
   #StudentTravel #EducationalTrip #ExperientialLearning #OutdoorLearning #StudentLeadership #SurfingIndia
   #LearnToSurf #ExploreEngageEvolve #ParentsOfIndia #LearnBeyondClassroom`
7. Append one line to `posted.log`: `D | theme | reel <media id> | post <media id> | stories <n>`, commit, push.
8. Report to the owner in under 80 words: what was published, with permalinks, and anything that failed.

Do not follow, unfollow, like or DM other accounts.
