# Orchestration

## Extract

The extract pipeline is an AWS Step Function that is triggered by an event containing a list of tables to extract and
additional data needed for the extract job. The pipeline is defined using Amazon States Language (ASL) in a JSON
configuration file. The pipeline starts with the "Extract Config Manager" state, which is a task that invokes a Lambda
function that retrieves the extract configuration from an S3 bucket and generates the input arguments for the extract
jobs.

The pipeline then moves on to the "Iterate Through Extract Tables" state, which is a map state that iterates through the
list of tables to extract and processes each table with the "ItemProcessor" state. The "ItemProcessor" state contains
a "Choice" state, named "Choose Job Type", that checks the "job_type" field in the input argument for each table. If the
value is "glue", the pipeline moves on to the "Glue Start Extract Job Run" state, if it is "emr" it would go to the
EMR run state, and the same goes for ECS, which is a task that starts a Glue job.
If the Glue job encounters any errors, it is caught by the "
Catch" state, "Handle Extract Job Run Status", which updates the extract tracking table with the failure status.

The pipeline also includes a state named "Handle Extract Job Run Status" that is used to update the extract tracking
table with the status of the job run, success or failure. This state is executed both when the job completes
successfully and when it encounters an error.

The pipeline is commented throughout and the comments provide an overview of the functionality of each state and how the
pipeline works.

1. The pipeline starts with the Extract Config Manager state, which is a task that invokes an AWS Lambda function. This
   function is responsible for consuming the event payload and constructing the input arguments for the extract jobs.
2. The output from the Extract Config Manager is passed to the next state, Iterate Through Extract Tables, which is a
   map state. This state iterates through each table specified in the tables_to_extract payload and processes them
   individually.
3. Within the map state, the Choose Job Type state is executed. This is a choice state that checks the job_type key in
   the current table's payload. If the value is "glue", the next state is Glue Start Extract Job Run, otherwise it goes
   to Handle Extract Job Run Status.
4. The Glue Start Extract Job Run state is a task that starts a Glue Job Run. The job name, number of workers, and
   worker type are specified in the pipeline's parameters. Additionally, the extract table, job type, source type, and
   other relevant details are passed as arguments to the Glue job.
5. Once the Glue Job Run is complete, the pipeline proceeds to the Handle Extract Job Run Status state. This state is
   responsible for handling the status of the Glue Job Run, such as checking for errors, and updating the extract
   tracking table.
6. After the Glue Job Run and status handling, the pipeline proceeds to the next table in the tables_to_extract payload
   and repeats the process until all tables have been processed.
7. Once all tables have been processed, the pipeline reaches the end of the Iterate Through Extract Tables state and the
   extract pipeline is complete.