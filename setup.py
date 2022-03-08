from cx_Freeze import setup, Executable

print(1)
setup(name="käive Boldi sõitudega",
      version="1",
      description="cxf proov",
      executables=[Executable("käive Boldi sõitudega.py")])
print(2)