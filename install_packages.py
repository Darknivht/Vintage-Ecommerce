import subprocess
import sys

packages = [
    'Django==5.2.4',
    'Pillow',
    'django-recaptcha',
    'django-humanize'
]

for package in packages:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")