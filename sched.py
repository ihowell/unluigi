import luigi
import time
from subprocess import Popen
import argparse
# import importlib.util
import os
import sys
import json
import workflow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "workflow", help="path to a python file containing a `Workflow` class")
    parser.add_argument("config_path", help="Path to a configuration json file.")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--local_scheduler", type=bool, default=False)
    args = parser.parse_args()

    if not os.path.isfile(args.workflow):
        raise Exception("Invalid workflow path " + args.workflow)

    if not os.path.isfile(args.config_path):
        raise Exception("Given config_path does not point to a file %s" % args.config_path)

    with open(args.config_path, 'r') as config_file:
        config = json.load(config_file)

    # spec = importlib.util.spec_from_file_location("workflow", args.workflow)
    # workflow = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(workflow)

    if not args.local_scheduler:
        if not os.path.exists(config['log_dir']):
            os.path.makedirs(config['log_dir'])
        proc = Popen(["luigid", "--logdir", config['log_dir']])
        time.sleep(1)

    create_workflows = workflow.CreateWorkflows(args.config_path)
    luigi.build([create_workflows],
                workers=args.workers,
                local_scheduler=args.local_scheduler)

    if not args.local_scheduler:
        proc.kill()


if __name__ == '__main__':
    print(sys.argv)
    main()
