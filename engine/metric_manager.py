class MetricManager:

    _metrics = []

    @classmethod
    def register(cls, metric):
        cls._metrics.append(metric)

    @classmethod
    def run_all(cls, tree, file_path, language):

        results = {}

        for metric in cls._metrics:
            output = metric.analyze(tree, file_path, language)

            if output:
                results.update(output)

        return results
