import luigi
import argparse
import importlib.util
import os
import unluigi.util.monitor_tools as monitor_tools
from unluigi.config.experiment import ExperimentConfig
from unluigi.util.parse_unknown_args import parse_cmdline_kwargs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "workflow", help="path to a python file containing a `Workflow` class")

    args, unknown_args = parser.parse_known_args()
    extra_args = parse_cmdline_kwargs(unknown_args)

    if not os.path.isfile(args.workflow):
        raise Exception("Invalid workflow path " + args.workflow)

    spec = importlib.util.spec_from_file_location("workflow", args.workflow)
    workflow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workflow)

    # Initiate logging by retrieving an experiment_id
    if ExperimentConfig().server_url is not None:
        monitor_tools.retrieve_new_experiment_id()

    tasks = workflow.create_tasks(**extra_args)
    luigi.build(tasks, local_scheduler=True)


if __name__ == '__main__':
    main()
