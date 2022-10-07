# Neptune + Kedro Integration

Kedro plugin for experiment tracking and metadata management. It lets you browse, filter and sort runs in a nice UI, visualize node/pipeline metadata, and compare pipelines.

## What will you get with this integration?

* **browse, filter, and sort** your model training runs
* **compare nodes and pipelines** on metrics, visual node outputs, and more
* **display all pipeline metadata** including learning curves for metrics, plots, and images, rich media like video and audio or interactive visualizations from Plotly, Altair, or Bokeh
* and do whatever else you would expect from a modern ML metadata store

![image](https://user-images.githubusercontent.com/97611089/160640893-9b95aac1-095e-4869-88a1-99f2cba5a59f.png)
*Kedro pipeline metadata in custom dashboard in the Neptune UI*

Note: Kedro-Neptune plugin supports distributed pipeline execution and works in Kedro setups that use orchestrators like Airflow or Kubeflow.

## Resources

* [Documentation](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro)
* [Code example on GitHub](https://github.com/neptune-ai/examples/blob/main/integrations-and-supported-tools/kedro/scripts/kedro_neptune_quickstart)
* [Runs logged in the Neptune app](https://app.neptune.ai/o/common/org/kedro-integration/e/KED-632/dashboard/Basic-pipeline-metadata-42874940-da74-4cdc-94a4-315a7cdfbfa8)
* How to [Compare Kedro pipelines](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro/compare-kedro-pipelines)
* How to [Compare results between Kedro nodes](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro/compare-results-between-kedro-nodes)
* How to [Display Kedro node metadata and outputs](https://docs.neptune.ai/integrations-and-supported-tools/automation-pipelines/kedro/display-kedro-node-metadata-and-outputs)

## Example

```python
# On the command line:
pip install neptune-client kedro kedro-neptune
kedro new --starter=pandas-iris

# In your Kedro project directory:
kedro neptune init
```
```python
# In a pipeline node, in nodes.py:
import neptune.new as neptune

# Add a Neptune run handler to the report_accuracy() function
# and log metrics to neptune_run
def report_accuracy(predictions: np.ndarray, test_y: pd.DataFrame,
                    neptune_run: neptune.run.Handler) -> None:
    target = np.argmax(test_y.to_numpy(), axis=1)
    accuracy = np.sum(predictions == target) / target.shape[0]

    neptune_run["nodes/report/accuracy"] = accuracy * 100

# Add the Neptune run handler to the Kedro pipeline
node(
    report_accuracy,
    ["example_predictions", "example_test_y", "neptune_run"],
    None,
    name="report")
```
```python
# On the command line, run the Kedro pipeline
kedro run
```



## Support

If you got stuck or simply want to talk to us, here are your options:

* Check our [FAQ page](https://docs.neptune.ai/getting-started/getting-help#frequently-asked-questions)
* You can submit bug reports, feature requests, or contributions directly to the repository.
* Chat! When in the Neptune application click on the blue message icon in the bottom-right corner and send a message. A real person will talk to you ASAP (typically very ASAP),
* You can just shoot us an email at support@neptune.ai
