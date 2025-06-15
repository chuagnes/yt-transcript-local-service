import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';
import clipboard from 'clipboardy';

const outputPath = path.resolve('./cookies.txt');
const envPath = path.resolve('./.env');

// Required cookies for authenticated YouTube access
const requiredCookieNames = ['SID', 'HSID', 'SSID', 'SAPISID', 'APISID', 'LOGIN_INFO', 'VISITOR_INFO1_LIVE', 'YSC'];

(async () => {
  const browser = await puppeteer.connect({
    browserURL: 'http://localhost:9222',
  });

  const page = await browser.newPage();
  await page.goto('https://youtube.com', { waitUntil: 'networkidle2' });

  console.log('🔓 Please log in to YouTube in the connected Chrome window...');
  await new Promise(resolve => setTimeout(resolve, 20000)); // 20 seconds

  const cookies = await page.cookies();
  const cookieMap = new Map(cookies.map(c => [c.name, c]));

  const missing = requiredCookieNames.filter(name => !cookieMap.has(name));
  if (missing.length) {
    console.error(`❌ Missing required cookies: ${missing.join(', ')}`);
    process.exit(1);
  }

  const netscapeFormatted = cookies.map(cookie => {
    const domain = cookie.domain.startsWith('.') ? cookie.domain : '.' + cookie.domain;
    const flag = cookie.domain.startsWith('.') ? 'TRUE' : 'FALSE';
    const path = cookie.path || '/';
    const secure = cookie.secure ? 'TRUE' : 'FALSE';
    const expires = cookie.expires || 0;

    return [
      domain,
      flag,
      path,
      secure,
      expires,
      cookie.name,
      cookie.value
    ].join('\t');
  });

  const header = '# Netscape HTTP Cookie File\n';
  fs.writeFileSync(outputPath, header + netscapeFormatted.join('\n'));
  console.log(`✅ Cookies saved to ${outputPath}`);

  const cookieBuffer = fs.readFileSync(outputPath);
  const base64 = cookieBuffer.toString('base64');
  await clipboard.write(base64);

  console.log('\n📋 Base64 cookie copied to clipboard.');

  // Update .env
  let envContent = '';
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, 'utf-8');
    envContent = envContent.replace(/^YOUTUBE_COOKIES_BASE64=.*$/m, '').trim();
  }

  const newEnvLine = `YOUTUBE_COOKIES_BASE64=${base64}`;
  envContent = (envContent + '\n' + newEnvLine).trim() + '\n';
  fs.writeFileSync(envPath, envContent);

  console.log(`✅ .env file updated at ${envPath}`);
  await browser.disconnect();
})();