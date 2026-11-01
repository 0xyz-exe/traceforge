const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const http = require('http');

function getAuthToken() {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      email: 'demo@traceforge.lan',
      password: 'Password123!'
    });

    const req = http.request('http://127.0.0.1:8002/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const data = JSON.parse(body);
          if (data.access_token) {
            resolve(data.access_token);
          } else {
            reject(new Error('No access_token in response: ' + body));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function main() {
  const screenshotsDir = path.join(__dirname, '..', 'docs', 'screenshots');
  fs.mkdirSync(screenshotsDir, { recursive: true });

  const token = await getAuthToken();
  console.log('Obtained TraceForge access_token for SecOps session');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: 'dark'
  });

  const page = await context.newPage();

  // Navigate to login first to set localStorage
  await page.goto('http://127.0.0.1:3456/login', { waitUntil: 'networkidle' });
  await page.evaluate(t => localStorage.setItem('access_token', t), token);

  // 1. Metrics Dashboard
  console.log('Capturing 01_metrics_dashboard.png...');
  await page.goto('http://127.0.0.1:3456/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  const out1 = path.join(screenshotsDir, '01_metrics_dashboard.png');
  await page.screenshot({ path: out1 });
  console.log(`Saved: ${out1} (${fs.statSync(out1).size} bytes)`);

  // 2. Trace Waterfall
  console.log('Capturing 02_trace_waterfall.png...');
  await page.goto('http://127.0.0.1:3456/traces/4bf92f3577b34da6a3ce929d0e0e4736', { waitUntil: 'networkidle' });
  await page.waitForSelector('text=Span Waterfall');
  await page.waitForTimeout(1500);
  const out2 = path.join(screenshotsDir, '02_trace_waterfall.png');
  await page.screenshot({ path: out2 });
  console.log(`Saved: ${out2} (${fs.statSync(out2).size} bytes)`);

  // 3. Log Explorer
  console.log('Capturing 03_log_explorer.png...');
  await page.goto('http://127.0.0.1:3456/logs', { waitUntil: 'networkidle' });
  await page.waitForSelector('text=Logs');
  await page.waitForTimeout(1500);
  const out3 = path.join(screenshotsDir, '03_log_explorer.png');
  await page.screenshot({ path: out3 });
  console.log(`Saved: ${out3} (${fs.statSync(out3).size} bytes)`);

  // 4. Incidents
  console.log('Capturing 04_incidents.png...');
  await page.goto('http://127.0.0.1:3456/incidents', { waitUntil: 'networkidle' });
  await page.waitForSelector('text=Incidents');
  await page.waitForTimeout(1500);
  const out4 = path.join(screenshotsDir, '04_incidents.png');
  await page.screenshot({ path: out4 });
  console.log(`Saved: ${out4} (${fs.statSync(out4).size} bytes)`);

  // 5. Login
  console.log('Capturing 05_login.png...');
  await page.evaluate(() => localStorage.clear());
  await page.goto('http://127.0.0.1:3456/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', 'secops@traceforge.internal');
  await page.fill('input[type="password"]', 'SuperSecretPass2026!');
  await page.waitForTimeout(800);
  const out5 = path.join(screenshotsDir, '05_login.png');
  await page.screenshot({ path: out5 });
  console.log(`Saved: ${out5} (${fs.statSync(out5).size} bytes)`);

  await browser.close();
  console.log('All 5 screenshots successfully captured!');
}

main().catch(err => {
  console.error('Capture failed:', err);
  process.exit(1);
});
