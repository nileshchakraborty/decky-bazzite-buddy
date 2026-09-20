export const MAX_RELEASE_PREVIEW_LINES = 48;
export const MAX_RELEASE_PREVIEW_CHARACTERS = 5000;

const TRUNCATION_NOTICE =
  "_Preview limited for Quick Access stability. Use View All Release Notes for the complete changelog._";

/**
 * Bound release Markdown before parsing so Quick Access never receives an
 * enormous hidden DOM. The complete release remains available through the
 * plugin's View All Release Notes action.
 *
 * @param {unknown} body
 * @returns {string}
 */
export function createReleasePreview(body) {
  if (typeof body !== "string" || body.length === 0) return "";

  const lines = body.split(/\r?\n/);
  const preview = [];
  let characterCount = 0;
  let truncated = false;

  for (const line of lines) {
    const separatorLength = preview.length === 0 ? 0 : 1;
    if (
      preview.length >= MAX_RELEASE_PREVIEW_LINES ||
      characterCount + separatorLength + line.length >
        MAX_RELEASE_PREVIEW_CHARACTERS
    ) {
      truncated = true;
      break;
    }

    preview.push(line);
    characterCount += separatorLength + line.length;
  }

  if (preview.length === 0) {
    preview.push(body.slice(0, MAX_RELEASE_PREVIEW_CHARACTERS));
    truncated = body.length > MAX_RELEASE_PREVIEW_CHARACTERS;
  } else if (preview.length < lines.length) {
    truncated = true;
  }

  if (!truncated) return preview.join("\n");

  const openFence =
    preview.filter((line) => line.trimStart().startsWith("```")).length % 2 ===
    1;
  if (openFence) preview.push("```");

  preview.push("", "---", "", TRUNCATION_NOTICE);
  return preview.join("\n");
}
