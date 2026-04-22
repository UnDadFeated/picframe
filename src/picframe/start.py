import logging
import logging.handlers
import argparse
import os
import locale
import sys
import subprocess
from shutil import copytree

from picframe import model, viewer_display, controller, __version__

PICFRAME_DATA_DIR = 'picframe_data'


def copy_files(pkgdir, dest, target):
    fullpath = os.path.join(pkgdir,  target)
    destination = os.path.join(dest,  PICFRAME_DATA_DIR)
    destination = os.path.join(destination,  target)
    copytree(fullpath,  destination)


def create_config(root):
    fullpath_root = os.path.join(root,  PICFRAME_DATA_DIR)
    fullpath = os.path.join(fullpath_root, 'config')
    source = os.path.join(fullpath, 'configuration_example.yaml')
    destination = os.path.join(fullpath, 'configuration.yaml')
    run_start = os.path.join(fullpath_root, 'run_start.py')  # TODO for work-around on RPi4

    with open(source, "r") as file:
        filedata = file.read()

    print("This will configure ", destination)
    print("To keep default, just hit enter")

    # replace all paths with selected picframe_data path
    filedata = filedata.replace("~/picframe_data", fullpath_root)

    # pic_dir
    pic_dir = input("Enter picture directory [~/Pictures]: ")
    if pic_dir == "":
        pic_dir = "~/Pictures"  # convert to absolute path too for work-around on RPi4 running as root
    pic_dir = os.path.expanduser(pic_dir)
    filedata = filedata.replace("~/Pictures", pic_dir)

    # deleted_pictures
    deleted_pictures = input("Enter picture directory [~/DeletedPictures]: ")
    if deleted_pictures == "":
        deleted_pictures = "~/DeletedPictures"
    deleted_pictures = os.path.expanduser(deleted_pictures)
    filedata = filedata.replace("~/DeletedPictures", deleted_pictures)

    # locale
    lan, enc = locale.getlocale()
    if not lan:
        (lan, enc) = ("en_US", "utf8")
    param = input("Enter locale [" + lan + "." + enc + "]: ") or (lan + "." + enc)
    filedata = filedata.replace("en_US.utf8", param)

    with open(destination, "w") as file:
        file.write(filedata)

    with open(run_start, "w") as file:  # TODO work-around for RPi4
        file.write("from picframe import start\nstart.main()\n")


def check_packages(packages):
    for package in packages:
        try:
            if package == 'paho.mqtt':
                import paho.mqtt
                print(package, ': ', paho.mqtt.__version__)
            elif package == 'ninepatch':
                import ninepatch  # noqa: F401
                print(package, ': installed, but no version info')
            else:
                print(package, ': ', __import__(package).__version__)
        except ImportError:
            print(package, ': Not found!')


def setup_logging(log_level='WARNING', log_max_days=10):
    """Set up logging with file rotation for runtime logs."""
    # Get the log directory from environment or default
    log_dir = os.path.expanduser('~/picframe_data/logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'picframe.log')
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.WARNING))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # File handler with rotation (10 days max)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, 
        when='midnight', 
        interval=1,  # daily rotation
        backupCount=log_max_days
    )
    file_handler.setLevel(logging.INFO)  # Capture INFO+ runtime logs in file
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler for INFO level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def run_startup_auto_update(updater_config, logger):
    if not updater_config.get('auto_update_on_start', False):
        return False

    git_branch = updater_config.get('git_branch', 'dev')
    repo_dir = os.path.expanduser(updater_config.get('repo_dir', '')).strip()

    try:
        if repo_dir:
            git_remote = updater_config.get('git_remote', 'fork')
            logger.info("Auto-update enabled. Checking %s/%s in %s", git_remote, git_branch, repo_dir)
            fetch_cmd = ["git", "fetch", git_remote, git_branch]
            subprocess.run(fetch_cmd, cwd=repo_dir, check=True, capture_output=True, text=True)

            local_rev = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True,
                capture_output=True, text=True
            ).stdout.strip()
            remote_rev = subprocess.run(
                ["git", "rev-parse", f"{git_remote}/{git_branch}"], cwd=repo_dir, check=True,
                capture_output=True, text=True
            ).stdout.strip()

            if local_rev == remote_rev:
                logger.info("Auto-update check complete: already up to date")
                return False

            logger.warning("Update available. Pulling %s/%s", git_remote, git_branch)
            pull_cmd = ["git", "pull", "--ff-only", git_remote, git_branch]
            subprocess.run(pull_cmd, cwd=repo_dir, check=True, capture_output=True, text=True)
            logger.warning("Auto-update applied successfully")
            return True

        pip_git_url = updater_config.get('pip_git_url', 'https://github.com/UnDadFeated/picframe.git')
        package_spec = f"git+{pip_git_url}@{git_branch}"
        logger.info("Auto-update enabled (pip mode). Installing %s", package_spec)
        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', package_spec]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        output = (result.stdout or '') + (result.stderr or '')
        if 'Successfully installed' in output or 'Successfully uninstalled' in output:
            logger.warning("Auto-update applied successfully via pip")
            return True

        logger.info("Auto-update check complete: package already satisfied")
        return False
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Startup auto-update failed: %s", exc)
        return False


