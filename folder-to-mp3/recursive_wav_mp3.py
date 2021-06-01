import argparse
import os
from pathlib import Path
import subprocess
import sys

def get_lame_call(platform):
    if platform == 'win32':
        win_exec_name = 'lame.exe'
        win_path = os.path.join('C:\\Program Files (x86)\\Lame For Audacity\\', win_exec_name)
        return win_path

    elif platform in ['linux', 'darwin']:
        return 'lame'

    else:
        raise ValueError('OS not implemented')

def main():
    """ Simple script to transform all wav files within a directory (and it subdirectories) to MP3 using LAME.
    
    Call the script with the argument --folder to give an specific folder, or use default the folder 'inputs'
    at the same level than this script.

    It skips files if a mp3 version already exists. (Same name but with .mp3 instead of .wav)
    """

    # LAME help
    # lame --preset help -> medium, standard, extreme, insane
    lame_preset_value = 'standard'

    print(f"Wav to MP3 conversion with lame preset: {lame_preset_value}")

    # Parse folder from args or use default path
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder')
    arg_path = parser.parse_args().folder

    # Directory with wav files
    directory_to_mp3 = arg_path if arg_path is not None else 'inputs'
    print(f"Converting directory '{directory_to_mp3}'")
    print("")

    # Lame path for each OS
    lame_app = get_lame_call(sys.platform)

    path = Path(directory_to_mp3)

    for p in path.rglob("*.wav"):
        dir_path = p.parent
        file_name = p.name
        file_path_wav = os.path.join(dir_path, file_name)
        file_path_mp3 = file_path_wav.replace('.wav', '.mp3')

        if not Path(file_path_mp3).is_file():
            commandLine = [lame_app, '--preset', lame_preset_value, file_path_wav]
            process = subprocess.Popen(commandLine, executable=lame_app)
            print(f"File '{file_path_mp3}': Rendered")
        else:
            print(f"File '{file_path_mp3}': Skipped")

    print("Finisehd!")


if __name__ == "__main__":
    main()
