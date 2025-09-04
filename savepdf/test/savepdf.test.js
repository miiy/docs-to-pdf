const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

describe('savepdf test', () => {
  test('test generating PDF', (done) => {
    const command = 'node savepdf.js --url "https://example.com" --title "Example Domain" --outputDir "./data/pdfs"';

    const outputDir = path.resolve(__dirname, './data/pdfs');
    const pdfFile = path.join(outputDir, 'Example Domain.pdf');

    exec(command, (error, stdout, stderr) => {
      console.log('script output:', stdout);

      const exists = fs.existsSync(pdfFile);
      if (exists) {
        const stats = fs.statSync(pdfFile);
        console.log(`PDF file size: ${stats.size} bytes`);
      }

      expect(exists).toBe(true);
      done();
    });
  }, 30000);
});
