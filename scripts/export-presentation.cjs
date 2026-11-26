/* Exporta o mesmo HTML para PDF 16:9; não acessa a aplicação nem o banco. */
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
(async () => {
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width:1920,height:1080}, reducedMotion:'reduce'});
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(pathToFileURL(path.join(root,'docs/apresentacao-helpdesk.html')).href);
    await page.evaluate(async () => {await document.fonts.ready; await Promise.all([...document.images].filter(i=>i.getAttribute("src")).map(i=>i.decode()));});
    await page.pdf({path:path.join(root,'docs/apresentacao-helpdesk.pdf'), printBackground:true,
      preferCSSPageSize:true, tagged:true});
    console.log('PDF gerado a partir do HTML: docs/apresentacao-helpdesk.pdf');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
