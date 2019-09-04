import luigi
import time
from subprocess import Popen
import argparse
import importlib.util
import os
import sys
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "workflow", help="path to a python file containing a `Workflow` class")
    parser.add_argument("config_path",
                        help="Path to a configuration json file.")
    args = parser.parse_args()

    if not os.path.isfile(args.workflow):
        raise Exception("Invalid workflow path " + args.workflow)

    if not os.path.isfile(args.config_path):
        raise Exception("Given config_path does not point to a file %s" %
                        args.config_path)

    with open(args.config_path, 'r') as config_file:
        config = json.load(config_file)

    spec = importlib.util.spec_from_file_location("workflow", args.workflow)
    workflow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workflow)

    if not os.path.exists(config['tmp_path']):
        os.makedirs(config['tmp_path'])

    if not config['local_scheduler']:
        if not os.path.exists(config['log_dir']):
            os.makedirs(config['log_dir'])
        proc = Popen(["luigid", "--logdir", config['log_dir']])
        time.sleep(1)

    create_workflows = workflow.CreateWorkflows(args.config_path)
    luigi.build([create_workflows],
                workers=config['max_running_jobs'],
                local_scheduler=config['local_scheduler'])

    if not config['local_scheduler']:
        proc.kill()


if __name__ == '__main__':
    print(sys.argv)
    main()
