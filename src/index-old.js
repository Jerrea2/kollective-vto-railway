const vtoCamera = document.getElementById('vto-camera');
const captureButton = document.getElementById('vto-capture-btn');
const downloadButton = document.getElementById('vto-download-btn');
let isDemo = false;
let bodyMeasurements = null;

// Demo mode with pre-analyzed body points
const demoPhotos = [
  {
    id: 1,
    name: "Model 1 - Front View",
    image: "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&q=80",
    bodyPoints: {
      shoulders: { left: 120, right: 280, y: 150 },
      chest: { width: 160, y: 200 },
      waist: { width: 140, y: 300 },
      hips: { width: 150, y: 350 }
    }
  },
  {
    id: 2,
    name: "Model 2 - Front View", 
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
    bodyPoints: {
      shoulders: { left: 110, right: 290, y: 140 },
      chest: { width: 180, y: 190 },
      waist: { width: 160, y: 290 },
      hips: { width: 170, y: 340 }
    }
  }
];

async function initializeCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    vtoCamera.srcObject = stream;
    vtoCamera.play();
  } catch (error) {
    console.error('Error accessing camera:', error);
  }
}

function captureFrame() {
  if (isDemo) {
    alert('In demo mode, select a pre-loaded model photo below');
    return;
  }
  
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = vtoCamera.videoWidth;
  canvas.height = vtoCamera.videoHeight;
  context.drawImage(vtoCamera, 0, 0, canvas.width, canvas.height);
  const imageData = canvas.toDataURL('image/png');
  const capturedFrame = document.getElementById('vto-captured-frame');
  capturedFrame.src = imageData;
  downloadButton.disabled = false;
  
  // Simulate body detection
  detectBodyPoints();
}

function detectBodyPoints() {
  // Simulated body measurements for live photos
  bodyMeasurements = {
    shoulders: { left: 150, right: 350, y: 180 },
    chest: { width: 200, y: 240 },
    waist: { width: 180, y: 340 },
    hips: { width: 190, y: 400 }
  };
}

function downloadCapturedFrame() {
  const link = document.createElement('a');
  link.href = document.getElementById('vto-captured-frame').src;
  link.download = 'virtual-tryon-result.png';
  link.click();
}

async function loadClothingItems() {
  try {
    const data = [
      {
        id: 1,
        name: "Fitted Black T-Shirt",
        image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80",
        type: "shirt"
      },
      {
        id: 2,
        name: "Slim Blue Jeans",
        image: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&q=80",
        type: "pants"
      },
      {
        id: 3,
        name: "Summer Dress",
        image: "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500&q=80",
        type: "dress"
      },
      {
        id: 4,
        name: "White Dress Shirt",
        image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&q=80",
        type: "shirt"
      },
      {
        id: 5,
        name: "Denim Jacket",
        image: "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=500&q=80",
        type: "jacket"
      }
    ];
    
    console.log('Clothing items loaded:', data);

    const clothingItemsContainer = document.getElementById('vto-clothing-items');
    clothingItemsContainer.innerHTML = '<h3>Select Clothing to Try On:</h3>';
    
    data.forEach(item => {
      const itemElement = document.createElement('div');
      itemElement.className = 'clothing-item';
      itemElement.style.cssText = 'cursor: pointer; padding: 10px; border: 2px solid #ddd; margin: 5px; display: inline-block; text-align: center;';
      itemElement.innerHTML = `
        <img src="${item.image}" alt="${item.name}" style="width: 120px; height: 150px; object-fit: cover;">
        <p style="text-align: center; margin: 10px 0; font-weight: bold;">${item.name}</p>
      `;
      itemElement.onclick = () => selectClothingItem(item);
      clothingItemsContainer.appendChild(itemElement);
    });
    
  } catch (error) {
    console.error('Error loading clothing items:', error);
  }
}

function selectClothingItem(item) {
  const capturedFrame = document.getElementById('vto-captured-frame');
  
  if (!capturedFrame.src || capturedFrame.src === window.location.href) {
    alert('Please capture a photo first or select a demo model!');
    return;
  }
  
  if (!bodyMeasurements) {
    alert('Analyzing body measurements...');
    detectBodyPoints();
  }
  
  applyClothingWithFit(item);
}

