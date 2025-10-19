const express = require("express");
const path = require("path");
const compression = require("compression");
const fs = require("fs");

const app = express();
const PORT = 8001;

// Включаем gzip/brotli поддержку
app.use(compression());

// Правильная обработка .br файлов через middleware
app.use((req, res, next) => {
  if (req.url.endsWith(".br")) {
    res.setHeader("Content-Encoding", "br");
    res.setHeader("Content-Type", "application/javascript");
  }
  if (req.url.endsWith(".gz")) {
    res.setHeader("Content-Encoding", "gzip");
    res.setHeader("Content-Type", "application/javascript");
  }
  next();
});

// Раздаём всё содержимое папки как статику
app.use(express.static(path.join(__dirname)));

app.listen(PORT, () => {
  console.log(`✅ Сервер запущен: http://localhost:${PORT}`);
});

