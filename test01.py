from conf import SAMPLE_INPUTS, SAMPLE_OUTPUTS
from moviepy import CompositeVideoClip, VideoFileClip
from moviepy.video import fx as vfx
import glob
import os


def generateclip(s):
    tokens = []
    for raw_token in s.split(" "):
        token = raw_token.strip()
        if not token:
            continue
        cleaned = token.lower()
        if cleaned.isalpha():
            if len(cleaned) > 1:
                tokens.extend(list(cleaned))
            else:
                tokens.append(cleaned)
        else:
            tokens.append(cleaned)

    print("[test01.generateclip] tokens:", tokens)
    print("[test01.generateclip] token_count:", len(tokens))
    clips = []

    alphabet_dir = os.path.join(SAMPLE_INPUTS, 'alphabets')
    os.chdir(alphabet_dir)
    for token in tokens:
        matched = None
        for file in glob.glob("*.mp4"):
            if token.lower() == os.path.splitext(file)[0].lower():
                matched = file
                break
        if matched:
            clip = VideoFileClip(os.path.join(alphabet_dir, matched))
            original_duration = clip.duration
            clip = clip.with_duration(min(2, clip.duration))
            print(
                "[test01.generateclip] token:",
                token,
                "file:",
                matched,
                "duration:",
                original_duration,
                "used_duration:",
                clip.duration,
            )
            clip = clip.with_effects([vfx.FadeIn(0.05), vfx.FadeOut(0.05)])
            clips.append(clip)
        else:
            print("[test01.generateclip] no alphabet clip matched token:", token)

    if not clips:
        return

    transition = 0.2
    prepared_clips = []
    for index, clip in enumerate(clips):
        clip = clip.with_effects([vfx.Resize((640, 480))])

        if index == 0:
            clip = clip.with_effects([vfx.FadeIn(0.15)])
        elif index == len(clips) - 1:
            clip = clip.with_effects([vfx.FadeOut(0.15)])
        else:
            clip = clip.with_effects([vfx.FadeIn(0.15), vfx.FadeOut(0.15)])

        prepared_clips.append(clip)

    composite_clips = []
    start_time = 0.0
    for index, clip in enumerate(prepared_clips):
        clip_start = 0.0 if index == 0 else start_time - transition
        composite_clips.append(clip.with_start(clip_start))
        start_time = clip_start + clip.duration
        print(
            "[test01.generateclip] timeline index:",
            index,
            "clip_start:",
            clip_start,
            "clip_duration:",
            clip.duration,
            "next_start_time:",
            start_time,
        )

    final_clip = CompositeVideoClip(composite_clips, size=(640, 480))
    final_clip = final_clip.with_duration(max((clip.start + clip.duration) for clip in composite_clips))
    print("[test01.generateclip] final_duration:", final_clip.duration)
    print("[test01.generateclip] expected_frame_count_at_24fps:", int(final_clip.duration * 24))
    os.chdir(SAMPLE_OUTPUTS)
    print("[test01.generateclip] writing output clipg.mp4")
    final_clip.write_videofile(
        "clipg.mp4",
        codec="libx264",
        preset="ultrafast",
        audio=False,
        fps=24,
        logger=None,
    )
    print("[test01.generateclip] finished writing output clipg.mp4")

    os.chdir(SAMPLE_INPUTS)
