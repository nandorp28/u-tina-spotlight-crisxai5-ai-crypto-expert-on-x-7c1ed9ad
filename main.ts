// Spotlight @crisxai5 entry for make.fun (Node 22, standard library only).
//
// The entry is the X post itself, so this program does one small, exact job:
// read POST.json from the repository root, check it is a JSON object naming
// a post address under a `url` string, and copy its bytes unchanged to
// /output/POST.json, where the house gate reads them. Nothing else is written
// and nothing about the post is scored from here: the house reads the post
// from X and its counts through FxTwitter.
//
// Determinism: the output is a byte-for-byte copy of the input file, so the
// two grader runs write identical bytes. No network, no clock, no files
// outside the repository.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const POST_FILE = "POST.json";

const sourcePath = join(BOT_DIR, POST_FILE);
const targetPath = join(OUTPUT_DIR, POST_FILE);

let raw: Buffer;
try {
  raw = readFileSync(sourcePath);
} catch (err) {
  console.error(`POST.json could not be read from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}

// Validate the shape the gate expects: a JSON object with a `url` string.
// An empty url is still a string: the gate refuses the placeholder, which is
// the correct outcome until the real post address is filled in.
let parsed: unknown;
try {
  parsed = JSON.parse(raw.toString("utf8"));
} catch (err) {
  console.error(`POST.json is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}

if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
  console.error("POST.json must be a JSON object, e.g. {\"url\": \"https://x.com/<handle>/status/<id>\"}");
  process.exit(1);
}

if (typeof (parsed as Record<string, unknown>).url !== "string") {
  console.error("POST.json must carry a `url` string naming the X post");
  process.exit(1);
}

// When a real address is filled in, it must look like an X post address:
// https://x.com/<handle>/status/<digits> (twitter.com and www./mobile.
// prefixes pass too). The empty placeholder is left alone so the gate,
// not this program, refuses it.
const url = (parsed as Record<string, unknown>).url as string;
const postPattern = /^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/[^/]+\/status\/\d+$/;
const iWebPattern = /^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/i\/web\/status\/\d+$/;
if (url !== "" && !postPattern.test(url) && !iWebPattern.test(url)) {
  console.error(`POST.json url does not look like an X post address: ${url}`);
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  writeFileSync(targetPath, raw);
} catch (err) {
  console.error(`POST.json could not be written to ${OUTPUT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
