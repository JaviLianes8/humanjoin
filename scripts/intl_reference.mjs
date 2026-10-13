// Record what Intl.ListFormat of this Node build prints, as a reference for the tests.
//
// Writes tests/upstream/intl-node.json (not committed; tests skip while it is absent).
// The tags are every locale of src/humanjoin/_cldr.json plus the hand-written probes
// below. The probe words for the contextual Spanish and Hebrew rules are hand-written too.
//
//     node scripts/intl_reference.mjs

import { readFileSync, writeFileSync } from "node:fs";

const root = new URL("..", import.meta.url);
const table = JSON.parse(readFileSync(new URL("src/humanjoin/_cldr.json", root), "utf8"));

const PROBES = [
  "en-US", "EN-us", "en-GB", "en-IN", "en-AU", "en-Cyrl", "es-MX", "es-419", "es-US",
  "pt-BR", "pt-AO", "fr-CA", "de-AT-1996", "de-CH-u-co-phonebk", "zh-CN", "zh-TW",
  "zh-HK", "zh-SG", "zh-MO", "yue-CN", "sr-RS", "sr-ME", "sr-BA", "pa-PK", "pa-IN",
  "az-IR", "uz-AF", "kk-CN", "ku-IQ", "ms-CC", "mn-CN", "sd-IN", "ha-CM", "iw", "in",
  "tl", "mo", "no", "heb", "eng", "spa", "xx", "en_US",
];
const TYPES = ["conjunction", "disjunction", "unit"];
const STYLES = ["long", "short", "narrow"];
// Items carry braces so a formatter that substitutes into its own output is caught.
const ITEMS = ["p{0}", "q{1}", "r", "s"];
const SPANISH = [
  "", " i", "i", "I", "Ícaro", "hi", "Hi", "hI", "hia", "hIa", "hie", "hiE", "hio", "hiu",
  "hielo", "hijo", "o", "O", "ho", "Ho", "hO", "hoja", "8", "80", "11", "110", "11 años",
  "11a", "1", "ola", "uva", "y", "e",
];
const cp = (...points) => String.fromCodePoint(...points);
const HEBREW = ["", " " + cp(0x5d0), "ABC", "1", cp(0x5d1, 0x5d9, 0x5ea), cp(0x5be), cp(0xfb1d), cp(0x1f600), "-x"];

function format(tag, type, style, items) {
  try {
    const formatter = new Intl.ListFormat(tag, { type, style });
    return [formatter.resolvedOptions().locale, formatter.format(items)];
  } catch (error) {
    return [null, error.name];
  }
}

const cases = [];
for (const tag of [...Object.keys(table.locales).sort(), ...PROBES]) {
  for (const type of TYPES) {
    for (const style of STYLES) {
      for (let n = 0; n <= ITEMS.length; n++) {
        cases.push([tag, type, style, n, ...format(tag, type, style, ITEMS.slice(0, n))]);
      }
    }
  }
}

const contextual = [];
for (const [tag, words] of [["es", SPANISH], ["es-MX", SPANISH], ["he", HEBREW], ["iw", HEBREW]]) {
  for (const type of TYPES) {
    for (const style of STYLES) {
      for (const word of words) {
        for (const items of [["a", word], ["a", "b", word]]) {
          contextual.push([tag, type, style, items, ...format(tag, type, style, items)]);
        }
      }
    }
  }
}

// Code points after which Hebrew "and" takes no hyphen, as inclusive ranges.
const hebrew = [];
const formatter = new Intl.ListFormat("he");
for (let point = 0; point <= 0x10ffff; point++) {
  if (point >= 0xd800 && point <= 0xdfff) continue;
  if (formatter.format([cp(0x5d0), cp(point)]).includes(cp(0x5d5) + "-")) continue;
  const last = hebrew[hebrew.length - 1];
  if (last && last[1] === point - 1) last[1] = point;
  else hebrew.push([point, point]);
}

const { node, icu, cldr, unicode } = process.versions;
const body = { node, icu, cldr, unicode, items: ITEMS, cases, contextual, hebrew };
writeFileSync(new URL("tests/upstream/intl-node.json", root), JSON.stringify(body) + "\n");
console.log(`intl-node.json: ${cases.length} cases, ${contextual.length} contextual`);
