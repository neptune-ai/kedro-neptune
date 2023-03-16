# Neptune + Kedro integration

Kedro plugin for experiment tracking and metadata management. It lets you browse, filter and sort runs in a nice UI, visualize node/pipeline metadata, and compare pipelines.

## What will you get with this integration?

* **browse, filter, and sort** your model training runs
* **compare nodes and pipelines** on metrics, visual node outputs, and more
* **display all pipeline metadata** including learning curves for metrics, plots, and images, rich media like video and audio or interactive visualizations from Plotly, Altair, or Bokeh
* and do whatever else you would expect from a modern ML metadata store

![image](https://user-images.githubusercontent.com/97611089/160640893-9b95aac1-095e-4869-88a1-99f2cba5a59f.png)
*Kedro pipeline metadata in custom dashboard in the Neptune web app*

Note: The Kedro-Neptune plugin supports distributed pipeline execution and works in Kedro setups that use orchestrators like Airflow or Kubeflow.

## Resources

* [Documentation](https://docs.neptune.ai/integrations/kedro)
* [Code example on GitHub](https://github.com/neptune-ai/examples/tree/main/integrations-and-supported-tools/kedro/scripts/kedro-neptune-quickstart)
* [Example run logged in the Neptune app](https://app.neptune.ai/o/common/org/kedro-integration/e/KED-1563/dashboard/Basic-pipeline-metadata-42874940-da74-4cdc-94a4-315a7cdfbfa8)
* How to [Compare Kedro pipelines](https://docs.neptune.ai/integrations/kedro_comparing_pipelines/)
* How to [Compare results between Kedro nodes](https://docs.neptune.ai/integrations/kedro_comparing_nodes/)
* How to [Display Kedro node metadata and outputs](https://docs.neptune.ai/integrations/kedro_displaying_node_outputs/)

## Example

On the command line:

```
pip install kedro neptune[kedro]
kedro new --starter=pandas-iris
```

In your Kedro project directory:

```
kedro neptune init
```

In a pipeline node, in `nodes.py`:

```python
import neptune

# Add a Neptune run handler to the report_accuracy() function

def report_accuracy(
    y_pred: pd.Series,
    y_test: pd.Series,
    neptune_run: neptune.handler.Handler,
) -> None:
    accuracy = (y_pred == y_test).sum() / len(y_test)
    logger = logging.getLogger(__name__)
    logger.info("Model has accuracy of %.3f on test data.", accuracy)

    # Log metrics to the Neptune run
    neptune_run["nodes/report/accuracy"] = accuracy * 100

# Add the Neptune run handler to the Kedro pipeline
node(
    func=report_accuracy,
    inputs=["y_pred", "y_test", "neptune_run"],
    outputs=None,
    name="report_accuracy",
)
```

On the command line, run the Kedro pipeline:

```
kedro run
```

## Support

If you got stuck or simply want to talk to us, here are your options:

* Check our [FAQ page](https://docs.neptune.ai/getting_help)
* You can submit bug reports, feature requests, or contributions directly to the repository.
* Chat! When in the Neptune application click on the blue message icon in the bottom-right corner and send a message. A real person will talk to you ASAP (typically very ASAP),
* You can just shoot us an email at support@neptune.ai
