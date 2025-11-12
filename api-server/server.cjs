// server.cjs - Revised for Visual Quality Enhancements

const express = require('express');
const cors = require('cors');
const path = require('path');
const sharp = require('sharp');
const multer = require('multer');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

const upload = multer({ dest: 'uploads/' });
if (!fs.existsSync('uploads')) fs.mkdirSync('uploads');

const clothingImagesPath = path.join(__dirname, 'clothing-images');
app.use('/api/clothing-images', express.static(clothingImagesPath));

const analytics = { tryOns: [], conversions: [] };

async function loadFaceModels() {
  console.log('⚠️  Using smart fallback positioning');
  return false;
}

async function detectFaceFallback(imagePath) {
  const metadata = await sharp(imagePath).metadata();
  return {
    box: {
      x: metadata.width * 0.35,
      y: metadata.height * 0.1,
      width: metadata.width * 0.3,
      height: metadata.height * 0.25
    },
    landmarks: {
      leftShoulder: { x: metadata.width * 0.3, y: metadata.height * 0.45 },
      rightShoulder: { x: metadata.width * 0.7, y: metadata.height * 0.45 }
    }
  };
}

async function getSmartPosition(userPhotoPath, clothingType) {
  const faceData = await detectFaceFallback(userPhotoPath);
  const shoulderWidth = faceData.landmarks.rightShoulder.x - faceData.landmarks.leftShoulder.x;
  const shoulderCenterX = (faceData.landmarks.leftShoulder.x + faceData.landmarks.rightShoulder.x) / 2;
  const shoulderY = faceData.landmarks.leftShoulder.y;

  const adjustments = {
    'white-tshirt.png': { widthMultiplier: 1.2, yOffset: -50 },
    'blue-shirt.png': { widthMultiplier: 1.2, yOffset: -55 },
    'bomber-jacket.png': { widthMultiplier: 1.3, yOffset: -60 },
    'summer-dress.png': { widthMultiplier: 1.1, yOffset: -45 }
  };

  const adjustment = adjustments[clothingType] || adjustments['white-tshirt.png'];
  return {
    width: Math.floor(shoulderWidth * adjustment.widthMultiplier),
    x: Math.floor(shoulderCenterX),
    y: Math.floor(shoulderY + adjustment.yOffset),
    shoulderAngle: calculateShoulderAngle(faceData.landmarks)
  };
}

function calculateShoulderAngle(landmarks) {
  const dx = landmarks.rightShoulder.x - landmarks.leftShoulder.x;
  const dy = landmarks.rightShoulder.y - landmarks.leftShoulder.y;
  return Math.atan2(dy, dx) * (180 / Math.PI);
}

async function warpClothingToPerspective(clothingBuffer, shoulderAngle) {
  const skew = shoulderAngle * 0.5;
  return await sharp(clothingBuffer)
    .affine([[1, Math.tan(skew * Math.PI / 180)], [0, 1]], {
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .toBuffer();
}

async function matchLighting(clothingBuffer, userPhotoPath) {
  const stats = await sharp(userPhotoPath).stats();
  const avgBrightness = (stats.channels[0].mean + stats.channels[1].mean + stats.channels[2].mean) / 3;
  const lightingAdjustment = 0.7 + (avgBrightness / 128) * 0.3;

  return await sharp(clothingBuffer)
    .modulate({ brightness: lightingAdjustment, saturation: 1.0, hue: -5 })
    .tint('#ffeedd')
    .toBuffer();
}

async function createDepthShadow(clothingBuffer, clothingMeta) {
  return await sharp(clothingBuffer)
    .blur(30)
    .modulate({ brightness: 0.25, saturation: 0.4 })
    .affine([[1.1, 0.08], [0, 1.25]], {
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .toBuffer();
}

async function featherEdges(clothingBuffer) {
  const mask = await sharp(clothingBuffer).extractChannel('alpha').blur(4).toBuffer();
  return await sharp(clothingBuffer).joinChannel(mask).toBuffer();
}

app.post('/api/try-on-2d', upload.single('userPhoto'), async (req, res) => {
  try {
    const { clothingItem } = req.body;
    const userPhotoPath = req.file.path;

    const position = await getSmartPosition(userPhotoPath, clothingItem);
    const clothingPath = path.join(__dirname, 'clothing-images', clothingItem);

    let processedClothing = await sharp(clothingPath)
      .resize(position.width, null, { fit: 'inside', withoutEnlargement: false })
      .toBuffer();

    processedClothing = await warpClothingToPerspective(processedClothing, position.shoulderAngle);
    processedClothing = await matchLighting(processedClothing, userPhotoPath);
    processedClothing = await featherEdges(processedClothing);

    const clothingMeta = await sharp(processedClothing).metadata();
    let finalX = Math.floor(position.x - clothingMeta.width / 2);
    let finalY = position.y;

    const imageMeta = await sharp(userPhotoPath).metadata();
    finalX = Math.max(0, Math.min(finalX, imageMeta.width - clothingMeta.width - 10));
    finalY = Math.max(0, Math.min(finalY, imageMeta.height - clothingMeta.height - 10));

    const depthShadow = await createDepthShadow(processedClothing, clothingMeta);

    const result = await sharp(userPhotoPath)
      .composite([
        { input: depthShadow, top: finalY + 15, left: finalX - 5, blend: 'multiply' },
        { input: processedClothing, top: finalY, left: finalX, blend: 'over' }
      ])
      .png()
      .toBuffer();

    fs.unlinkSync(userPhotoPath);
    analytics.tryOns.push({ item: clothingItem, timestamp: new Date(), sessionId: req.ip });
    res.set('Content-Type', 'image/png');
    res.send(result);

  } catch (error) {
    console.error('❌ Overlay error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, async () => {
  console.log(`🚀 VTO Server running on port ${PORT}`);
  if (!(await loadFaceModels())) console.log('⚠️  Running with fallback positioning');
});
