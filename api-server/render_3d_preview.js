// render_3d_preview.js
// Node.js + Three.js script for headless server-side 3D rendering
import { createCanvas } from &#39;canvas&#39;;
import { GLTFLoader } from &#39;three/examples/jsm/loaders/GLTFLoader.js&#39;;
import * as THREE from &#39;three&#39;;
import { readFileSync, writeFileSync } from &#39;fs&#39;;
import { loadImage } from &#39;canvas&#39;;
import { join } from &#39;path&#39;;
import { fileURLToPath } from &#39;url&#39;;
import puppeteer from &#39;puppeteer&#39;;
// Get CLI args
const args = process.argv.slice(2);
const [userImagePath, modelPath, outputPath] = args;
(async () =&gt; {
const browser = await puppeteer.launch({ headless: true, args: [&#39;--no-sandbox&#39;] });
const page = await browser.newPage();
const html = `
&lt;html&gt;
&lt;body style=&quot;margin: 0; overflow: hidden&quot;&gt;
&lt;script type=&quot;module&quot;&gt;
import * as THREE from &#39;https://cdn.skypack.dev/three@0.150.1&#39;;
import { GLTFLoader } from
&#39;https://cdn.skypack.dev/three/examples/jsm/loaders/GLTFLoader.js&#39;;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 1000);
camera.position.z = 2;
const renderer = new THREE.WebGLRenderer({ preserveDrawingBuffer: true });
renderer.setSize(512, 512);
document.body.appendChild(renderer.domElement);
const light = new THREE.AmbientLight(0xffffff, 1);
scene.add(light);
const loader = new GLTFLoader();
loader.load(&#39;${modelPath}&#39;, (gltf) =&gt; {
scene.add(gltf.scene);
});

const bgTexture = new THREE.TextureLoader().load(&#39;${userImagePath}&#39;);
scene.background = bgTexture;
function animate() {
requestAnimationFrame(animate);
renderer.render(scene, camera);
}
animate();
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
`;
await page.setContent(html);
await page.waitForTimeout(5000); // wait for scene load
const screenshot = await page.screenshot({ path: outputPath });
await browser.close();
})();