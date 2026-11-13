const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const fs=require('node:fs');const assert=require('node:assert/strict');
const values=Object.fromEntries(fs.readFileSync(process.env.NODE6_ENV,'utf8').split('\n').filter(line=>line.includes('=')).map(line=>{const i=line.indexOf('=');return[line.slice(0,i),line.slice(i+1)]}));
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});try{
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.NODE6_URL||'http://127.0.0.1:8606');await page.locator('#token').fill(values.NODE6_TOKEN);await page.locator('#connect').click();
  await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('Nodo activo'));
  assert.equal(await page.locator('#token').inputValue(),'');
  if(width===390){
   await page.locator('#duration').fill('1');await page.locator('#reel').click();await page.locator('#video-preview').waitFor({state:'visible'});
   await page.waitForFunction(()=>document.querySelector('video').videoWidth===1080);
   await page.locator('#draft').click();await page.waitForFunction(()=>document.querySelector('#result').textContent.includes('Borrador preparado'));
   await page.locator('#upload').click();await page.waitForFunction(()=>document.querySelector('#message').textContent.includes('Selecciona la clasificación'));
  }
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert.deepEqual(errors,[]);
  await page.evaluate(()=>window.scrollTo(0,0));
  if(process.env.SGA_SCREENSHOTS)await page.screenshot({path:process.env.SGA_SCREENSHOTS+'/node6-'+width+'.png',fullPage:true});
  console.log('PASS studio',width,width===390?'real MP4 preview, draft, explicit private-upload controls':'authentication and responsive layout');await page.close();
 }
}finally{await browser.close()}})().catch(error=>{console.error(error.message);process.exit(1)});
