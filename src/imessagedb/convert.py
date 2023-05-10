import heic2png
import os
import ffmpeg
import os

def convert_heic_image(heic_location, png_location, verbose=False) -> bool:

    # Don't do the expensive conversion if we've already converted it
    if os.path.exists(png_location):
        return True
    else:
        try:
            if verbose:
                print(f"Converting {os.path.basename(png_location)}")
            heic_image = heic2png.HEIC2PNG(heic_location)
            heic_image.save(png_location)

            return True
        except Exception as exp:
            print(f'Failed to convert {heic_location} to {png_location}: {exp}')
            return False


def convert_audio_video(original, converted, verbose=False):
    if os.path.exists(converted):
        return True
    else:
        try:
            if verbose:
                print(f"Converting {os.path.basename(converted)}")
            stream = ffmpeg.input(original)
            stream = ffmpeg.output(stream, converted)
            stream = ffmpeg.overwrite_output(stream)
            ffmpeg.run(stream, quiet=True)
            return True
        except Exception as exp:
            print(f'Failed to convert {original} to {converted}: {exp}')
            return False
