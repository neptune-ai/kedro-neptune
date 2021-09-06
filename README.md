# Kedro-Neptune plugin

Main docs page for [Kedro-Neptune plugin](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro)

[See this example in Neptune](https://app.neptune.ai/o/common/org/kedro-integration/e/KED-632/dashboard/Basic-pipeline-metadata-42874940-da74-4cdc-94a4-315a7cdfbfa8)
![Kedro pipeline metadata in custom dashboard in the Neptune UI](https://gblobscdn.gitbook.com/assets%2F-MT0sYKbymfLAAtTq4-t%2F-MhlqBKa6Qzf17-9eW1Z%2F-MhlqL1-UuAUaaJr1ogh%2Fkedro-dashboard.png?alt=media&token=4e841fda-ff91-4fc7-bfc6-6af1445b6772)


## What will you get with this integration?

[Kedro](https://kedro.readthedocs.io/en/stable/index.html) is a popular open-source project that **helps standardize ML workflows**. It gives you a clean and powerful pipeline abstraction where you put all your ML code logic.

[Kedro-Neptune plugin](https://github.com/neptune-ai/kedro-neptune) lets you have all the benefits of a nicely organized kedro pipeline with a powerful user interface built for ML metadata management that lets you:

* **browse, filter, and sort** your model training runs
* **compare nodes and pipelines** on metrics, visual node outputs, and more
* **display all pipeline metadata** including learning curves for metrics, plots, and images, rich media like video and audio or interactive visualizations from Plotly, Altair, or Bokeh
* and do whatever else you would expect from a modern ML metadata store



## Installation

Before you start, make sure that:

* You have `Python 3.6+` in your system,
* You are already a [registered user](https://neptune.ai/register) so that you can log metadata to your [private projects](https://docs.neptune.ai/administration/workspace-project-and-user-management/projects).
* You have your [Neptune API token set to the `NEPTUNE_API_TOKEN`environment variable](../../getting-started/installation.md#authentication-neptune-api-token).

### Install neptune-client, kedro, and kedro-neptune

Depending on your operating system open a terminal or CMD and run this command. All required libraries are available via `pip` and `conda`:

```bash
pip install neptune-client kedro kedro-neptune
```

For more, see [installing neptune-client](https://docs.neptune.ai/getting-started/installation).

## Quickstart

<table>
  <thead>
    <tr>
      <th style="text-align:center">
        <p>&#x200B;<a href="https://github.com/neptune-ai/examples/blob/main/integrations-and-supported-tools/kedro/scripts/kedro_neptune_quickstart">&#x200B;<img src="https://firebasestorage.googleapis.com/v0/b/gitbook-28427.appspot.com/o/assets%2F-MT0sYKbymfLAAtTq4-t%2Fsync%2F182a1a3f734fc1b7d712c68b04c29bad9460d6cd.png?generation=1619014771581311&amp;alt=media" alt/>&#x200B;</a>&#x200B;</p>
        <p><a href="https://github.com/neptune-ai/examples/blob/main/integrations-and-supported-tools/kedro/scripts/kedro_neptune_quickstart">&#x200B;See code examples on GitHub</a>&#x200B;</p>
      </th>
      <th style="text-align:center">
        <p>&#x200B;<a href="https://app.neptune.ai/o/common/org/kedro-integration/e/KED-632/dashboard/Basic-pipeline-metadata-42874940-da74-4cdc-94a4-315a7cdfbfa8">&#x200B;<img src="https://firebasestorage.googleapis.com/v0/b/gitbook-28427.appspot.com/o/assets%2F-MT0sYKbymfLAAtTq4-t%2Fsync%2F0873e466caf5ef7ed205a2b4287a69dcfb39f1f2.png?generation=1619014771570557&amp;alt=media" alt/>&#x200B;</a>&#x200B;</p>
        <p><a href="https://app.neptune.ai/o/common/org/kedro-integration/e/KED-632/dashboard/Basic-pipeline-metadata-42874940-da74-4cdc-94a4-315a7cdfbfa8">&#x200B;See runs logged to Neptune</a>&#x200B;</p>
      </th>
    </tr>
  </thead>
  <tbody></tbody>
</table>

This quickstart will show you how to:

* Connect Neptune to your Kedro project
* Log pipeline and dataset metadata to Neptune
* Add explicit metadata logging to a node in your pipeline  
* Explore logged metadata in the Neptune UI.

### **Before you start**

* [Have Kedro installed](https://kedro.readthedocs.io/en/stable/02_get_started/02_install.html)
* [Have neptune-client and kedro-neptune plugin installed](kedro.md#install-neptune-client-kedro-and-kedro-neptune)

### **Step 1: Create a Kedro project from "pandas-iris" starter**

* Go to your console and create a [Kedro starter project "pandas-iris"](https://kedro.readthedocs.io/en/stable/02_get_started/05_example_project.html)

```bash
kedro new --starter=pandas-iris
```

* Follow instructions and choose a name for your Kedro project. For example,  "Great-Kedro-Project"
* Go to your new Kedro project directory

If everything was set up correctly you should see the following directory structure: 

```text
Great-Kedro-Project # Parent directory of the template
├── conf            # Project configuration files
├── data            # Local project data (not committed to version control)
├── docs            # Project documentation
├── logs            # Project output logs (not committed to version control)
├── notebooks       # Project related Jupyter notebooks (can be used for experimental code before moving the code to src)
├── README.md       # Project README
├── setup.cfg       # Configuration options for `pytest` when doing `kedro test` and for the `isort` utility when doing `kedro lint`
├── src             # Project source code
    ├── pipelines   
        ├── data_science
            ├── nodes.py
            ├── pipelines.py
            └── ...
```

You will use `nodes.py` and `pipelines.py` files in this quickstart.

### **Step 2: Initialize kedro-neptune plugin**

* Go to your Kedro project directory and run

```text
kedro neptune init
```

The command line will ask for your Neptune API token  

* Input your [Neptune API token](../../getting-started/installation.md#authentication-neptune-api-token):
  * Press enter if it was set to the `NEPTUNE_API_TOKEN` environment variable
  * Pass a different environment variable to which you set your Neptune API token. For example   `MY_SPECIAL_NEPTUNE_TOKEN_VARIABLE` 
  * Pass your Neptune API token as a string 

The command line will ask for your Neptune project name  

* Input your [Neptune project name](../../getting-started/installation.md#setting-the-project-name):
  * Press enter if it was set to the `NEPTUNE_PROJECT` environment variable
  * Pass a different environment variable to which you set your Neptune project name. For example   `MY_SPECIAL_NEPTUNE_PROJECT_VARIABLE` 
  * Pass your project name as a string in a format `WORKSPACE/PROJECT`

If everything was set up correctly you should:

* see the message: _"kedro-neptune plugin successfully configured"_
* see three new files in your kedro project:
  * Credentials file:`YOUR_KEDRO_PROJECT/conf/local/credentials_neptune.yml`
  * Config file:`YOUR_KEDRO_PROJECT/conf/base/neptune.yml`
  * Catalog file:`YOUR_KEDRO_PROJECT/conf/base/neptune_catalog.yml`

You can always go to those files and change the initial configuration. 

### **Step 3: Add Neptune logging to a Kedro node**

* Go to a pipeline node _src/KEDRO\_PROJECT/pipelines/data\_science/nodes.py_
* Import Neptune client toward the top of the _nodes.py_

```python
import neptune.new as neptune
```

* Add **neptune\_run** argument of type `neptune.run.Handler` to the `report_accuracy` function 

```python
def report_accuracy(predictions: np.ndarray, test_y: pd.DataFrame, 
                    neptune_run: neptune.run.Handler) -> None:
...
```

You can treat **neptune\_run** like a normal [Neptune Run ](../../you-should-know/core-concepts.md#run)and [log any ML metadata to it](../../you-should-know/what-can-you-log-and-display.md). 

**Important**  
You have to use a special string "**neptune\_run"** to use the Neptune Run handler in Kedro pipelines.

* Log metrics like accuracy to **neptune\_run**  

```python
def report_accuracy(predictions: np.ndarray, test_y: pd.DataFrame, 
                    neptune_run: neptune.run.Handler) -> None:
    target = np.argmax(test_y.to_numpy(), axis=1)
    accuracy = np.sum(predictions == target) / target.shape[0]
    
    neptune_run['nodes/report/accuracy'] = accuracy * 100
```

You can log metadata from any node to any [Neptune namespace](../../you-should-know/logging-metadata.md#run-structure-namespaces) you want. 

* Log images like a confusion matrix to **neptune\_run**

```python
def report_accuracy(predictions: np.ndarray, test_y: pd.DataFrame, 
                    neptune_run: neptune.run.Handler) -> None:
    target = np.argmax(test_y.to_numpy(), axis=1)
    accuracy = np.sum(predictions == target) / target.shape[0]
    
    fig, ax = plt.subplots()
    plot_confusion_matrix(target, predictions, ax=ax)
    neptune_run['nodes/report/confusion_matrix'].upload(fig)
```

**Note**  
You can log metrics, text, images, video, interactive visualizations, and more.   
See a full list of [What you can log and display](../../you-should-know/what-can-you-log-and-display.md) in Neptune.

### **Step 4: Add Neptune Run handler to the Kedro pipeline**

* Go to a pipeline definition, _src/KEDRO\_PROJECT/pipelines/data\_science/pipelines.py_
* Add **neptune\_run** Run handler as an input to the `report` node

```python
node(
    report_accuracy,
    ["example_predictions", "example_test_y", "neptune_run"],
    None,
    name="report"),
```

### **Step 5: Run Kedro pipeline**

Go to your console and execute your Kedro pipeline

```bash
kedro run
```

A link to the Neptune Run associated with the Kedro pipeline execution will be printed to the console.

### **Step 6: Explore results in the Neptune UI** 

* Click on the Neptune Run link in your console or use an example link

[https://app.neptune.ai/common/kedro-integration/e/KED-632](https://app.neptune.ai/common/kedro-integration/e/KED-632)

* Go to the **kedro** namespace where metadata about Kedro pipelines are logged \(see [how to change the default logging location](kedro.md#configure-base-neptune-yml)\)

![Default Kedro namespace in Neptune UI](https://gblobscdn.gitbook.com/assets%2F-MT0sYKbymfLAAtTq4-t%2F-MhlohCAeyv1RNJRkQpG%2F-Mhlp1caicNHOPRs53sv%2Fkedro-all-metadata.png?alt=media&token=22a5d272-9468-407a-a575-e0264b513296)

* See pipeline and node parameters in _**kedro/catalog/parameters**_ 

![Pipeline parameters logged from Kedro to Neptune UI](https://gblobscdn.gitbook.com/assets%2F-MT0sYKbymfLAAtTq4-t%2F-MhlohCAeyv1RNJRkQpG%2F-MhlpBjn-x3c9rhDwekN%2Fkedro-parameters.png?alt=media&token=35cc9a0d-aeae-4b4a-a365-a039da0dd97f)

* See execution parameters in _**kedro/run\_params**_

![Execution parameters logged from Kedro to Neptune UI](https://gblobscdn.gitbook.com/assets%2F-MT0sYKbymfLAAtTq4-t%2F-MhlpF4GGb5JVx-RsqWU%2F-MhlpQiwPa2bpEyGKcR9%2Fkedro-run_params.png?alt=media&token=09827e1d-d2b0-4748-a546-33d133169e24)

* See metadata about the datasets in _**kedro/catalog/datasets/example\_iris\_data**_

![Dataset metadata logged from Kedro to Neptune UI](https://gblobscdn.gitbook.com/assets%2F-MT0sYKbymfLAAtTq4-t%2F-MhlpTH5O7VmBG0MbKzT%2F-Mhlpc79AxCv0s-AUSBB%2Fkedro-dataset-metadata.png?alt=media&token=e58f791a-5988-4c62-aa7b-923f8c4ab8e0)

* See the metrics \(accuracy\) you logged explicitly in the _**kedro/nodes/report/accuracy**_

![Metrics logged from Kedro to Neptune UI](https://gblobscdn.gitbook.com/assets%2F-MT0sYKbymfLAAtTq4-t%2F-MhlpewQ2UncQWdWiW1g%2F-MhlptBzz5sgeIfGp9FL%2Fkedro-accuracy.png?alt=media&token=21a5c03e-e3fe-48be-b1ce-f230e99b5df5)

* See charts \(confusion matrix\) you logged explicitly in the _**kedro/nodes/report/confusion\_matrix**_

![Confusion matrix logged from Kedro to Neptune UI](https://gblobscdn.gitbook.com/assets%2F-MT0sYKbymfLAAtTq4-t%2F-MhlpwncSgltb8WI26mz%2F-Mhlq4WAw7s_QeePOYA1%2Fkedro-confusion-matrix.png?alt=media&token=f0a681e6-3765-4071-91e6-6295cb81cc0c)

## See also

* Main docs page for [Kedro-Neptune plugin](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro)
* How to [Compare Kedro pipelines](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro/compare-kedro-pipelines)
* How to [Compare results between Kedro nodes](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro/compare-results-between-kedro-nodes)
* How to [Display Kedro node metadata and outputs](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro/display-kedro-node-metadata-and-outputs)
