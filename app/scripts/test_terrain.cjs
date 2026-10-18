const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.argv[2] || 'http://127.0.0.1:8000/';
const out = process.argv[3] || '/tmp/georef-lidar-validation';
fs.mkdirSync(out, {recursive: true});
(async () => {
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}});
  const page = await context.newPage();
  const responses = [], errors = [], failures = [], requestUrls = [];
  const terrainUrl = url => url.includes('services.nconemap.gov') && url.includes('/exportImage?');
  page.on('response', response => {if (terrainUrl(response.url())) responses.push(response);});
  page.on('request', request => requestUrls.push(request.url()));
  page.on('pageerror', error => errors.push(error.message));
  page.on('requestfailed', request => failures.push(request.failure().errorText));
  const terrainImages = 'img.leaflet-tile[src*="services.nconemap.gov"]';
  const loaded = () => page.waitForFunction(() => document.getElementById('terrain-status').textContent.endsWith(': loaded.'), null, {timeout: 60000});
  const result = {base, checkedAt: new Date().toISOString(), tests: []};
  try {
    await page.goto(base);
    assert.equal(await page.locator('#visible').isChecked(), false);
    assert.equal(await page.locator('#terrain').inputValue(), 'none');
    assert.equal(await page.locator(terrainImages).count(), 0);
    assert.equal(requestUrls.filter(terrainUrl).length, 0);
    assert.equal(await page.locator('#terrain-opacity').isDisabled(), true);
    assert.equal(await page.locator('#terrain-key').isVisible(), false);
    result.tests.push('LiDAR defaults off without terrain requests; opacity disabled and legend hidden');
    await page.locator('#terrain').selectOption('hillshade');
    await loaded();
    assert.equal(await page.locator('#terrain-location').inputValue(), 'eno');
    await page.locator('#terrain-location').selectOption('state');
    await page.waitForTimeout(400);
    await loaded();
    assert.ok(await page.locator(terrainImages + '.leaflet-tile-loaded').count() > 0);
    assert.match(await page.locator('#terrain-hint').textContent(), /Terrain overview/);
    await page.screenshot({path: `${out}/state-hillshade.png`, fullPage: true});
    result.tests.push('statewide hillshade loads at overview zoom; historical map defaults off');

    await page.locator('#terrain-location').selectOption('eno');
    await loaded();
    await page.waitForTimeout(300);
    assert.ok(await page.locator(terrainImages + '.leaflet-tile-loaded').count() > 0);
    assert.match(await page.locator('.leaflet-control-attribution').textContent(), /NC OneMap/);
    assert.equal(await page.locator('#slope-legend').isVisible(), false);
    await page.screenshot({path: `${out}/eno-hillshade.png`, fullPage: true});
    const first = responses.find(response => response.url().includes('DEM03_hillshade'));
    const png = await first.body();
    assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
    fs.writeFileSync(`${out}/hillshade-tile.png`, png);
    result.tests.push('real NC LiDAR hillshade renders near Eno River with source attribution');

    await page.locator('#terrain-opacity').fill('40');
    assert.equal(await page.locator('#terrain-percent').textContent(), '40%');
    assert.equal(await page.locator(terrainImages).first().evaluate(img => img.closest('.leaflet-layer').style.opacity), '0.4');
    await page.locator('#visible').check();
    await page.waitForFunction(() => document.getElementById('layer-status').textContent.endsWith(': loaded.'));
    assert.match(await page.locator('#terrain-hint').textContent(), /Historical map is visible/);
    assert.equal(await page.locator(terrainImages).first().evaluate(img => img.closest('.leaflet-layer').style.zIndex), '2');
    assert.equal(await page.locator('img[src*="/history/wms"]').first().evaluate(img => img.closest('.leaflet-layer').style.zIndex), '3');
    await page.locator('#visible').uncheck();
    await page.locator('#terrain-opacity').fill('100');
    result.tests.push('independent terrain opacity, historical comparison and layer order');

    await page.locator('#terrain').selectOption('slope');
    await loaded();
    assert.equal(await page.locator('#slope-legend').isVisible(), true);
    assert.match(await page.locator('#slope-legend').textContent(), /90°.*0°/s);
    await page.waitForTimeout(300);
    await page.screenshot({path: `${out}/eno-slope.png`, fullPage: true});
    const slope = responses.find(response => response.url().includes('DEM03_slope'));
    fs.writeFileSync(`${out}/slope-tile.png`, await slope.body());
    result.tests.push('real slope imagery and original provider legend in degrees');

    const beforeZoom = new Set(responses.map(response => response.url()));
    await Promise.all([
      page.waitForResponse(response => terrainUrl(response.url()) && !beforeZoom.has(response.url())),
      page.locator('.leaflet-control-zoom-in').click()
    ]);
    await loaded();
    const beforePan = new Set(responses.map(response => response.url()));
    const box = await page.locator('#map').boundingBox();
    await Promise.all([
      page.waitForResponse(response => terrainUrl(response.url()) && !beforePan.has(response.url())),
      (async () => {
        await page.mouse.move(box.x + box.width * .65, box.y + box.height * .35);
        await page.mouse.down();
        await page.mouse.move(box.x + box.width * .2, box.y + box.height * .35, {steps: 12});
        await page.mouse.up();
      })()
    ]);
    await loaded();
    result.tests.push('detail zoom and drag request new Web Mercator terrain BBOX tiles');

    await page.locator('#terrain').selectOption('hillshade');
    await loaded();
    for (const example of ['french-broad', 'haw', 'neuse']) {
      await page.locator('#terrain-location').selectOption(example);
      await page.waitForTimeout(400);
      await loaded();
      assert.ok(await page.locator(terrainImages + '.leaflet-tile-loaded').count() > 0);
    }
    result.tests.push('western NC, Haw and Neuse public navigation examples load terrain');
    await page.locator('#terrain').selectOption('none');
    assert.equal(await page.locator(terrainImages).count(), 0);
    assert.equal(await page.locator('#terrain-key').isVisible(), false);
    assert.equal(await page.locator('#terrain-opacity').isDisabled(), true);
    assert.ok(await page.locator('img[src*="tile.openstreetmap.org"]').count() > 0);
    result.tests.push('terrain off preserves basemap and clears legend');

    assert.deepEqual(errors, []);
    assert.deepEqual(failures.filter(error => error !== 'net::ERR_ABORTED'), []);
    assert.ok(requestUrls.filter(url => !url.startsWith('http://127.0.0.1')).every(url => url.startsWith('https:')));
    for (const response of responses) {
      assert.equal(response.status(), 200);
      assert.match(response.headers()['content-type'], /^image\/png/);
      assert.equal(response.request().redirectedFrom(), null);
      const params = new URL(response.url()).searchParams;
      assert.equal(params.get('bboxSR'), '3857');
      assert.equal(params.get('imageSR'), '3857');
      assert.equal(params.get('size'), '512,512');
      const [west, south, east, north] = params.get('bbox').split(',').map(Number);
      assert.ok(west < east && south < north && west < -8000000 && north > 3500000);
      assert.ok(Math.abs((east - west) - (north - south)) < .01);
    }
    result.liveTerrainResponses = responses.length;
    result.tests.push('PNG responses, meter BBOX ordering, normal HTTPS/TLS and no unexpected request or script errors');

    await page.route('**/DEM03_*/ImageServer/exportImage?**', route => route.abort('connectionrefused'));
    await page.locator('#terrain').selectOption('slope');
    await page.waitForFunction(() => /failed|unavailable/.test(document.getElementById('terrain-status').textContent));
    assert.ok(await page.locator('img[src*="tile.openstreetmap.org"]').count() > 0);
    await page.unroute('**/DEM03_*/ImageServer/exportImage?**');
    await page.locator('#retry').click();
    await loaded();
    result.tests.push('terrain service outage leaves basemap usable; retry recovers');

    await page.locator('#terrain-location').selectOption('state');
    await page.waitForTimeout(400);
    await loaded();
    assert.ok(await page.locator(terrainImages + '.leaflet-tile-loaded').count() > 0);
    await page.screenshot({path: `${out}/state-slope.png`, fullPage: true});
    await page.locator('#inspect').click();
    await loaded();
    result.tests.push('statewide slope loads; Inspect here loads detailed terrain');
    await page.setViewportSize({width: 390, height: 844});
    await page.waitForTimeout(400);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({path: `${out}/mobile.png`, fullPage: true});
    result.tests.push('mobile controls fit without horizontal overflow');
    fs.writeFileSync(`${out}/results.json`, JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.log('State:', await page.locator('#terrain-status').textContent());
    console.log('Requests failed:', failures);
    await page.screenshot({path: `${out}/failure.png`, fullPage: true});
    throw error;
  } finally {await browser.close();}
})().catch(error => {console.error(error); process.exitCode = 1;});
