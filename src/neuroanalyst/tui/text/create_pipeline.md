# Create a Pipeline
**All the computational units in your pipeline have been registered as logics, and built as containerized processes. Now, you arrange them into a pipeline.**

At this step-
1. Provide information about your data pipeline (the whys and the hows). Exhaustive metadata will help maintain provenance and enhance downstream AI-powered analysis.
2. Set the number of steps in the pipeline and select the processes that will be executed at each step.
3. As you add a process, you may notice a window pop up asking for more information about certain binds and environment variables. Note that when you create the process, you added these parameters. At this stage, providing values to them will help in execution of the process.
4. Select Execution Mode - Choose CONTAINER to run all the processes as Singulairty containers, and VENV to run them within virtual environments. Make sure that you have first built the environments for each process.
5. Select HPC Scheduler - Choose scheduler if you are running this on a HPC, or High Performance Computing cluster. This will enable the pipeline to run processes using the selected scheduler - this utilizing the computational capabilities of the HPC.
6. Starting Scope - This will tell the pipeline if the first step of the pipeline will work raw data or the data of any existing pipeline.
7. Select the BIDS filters that will identify the files to be processed in the first step. The files for the next steps will be identified by the output_entities in the logic of the previous step. This will be handled internally. Run the check button to see if you are retrieving the right files for the first step.