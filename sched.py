import luigi
import time
from subprocess import Popen
import argparse
# import importlib.util
import os
import sys
import workflow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "workflow", help="path to a python file containing a `Workflow` class")
    parser.add_argument("config", help="Path to a configuration json file.")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--local_scheduler", type=bool, default=False)
    args = parser.parse_args()

    if not os.path.isfile(args.workflow):
        print("Invalid workflow path " + args.workflow)
        exit(1)

    # spec = importlib.util.spec_from_file_location("workflow", args.workflow)
    # workflow = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(workflow)

    if not args.local_scheduler:
        proc = Popen([
            "luigid", "--logdir", "/Users/ihowell/Projects/luigi_workflows/log"
        ])
        time.sleep(1)
    create_workflows = workflow.CreateWorkflows(args.config)
    luigi.build([create_workflows],
                workers=args.workers,
                local_scheduler=args.local_scheduler)
    if not args.local_scheduler:
        proc.kill()


if __name__ == '__main__':
    print(sys.argv)
    main()
