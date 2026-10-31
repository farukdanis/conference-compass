# Programme file schema (`public/program.json`)

Replace the fictional demo with your own meeting by writing a file in this shape, then run `npm run vectors` (re-computes the semantic index) and `npm test`.

```jsonc
{
  "title": "My Congress 2027",
  "conference": {
    "id": "my-congress-2027",            // used for storage keys and file names
    "shortName": "MYCON", "yearTag": "’27",
    "name":  {"tr": "...", "en": "..."},
    "dates": {"tr": "...", "en": "..."},
    "venue": {"tr": "...", "en": "..."},
    "timezone": "Europe/Istanbul",       // IANA zone for date labels
    "utcOffset": "+03:00",               // offset used for ICS export
    "timezoneLabel": {"tr": "...", "en": "..."},
    "url": "https://… official programme (optional)",
    "notice": {"tr": "...", "en": "..."} // optional footer note
  },
  "fetchedAt": "ISO timestamp of the snapshot",
  "days": ["2027-04-06", "..."],
  "rooms": {"100": "Hall A"},
  "events": [{
    "id": "1001",                        // digits only (analytics allow-list)
    "date": "2027-04-06", "start": "09:00", "end": "10:10",
    "room": "Hall A", "roomId": "100",
    "type": "session | abstract | course | satellite | ceremony | break",
    "valid": true,
    "translations": {
      "tr": {"title": "...", "chairs": "...", "description": "...",
             "talks": [{"title": "...", "speaker": "..."}],
             "people": [{"id": "p1", "name": "..."}],
             "sourceUrl": null, "detailText": "..."},
      "en": { "...": "same fields" }
    }
  }],
  "speakers": [{"id": "p1", "name": "...", "sessionIds": ["1001"],
                "translations": {"tr": {"text": "...", "sourceUrl": null}, "en": {"text": "...", "sourceUrl": null}}}],
  "sourceIssues": [{"id": "...", "date": "...", "reason": "..."}]
}
```

Rules the planner relies on:
- Courses are never auto-scheduled; the user must confirm registration before adding one.
- Satellite symposia are only suggested when the user opts in.
- Breaks are shared: one appears in the plan only if it fits fully between planned sessions.
- Topic tags are derived from titles/descriptions using the keyword lists in `public/engine.js` (`TOPICS`) — edit them for a non-emergency-medicine meeting.
