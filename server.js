const express = require("express");

const { spawn } = require('child_process');
const { Console } = require("console");
const app = express();
const path = require('path');
let ejs = require('ejs');
var bodyParser = require('body-parser');
const fs = require("fs");
app.use(express.urlencoded());
app.use(express.json());
app.set('view engine', 'ejs');

const port = process.env.PORT || 3000
let inputLine = ""
let done = false
let dataString = ""
let requiredData = ""
var python = null
//static images file
app.use(express.static('public'));
app.use('/img', express.static('images'));

// Speech generation page
app.get('/speech', function (req, res) {
  res.sendFile(path.join(__dirname + '/s2t.html'));
});

// Home page landing page
app.get("/", function (req, res) {
  inputLine = ""
  done = false
  dataString = ""
  requiredData = ""
  if (python != null)
    python.kill('SIGINT');
  res.sendFile(path.join(__dirname + "/index.html"));
});

// Signup page
app.get("/signup", function (req, res) {
  res.sendFile(path.join(__dirname + "/signup.html"));
});

// Login page
app.get("/login", function (req, res) {
  res.sendFile(path.join(__dirname + "/login.html"));
});

// Change password page
app.get("/change-password", function (req, res) {
  res.sendFile(path.join(__dirname + "/change-password.html"));
});

// Auth landing route for generation page
app.get("/generate", function (req, res) {
  res.sendFile(path.join(__dirname + "/generate.html"));
});

// User profile page
app.get("/profile", function (req, res) {
  res.sendFile(path.join(__dirname + "/profile.html"));
});

//Final speach file done.html
app.post("/speach", function (req, res) {
  inputLine = req.body.textbox;
  dataString = "";
  requiredData = "";
  done = false;

  if (python != null) {
    python.kill('SIGINT');
    python = null;
  }

  isItDoneYet().then((msg) => {
    console.log(msg);
    console.log(inputLine);
    console.log("data->\n" + dataString);
    const startIndex = dataString.indexOf("ISL:{");
    const endIndex = dataString.indexOf("}");
    if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
      requiredData = dataString.substring(startIndex + 5, endIndex);
    } else {
      requiredData = dataString.trim();
    }
    done = true;
    res.render('result', { done: done, islSyntax: requiredData, normalSyntax: inputLine });
  }).catch((msg) => {
    console.log(msg);
    res.status(500).send('Video generation failed. Please try again.');
  });
});
//done request video 
app.get("/video", function (req, res) {
  
  //res.sendFile('/data/samples/output/clipg.mp4', { root: __dirname });  
  const range = req.headers.range;
  if (!range) {
    return res.status(400).send("Requires Range header");
  }

  // get video stats (about 61MB)
  const videoPath = path.resolve(__dirname + "/data/samples/output/clipg.mp4");
  const videoSize = fs.statSync(videoPath).size;

  // Parse Range
  // Example: "bytes=32324-"
  const CHUNK_SIZE = 10 ** 6; // 1MB
  const start = Number(range.replace(/\D/g, ""));
  const end = Math.min(start + CHUNK_SIZE, videoSize - 1);

  // Create headers
  const contentLength = end - start + 1;
  const headers = {
    "Content-Range": `bytes ${start}-${end}/${videoSize}`,
    "Accept-Ranges": "bytes",
    "Content-Length": contentLength,
    "Content-Type": "video/mp4",
  };

  // create video read stream for this particular chunk
  var videoStream = fs.createReadStream(videoPath, { start, end });

  // HTTP Status 206 for Partial Content
  res.writeHead(206, headers);


  // Stream the video chunk to the client
  videoStream.pipe(res);
})

//this the python promise 
const isItDoneYet = () => new Promise((resolve, reject) => {
  python = spawn(process.env.PYTHON_BIN || 'python3', ['speech_recog.py', inputLine])
  let c = false
  python.stdout.on('data', function (data) {
    dataString += data.toString();
  })
  python.stderr.on('data', function (data) {
    console.error('PY STDERR:', data.toString());
    dataString += data.toString();
  })
  python.on('exit', (code) => {
    console.log(`child process close all stdio with code ${code}`);
    if (code == 0)
      c = true;
    if (c) {
      const workDone = 'Here is the thing I built'
      resolve(workDone)
    } else {
      const why = 'Sorry I failed to built it'
      reject(why)
    }
  });

})

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