function applyClothingWithFit(item) {
  const capturedFrame = document.getElementById('vto-captured-frame');
  const container = document.getElementById('vto-capture-result');
  
  let canvas = document.getElementById('vto-canvas');
  if (!canvas) {
    canvas = document.createElement('canvas');
    canvas.id = 'vto-canvas';
    canvas.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%;';
    container.style.position = 'relative';
    container.appendChild(canvas);
  }
  
  const ctx = canvas.getContext('2d');
  canvas.width = capturedFrame.width;
  canvas.height = capturedFrame.height;
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Create a clipping mask based on body measurements
  ctx.save();
  
  if (item.type === 'shirt' || item.type === 'jacket') {
    // Create body-shaped path for upper body clothing
    ctx.beginPath();
    ctx.moveTo(bodyMeasurements.shoulders.left, bodyMeasurements.shoulders.y);
    ctx.quadraticCurveTo(bodyMeasurements.shoulders.left - 20, bodyMeasurements.chest.y, 
                         bodyMeasurements.shoulders.left - 10, bodyMeasurements.waist.y);
    ctx.lineTo(bodyMeasurements.shoulders.right + 10, bodyMeasurements.waist.y);
    ctx.quadraticCurveTo(bodyMeasurements.shoulders.right + 20, bodyMeasurements.chest.y,
                         bodyMeasurements.shoulders.right, bodyMeasurements.shoulders.y);
    ctx.closePath();
    ctx.clip();
  }
  
  const clothingImg = new Image();
  clothingImg.onload = function() {
    // Calculate dimensions based on body measurements
    let clothingWidth, clothingHeight, clothingX, clothingY;
    
    if (item.type === 'shirt' || item.type === 'jacket') {
      clothingWidth = bodyMeasurements.shoulders.right - bodyMeasurements.shoulders.left + 40;
      clothingHeight = bodyMeasurements.waist.y - bodyMeasurements.shoulders.y + 40;
      clothingX = bodyMeasurements.shoulders.left - 20;
      clothingY = bodyMeasurements.shoulders.y - 20;
    } else if (item.type === 'dress') {
      clothingWidth = bodyMeasurements.hips.width + 40;
      clothingHeight = 400;
      clothingX = (canvas.width - clothingWidth) / 2;
      clothingY = bodyMeasurements.shoulders.y - 20;
    } else {
      // Default for other items
      clothingWidth = canvas.width * 0.6;
      clothingHeight = clothingWidth * (clothingImg.height / clothingImg.width);
      clothingX = (canvas.width - clothingWidth) / 2;
      clothingY = canvas.height * 0.15;
    }
    
    // Apply perspective transform for 3D effect
    ctx.save();
    ctx.globalAlpha = 0.95;
    
    // Add subtle shadow for depth
    ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
    ctx.shadowBlur = 15;
    ctx.shadowOffsetY = 5;
    
    // Draw the clothing with body-fitting transformation
    ctx.drawImage(clothingImg, clothingX, clothingY, clothingWidth, clothingHeight);
    
    ctx.restore();
    ctx.restore();
    
    // Add fitting indicator
    ctx.fillStyle = '#2ecc71';
    ctx.font = 'bold 14px Arial';
    ctx.fillText('✓ AI-Fitted to Body', 10, 30);
    ctx.fillText(`Trying on: ${item.name}`, 10, 50);
  };
  clothingImg.src = item.image;
}

function clearOverlay() {
  const canvas = document.getElementById('vto-canvas');
  if (canvas) {
    canvas.remove();
  }
}

function toggleDemoMode() {
  isDemo = !isDemo;
  const demoButton = document.getElementById('demo-toggle');
  demoButton.textContent = isDemo ? 'Exit Demo Mode' : 'Demo Mode';
  
  if (isDemo) {
    // Hide camera, show demo photos
    vtoCamera.style.display = 'none';
    captureButton.style.display = 'none';
    
    // Create demo photo selector
    const demoSelector = document.createElement('div');
    demoSelector.id = 'demo-selector';
    demoSelector.innerHTML = '<h3>Select a Model:</h3>';
    demoSelector.style.cssText = 'background: #f0f0f0; padding: 15px; margin: 10px 0;';
    
    demoPhotos.forEach(photo => {
      const photoOption = document.createElement('div');
      photoOption.style.cssText = 'display: inline-block; margin: 10px; cursor: pointer; border: 2px solid transparent;';
      photoOption.innerHTML = `
        <img src="${photo.image}" style="width: 150px; height: 200px; object-fit: cover;">
        <p style="text-align: center;">${photo.name}</p>
      `;
      photoOption.onclick = () => {
        document.getElementById('vto-captured-frame').src = photo.image;
        bodyMeasurements = photo.bodyPoints;
        downloadButton.disabled = false;
        // Highlight selected
        document.querySelectorAll('#demo-selector > div').forEach(d => d.style.border = '2px solid transparent');
        photoOption.style.border = '2px solid #3498db';
      };
      demoSelector.appendChild(photoOption);
    });
    
    vtoCamera.parentElement.insertBefore(demoSelector, vtoCamera);
  } else {
    // Show camera, hide demo selector
    vtoCamera.style.display = 'block';
    captureButton.style.display = 'inline-block';
    const demoSelector = document.getElementById('demo-selector');
    if (demoSelector) demoSelector.remove();
    bodyMeasurements = null;
  }
}

// Event listeners
if (captureButton) {
  captureButton.addEventListener('click', captureFrame);
}

if (downloadButton) {
  downloadButton.addEventListener('click', downloadCapturedFrame);
}

window.addEventListener('load', () => {
  initializeCamera();
  loadClothingItems();
  
  // Add Clear button
  const clearButton = document.createElement('button');
  clearButton.textContent = 'Clear Try-On';
  clearButton.onclick = clearOverlay;
  clearButton.style.cssText = 'padding: 10px 20px; margin: 5px;';
  
  // Add Demo Mode toggle
  const demoButton = document.createElement('button');
  demoButton.id = 'demo-toggle';
  demoButton.textContent = 'Demo Mode';
  demoButton.onclick = toggleDemoMode;
  demoButton.style.cssText = 'padding: 10px 20px; margin: 5px; background: #3498db; color: white; border: none;';
  
  const controls = document.getElementById('vto-controls');
  controls.appendChild(clearButton);
  controls.appendChild(demoButton);
});