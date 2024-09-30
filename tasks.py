from invoke import task


@task
def fetch(c):
    """Fetch audio from youtube lnk"""
    c.run("python download_audio.py")


@task
def guifetch(c):
    """Fetch audio, using the gui"""
    c.run("python3 download_audio_gui.py")


@task
def transcribe(c):
    """Segment and transcribe the audio"""
    c.run("python transcribe.py")
