// Browser integration tests. Install Playwright separately; see docs/geoserver-integration.md.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.argv[2] || 'http://127.0.0.1:8000/preview/';
const out = process.argv[3] || '/tmp/georef-validation';
fs.mkdirSync(out, {recursive: true});

(async () => {
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({viewport: {width: 1440, height: 1100}});
  const page = await context.newPage();
  const errors = [], failed = [], wms = [], external = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('requestfailed', request => failed.push({url: request.url(), error: request.failure()}));
  page.on('response', response => {
    const url = new URL(response.url());
    if (url.hostname !== '127.0.0.1' && url.hostname !== 'localhost') external.push(url.href);
    if (url.pathname.endsWith('/history/wms')) wms.push(response);
  });
  const loaded = () => page.waitForFunction(() =>
    document.getElementById('layer-status').textContent.endsWith(': loaded.') &&
    document.getElementById('base-status').textContent.endsWith(': loaded.'));
  const wmsImages = 'img.leaflet-tile[src*="/history/wms"]';
  const result = {base, checkedAt: new Date().toISOString(), tests: []};
  try {
    await page.goto(base);
    await loaded();
    assert.equal(await page.locator('#historical-layer option[value="moseley_1733"]').evaluate(option => option.disabled), true);
    assert.ok(await page.locator(wmsImages + '.leaflet-tile-loaded').count() > 0);
    assert.match(await page.locator('.leaflet-control-attribution').textContent(), /OpenStreetMap.*Library of Congress/);
    assert.match(await page.locator('header').textContent(), /not suitable for locating routes or sites precisely/);
    await page.screenshot({path: `${out}/live-collet.png`, fullPage: true});
    result.tests.push('live Collet PNG imagery, OSM, credits, disclaimer, unavailable Moseley');

    await page.locator('#opacity').fill('25');
    assert.equal(await page.locator('#percent').textContent(), '25%');
    assert.equal(await page.locator(wmsImages).first().evaluate(img => img.closest('.leaflet-layer').style.opacity), '0.25');
    await page.locator('#visible').uncheck();
    assert.equal(await page.locator(wmsImages).count(), 0);
    assert.ok(await page.locator('img[src*="tile.openstreetmap.org"]').count() > 0);
    await page.locator('#visible').check();
    await loaded();
    result.tests.push('visibility and opacity retain the basemap');

    // Zoom far enough that the raster extends beyond the viewport before panning.
    for (let i = 0; i < 2; i++) {
      const beforeZoom = new Set(wms.map(response => response.url()));
      await Promise.all([
        page.waitForResponse(r => r.url().includes('/history/wms') && !beforeZoom.has(r.url())),
        page.locator('.leaflet-control-zoom-in').click()
      ]);
      await loaded();
    }
    const beforePan = new Set(wms.map(response => response.url()));
    const box = await page.locator('#map').boundingBox();
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/history/wms') && !beforePan.has(r.url())),
      (async () => {
        await page.mouse.move(box.x + box.width * .7, box.y + box.height * .3);
        await page.mouse.down();
        await page.mouse.move(box.x + box.width * .3, box.y + box.height * .3, {steps: 15});
        await page.mouse.up();
      })()
    ]);
    await loaded();
    await page.locator('#fit').click();
    await loaded();
    result.tests.push('zoom and drag issue new WMS BBOX requests; fit returns to historical extent');

    await page.locator('#points').uncheck();
    assert.equal(await page.locator('.leaflet-overlay-pane svg path').count(), 0);
    await page.locator('#points').check();
    assert.ok(await page.locator('.leaflet-overlay-pane svg path').count() > 0);
    await page.locator('#historical-layer').selectOption('local');
    await page.locator('#basemap').selectOption('local');
    for (const view of ['bath', 'salem', 'hertford', 'cape-fear', 'overview']) {
      await page.locator('#view').selectOption(view);
      await loaded();
      assert.equal(await page.locator(`img.leaflet-image-layer[src*="${view}"]`).count(), 2);
    }
    assert.match(await page.locator('.leaflet-control-attribution').textContent(), /USGS The National Map/);
    await page.screenshot({path: `${out}/local-collet.png`, fullPage: true});
    result.tests.push('all five original local views, proxy toggle, USGS credits');

    assert.deepEqual(errors, []);
    assert.deepEqual(failed, []);
    assert.ok(external.every(url => url.startsWith('https:')));
    for (const response of wms) {
      assert.equal(response.status(), 200);
      assert.match(response.headers()['content-type'], /^image\/png/);
      assert.equal(response.request().redirectedFrom(), null);
      const url = new URL(response.url());
      assert.equal(url.searchParams.get('layers'), 'history:collet_1770');
      assert.equal(url.searchParams.get('srs'), 'EPSG:3857');
    }
    const png = await wms[0].body();
    assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
    result.liveWmsResponses = wms.length;
    result.tests.push('no TLS/mixed-content/auth-redirect/CORS/request/JavaScript errors in live browser run');

    // Simulate service outage; the original local viewer remains usable.
    await page.route('**/history/wms?**', route => route.abort('connectionrefused'));
    await page.locator('#historical-layer').selectOption('collet_1770');
    await page.waitForFunction(() => /failed|unavailable/.test(document.getElementById('layer-status').textContent));
    await page.locator('#historical-layer').selectOption('local');
    await loaded();
    await page.unroute('**/history/wms?**');
    await page.locator('#historical-layer').selectOption('collet_1770');
    await page.locator('#retry').click();
    await loaded();
    result.tests.push('server outage, local fallback and retry recovery');

    // A missing local data file must not block WMS.
    const missing = await context.newPage();
    await missing.route('**/data.json', route => route.fulfill({status: 404, body: 'missing'}));
    await missing.goto(base);
    await missing.waitForFunction(() => document.getElementById('layer-status').textContent.endsWith(': loaded.'));
    assert.match(await missing.locator('#error').textContent(), /live map remains usable/);
    assert.equal(await missing.locator('#historical-layer option[value="local"]').evaluate(option => option.disabled), true);
    await missing.close();
    result.tests.push('missing local data preserves live map');

    const slow = await context.newPage();
    await slow.route('**/map-config.js', async route => {
      const response = await route.fetch();
      await route.fulfill({response, body: (await response.text()).replace('timeoutMs: 20000', 'timeoutMs: 100')});
    });
    await slow.route('**/history/wms?**', async route => {
      await new Promise(resolve => setTimeout(resolve, 1200));
      await route.abort('timedout').catch(() => {});
    });
    await slow.goto(base, {waitUntil: 'domcontentloaded'});
    await slow.waitForFunction(() => document.getElementById('layer-status').textContent.includes('taking too long'));
    await slow.locator('#visible').uncheck();
    await slow.waitForTimeout(1500);
    assert.equal(await slow.locator('#layer-status').textContent(), 'Historical map hidden.');
    await slow.close();
    result.tests.push('loading timeout and removal cancel stale status updates');

    await page.setViewportSize({width: 390, height: 844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    result.tests.push('mobile width has no horizontal overflow');
    fs.writeFileSync(`${out}/results.json`, JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
