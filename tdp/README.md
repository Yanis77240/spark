# TDP Spark Notes

The version 2.3.5-TDP-0.1.0-SNAPSHOT of Apache Hive is based on the `branch-2.3` tag of the Apache [repository](https://github.com/apache/spark/tree/branch-2.3).

## Jenkinfile

The file `./Jenkinsfile-sample` can be used in a Jenkins / Kubernetes environment to build and execute the unit tests of the Spark project. See []() for details on the environment.

## Making a release

```
./dev/make-distribution.sh --name tdp --tgz -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 -Pflume
```

The command generates a `.tar.gz` file of the release at `./spark-2.3.5-TDP-0.1.0-SNAPSHOT-bin-tdp.tgz`.

## Testing parameters

```
mvn test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 --fail-never
```

- -Phive -Phive-thriftserver: Enables Hive integration for Spark SQL along with its JDBC server and CLI
- -Pyarn: Embeds the YARN jars in the distribution
- -Phadoop-3.1: Custom made profile for Hadoop 3.1.1-TDP-0.1.0-SNAPSHOT. Activates Curator version 2.12.0 which is the same as the one used in Hadoop 3.1.1-TDP-0.1.0-SNAPSHOT. This was inspired by the way Hortonworks did for [Spark in HDP 3.1.5.0-152](https://github.com/hortonworks/spark2-release/blob/HDP-3.1.5.0-152-tag/pom.xml).
- -Pflume: Builds the Flume jars, needed by Oozie
- --fail-never: Does not interrupt the tests if one module fails

**Note:** The command `sudo update-java-alternatives --set /usr/lib/jvm/java-1.8.0-openjdk-amd64`, we need to figure out why the `JAVA_HOME` is not picked for this project.

## Test execution notes

See `./test_notes.txt`
