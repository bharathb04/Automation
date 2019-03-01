import subprocess 
import shlex

class Result:
    pass


def run(command, issuesErrorMessages = True):
    result = Result()

    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()

    result.exit_code = p.returncode
    result.stdout = stdout
    result.stderr = stderr
    result.command = command

    if p.returncode != 0 and issuesErrorMessages:
        print('Error executing command [%s]' % command)
        print('stderr: [%s]' % stderr)
        print('stdout: [%s]' % stdout)

    return result