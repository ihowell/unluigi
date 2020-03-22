import subprocess as sub
import os


def ex_local(command):
    '''
    Execute command locally through the shell (not through resource manager).

    We execute through the shell to ensure environment variables are set correctly

    Args:
       command (str|[str]): The command string or list of command and parameters to execute.
    '''
    # If list, convert to string
    if isinstance(command, list):
        command = sub.list2cmdline(command)

    completed_proc = sub.run(command,
                             shell=True,
                             capture_output=True,
                             check=True)
    return (completed_proc.returncode, completed_proc.stdout,
            completed_proc.stderr)


def record_output(base_path, task_name, returncode, stdout, stderr):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    with open("%s/%s.retcode" % (base_path, task_name), 'w') as out_file:
        out_file.write(str(returncode))
    with open("%s/%s.out" % (base_path, task_name), 'w') as out_file:
        out_file.write(stdout.decode("utf-8"))
    with open("%s/%s.err" % (base_path, task_name), 'w') as out_file:
        out_file.write(stderr.decode("utf-8"))

    if returncode > 0:
        raise Exception("Received error code %s in %s" %
                        (returncode, task_name))
