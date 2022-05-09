# TDP Spark Notes

The version 3.2.2-TDP-0.1.0-SNAPSHOT of Apache Spark is based on the `branch-3.2` branch of the [Apache repository](https://github.com/apache/spark/tree/branch-3.2).

## Jenkinfile

The file `./Jenkinsfile-sample` can be used in a Jenkins / Kubernetes environment to build and execute the unit tests of the Spark project. See [Jenkinsfile.sample](Jenkinsfile.sample) for details on the environment.

## Making a release

```bash
./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1
```

The command generates a `.tar.gz` file of the release at `./spark-3.2.2-TDP-0.1.0-SNAPSHOT-bin-tdp.tgz`.

## Testing parameters

```bash
export MAVEN_OPTS="-Xss64m -Xmx2g -XX:ReservedCodeCacheSize=1g"
export DEFAULT_ARTIFACT_REPOSITORY="file:$HOME/.m2/repository/"
./build/mvn test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 --fail-never
```

- `-Phive -Phive-thriftserver`: Enables Hive integration for Spark SQL along with its JDBC server and CLI
- `-Pyarn`: Embeds the YARN jars in the distribution
- `-Phadoop-3.1`: Custom made profile for Hadoop 3.1.1-TDP-0.1.0-SNAPSHOT. Activates Curator version 2.12.0 which is the same as the one used in Hadoop 3.1.1-TDP-0.1.0-SNAPSHOT. This was inspired by the way Hortonworks did for [Spark in HDP 3.1.5.0-152](https://github.com/hortonworks/spark2-release/blob/HDP-3.1.5.0-152-tag/pom.xml).
- `--fail-never`: Does not interrupt the tests if one module fails

### Generating HTML test reports

```bash
./build/mvn surefire-report:report-only -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1
```

### Testing a specific class

```bash
PACKAGE_DIR=./resource-managers/yarn
TEST_CLASS=org.apache.spark.deploy.yarn.YarnClusterSuite
./build/mvn test -Dtest=none -DwildcardSuites="$TEST_CLASS" -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -pl "$PACKAGE_DIR"
```

## Test notes

See [test-notes](./test-notes.md)
