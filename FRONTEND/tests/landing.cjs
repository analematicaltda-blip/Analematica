const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.SGA_WEB_URL || 'http://127.0.0.1:18090';
(async () => {
 const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || undefined,headless:true,args:['--no-sandbox']});
 const results=[];
 try {
  for (const width of [1440,768,390,320]) {
   const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce',serviceWorkers:'block'});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',r=>{
    const u=new URL(r.request().url());
    if(u.pathname.includes('/api/')) return r.fulfill({json:u.pathname.endsWith('/landing')?{}:[]});
    if(u.origin!==new URL(base).origin) return r.abort();
    return r.continue();
   });
   await page.addInitScript(()=>{if(window.top===window)localStorage.setItem('sgacd_cookie_consent','essential_only');});
   await page.goto(base+'/index.html');
   await page.waitForSelector('.sga-carousel-slide');
   assert.equal(await page.locator('#carrusel-moderno').evaluate(e=>e.nextElementSibling.id),'admin-territorial-control','Requested search block must follow image carousel');
   const before=await page.locator('#admin-jurisdiction option').count();
   assert.equal(before,3,'Preserve territorial options');
   await page.locator('#admin-jurisdiction').selectOption('departamental');
   assert.equal(await page.locator('#admin-jurisdiction').inputValue(),'departamental');
   await page.locator('#admin-activity-target').selectOption('arpa');
   assert.equal(await page.locator('#admin-activity-target').inputValue(),'arpa');
   await page.evaluate(()=>window.SGAModernCarousel.goToSlide(3));
   await page.evaluate(()=>window.SGAModernCarousel.init('modern-carousel-container',[{title:'Prueba <img src=x onerror=alert(1)>',subtitle:'Descripción',tag:'Actividad',imageUrl:'assets/no-such-image.webp'}]));
   await page.locator('#sga-carousel-next').click();
   assert.equal(await page.locator('.sga-carousel-slide.active').count(),1,'Reinitialization must reset active slide');
   assert.equal(await page.locator('#sga-carousel-indicator').textContent(),'2 / 10');
   await page.locator('#sga-carousel-prev').focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#sga-carousel-indicator').textContent(),'1 / 10');
   assert.equal(await page.locator('.slide-floating-title img').count(),0,'Admin text must be escaped');
   await page.waitForFunction(()=>document.querySelector('.sga-carousel-slide img').complete);
   const image=await page.locator('.sga-carousel-slide img').first().evaluate(e=>({width:e.naturalWidth,src:e.getAttribute('src')}));
   assert.ok(image.width>0,'A visible local fallback must survive image failures');
   const report=await page.evaluate(()=>{
    const section=document.querySelector('#admin-territorial-control');const input=section.querySelector('select');const c=getComputedStyle(input);
    return {width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,formOverflow:section.scrollWidth>section.clientWidth,background:c.backgroundColor,color:c.color,radius:parseFloat(c.borderRadius),sections:document.querySelectorAll('main > section').length};
   });
   assert.equal(report.sections,12,'Keep every landing section');assert.equal(report.overflow,false);assert.equal(report.formOverflow,false);assert.ok(report.radius>=12);
   assert.notEqual(report.background,'rgb(255, 255, 255)');assert.deepEqual(errors,[]);
   results.push(report);
   if(process.env.SGA_SCREENSHOTS){await page.locator('#carrusel-moderno').scrollIntoViewIfNeeded();await page.screenshot({path:process.env.SGA_SCREENSHOTS+'/landing-'+width+'.png'});}
   await page.close();
  }
  console.log(JSON.stringify(results,null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
