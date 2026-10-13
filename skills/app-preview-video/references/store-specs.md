# Store specifications and content rules

Checked 2026-10-13 against Apple App Store Connect Help, Apple's app preview
guidance, App Review Guideline 2.3, and Google Play Console Help. The build
script encodes to these numbers; re-verify before a submission when this page
is older than a few months.

## App Store

| Item | Requirement |
| --- | --- |
| Count | Up to 3 previews per device size and locale; previews show before screenshots |
| Duration | 15–30 s |
| Orientation | iOS portrait or landscape; macOS/tvOS/visionOS landscape only |
| Container | `.mp4`, `.mov`, `.m4v` |
| Video | H.264 High profile ≤ level 4.0, progressive, ≤ 30 fps, 10–12 Mbps (or ProRes 422 HQ) |
| Audio | AAC 256 kbps stereo, 44.1 or 48 kHz; all tracks enabled |
| File size | ≤ 500 MB |
| Poster frame | Chosen in App Store Connect; default is the frame at 5 s. Shown when autoplay is off. Changing it later needs a new app version |
| Processing | Up to 24 h after upload |

Accepted resolutions (portrait / landscape):

| Display | Resolution |
| --- | --- |
| iPhone 6.9", 6.5", 6.1", 5.8" | 886×1920 / 1920×886 |
| iPhone 5.5", 4" | 1080×1920 / 1920×1080 |
| iPhone 4.7" | 750×1334 / 1334×750 |
| iPad 13", 12.9", 11", 10.5" | 1200×1600 / 1600×1200 |
| iPad 9.7" | 900×1200 / 1200×900 |
| Mac, Apple TV | 1920×1080 |
| Apple Vision Pro | 3840×2160 |

A missing size falls back to a scaled preview from a larger display; a missing
locale falls back to the next best language.

Content rules (Guideline 2.3.4 and the preview guidance):

- Footage must be a screen capture of the app itself. Nothing filmed outside
  the app: no hands, no fingers, no over-the-shoulder shots.
- Touch hotspots, text overlays, and narration are allowed to explain the
  footage. Capture at native resolution; simple dissolves and fades only.
  A transition must not imply a feature the app lacks.
- No prices, no dates or seasonal references, no ranking claims. Disclose on
  screen when a shown feature needs a purchase, subscription, or login.
- Suitable for all ages. No licensed music, film, trademarks, or brands
  without rights for marketing in every territory.
- Previews autoplay muted on the product page and in search; write for a
  muted first viewing.

## Google Play

| Item | Requirement |
| --- | --- |
| Delivery | A YouTube URL in the store listing: public or unlisted, embeddable, monetization off, no age restriction, no playlist or timecode parameters |
| Length | Short; only the first 30 s autoplay (muted, inline, on supporting devices) |
| Orientation | Match the app; portrait with no black side bars |
| Cover | The feature graphic (1024×500) is the play-button cover; keep logo and key UI out of its crop zones |
| Localization | One video per market where the listing is localized |

Content guidance (strongly recommended, enforced for featuring):

- Real in-app use in the first 10 s and in at least 80 % of the video. Limit
  logos, title cards, and promotional footage.
- No fingers or hands on the device unless the core use is off-device.
- On-screen copy for muted viewing; no price, promotional terms, performance
  or ranking claims, or calls to action. Google Play awards may be shown.
- Captions for accessibility: upload the generated `.srt` with the video.
- Avoid time-sensitive content, or replace the video when it expires.

Games must have a video to appear in some Play placements.

## Conversion notes

Practitioner data, not controlled studies; treat percentages as unverified:

- The first 3 s carry most of the decision. Videos that open on a logo or a
  loading screen lose most viewers there.
- The poster frame is the only visual when autoplay is off.
- Video helps most where motion is the value (games, fitness, media editing,
  AR). For a utility app, run a store A/B test (Apple Product Page
  Optimization, Play store listing experiments) before committing; a weak
  video can convert worse than screenshots alone.
