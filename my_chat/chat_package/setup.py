# from setuptools import setup
import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {"packages": ["src"]}

setup(name='chat_package',
      version='0.0.1',
      author='Konstantin Troshenkin',
      description='Chat application',
      options={
          'build_exe': build_exe_options
      },
      executables=[Executable('client.py', base=base)]
      )
