# UNL Luigi

Starter code for running luigi on UNL's HCC cluster. This tool filly the void of dynamically creating jobs for multiple dependencies and dynamically filling parameters when submitting many jobs to HCC. In addition, it fixes the pipeline issue of needing to run commands in sequence.

This project accomplishes this by extending the Luigi Repository (https://github.com/spotify/luigi) to use with Crane's htcondor submission and bash command submission. To learn more, take a look at the `ShellTask` and `SlurmTask` files. (`SlurmTask` is taken from the [Sciluigi](https://github.com/pharmbio/sciluigi) project).

To effectively use this project, a working knowledge of luigi is require. The documentation is available at: https://luigi.readthedocs.io/en/stable/.

## Usage

This project is intended to be integrated into an `externalTools/` directory or the like within given projects. It is written as starter code and not as a library.
1. First, create your tasks, extending either the `ShellTask` or `SlurmTask` classes. Note that only commands used run using `self.run_command` or `self.ex` respectively will execute on other nodes.
2. Create a workflow that links together tasks. One useful utility for sequentially linking these tasks is `util.TaskSequence`, which is a method that takes a list of tasks and makes the next item in a list `require` the previous item.
3. Define the `CreateWorkflows` task, which is what the main scheduler in `sched.py` looks for. Here, you can create many parameterized workflows and return them all in a list in the `requires` function, which luigi will create the dependency graph with and start execution.
4. Finally, modify the `sched.submit` file to point to the correct workflow and configuration path before executing `condor_submit sched.submit` to submit the job to condor.

Note: You may receive an error from condor if the `logs/` directory does not exist in this projects directory.

This repository provides an example of this process as well as example configuration files to get started.

## Pull Requests

If you would like to suggest any additions that would be useful to the general user (not project specific) or find any bugs, please feel free to submit a pull request or file an issue.
