import os
import argparse
import soundfile as sf
import glob
import tqdm.contrib.concurrent
import functools
from pysndfx import AudioEffectsChain

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--wham_dir', type=str, required=True,
                    help='Path to wham_noise root directory')


def main(args):
    wham_noise_dir = args.wham_dir
    # Get train dir
    subdir = os.path.join(wham_noise_dir, 'tr')
    # List files in that dir
    sound_paths = glob.glob(os.path.join(subdir, '**/*.wav'),
                            recursive=True)
    # Avoid running this script if it already have been run
    if len(sound_paths) == 60000:
        print("It appears that augmented files have already been generated."
              "If the augmentation process went well the first time you ran "
              "generate_librimix.sh please comment out the line relative to"
              " augment_train_noise.py. Skipping data augmentation ")
        return
    elif len(sound_paths) != 20000:
        print("It appears that augmented files have not been generated properly"
              "Resuming augmentation")
        to_be_removed_08 = [x for path in sound_paths if 'sp08' in path for x in (path,path.replace(('sp08'),''))]
        to_be_removed_12 = [x for path in sound_paths if 'sp12' in path for x in (path,path.replace(('sp12'),''))]
        sound_paths_08 = list(set(sound_paths) - set(to_be_removed_08))
        sound_paths_12 = list(set(sound_paths) - set(to_be_removed_12))
        augment_noise(sound_paths_08, 0.8)
        augment_noise(sound_paths_12, 1.2)
    else:
        print(f'Augmenting {subdir} files')
        # Transform audio speed
        augment_noise(sound_paths, 0.8)
        augment_noise(sound_paths, 1.2)


def augment_noise(sound_paths, speed):
    print(f"Change speed with factor {speed}")
    tqdm.contrib.concurrent.process_map(
        functools.partial(apply_fx, speed=speed),
        sound_paths,
        chunksize=10
    )


def apply_fx(sound_path, speed):
    # Get the effect
    fx = (AudioEffectsChain().speed(speed))
    s, rate = sf.read(sound_path)
    # Get 1st channel
    s = s[:, 0]
    # Apply effect
    s = fx(s)
    # Write the file
    sf.write(f"""{sound_path.replace(
        '.wav',f"sp{str(speed).replace('.','')}" +'.wav')}""", s, rate)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
