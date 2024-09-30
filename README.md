# `audio-manipulation`

## Downloading audio from Youtube video

**Using `invoke` script:**

```bash
invoke fetch
```

**Calling file directly:**

```bash
python download_mp3.py "https://youtube.com/watch?v=example" -o "/path/to/output" -f "%(title)s.%(ext)s" -q 192
```