def main():
    # First, create a basic logger to capture early startup messages
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger("start.py")
    logger.info('starting %s', sys.argv)

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--initialize",
                       help="creates standard file structure for picframe in destination directory",
                       metavar=('DESTINATION_DIRECTORY'))
    group.add_argument("-v", "--version", help="print version information",
                       action="store_true")
    group.add_argument("configfile", nargs='?', help="/path/to/configuration.yaml")
    args = parser.parse_args()
    if args.initialize:
        if os.geteuid() == 0:
            print("Don't run the initialize step with sudo. It might put the files in the wrong place!")
            return
        pkgdir = sys.modules['picframe'].__path__[0]
        try:
            dest = os.path.abspath(os.path.expanduser(args.initialize))
            copy_files(pkgdir, dest, 'html')
            copy_files(pkgdir, dest, 'config')
            copy_files(pkgdir, dest, 'data')
            create_config(dest)
            print('created {}/picframe_data'.format(dest))
        except Exception as e:
            print("Can't copy files to: ", args.initialize, ". Reason: ", e)
        return
    elif args.version:
        print("picframe version: ", __version__)
        print("\nChecking required packages......")  # TODO update list of packages
        required_packages = ['PIL',
                             'pi3d',
                             'yaml',
                             'paho.mqtt',
                             'iptcinfo3',
                             'numpy',
                             'ninepatch',
                             'pi_heif',
                             'defusedxml',
                             'vlc']
        check_packages(required_packages)
        return
    elif args.configfile:
        m = model.Model(args.configfile)
    else:
        m = model.Model()

    # Set up logging based on config after model is loaded
    viewer_config = m.get_viewer_config()
    log_level = viewer_config.get('log_level', 'WARNING')
    log_max_days = viewer_config.get('log_max_days', 10)
    setup_logging(log_level, log_max_days)
    startup_logger = logging.getLogger("start.py")
    updater_config = m.get_viewer_config().get('updater', {}) if hasattr(m, 'get_viewer_config') else {}
    did_update = run_startup_auto_update(updater_config, startup_logger)
    if did_update and updater_config.get('restart_after_update', True):
    startup_logger.warning("Restarting picframe after auto-update - gracefully shutting down")
    # Get current process PID before we do anything
    current_pid = os.getpid()
        # Send SIGTERM to gracefully stop the current process (this will trigger clean shutdown in controller)
        try:
            import signal
            os.kill(current_pid, signal.SIGTERM)
        except OSError:
            pass
        
        # Wait briefly for clean shutdown (max 3 seconds)
        for _ in range(30):
            time.sleep(0.1)
            try:
                os.kill(current_pid, 0)
            except OSError:
                break  # Process has exited
        
        # Small delay then restart
        time.sleep(0.5)
        os.execv(sys.executable, [sys.executable] + sys.argv)

    v = viewer_display.ViewerDisplay(m.get_viewer_config())
    c = controller.Controller(m, v)
    c.start()
    c.loop()
    c.stop()


if __name__ == "__main__":
    main()
