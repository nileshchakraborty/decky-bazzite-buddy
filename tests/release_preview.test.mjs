import assert from "node:assert/strict";
import test from "node:test";

import {
  createReleasePreview,
  MAX_RELEASE_PREVIEW_CHARACTERS,
  MAX_RELEASE_PREVIEW_LINES,
} from "../src/releasePreview.js";

test("keeps a short release body unchanged", () => {
  const body = "# Release\n\n- Fix one\n- Fix two";
  assert.equal(createReleasePreview(body), body);
});

test("bounds a release body by line count", () => {
  const body = Array.from(
    { length: MAX_RELEASE_PREVIEW_LINES + 10 },
    (_, index) => `- Change ${index}`,
  ).join("\n");
  const preview = createReleasePreview(body);

  assert.match(preview, /Preview limited for Quick Access stability/);
  assert.doesNotMatch(preview, /Change 57/);
});

test("bounds a release body by character count", () => {
  const body = "x".repeat(MAX_RELEASE_PREVIEW_CHARACTERS + 100);
  const preview = createReleasePreview(body);

  assert.match(preview, /Preview limited for Quick Access stability/);
  assert.equal(preview.match(/^x+/)?.[0].length, MAX_RELEASE_PREVIEW_CHARACTERS);
});

test("closes an open fenced code block when truncating", () => {
  const body = [
    "```text",
    ...Array.from({ length: MAX_RELEASE_PREVIEW_LINES }, () => "content"),
  ].join("\n");
  const preview = createReleasePreview(body);

  assert.equal(
    preview.split("\n").filter((line) => line.startsWith("```")).length % 2,
    0,
  );
});

test("handles a missing release body", () => {
  assert.equal(createReleasePreview(undefined), "");
});
