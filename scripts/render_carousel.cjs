// Render the existing component once for the published HTML, without browser dependencies.
const fs=require('node:fs');
const vm=require('node:vm');
const container={innerHTML:'',setAttribute(){}};
const context={window:{matchMedia:()=>({matches:true})},document:{hidden:false,addEventListener(){},getElementById:id=>id==='modern-carousel-container'?container:null},clearInterval(){},setInterval(){}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
context.window.SGAModernCarousel.init('modern-carousel-container');
process.stdout.write(container.innerHTML);
