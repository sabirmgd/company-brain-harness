#!/usr/bin/env python3
"""Export scoped Fireflies transcripts as normalized Company Brain records."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_TOKEN = os.environ.get("FIREFLIES_API_KEY") or os.environ.get("COMPANY_FIREFLIES_API_KEY")
API_URL = "https://api.fireflies.ai/graphql"


TRANSCRIPTS_QUERY = """
query Transcripts(
  $title: String,
  $keyword: String,
  $fromDate: DateTime,
  $toDate: DateTime,
  $limit: Int,
  $skip: Int,
  $mine: Boolean,
  $organizer_email: String,
  $participant_email: String
) {
  transcripts(
    title: $title,
    keyword: $keyword,
    fromDate: $fromDate,
    toDate: $toDate,
    limit: $limit,
    skip: $skip,
    mine: $mine,
    organizer_email: $organizer_email,
    participant_email: $participant_email
  ) {
    id
    title
    date
    dateString
    duration
    organizer_email
    host_email
    participants
    privacy
    transcript_url
    summary {
      keywords
      action_items
      outline
      overview
      bullet_gist
      notes
      gist
      short_summary
      short_overview
      meeting_type
      topics_discussed
      transcript_chapters
    }
  }
}
"""


TRANSCRIPTS_WITH_SENTENCES_QUERY = """
query Transcripts(
  $title: String,
  $keyword: String,
  $fromDate: DateTime,
  $toDate: DateTime,
  $limit: Int,
  $skip: Int,
  $mine: Boolean,
  $organizer_email: String,
  $participant_email: String
) {
  transcripts(
    title: $title,
    keyword: $keyword,
    fromDate: $fromDate,
    toDate: $toDate,
    limit: $limit,
    skip: $skip,
    mine: $mine,
    organizer_email: $organizer_email,
    participant_email: $participant_email
  ) {
    id
    title
    date
    dateString
    duration
    organizer_email
    host_email
    participants
    privacy
    transcript_url
    sentences {
      index
      speaker_name
      speaker_id
      raw_text
      start_time
      end_time
      text
    }
    summary {
      keywords
      action_items
      outline
      overview
      bullet_gist
      notes
      gist
      short_summary
      short_overview
      meeting_type
      topics_discussed
      transcript_chapters
    }
  }
}
"""


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "meeting"


def clip(value: str, limit: int) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 20)].rstrip() + "\n\n[summary clipped]"


def graphql(query: str, variables: dict[str, Any], *, token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        raise RuntimeError(f"Fireflies API returned HTTP {exc.code}: {body}") from exc
    if payload.get("errors"):
        raise RuntimeError(f"Fireflies API errors: {payload['errors']}")
    return payload


def load_input_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        rows = data.get("transcripts")
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
        rows = data.get("data", {}).get("transcripts") if isinstance(data.get("data"), dict) else None
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    raise ValueError(f"{path}: expected Fireflies transcript JSON")


def fetch_transcripts(args: argparse.Namespace) -> list[dict[str, Any]]:
    if not args.api_token:
        raise RuntimeError("missing FIREFLIES_API_KEY or --api-token")
    if not any([args.search, args.title, args.keyword, args.organizer_email, args.participant_email]):
        raise RuntimeError("refusing broad Fireflies export; pass --search, --title, --keyword, --organizer-email, or --participant-email")

    searches: list[dict[str, Any]] = []
    if args.search:
        searches.append({"title": args.search})
        searches.append({"keyword": args.search})
    else:
        searches.append({"title": args.title, "keyword": args.keyword})

    transcripts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for search in searches:
        skip = 0
        while len(transcripts) < args.limit:
            batch_limit = min(args.page_size, args.limit - len(transcripts))
            variables = {
                "title": search.get("title"),
                "keyword": search.get("keyword"),
                "fromDate": args.from_date,
                "toDate": args.to_date,
                "limit": batch_limit,
                "skip": skip,
                "mine": args.mine,
                "organizer_email": args.organizer_email,
                "participant_email": args.participant_email,
            }
            query = TRANSCRIPTS_WITH_SENTENCES_QUERY if args.include_raw_transcript else TRANSCRIPTS_QUERY
            data = graphql(query, variables, token=args.api_token)
            rows = data.get("data", {}).get("transcripts") or []
            if not rows:
                break
            new_count = 0
            for row in rows:
                transcript_id = str(row.get("id") or "")
                if transcript_id in seen:
                    continue
                seen.add(transcript_id)
                transcripts.append(row)
                new_count += 1
                if len(transcripts) >= args.limit:
                    break
            if len(rows) < batch_limit or new_count == 0:
                break
            skip += len(rows)
    return transcripts


def list_block(title: str, values: list[Any] | None) -> list[str]:
    clean = [str(value).strip() for value in values or [] if str(value).strip()]
    if not clean:
        return []
    return [f"## {title}", "", *[f"- {value}" for value in clean], ""]


def text_block(title: str, value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [f"## {title}", "", text, ""]


def meeting_summary(transcript: dict[str, Any], *, limit: int) -> str:
    summary = transcript.get("summary") if isinstance(transcript.get("summary"), dict) else {}
    parts: list[str] = []
    parts.extend(text_block("Short Summary", summary.get("short_summary") or summary.get("short_overview") or summary.get("gist")))
    parts.extend(text_block("Overview", summary.get("overview")))
    parts.extend(text_block("Meeting Notes", summary.get("notes")))
    parts.extend(text_block("Bullet Gist", summary.get("bullet_gist")))
    parts.extend(list_block("Topics Discussed", summary.get("topics_discussed")))
    parts.extend(text_block("Action Items", summary.get("action_items")))
    parts.extend(text_block("Outline", summary.get("outline")))
    parts.extend(list_block("Keywords", summary.get("keywords")))
    parts.extend(list_block("Transcript Chapters", summary.get("transcript_chapters")))
    if not parts:
        parts = ["No Fireflies summary fields were available for this meeting.", ""]
    return clip("\n".join(parts).strip(), limit)


def raw_transcript(transcript: dict[str, Any]) -> str:
    rows = transcript.get("sentences") if isinstance(transcript.get("sentences"), list) else []
    lines = [f"# Raw Transcript: {transcript.get('title') or transcript.get('id') or 'Fireflies Meeting'}", ""]
    for row in rows:
        if not isinstance(row, dict):
            continue
        text = str(row.get("text") or row.get("raw_text") or "").strip()
        if not text:
            continue
        speaker = str(row.get("speaker_name") or row.get("speaker_id") or "Unknown speaker").strip()
        start = row.get("start_time")
        end = row.get("end_time")
        timing = ""
        if start is not None and end is not None:
            timing = f" [{start}-{end}]"
        elif start is not None:
            timing = f" [{start}]"
        lines.append(f"{speaker}{timing}: {text}")
    if len(lines) <= 2:
        lines.append("No sentence-level transcript content was available.")
    return "\n".join(lines).strip() + "\n"


def normalize_transcript(transcript: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    transcript_id = str(transcript.get("id") or "").strip()
    title = str(transcript.get("title") or transcript_id or "Untitled Fireflies Meeting").strip()
    occurred_at = transcript.get("dateString") or transcript.get("date")
    date_slug = slugify(str(occurred_at or "")[:10])
    id_slug = slugify(transcript_id[:8])
    participants = [str(value).strip() for value in transcript.get("participants") or [] if str(value).strip()]
    tags = ["fireflies", "meeting", "source"]
    if args.search:
        tags.append(slugify(args.search))
    privacy = str(transcript.get("privacy") or "").lower()
    visibility = args.visibility
    if privacy in {"private", "only_me"}:
        visibility = "private"
    record = {
        "external_id": transcript_id,
        "title": title,
        "summary": meeting_summary(transcript, limit=args.summary_chars),
        "target_path": f"{args.target_prefix.strip('/')}/{date_slug}-{slugify(title)}-{id_slug}.md",
        "tags": tags,
        "artifact_type": args.artifact_type,
        "visibility": visibility,
        "author": transcript.get("organizer_email") or transcript.get("host_email") or "Fireflies",
        "occurred_at": occurred_at,
        "url": transcript.get("transcript_url"),
        "cursor": transcript.get("dateString") or transcript.get("date") or transcript_id,
        "participants_count": len(participants),
        "duration_minutes": transcript.get("duration"),
    }
    if args.include_raw_transcript:
        record["raw_body"] = raw_transcript(transcript)
        record["raw_format"] = "md"
    return record


def write_jsonl(records: list[dict[str, Any]], path: Path | None) -> None:
    if path is None:
        for record in records:
            print(json.dumps(record, sort_keys=True))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export Fireflies meeting summaries to normalized Company Brain JSONL.")
    parser.add_argument("--api-token", default=DEFAULT_TOKEN, help="Fireflies API token; defaults to FIREFLIES_API_KEY")
    parser.add_argument("--search", default=None, help="run both title and keyword searches for this term")
    parser.add_argument("--title", default=None)
    parser.add_argument("--keyword", default=None)
    parser.add_argument("--from-date", default=None)
    parser.add_argument("--to-date", default=None)
    parser.add_argument("--organizer-email", default=None)
    parser.add_argument("--participant-email", default=None)
    parser.add_argument("--mine", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--page-size", type=int, default=25)
    parser.add_argument("--target-prefix", default="Intelligence/meetings/fireflies")
    parser.add_argument("--artifact-type", default="meeting_summary")
    parser.add_argument("--visibility", default="team")
    parser.add_argument("--summary-chars", type=int, default=6000)
    parser.add_argument("--include-raw-transcript", action="store_true", help="include sentence-level transcript text for private raw evidence storage")
    parser.add_argument("--input-json", type=Path, default=None, help="offline Fireflies transcript JSON fixture")
    parser.add_argument("--output-jsonl", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        transcripts = load_input_json(args.input_json) if args.input_json else fetch_transcripts(args)
        records = [normalize_transcript(item, args) for item in transcripts if item.get("id")]
        write_jsonl(records, args.output_jsonl)
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    if args.output_jsonl:
        print(json.dumps({
            "action": "exported",
            "connector": "fireflies",
            "count": len(records),
            "output_jsonl": str(args.output_jsonl),
            "note": "credentials were read from arguments/environment and were not written",
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
