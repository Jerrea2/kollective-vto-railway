// VTO Widget - Revised Complete Version
const vtoCamera = document.getElementById('vto-camera');
const captureButton = document.getElementById('vto-capture-btn');
const downloadButton = document.getElementById('vto-download-btn');

// Point to your server on port 3001
const API_URL = 'http://127.0.0.1:3001';

// Global variable to store captured image
window.capturedImageBlob = null;

async function initializeCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    vtoCamera.srcObject = stream;
    vtoCamera.play();
    console.log('Camera initialized');
  } catch (error) {
    console.error('Camera error:', error);
    alert('Unable to access camera. Please ensure camera permissions are granted.');
  }
}

function captureFrame(e) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  console.log('Capture button clicked');
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = vtoCamera.videoWidth;
  canvas.height = vtoCamera.videoHeight;
  context.drawImage(vtoCamera, 0, 0, canvas.width, canvas.height);
  
  canvas.toBlob((blob) => {
    window.capturedImageBlob = blob;
    console.log('Image captured, blob size:', blob.size);
    const imageData = canvas.toDataURL('image/png');
    const capturedFrame = document.getElementById('vto-captured-frame');
    capturedFrame.src = imageData;
    capturedFrame.style.display = 'block';
    downloadButton.disabled = false;
  });
}

function downloadCapturedFrame() {
  const link = document.createElement('a');
  const resultImg = document.getElementById('result-image');
  
  if (resultImg && resultImg.src) {
    // Download the try-on result
    link.href = resultImg.src;
    link.download = `virtual-tryon-result-${Date.now()}.png`;
  } else {
    // Download the captured photo
    link.href = document.getElementById('vto-captured-frame').src;
    link.download = `captured-photo-${Date.now()}.png`;
  }
  
  link.click();
}

async function loadClothingItems() {
  // Use your actual clothing images from the server
  const data = [
    {
      id: 1,
      name: "White T-Shirt",
      image: `${API_URL}/api/clothing-images/white-tshirt.png`,
      filename: "white-tshirt.png"
    },
    {
      id: 2,
      name: "Blue Shirt",
      image: `${API_URL}/api/clothing-images/blue-shirt.png`,
      filename: "blue-shirt.png"
    },
    {
      id: 3,
      name: "Bomber Jacket",
      image: `${API_URL}/api/clothing-images/bomber-jacket.png`,
      filename: "bomber-jacket.png"
    },
    {
      id: 4,
      name: "Summer Dress",
      image: `${API_URL}/api/clothing-images/summer-dress.png`,
      filename: "summer-dress.png"
    }
  ];
  
  console.log('Clothing items loaded:', data);

  const clothingItemsContainer = document.getElementById('vto-clothing-items');
  clothingItemsContainer.innerHTML = '<h3>Select clothing to try on:</h3>';
  
  data.forEach(item => {
    const itemElement = document.createElement('div');
    itemElement.className = 'clothing-item';
    itemElement.style.cssText = `
      cursor: pointer; 
      padding: 10px; 
      border: 2px solid #ddd; 
      margin: 5px; 
      display: inline-block;
      transition: all 0.3s;
      background: white;
      border-radius: 5px;
    `;
    itemElement.innerHTML = `
      <img src="${item.image}" alt="${item.name}" style="width: 120px; height: 150px; object-fit: contain;">
      <p style="text-align: center; margin: 10px 0; font-weight: bold;">${item.name}</p>
    `;
    itemElement.onmouseover = () => itemElement.style.borderColor = '#007bff';
    itemElement.onmouseout = () => itemElement.style.borderColor = '#ddd';
    itemElement.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      selectClothingItem(item);
    };
    clothingItemsContainer.appendChild(itemElement);
  });
}

async function selectClothingItem(item) {
  console.log('Clothing item selected:', item.name, item.filename);
  
  if (!window.capturedImageBlob) {
    alert('Please capture your photo first!');
    return;
  }
  
  // Create form data
  const formData = new FormData();
  formData.append('userPhoto', window.capturedImageBlob, 'capture.png');
  formData.append('clothingItem', item.filename);
  
  // Direct fetch without try-catch to see real error
  fetch('http://127.0.0.1:3001/api/try-on-2d', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    console.log('Got response:', response.status);
    if (!response.ok) throw new Error('Server error');
    return response.blob();
  })
  .then(blob => {
    console.log('Got blob:', blob.size);
    const url = URL.createObjectURL(blob);
    displayResult(url, item);
  })
  .catch(error => {
    console.error('Actual error:', error);
    alert('Try-on failed: ' + error.message);
  });
}

function displayResult(imageUrl, item) {
  console.log('Displaying result for:', item.name);
  
  const container = document.getElementById('vto-capture-result');
  
  // Hide the original captured frame
  const capturedFrame = document.getElementById('vto-captured-frame');
  capturedFrame.style.display = 'none';
  
  // Create or update result image
  let resultImg = document.getElementById('result-image');
  if (!resultImg) {
    resultImg = document.createElement('img');
    resultImg.id = 'result-image';
    resultImg.style.cssText = 'max-width: 100%; border: 2px solid #4CAF50; margin-top: 20px; border-radius: 5px;';
    container.appendChild(resultImg);
  }
  
  resultImg.src = imageUrl;
  resultImg.alt = `Try-on result: ${item.name}`;
  
  // Success message
  let successDiv = document.getElementById('success-message');
  if (!successDiv) {
    successDiv = document.createElement('div');
    successDiv.id = 'success-message';
  }
  successDiv.style.cssText = `
    background: #4CAF50;
    color: white;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
  `;
  successDiv.textContent = `✓ ${item.name} applied successfully!`;
  container.appendChild(successDiv);
  
  setTimeout(() => successDiv.remove(), 3000);
  
  // Update download button to download the result
  downloadButton.onclick = () => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `virtual-tryon-${item.name.replace(/\s+/g, '-')}-${Date.now()}.png`;
    link.click();
  };
}

// Simple test function
async function testTryOn() {
  if (!window.capturedImageBlob) {
    alert('Capture a photo first!');
    return;
  }
  
  console.log('Running test try-on...');
  
  const formData = new FormData();
  formData.append('userPhoto', window.capturedImageBlob);
  formData.append('clothingItem', 'white-tshirt.png');
  
  try {
    const response = await fetch('http://localhost:3001/api/try-on-2d', {
      method: 'POST',
      body: formData
    });
    
    console.log('Test response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // Display the result
    displayResult(url, { name: 'Test White T-Shirt' });
    
    console.log('Test successful!');
  } catch (error) {
    console.error('Test failed:', error);
    alert(`Test failed: ${error.message}`);
  }
}

// Make testTryOn available globally
window.testTryOn = testTryOn;

// Initialize everything
if (captureButton) {
  captureButton.addEventListener('click', (e) => captureFrame(e));
}

if (downloadButton) {
  downloadButton.addEventListener('click', downloadCapturedFrame);
}

window.addEventListener('load', () => {
  console.log('Page loaded, initializing...');
  initializeCamera();
  loadClothingItems();
});