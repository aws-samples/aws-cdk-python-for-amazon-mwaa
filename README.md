# Python CDK for deploying Amazon Managed Workflows for Apache Airflow (MWAA)

This sample shows you how to configure [Amazon MWAA](https://aws.amazon.com/managed-workflows-for-apache-airflow/) via AWS CDK (Python). 

MWAA is a managed [Apache Airflow](https://airflow.apache.org/) offering from AWS. Airflow is a popular open-source tool to programmatically author, schedule, and monitor workflows.

It maintains the workflows in a [Directed Acyclic Graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph).

Detailed architecture can be found in the [Airflow website](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html). 

Deploying MWAA in AWS requires a few components - an S3 bucket (to store the code for DAGs, and requirements/dependencies), IAM role(s) for the executor, as well as the user, a VPC with VPC endpoints (for private resource connectivity), a security group. and the MWAA environment itself.

* The Bucket and its deployment is contained in the [airflow_source_stack.py](./aws_cdk_python_for_amazon_mwaa/airflow_source_stack.py) in the [aws_cdk_python_for_amazon_mwaa](./aws_cdk_python_for_amazon_mwaa/) directory. The DAG code is in the [dags](./dags/) folder. And the requirements/dependencies are in the [requires](./requires/) folder. This sample uses the [S3 Bucket Deployment](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3_deployment/BucketDeployment.html) CDK construct to upload these components to AWS S3 from the local repository.

* The rest of the components are in the [aws_cdk_python_for_amazon_mwaa_stack.py](./aws_cdk_python_for_amazon_mwaa/aws_cdk_python_for_amazon_mwaa_stack.py) file in the [aws_cdk_python_for_amazon_mwaa](./aws_cdk_python_for_amazon_mwaa/) directory.

NOTE:
* Deploying this will deploy a VPC. If you'd like to use a specific [CIDR](https://aws.amazon.com/what-is/cidr) range for your VPC, you can alter the value [here](./aws_cdk_python_for_amazon_mwaa/aws_cdk_python_for_amazon_mwaa_stack.py?plain=1#L233).
* If you'd like to change the name of the MWAA Environment, you can do so by modifying the value [here](./aws_cdk_python_for_amazon_mwaa/aws_cdk_python_for_amazon_mwaa_stack.py?plain=1#L194).
* **Creation of the MWAA environment take about 30-45 minutes**. Feel free to get a cup of coffee or something when the Cloudformation stack is creating the MWAA environment.
* There is a [utility/script](https://github.com/awslabs/aws-support-tools/blob/master/MWAA/verify_env/verify_env.py) that you can run to see if your configuration is correct for MWAA (*whilst it is deploying*)
* MWAA supports limited versions of Airflow. The [requirements file](./requires/requirements-2024-01-12-1518.txt) needs to have a `--constraint` url specified. This ensures a specific version of Airflow with a specific version of Python3 is installed.
    * In this sample, Airflow version is 2.7.2 and Python version is 3.11.
    * It also installs the [airflow operator/connector](https://airflow.apache.org/docs/apache-airflow-providers-snowflake/stable/operators/snowflake.html) for [Snowflake](https://www.snowflake.com/en/). 
    * More details on supported version can be found in the [AWS documentation](https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html).

## Deploying your environment

### Pre-requisites:

* Since this is a CDK project, you should have [npm](https://www.npmjs.com/) installed (which is the package manager for TypeScript/JavaScript).
    * You can find installation instructions for npm [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

* Install CDK via `npm install -g aws-cdk`.

* Install [AWS CLI](https://aws.amazon.com/cli/) on your computer (*if not already done so*).
    *  `pip install awscli`. This means need to have python installed on your computer (if it is not already installed.)
    * You need to also configure and authenticate your AWS CLI to be able to interact with AWS programmatically. Detailed instructions of how you could do that are provided [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

### Install dependencies

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate

# for other shells like fish, you can do source .venv/bin/activate.fish
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

### Deploy the AirflowSourceStack

```
cdk deploy AirflowSourceStack

# You can optionally specify `--profile` at the end of that command if you wish to not use the default AWS profile.
```

### Deploy the AwsCdkPythonForAmazonMwaaStack

```
cdk deploy AwsCdkPythonForAmazonMwaaStack

# You can optionally specify `--profile` at the end of that command if you wish to not use the default AWS profile.
```

### Run the example DAG

After successfuly deployment of you MWAA environment, you can navigate to the MWAA in the management console, and click on the link to the Webserver UI. This will open the typical Airflow web UI. You can test the [example dag](./dags/example_dag.py) provided in this repository by enabling it and running it.


## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
