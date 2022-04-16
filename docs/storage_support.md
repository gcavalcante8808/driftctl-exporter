## A note about the ResultPath determines how to retrieve/store driftctl json result files

As stated in the README.MD file, the environment variable `RESULT_PATH` should have a value that is valid in terms of the RFC1808 (rURL), resulting in values like these ones:

 * s3://my-bucket/some-path/my-object.json
 * file:///var/folder/result.json

In terms of implementation, the `RESULT_PATH` will be written by `scan.py` to persist the `drictl scan` result and will be ready by `web.py` to create the `/metrics` endpoint. 
The main thing about the scheme/protocol that compounds the value is that the drifctl-exporter decides how to access (open or save) result files using the `SmartyResultRepositoryFactory`, which in time check if the specified scheme is present on its lookup table/enum and returns the appropriate instance:

```python
class SupportedRepositories(enum.Enum):
    FILE = ResultFileStorage
    S3 = S3Repository

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))


class SmartyResultRepositoryFactory:
    @staticmethod
    def get_repository_by_scheme_url(url: Rfc1808Url):
        repository = getattr(SupportedRepositories, url.scheme.upper(), None)
        if not repository:
            raise ValueError(
                f"Only {SupportedRepositories.list()} repositories are supported. The {url.scheme} storage, "
                f"isn't supported.")

        return repository.value()
```

The entries present on the `SupportedRepositories` are in turn, the upper string representation of the `scheme` of results path URL, where each name have a value that is the RepositoryClass itself (not instance). With this in mind, a simple use of the smarty result repository can be seen at `src/exporter/tests/test_repositories.py` but will be roughly something like this:

```python
url = Rfc1808Url.from_url('s3://my-bucket/my-path/results.json')
repository = SmartyResultRepositoryFactory.get_repository_by_scheme_url(url)
```
