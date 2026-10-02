# Experiments with PyFLP

An original dark phonk composition created by generating FL Studio project events and sampler assets with Python, then rendering the result in FL Studio.

## Replacement drop study

A 16-bar listening study responding to feedback about disconnected drums, melody and vocals. The kick and bass share syncopated accents; a half-time clap, broken swung hats and a sparse D-F-Eb melodic cell form four related phrases. The pad follows the same D/Eb/D roots. No vocal plays. This is a short alternative to evaluate before writing another full arrangement.

- [Listen](projects/NIGHT%20GRAVE%20-%20DROP%20STUDY/NIGHT%20GRAVE%20-%20DROP%20STUDY.mp3)
- [Complete FLP and samples](downloads/NIGHT%20GRAVE%20-%20DROP%20STUDY%20-%20complete%20project.zip)

Native FL Studio export: 30 seconds including tails, peak -5.80 dBFS. Technical validation confirms loading and signal levels; it does not establish musical quality. Rebuild with `python build_drop_study.py`, then export natively and run `python package_drop_study.py`.

## NIGHT GRAVE V3 â€” latest revision

144 BPM Â· D Phrygian Â· 88 bars. A rounded FM tine replaces the sharp cowbell. The quieter melody leaves room for pitched vocal answers, a fuller harmonic pad, a detuned drone and filtered delays. Six editable native Reeverb 2 inserts provide space.

- [Complete project ZIP](downloads/NIGHT%20GRAVE%20V3%20-%20complete%20project.zip)
- [FLP](projects/NIGHT%20GRAVE%20V3/NIGHT%20GRAVE%20V3.flp)
- [MP3](projects/NIGHT%20GRAVE%20V3/NIGHT%20GRAVE%20V3.mp3)
- [Native render checks](projects/NIGHT%20GRAVE%20V3/validation.json)

16 sampler channels, 24 patterns and 221 clips. Open the ZIP in FL Studio, or keep the FLP beside its WAV samples. Run `python build_dark_phonk_v3.py` to rebuild with the same local packs; `package_v3.py` packages the native render after it is exported to `NIGHT GRAVE V3/FL Render`. The builder writes FL 24 version metadata to match the modern 60-byte playlist format.

The vocal source is a local Phonk pack sample; review its license before commercial distribution. Render validation checks loading, duration and signal levels; the musical result still benefits from listening and personal feedback.

## NIGHT GRAVE V2

144 BPM Â· D Phrygian Â· 88 bars Â· 2:28 including effect tails.

- [Download the complete project ZIP](downloads/NIGHT%20GRAVE%20V2%20-%20complete%20project.zip)
- [FL Studio project](projects/NIGHT%20GRAVE%20V2/NIGHT%20GRAVE%20V2.flp)
- [MP3](projects/NIGHT%20GRAVE%20V2/NIGHT%20GRAVE%20V2.mp3)
- [WAV](projects/NIGHT%20GRAVE%20V2/NIGHT%20GRAVE%20V2.wav)

Open the ZIP directly in FL Studio, or keep the FLP and all its WAV samples together in the project directory. The checked-in FLP uses sample filenames rather than machine-specific paths.

The project contains 14 sampler instruments, 22 editable piano-roll patterns, 185 playlist clips, and nine section markers. Its arrangement includes an intro, two builds, two drops, a breakdown, and an outro. The revision uses a steadier kick/bass groove, restrained fills, a repeating tuned cowbell hook, a detuned pad, and filtered phrase-ending delays.

Native Fruity Reeverb 2 is included on the clap, cowbell, and pad at 12%, 23%, and 42% slot blend respectively. Fruity Limiter is on the master. The effects, envelopes, notes, and mixer routing remain editable; sample sound design is printed into the supplied assets.

## Validation

The supplied audio was rendered in FL Studio **24.2.2.4597**, rather than by the Python script. The complete native render is 147.83 seconds at 44.1 kHz, with a peak of -5.53 dBFS and no nonfinite samples. See [validation.json](projects/NIGHT%20GRAVE%20V2/validation.json) and [production.json](projects/NIGHT%20GRAVE%20V2/production.json) for details.

An initial attempt to combine older reverb preset payloads with a different plugin wrapper froze FL Studio. The final project uses a complete compatible Reeverb 2 slot state from the installed demo project, and passed a full native render after that correction. PyFLP structural parsing alone did not catch the incompatibility.

## Rebuilding

The builder requires Windows, Python, FFmpeg on `PATH`, and the same FL Studio installation and local sample packs used for this experiment. The installation path is currently `C:\Program Files\Image-Line\FL Studio 2024`; change `PACKS` and `template` in the script if necessary. The Phonk folder contains locally installed samples and may not be present in another installation.

```powershell
python -m pip install -r requirements.txt
python build_dark_phonk_v2.py
```

This writes a new `NIGHT GRAVE V2` directory containing the generated FLP and samples. It does not export audio. Close other FL Studio instances before using its command-line renderer:

```powershell
& 'C:\Program Files\Image-Line\FL Studio 2024\FL64.exe' /Ewav /R '.\NIGHT GRAVE V2\NIGHT GRAVE V2.flp'
```

The script includes a compatibility adjustment for PyFLP 2.2.1 on newer Python versions. This is an experimental native-file writer; validate rebuilt projects in FL Studio.

Reference direction: [Kordhell â€” Murder In My Mind](https://kordhell.bandcamp.com/album/murder-in-my-mind) and [INTERWORLD â€” METAMORPHOSIS](https://www.youtube.com/watch?v=lJvRohYSrZM). The melody and arrangement are original.
