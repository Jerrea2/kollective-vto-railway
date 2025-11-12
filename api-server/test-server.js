const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());

app.get('/health', (req, res) => {
  console.log('Someone visited /health!');
  res.json({ status: 'OK' });
});

app.listen(3000, () => {
  console.log('TEST SERVER RUNNING ON 3000!');
});