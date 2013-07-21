import subprocess
import re

class Wrapper:
    def __init__(self, log):
        self.log = log

    def run(self):
        output = []
        startup_done = False

        try:
            process = subprocess.Popen(['java', '-jar', 'minecraft_server.jar', 'nogui'],
                stdin  = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                bufsize = 1,
                close_fds = True)
        except OSError as e:
            self.log(0, "error: couldn't start java: {0}".format(e))
            raise SystemExit(1)

        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip('\r\n')
            line = re.sub('^(\d{4}-\d{2}-\d{2} |)(\d{2}:\d{2}:\d{2}) ', '', line)

            #Log
            output.append(line)
            self.log(2, line)

            #Check for "Done!" message
            m = re.search(r'Done \([0-9\.]+s\)\!.*', line)
            if m:
                startup_done = True
                process.stdin.write('stop\n')

        if not startup_done:
            self.log(0, "error: server failed to start!")
            for line in output:
                self.log(1, line)
            raise SystemExit(1)
