const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=process.env.SGA_WEB_URL||'http://127.0.0.1:18080';
const expected=['carrusel-moderno','admin-territorial-control','presentacion','partners','hero','monitor-vivo','carrusel-destacados','funcionalidades','faq','planes','oferta-lanzamiento','registro'];
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 try {
  for(const width of [1440,1024,768,390,320]){
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce',serviceWorkers:'block'});
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',r=>{
    const u=new URL(r.request().url());
    if(u.pathname.endsWith('/public/landing'))return r.fulfill({json:{hero_title:'Institución configurada por administrador',hero_subtitle:'Descripción guardada por administrador',hero_video_url:'https://youtu.be/aqz-KE-bpKQ',carousel_slides_json:JSON.stringify([{title:'Portada del administrador',subtitle:'Contenido institucional',tag:'Institución',imageUrl:'assets/images/carousel-fallback.svg'}])}});
    if(u.pathname.includes('/api/'))return r.fulfill({status:503,json:{detail:'test offline'}});
    if(u.origin!==new URL(base).origin)return r.abort();
    return r.continue();
   });
   await page.addInitScript(()=>{if(window===top)localStorage.setItem('sgacd_cookie_consent','essential_only')});
   await page.goto(base+'/index.html');
   await page.waitForFunction(()=>document.querySelector('#hero h1').textContent==='Institución configurada por administrador');
   assert.deepEqual(await page.locator('main > section').evaluateAll(nodes=>nodes.map(n=>n.id)),expected);
   assert.equal(await page.locator('#hero .hero-tagline').textContent(),'Descripción guardada por administrador');
   assert.equal(await page.locator('.slide-floating-title').first().textContent().then(s=>s.trim()),'Portada del administrador');
   assert.equal(await page.locator('#video-container iframe').getAttribute('src'),'https://www.youtube-nocookie.com/embed/aqz-KE-bpKQ');
   const header=page.locator('header[role=banner]');const first=await header.boundingBox();
   assert.ok(first.y>=0 && first.y<20);
   const carousel=await page.locator('#carrusel-moderno').boundingBox();
   assert.ok(carousel.y<140,'No empty screen above primary carousel');
   await page.evaluate(()=>window.scrollTo(0,2000));
   assert.ok(Math.abs((await header.boundingBox()).y-first.y)<1,'Header must float across the page');
   if(width<=1100){
    const menu=page.locator('.mobile-menu-btn');await menu.click();
    assert.equal(await menu.getAttribute('aria-expanded'),'true');
    await page.locator('#landing-navigation a[href="#partners"]').click();
    assert.equal(await menu.getAttribute('aria-expanded'),'false');
    await menu.click();await page.keyboard.press('Escape');assert.equal(await menu.getAttribute('aria-expanded'),'false');
   }
   const allies=page.locator('#corporate-allies-grid');await allies.scrollIntoViewIfNeeded();
   assert.equal(await allies.locator('.ally-card').count(),4,'Keep all four corporate entries');
   const previous=await allies.evaluate(e=>e.scrollLeft);
   await page.getByRole('button',{name:'Empresa siguiente',exact:true}).click();
   assert.ok(await allies.evaluate(e=>e.scrollLeft)>previous,'Affiliates next button must advance');
   await page.getByRole('button',{name:'Empresa anterior',exact:true}).click();
   assert.ok(Math.abs(await allies.evaluate(e=>e.scrollLeft))<=2,'Previous returns to first card within snap padding');
   assert.ok((await page.locator('#clients-grid').textContent()).includes('Academia Central'));
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   assert.notEqual(await page.locator('.stat-number').first().textContent(),'0');
   assert.ok(await page.locator('.stat-number').evaluateAll(nodes=>nodes.every(n=>n.scrollWidth<=n.clientWidth+1)),'Statistics must not overflow or break numbers across lines');
   assert.equal(await page.locator('#main-footer .floating-social-bar a').count(),3);
   assert.deepEqual(errors,[]);
   if(process.env.SGA_SCREENSHOTS){
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:process.env.SGA_SCREENSHOTS+'/order-'+width+'.png',fullPage:true});
    if(width===1440 || width===390) await page.screenshot({path:process.env.SGA_SCREENSHOTS+'/top-'+width+'.png'});
   }
   console.log('PASS order/menu/affiliates/admin settings',width);
   await context.close();
  }
  const nativeContext=await browser.newContext({serviceWorkers:'block'});
  const nativePage=await nativeContext.newPage();
  await nativePage.route('**/*',r=>{
   const u=new URL(r.request().url());
   if(u.pathname.endsWith('/public/landing'))return r.fulfill({json:{hero_video_url:'assets/video/not-uploaded.mp4'}});
   if(u.origin!==new URL(base).origin)return r.abort();
   if(u.pathname.includes('/api/'))return r.fulfill({json:[]});
   return r.continue();
  });
  await nativePage.goto(base+'/index.html');
  await nativePage.waitForSelector('.video-status');
  assert.ok((await nativePage.locator('#video-container video').getAttribute('src')).endsWith('assets/video/not-uploaded.mp4'));
  assert.ok((await nativePage.locator('.video-status').textContent()).includes('no está disponible'));
  console.log('PASS missing configured native video: source preserved and status shown');
  await nativeContext.close();
  const context=await browser.newContext({javaScriptEnabled:false});
  const page=await context.newPage();await page.goto(base+'/index.html');
  assert.deepEqual(await page.locator('main > section').evaluateAll(nodes=>nodes.map(n=>n.id)),expected);
  console.log('PASS published section order without JavaScript');await context.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
