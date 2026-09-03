import { chromium } from 'playwright';

const base = 'https://gsh4124-cyber.github.io/pc-checkup';
const expectedSitemapUrls = 117;
const problems = [];
const assert = (ok, message) => { if (!ok) problems.push(message); };

const sitemapResponse = await fetch(`${base}/sitemap.xml`);
assert(sitemapResponse.ok, `sitemap HTTP ${sitemapResponse.status}`);
const sitemap = await sitemapResponse.text();
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
assert(urls.length === expectedSitemapUrls, `expected ${expectedSitemapUrls} sitemap URLs, got ${urls.length}`);

for (let i = 0; i < urls.length; i += 12) {
  const batch = urls.slice(i, i + 12);
  const results = await Promise.all(batch.map(async url => {
    try {
      const response = await fetch(url, { redirect: 'follow' });
      return { url, ok: response.ok, status: response.status };
    } catch (error) {
      return { url, ok: false, status: 0, error: String(error) };
    }
  }));
  for (const result of results) {
    assert(result.ok, `${result.url}: HTTP ${result.status}${result.error ? ` ${result.error}` : ''}`);
  }
}

const browser = await chromium.launch({ headless: true });
const representative = [
  { path: '/', lang: 'ko', browserLocale: 'ko-KR' },
  { path: '/en/', lang: 'en', browserLocale: 'en-US' },
  { path: '/ja/', lang: 'ja', browserLocale: 'ja-JP' },
  { path: '/zh-CN/', lang: 'zh-CN', browserLocale: 'zh-CN' },
  { path: '/ru/', lang: 'ru', browserLocale: 'ru-RU' },
];

for (const item of representative) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: item.browserLocale });
  const page = await context.newPage();
  const pageErrors = [];
  const externalRequests = new Set();
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.protocol === 'http:' || url.protocol === 'https:') {
      if (url.origin !== 'https://gsh4124-cyber.github.io') externalRequests.add(url.origin);
    }
  });

  const response = await page.goto(`${base}${item.path}`, { waitUntil: 'networkidle', timeout: 30000 });
  assert(response?.ok(), `${item.path}: navigation failed`);
  assert(new URL(page.url()).pathname === `/pc-checkup${item.path}`, `${item.path}: unexpected locale redirect to ${page.url()}`);
  assert((await page.locator('html').getAttribute('lang')) === item.lang, `${item.path}: html lang mismatch: ${await page.locator('html').getAttribute('lang')}`);
  assert(await page.locator('.brand').isVisible(), `${item.path}: brand not visible`);
  assert((await page.locator('#languagePicker').count()) === 1, `${item.path}: canonical language selector must exist exactly once`);
  assert((await page.locator('.lang-switch').count()) === 0, `${item.path}: retired duplicate .lang-switch is still present`);
  assert((await page.locator('header select[aria-label]').count()) === 1, `${item.path}: header contains duplicate language selects`);
  assert((await page.locator('a[href$="checkup.html"]').count()) > 0, `${item.path}: PC checkup entry missing`);
  assert((await page.locator('a[href$="mobile.html"]').count()) > 0, `${item.path}: mobile checkup entry missing`);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  assert(!overflow, `${item.path}: mobile horizontal overflow`);
  assert(pageErrors.length === 0, `${item.path}: page errors: ${pageErrors.join(' | ')}`);
  assert(externalRequests.size === 0, `${item.path}: unexpected external network origins: ${[...externalRequests].join(', ')}`);
  await context.close();
}

for (const path of ['/en/keyboard.html', '/en/mobile.html', '/zh-CN/keyboard.html', '/ru/mobile.html']) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const pageErrors = [];
  const externalRequests = new Set();
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('request', request => {
    const url = new URL(request.url());
    if ((url.protocol === 'http:' || url.protocol === 'https:') && url.origin !== 'https://gsh4124-cyber.github.io') externalRequests.add(url.origin);
  });
  const response = await page.goto(`${base}${path}`, { waitUntil: 'networkidle', timeout: 30000 });
  assert(response?.ok(), `${path}: navigation failed`);
  assert(await page.locator('.brand').isVisible(), `${path}: brand not visible`);
  assert((await page.locator('#languagePicker').count()) === 1, `${path}: canonical language selector must exist exactly once`);
  assert((await page.locator('.lang-switch').count()) === 0, `${path}: retired duplicate .lang-switch is still present`);
  assert((await page.locator('header select[aria-label]').count()) === 1, `${path}: header contains duplicate language selects`);
  assert(pageErrors.length === 0, `${path}: page errors: ${pageErrors.join(' | ')}`);
  assert(externalRequests.size === 0, `${path}: unexpected external network origins: ${[...externalRequests].join(', ')}`);
  await page.close();
}

await browser.close();

if (problems.length) {
  console.error(problems.join('\n'));
  process.exit(1);
}
console.log(`DEVICE CHECKUP production QA passed: ${urls.length} sitemap URLs reachable; representative ko/en/ja/zh-CN/ru mobile surfaces and tool pages had one language selector, no page errors, no horizontal overflow on home surfaces, and no unexpected external network origins.`);
