# vysvedcenie-poslancov

This repo contains code to:
- scrape data about Slovak politicians
- create a dashboard with summary stats (currently running [here](https://vysvedcenie-poslancov.herokuapp.com/))
## Dependencies
We recommend a standard Anaconda installation of Python 3. To use the dashboard, one needs Plotly Dash. The relevant packages are `dash`, `dash-core-components`, `dash-html-components`, and `plotly`.

```
conda install -c conda-forge dash
conda install -c conda-forge dash-core-components
conda install -c conda-forge dash-html-components
conda install -c plotly plotly
```

## Dashboard
Once all the dependencies are installed, the dashboard can be started by running:
```
python main.py
```
Open up the browser at `localhost:8050` and enjoy :)
