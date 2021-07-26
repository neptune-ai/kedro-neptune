import os

from kedro.framework.session import KedroSession


class TestPlanets:
    def test_basename(self):
        os.chdir('examples/planets')

        with KedroSession.create("planets") as session:
            session.run()
