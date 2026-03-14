import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { globby } from 'globby';
import * as cheerio from 'cheerio';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');

const args = new Set(process.argv.slice(2));
const DRY_RUN = args.has('--dry-run');
const WRITE = args.has('--write');

if (DRY_RUN === WRITE) {
  console.error('Usage: node tools/wrap-site.mjs --dry-run | --write');
  process.exit(2);
}

const SKIP_DIRS = new Set([
  'node_modules',
  '.git',
  '__pycache__',
  'tools',
  '_site',
  'dist',
  'build'
]);

function shouldSkip(filePath) {
  const rel = path.relative(repoRoot, filePath);
  const parts = rel.split(path.sep);
  return parts.some(p => SKIP_DIRS.has(p));
}

function ensureHeadAssets($) {
  const head = $('head');
  if (!head.length) return { changed: false, notes: ['missing <head>'] };

  let changed = false;

  const wantLinks = [
    { tag: 'link', attr: 'href', value: '/css/styles.css', html: '<link rel="stylesheet" href="/css/styles.css">' },
  ];
  const wantScripts = [
    { src: 'https://static.elfsight.com/platform/platform.js', html: '<script src="https://static.elfsight.com/platform/platform.js" defer></script>' },
    { src: '/js/site.js', html: '<script src="/js/site.js" defer></script>' }
  ];

  for (const w of wantLinks) {
    const exists = head.find(`${w.tag}[${w.attr}="${w.value}"]`).length > 0;
    if (!exists) {
      head.append(`\n  ${w.html}`);
      changed = true;
    }
  }

  for (const w of wantScripts) {
    const exists = head.find(`script[src="${w.src}"]`).length > 0;
    if (!exists) {
      head.append(`\n  ${w.html}`);
      changed = true;
    }
  }

  // Remove duplicate site.js / elfsight script tags if any
  const dedupeSrcs = new Set(['/js/site.js', 'https://static.elfsight.com/platform/platform.js']);
  for (const src of dedupeSrcs) {
    const nodes = head.find(`script[src="${src}"]`).toArray();
    if (nodes.length > 1) {
      for (let i = 1; i < nodes.length; i++) {
        $(nodes[i]).remove();
        changed = true;
      }
    }
  }

  return { changed, notes: [] };
}

function ensureRatingWidget($) {
  const body = $('body');
  if (!body.length) return { changed: false, notes: ['missing <body>'] };

  const existing = $('#rating-widget');
  if (existing.length) return { changed: false, notes: [] };

  body.append(`\n\n<div id="rating-widget" style="position:fixed;right:14px;bottom:14px;z-index:9999;max-width:220px;pointer-events:auto;">\n  <div class="elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875"></div>\n</div>\n`);
  return { changed: true, notes: [] };
}

function ensureReviewsEmbed($, relPath) {
  // Rule: reviews list embedded before FAQ on every page except booking/form page.
  if (relPath.replace(/\\/g, '/').startsWith('book-now/')) return { changed: false, notes: [] };

  if ($('#reviews-embed').length) return { changed: false, notes: [] };

  const faq = $('#faq');
  if (faq.length) {
    faq.before(`\n<section id="reviews-embed" class="shell">\n  <div class="elfsight-app-b029cad3-6f49-425c-9793-f556870797bb"></div>\n</section>\n`);
    return { changed: true, notes: [] };
  }

  // If no #faq, do nothing (avoid guessing placement on non-standard pages)
  return { changed: false, notes: ['no #faq anchor; skipped reviews embed'] };
}

async function main() {
  const htmlFiles = await globby(['**/*.html'], {
    cwd: repoRoot,
    absolute: true,
    gitignore: true,
  });

  const candidates = htmlFiles.filter(f => !shouldSkip(f));

  let changedFiles = 0;
  const notesByFile = [];

  for (const absPath of candidates) {
    const rel = path.relative(repoRoot, absPath);
    const raw = await fs.readFile(absPath, 'utf8');
    const $ = cheerio.load(raw, { decodeEntities: false });

    const notes = [];
    let changed = false;

    const headRes = ensureHeadAssets($);
    changed ||= headRes.changed;
    notes.push(...headRes.notes);

    const ratingRes = ensureRatingWidget($);
    changed ||= ratingRes.changed;
    notes.push(...ratingRes.notes);

    const reviewsRes = ensureReviewsEmbed($, rel);
    changed ||= reviewsRes.changed;
    notes.push(...reviewsRes.notes);

    if (changed) {
      changedFiles++;
      if (WRITE) {
        await fs.writeFile(absPath, $.html(), 'utf8');
      }
    }

    if (notes.length) notesByFile.push({ rel, notes });
  }

  console.log(`wrap-site: scanned ${candidates.length} HTML files`);
  console.log(`wrap-site: ${WRITE ? 'updated' : 'would update'} ${changedFiles} file(s)`);

  const noisy = notesByFile.slice(0, 30);
  if (noisy.length) {
    console.log('\nNotes (first 30):');
    for (const entry of noisy) {
      console.log(`- ${entry.rel}: ${entry.notes.join('; ')}`);
    }
  }

  if (DRY_RUN) {
    console.log('\nDry run only. To apply changes: npm run wrap:write');
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
