# Create a Process
**Once a Logic has been registered, you can create a containerized Process. This Process will then be orchestrated by a pipeline.**

At this step-
1. Select a Logic to build the Process on.
2. Set parameters that will be used when the Process will be executed in a Pipeline.
    - Base image - Base Singularity or Docker image upon which the Process image will be built. This is relevant if executing a Singularity image.
    - Python packages - List of python packages that will need to be installed within the container for your code to work.
    - System packages - List of system packages that must be installed within the containerized environment.
    - Environment variables - Any environment variables that are accessed by your code. The value will be set at runtime.
    - Binds - Any paths that will be used by your code. The corresponding host mount path will be added in runtime.
    - Command Flags - Any additional flags that will be required when the containerized environment is being constructed. (e.g. --fakeroot, --tmpdir)

```
- For example, if your logic loads a FSL Singularity image from the host machine which is referred to as FSL_IMG_NAME in your function, add FSL_IMG_NAME as an environment variable. Or, if your code loads files from the host which is internally referred to as /opt/fsl_images, add '/opt/fsl_images' as a bind.
- Similarly, if your function requires external python packages such as 'nibabel' and 'numpy', include that in the Python packages.
- The function is provided as a reference as you add the parameters.
```

```python
import os
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np

def fsl_bet(input_filepath: str):
    fsl_img_name = os.getenv("FSL_IMG_NAME")
    fsl_img_path = f"/opt/fsl_images/{fsl_img_name}"
    .
    .
    .
    .

```