
# voice_to_signLanguage
Voice to Sign Language Conversion


## Usage

Install dependencies

```
npm install
```
```
pip install pipenv
```
```
pip install pipenv
```
```
pipenv install
```
```
pipenv shell
```
```
nodemon server.js
```

## Cloud deployment

This project can be deployed as a Docker service on Render or another Docker-capable host.
The Docker image installs Node.js, Python 3, FFmpeg, MoviePy, and NLTK. The Express server uses the host-provided `PORT` and invokes Python with `python3`.

### Render
1. Push this folder to GitHub.
2. Create a new **Web Service** on Render and select the repository.
3. Choose **Docker** as the runtime.
4. Deploy.
