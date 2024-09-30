# `audio-manipulation`

## Downloading audio from Youtube video

**Using `invoke` script:**

```bash
invoke fetch
```

(Or for a GUI experience:)

```bash
invoke guifetch
```

**Calling file directly:**

```bash
python download_mp3.py "https://youtube.com/watch?v=example" -o "/path/to/output" -f "%(title)s.%(ext)s" -q 192
```
