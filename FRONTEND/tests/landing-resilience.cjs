const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=process.env.SGA_WEB_URL||'http://127.0.0.1:18080';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 try{
  for(const missingStyles of [false,true]) for(const width of [1440,390,320]){
   const context=await browser.newContext({viewport:{width,height:1000},serviceWorkers:'block',reducedMotion:'reduce'});
   const page=await context.newPage();
   await page.route('**/*',r=>{
    const u=new URL(r.request().url());
    if(missingStyles && u.pathname.endsWith('/vanguard.css'))return r.abort();
    if(u.pathname.includes('/api/')){
     if(u.pathname.endsWith('/public/events'))return r.fulfill({status:503,json:{detail:'test offline'}});
     return r.fulfill({json:{}});
    }
    if(u.hostname==='images.unsplash.com')return r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="360"><rect width="600" height="360" fill="#12304A"/></svg>'});
    if(u.origin!==new URL(base).origin)return r.abort();
    return r.continue();
   });
   await page.addInitScript(()=>{if(top===window)localStorage.setItem('sgacd_cookie_consent','essential_only')});
   await page.goto(base+'/index.html');
   await page.waitForSelector('.monitor-card');
   assert.equal(await page.locator('.monitor-card').count(),4);
   const gallery=page.locator('.card-gallery-wrapper').first();
   const frame=await gallery.boundingBox();
   assert.ok(frame.height<=240,'Gallery must not stack five photos vertically: '+frame.height);
   const photos=gallery.locator('.card-gallery-img');assert.equal(await photos.count(),5);
   await gallery.locator('.gallery-arrow-btn.next').click();
   await page.waitForTimeout(650);
   const photo2=await photos.nth(1).boundingBox();
   assert.ok(Math.abs(photo2.x-frame.x)<2,'Second photo must align with viewport after Next');
   assert.ok(Math.abs(photo2.width-frame.width)<2,'One photo must fill one viewport');
   await gallery.locator('.gallery-arrow-btn.prev').click();
   await page.waitForTimeout(650);
   assert.ok(Math.abs((await photos.first().boundingBox()).x-frame.x)<2);
   await page.locator('.filter-btn[data-filter="cultura"]').click();assert.equal(await page.locator('.monitor-card').count(),2);
   await page.locator('.filter-btn[data-filter="all"]').click();assert.equal(await page.locator('.monitor-card').count(),4);
   console.log('PASS gallery',width,'five photos, next/previous, filters, missing optional CSS:',missingStyles);
   if(process.env.SGA_SCREENSHOTS && !missingStyles){await page.locator('#monitor-vivo').scrollIntoViewIfNeeded();await page.screenshot({path:process.env.SGA_SCREENSHOTS+'/galleries-'+width+'.png'});}
   await context.close();
  }
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:1000}});
  const page=await context.newPage();await page.goto(base+'/index.html');
  assert.equal(await page.locator('.sga-carousel-slide').count(),10,'Primary carousel must exist before application JavaScript');
  assert.equal(await page.locator('main > section').count(),12);
  // With JavaScript disabled, selector order proves the structure itself was published.
  assert.equal(await page.locator('#carrusel-moderno + #admin-territorial-control').count(),1);
  assert.ok(await page.locator('#modern-carousel-container').boundingBox());
  assert.equal(await page.locator('link[href*="sky-theme.css"]').count(),1);
  const html=await page.content();assert.match(html,/js\/main\.js\?v=[a-f0-9]+/,'Asset URLs need release hashes');
  console.log('PASS static landing: ten slides, search directly below, theme loaded without JavaScript, versioned assets');
  await context.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
