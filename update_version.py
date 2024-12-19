import sys
import toml

def update_pyproject_version(version):
    """Update version in pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        config = toml.load(f)

    config["tool"]["poetry"]["version"] = version

    with open("pyproject.toml", "w") as f:
        toml.dump(config, f)
    print(f"Updated pyproject.toml to version {version}")

def update_setup_py_version(version):
    """Update version in setup.py."""
    setup_file = "setup.py"
    with open(setup_file, "r") as f:
        lines = f.readlines()

    with open(setup_file, "w") as f:
        for line in lines:
            if line.startswith("    version="):
                f.write(f"    version='{version}',\n")
            else:
                f.write(line)
    print(f"Updated setup.py to version {version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <version>")
        sys.exit(1)

    new_version = sys.argv[1]
    update_pyproject_version(new_version)
    update_setup_py_version(new_version)
