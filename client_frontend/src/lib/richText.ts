import DOMPurify from "dompurify";

const ALLOWED_TAGS = [
  "p",
  "br",
  "strong",
  "b",
  "em",
  "i",
  "u",
  "s",
  "ul",
  "ol",
  "li",
  "h2",
  "h3",
  "blockquote",
  "a",
];

const ALLOWED_ATTR = ["href", "target", "rel"];

export function isRichHtml(content: string) {
  return /<[a-z][\s\S]*>/i.test(content.trim());
}

export function plainTextToHtml(content: string) {
  const trimmed = content.trim();
  if (!trimmed) return "";
  if (isRichHtml(trimmed)) return trimmed;

  return trimmed
    .split(/\n{2,}/)
    .map((paragraph) => `<p>${paragraph.replace(/\n/g, "<br>")}</p>`)
    .join("");
}

export function sanitizeRichHtml(content: string) {
  const html = isRichHtml(content) ? content : plainTextToHtml(content);
  if (!html) return "";

  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ADD_ATTR: ["target"],
  });
}
