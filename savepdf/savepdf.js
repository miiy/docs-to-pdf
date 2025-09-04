const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function savePageAsPDF(page, url, fileName, outputDir, selector = null) {
  try {
    console.log(`visiting: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle0' });

    const filePath = path.join(outputDir, fileName);
    console.log(`saving: ${fileName}`);

    let pdfOptions = {
      path: filePath,
      format: 'A4',
      printBackground: true,
      margin: { top: '0.4in', right: '0.4in', bottom: '0.4in', left: '0.4in' }
    };

    // If selector is provided, only print that element
    if (selector) {
      console.log(`waiting for selector: ${selector}`);
      await page.waitForSelector(selector);
      
      // Get the element and its bounding box
      const element = await page.$(selector);
      if (element) {
        // Get element info for debugging
        const elementInfo = await page.evaluate((el) => {
          return {
            tagName: el.tagName,
            className: el.className,
            id: el.id,
            textContent: el.textContent.substring(0, 100) + '...',
            offsetWidth: el.offsetWidth,
            offsetHeight: el.offsetHeight
          };
        }, element);
        
        console.log(`element found:`, elementInfo);
        
        const boundingBox = await element.boundingBox();
        if (boundingBox) {
          console.log(`bounding box:`, boundingBox);
          
          // Hide all elements except the target element and its parents
          await page.evaluate((sel) => {
            const targetElement = document.querySelector(sel);
            if (targetElement) {
              // First, make sure target element and its parents are visible
              let current = targetElement;
              while (current && current !== document.documentElement) {
                current.style.display = '';
                current.style.visibility = 'visible';
                current.style.opacity = '1';
                current = current.parentElement;
              }
              
              // Hide all direct children of body except the one containing our target
              const bodyChildren = Array.from(document.body.children);
              bodyChildren.forEach(child => {
                if (!child.contains(targetElement)) {
                  child.style.display = 'none';
                }
              });
              
              // Also hide any siblings of the target's parent containers
              let currentElement = targetElement;
              let parent = currentElement.parentElement;
              while (parent && parent !== document.body) {
                const siblings = Array.from(parent.children);
                siblings.forEach(sibling => {
                  if (sibling !== currentElement && !sibling.contains(currentElement)) {
                    sibling.style.display = 'none';
                  }
                });
                currentElement = parent;
                parent = parent.parentElement;
              }
            }
          }, selector);
          
          // Use clip to focus on the element area
          pdfOptions.clip = {
            x: Math.max(0, boundingBox.x),
            y: Math.max(0, boundingBox.y),
            width: boundingBox.width,
            height: boundingBox.height
          };
          
          console.log(`printing only element: ${selector}`);
        } else {
          console.log(`element ${selector} has no bounding box, printing full page`);
        }
      } else {
        console.log(`element ${selector} not found, printing full page`);
      }
    }

    await page.pdf(pdfOptions);

    console.log(`✅ saved: ${fileName}`);
    return { success: true, fileName };
  } catch (error) {
    console.error(`❌ save failed ${fileName}:`, error.message);
    return { success: false, fileName: fileName, error: error.message };
  }
}

(async () => {
  const args = require('minimist')(process.argv.slice(2));
  const url = args.url || args.u;
  let fileName = args.fileName || args.f || 'untitled';
  const outputDir = args.outputDir || args.o || './data/pdfs';
  const selector = args.selector || args.s;
  const proxy = args.proxy || args.p;
  const proxyUsername = args.proxyUsername || args.pu;
  const proxyPassword = args.proxyPassword || args.pp;

  // ensure .pdf extension is present
  if (!fileName.endsWith('.pdf')) {
    fileName = `${fileName}.pdf`;
  }

  if (!url) {
    console.error('missing required parameter: --url');
    process.exit(1);
  }

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Configure browser launch options
  const launchOptions = { 
    headless: true, 
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  };

  // Add proxy configuration if provided
  if (proxy) {
    console.log(`using proxy: ${proxy}`);
    launchOptions.args.push(`--proxy-server=${proxy}`);
  }

  const browser = await puppeteer.launch(launchOptions);
  const page = await browser.newPage();
  
  // Set proxy authentication if needed
  if (proxy && proxyUsername && proxyPassword) {
    await page.authenticate({
      username: proxyUsername,
      password: proxyPassword
    });
  }
  
  const result = await savePageAsPDF(page, url, fileName, outputDir, selector);
  console.log(`result: ${JSON.stringify(result)}`);
  await browser.close();
})();