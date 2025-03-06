from hspipy import HSP
import pandas as pd

df = pd.DataFrame([[15.8, 8.8, 19.4, 1]], columns=["D", "P", "H", "Score"])
hsp = HSP()  # No arguments
hsp.get(df)  # Pass DataFrame to get()
print(hsp.d, hsp.p, hsp.h)  # Should output 15.8, 8.8, 19.4