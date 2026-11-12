# Scientific constants

Import constants for use in calculations:

```python
from labplotlib import Measurement, consts

temperature = Measurement(300, 3)
energy = consts.kb * temperature
```

To list the constants, run the source file directly from the project root:

```powershell
python .\src\labplotlib\consts.py
```