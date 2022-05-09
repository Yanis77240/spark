# Test notes

- [Code changes](#code-changes)
- [Test Command](#test-command)
- [Test results](#test-results)
- [Test failures and solutions](#test-failures-and-solutions)
  - [spark-core](#spark-core)
  - [spark-sql](#spark-sql)
  - [spark-hive](#spark-hive)
  - [spark-hive-thriftserver](#spark-hive-thriftserver)

## Code changes

1. Spark version: `3.2.2-SNAPSHOT` → `3.2.2-TDP-0.1.0-SNAPSHOT`
2. Hive version: `2.3.9` → `2.3.10-TDP-0.1.0-SNAPSHOT`
3. Hadoop profile:

   ```xml
   <profile>
     <id>hadoop-3.1</id>
     <properties>
       <hadoop.version>3.1.1-TDP-0.1.0-SNAPSHOT</hadoop.version>
       <curator.version>2.12.0</curator.version>
       <hadoop-client-api.artifact>hadoop-client</hadoop-client-api.artifact>
       <hadoop-client-runtime.artifact>hadoop-yarn-api</hadoop-client-runtime.artifact>
       <hadoop-client-minicluster.artifact>hadoop-client</hadoop-client-minicluster.artifact>
     </properties>
     <dependencies>
       <dependency>
         <groupId>org.apache.hadoop</groupId>
         <artifactId>hadoop-yarn-common</artifactId>
       </dependency>
       <dependency>
         <groupId>org.apache.hadoop</groupId>
         <artifactId>hadoop-yarn-server-web-proxy</artifactId>
       </dependency>
       <dependency>
         <groupId>org.apache.hadoop</groupId>
         <artifactId>hadoop-yarn-client</artifactId>
       </dependency>
       <dependency>
         <groupId>org.apache.hadoop</groupId>
         <artifactId>hadoop-yarn-server-resourcemanager</artifactId>
         <scope>test</scope>
       </dependency>
       <dependency>
         <groupId>org.apache.hadoop</groupId>
         <artifactId>hadoop-yarn-server-tests</artifactId>
         <classifier>tests</classifier>
         <scope>test</scope>
       </dependency>
     </dependencies>
   </profile>
   ```

4. Set `DEFAULT_ARTIFACT_REPOSITORY` to local Maven cache before running tests:
   ```bash
   export DEFAULT_ARTIFACT_REPOSITORY="file:$HOME/.m2/repository/"
   # Tried
   # export DEFAULT_ARTIFACT_REPOSITORY="file:$HOME/.m2/repository/,https://maven-central.storage-download.googleapis.com/maven2/"
   # at first but Ivy did not resolve comma-separated string
   ```
5. Correct function `isHadoop3()` in [VersionUtils.scala](../core/src/main/scala/org/apache/spark/util/VersionUtils.scala) to fix issue with Hadoop < 3.3.1 where LZ4 codec tests fail:

   ```scala
   def isHadoop3: Boolean = majorMinorVersion(VersionInfo.getVersion) == (3, 3)
   ```

   This results in disabling tests related to LZ4 as in [SPARK-36820](https://issues.apache.org/jira/browse/SPARK-36820) corrected in [apache/spark#34064](https://github.com/apache/spark/pull/34064) for Hadoop 2.7.

6. Modify test `SPARK-32212` in [HadoopVersionInfoSuite.scala](../sql/hive/src/test/scala/org/apache/spark/sql/hive/client/HadoopVersionInfoSuite.scala) to include TDP's version of Hadoop that do not support shaded client:
   ```scala
   test("SPARK-32212: built-in Hadoop version should support shaded client if it is not hadoop 2 or hadoop 3.1") {
     val hadoopVersion = VersionInfo.getVersion
     if (!hadoopVersion.startsWith("2") && !hadoopVersion.startsWith("3.1")) {
       assert(IsolatedClientLoader.supportsHadoopShadedClient(hadoopVersion))
     }
   }
   ```
7. Modify test `SPARK-33084` in [SQLQuerySuite.scala](../sql/core/src/test/scala/org/apache/spark/sql/SQLQuerySuite.scala) to point to TDP's version of Hive:
   ```scala
   test("SPARK-33084: Add jar support Ivy URI in SQL") {
     val sc = spark.sparkContext
     val hiveVersion = "2.3.10-TDP-0.1.0-SNAPSHOT"
   ```

## Test Command

```bash
export DEFAULT_ARTIFACT_REPOSITORY="file:$HOME/.m2/repository/"
./build/mvn test -Phive -Phive-thriftserver -Pyarn -Phadoop-3.1 --fail-never
```

## Test results

| Package                         | Tests     | Failures    | Skipped | Success rate |
| ------------------------------- | --------- | ----------- | ------- | ------------ |
| spark-core                      | 3167      | 12 → 1      | 9       | 99.684%      |
| spark-graphx                    | 109       | 0           | 0       | 100%         |
| spark-launcher                  | 46        | 0           | 0       | 100%         |
| spark-mllib-local               | 96        | 0           | 0       | 100%         |
| spark-mllib                     | 1767      | 0           | 7       | 99.604%      |
| spark-repl                      | 44        | 0           | 0       | 100%         |
| spark-streaming                 | 441       | 0           | 1       | 99.773%      |
| spark-kvstore                   | 105       | 0           | 0       | 100%         |
| spark-network-common            | 103       | 0           | 0       | 100%         |
| spark-network-shuffle           | 132       | 0           | 0       | 100%         |
| spark-sketch                    | 34        | 0           | 0       | 100%         |
| spark-unsafe                    | 77        | 0           | 1       | 98.701%      |
| spark-avro                      | 276       | 0           | 2       | 99.275%      |
| spark-sql-kafka-0-10            | 484       | 0           | 0       | 100%         |
| spark-streaming-kafka-0-10      | 10        | 0           | 0       | 100%         |
| spark-token-provider-kafka-0-10 | 44        | 0           | 0       | 100%         |
| spark-yarn                      | 147       | 0           | 1       | 96.599%      |
| spark-catalyst                  | 6515      | 0           | 5       | 99.923%      |
| spark-sql                       | 10755     | 5 → 4       | 34      | 99.637%      |
| spark-hive                      | 4312      | 4 → 3       | 604     | 85.9%        |
| spark-hive-thriftserver         | 562       | 5           | 20      | 95.552%      |
| **Total**                       | **29226** | **25 → 13** | **669** | **99.976%**  |

## Test failures and solutions

### spark-core

#### Class: `org.apache.spark.SparkContextSuite`

- Error:

  ```
  [unresolved dependency: org.apache.hive#hive-storage-api;2.7.0: not found]
  [unresolved dependency: org.apache.hive#hive-storage-api;2.6.0: not found]
  ```

  - Status: **11 failures resolved** + 1 failure ignored
  - Tests (~~11 failures~~ 1 failure):

    - `SPARK-33084: Add jar support Ivy URI -- test different version`
    - ~~`SPARK-33084: Add jar support Ivy URI -- default transitive = true`~~
    - ~~`SPARK-33084: Add jar support Ivy URI -- invalid transitive use default false`~~
    - ~~`SPARK-33084: Add jar support Ivy URI -- transitive=true will download dependency jars`~~
    - ~~`SPARK-34506: Add jar support Ivy URI -- transitive=false will not download dependency jars`~~
    - ~~`SPARK-34506: Add jar support Ivy URI -- test exclude param when transitive unspecified`~~
    - ~~`SPARK-33084: Add jar support Ivy URI -- test exclude param when transitive=true`~~
    - ~~`SPARK-33084: Add jar support Ivy URI -- test invalid param`~~
    - ~~`SPARK-33084: Add jar support Ivy URI -- test multiple transitive params`~~
    - ~~`SPARK-33084: Add jar support Ivy URI -- test param key case sensitive`~~
    - ~~`SPARK-33084: Add jar support Ivy URI -- test transitive value case insensitive`~~

  - Cause: Apache Ivy doesn't support comma-separated repositories lists
  - Solution:
    - Only use the local Maven cache as `DEFAULT_ARTIFACT_REPOSITORY`. See [Code changes 4.](#code-changes)
    - The failure related to `hive-storage-api;2.6.0` remains because the version `2.3.10-TDP-0.1.0-SNAPSHOT` of Hive only contains `hive-storage-api:2.7.0`
  - Stack trace:

    ```
    java.lang.RuntimeException: [unresolved dependency: org.apache.hive#hive-storage-api;2.7.0: not found]
    at org.apache.spark.deploy.SparkSubmitUtils$.resolveMavenCoordinates(SparkSubmit.scala:1447)
        at org.apache.spark.util.DependencyUtils$.resolveMavenDependencies(DependencyUtils.scala:185)
    at org.apache.spark.util.DependencyUtils$.resolveMavenDependencies(DependencyUtils.scala:159)
        at org.apache.spark.SparkContext.addJar(SparkContext.scala:1996)
        at org.apache.spark.SparkContext.addJar(SparkContext.scala:1928)
        at org.apache.spark.SparkContextSuite.$anonfun$new$115(SparkContextSuite.scala:1041)
        at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
        at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
    at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
        at org.scalatest.Transformer.apply(Transformer.scala:22)
        at org.scalatest.Transformer.apply(Transformer.scala:20)
        at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
        at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
        at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
        at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
        at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
        at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
        at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
    at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
        at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
        at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
        at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
        at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
        at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
        at scala.collection.immutable.List.foreach(List.scala:431)
        at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
        at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
        at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
        at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
        at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
        at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
        at org.scalatest.Suite.run(Suite.scala:1112)
        at org.scalatest.Suite.run$(Suite.scala:1094)
        at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
        at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
        at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
        at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
        at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
    at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
        at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
        at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
        at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
        at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
        at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
        at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
        at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
        at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
        at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
        at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
        at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
        at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
        at org.scalatest.Suite.run(Suite.scala:1109)
        at org.scalatest.Suite.run$(Suite.scala:1094)
        at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
        at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
        at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
        at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
        at scala.collection.immutable.List.foreach(List.scala:431)
        at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
        at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
        at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
        at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
        at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
        at org.scalatest.tools.Runner$.main(Runner.scala:775)
        at org.scalatest.tools.Runner.main(Runner.scala)
    ```

#### Class: `org.apache.spark.FileSuite`

- Error:

  ```
  java.lang.RuntimeException: native lz4 library not available
  ```

  - Status: **Resolved**
  - Tests (~~1 failure~~):

    - ~~`SequenceFile (compressed) - lz4`~~

  - Cause: Tests related to LZ4 fail for Hadoop < 3.3.1 (see [apache/spark#34064](https://github.com/apache/spark/pull/34064))
  - Solution: Correct function `isHadoop3()`. See [Code changes 5.](#code-changes)
  - Stack trace:

    ```
    Cause: org.apache.spark.SparkException: Job aborted due to stage failure: Task 0 in stage 1.0 failed 1 times, most recent failure: Lost task 0.0 in stage 1.0 (TID 1) (localhost executor driver): java.lang.RuntimeException: native lz4 library not available
      at org.apache.hadoop.io.compress.Lz4Codec.getCompressorType(Lz4Codec.java:125)
      at org.apache.hadoop.io.compress.CodecPool.getCompressor(CodecPool.java:150)
      at org.apache.hadoop.io.compress.CodecPool.getCompressor(CodecPool.java:168)
      at org.apache.hadoop.io.SequenceFile$Writer.init(SequenceFile.java:1304)
      at org.apache.hadoop.io.SequenceFile$Writer.&lt;init&gt;(SequenceFile.java:1192)
      at org.apache.hadoop.io.SequenceFile$BlockCompressWriter.&lt;init&gt;(SequenceFile.java:1552)
      at org.apache.hadoop.io.SequenceFile.createWriter(SequenceFile.java:289)
      at org.apache.hadoop.io.SequenceFile.createWriter(SequenceFile.java:542)
      at org.apache.hadoop.mapred.SequenceFileOutputFormat.getRecordWriter(SequenceFileOutputFormat.java:64)
      at org.apache.spark.internal.io.HadoopMapRedWriteConfigUtil.initWriter(SparkHadoopWriter.scala:238)
      at org.apache.spark.internal.io.SparkHadoopWriter$.executeTask(SparkHadoopWriter.scala:126)
      at org.apache.spark.internal.io.SparkHadoopWriter$.$anonfun$write$1(SparkHadoopWriter.scala:88)
      at org.apache.spark.scheduler.ResultTask.runTask(ResultTask.scala:90)
      at org.apache.spark.scheduler.Task.run(Task.scala:131)
      at org.apache.spark.executor.Executor$TaskRunner.$anonfun$run$3(Executor.scala:506)
      at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1491)
      at org.apache.spark.executor.Executor$TaskRunner.run(Executor.scala:509)
      at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
      at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
      at java.lang.Thread.run(Thread.java:748)
    ```

### spark-sql

#### Class: `org.apache.spark.sql.jdbc.JDBCV2Suite`

- Error:

  ```
  org.scalatest.exceptions.TestFailedException: "== Parsed Logical Plan == ... did not contain "PushedAggregates: [COUNT(`名`)]"
  ```

  - Status:
  - Tests (1 failure):

    - `column name with non-ascii`

  - Cause: Character set issue
  - Solution:

  - Stack trace:

    ```
    org.scalatest.exceptions.TestFailedException: &quot;== Parsed Logical Plan ==
    'Project [unresolvedalias('COUNT('?), None)]
    +- 'UnresolvedRelation [h2, test, person], [], false

    == Analyzed Logical Plan ==
    count(?): bigint
    Aggregate [count(?#x) AS count(?)#xL]
    +- SubqueryAlias h2.test.person
      +- RelationV2[?#x] test.person

    == Optimized Logical Plan ==
    Aggregate [sum(COUNT(?)#xL) AS count(?)#xL]
    +- RelationV2[COUNT(?)#xL] test.person

    == Physical Plan ==
    AdaptiveSparkPlan isFinalPlan=false
    +- HashAggregate(keys=[], functions=[sum(COUNT(?)#xL)], output=[count(?)#xL])
      +- Exchange SinglePartition, ENSURE_REQUIREMENTS, [id=#x]
          +- HashAggregate(keys=[], functions=[partial_sum(COUNT(?)#xL)], output=[sum#xL])
            +- Scan org.apache.spark.sql.execution.datasources.v2.jdbc.JDBCScan$$anon$1@639e1e2c [COUNT(?)#xL] PushedAggregates: [COUNT(`?`)], PushedFilters: [], PushedGroupby: [], ReadSchema: struct<COUNT(?):bigint>" did not contain "PushedAggregates: [COUNT(`名`)]"
      at org.scalatest.Assertions.newAssertionFailedException(Assertions.scala:472)
      at org.scalatest.Assertions.newAssertionFailedException$(Assertions.scala:471)
      at org.scalatest.Assertions$.newAssertionFailedException(Assertions.scala:1231)
      at org.scalatest.Assertions$AssertionsHelper.macroAssert(Assertions.scala:1295)
      at org.apache.spark.sql.ExplainSuiteHelper.$anonfun$checkKeywordsExistsInExplain$2(ExplainSuite.scala:66)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.WrappedArray.foreach(WrappedArray.scala:38)
      at org.apache.spark.sql.ExplainSuiteHelper.$anonfun$checkKeywordsExistsInExplain$1(ExplainSuite.scala:65)
      at org.apache.spark.sql.ExplainSuiteHelper.$anonfun$checkKeywordsExistsInExplain$1$adapted(ExplainSuite.scala:64)
      at org.apache.spark.sql.ExplainSuiteHelper.withNormalizedExplain(ExplainSuite.scala:43)
      at org.apache.spark.sql.ExplainSuiteHelper.withNormalizedExplain$(ExplainSuite.scala:42)
      at org.apache.spark.sql.jdbc.JDBCV2Suite.withNormalizedExplain(JDBCV2Suite.scala:33)
      at org.apache.spark.sql.ExplainSuiteHelper.checkKeywordsExistsInExplain(ExplainSuite.scala:64)
      at org.apache.spark.sql.ExplainSuiteHelper.checkKeywordsExistsInExplain$(ExplainSuite.scala:62)
      at org.apache.spark.sql.jdbc.JDBCV2Suite.checkKeywordsExistsInExplain(JDBCV2Suite.scala:33)
      at org.apache.spark.sql.ExplainSuiteHelper.checkKeywordsExistsInExplain(ExplainSuite.scala:72)
      at org.apache.spark.sql.ExplainSuiteHelper.checkKeywordsExistsInExplain$(ExplainSuite.scala:71)
      at org.apache.spark.sql.jdbc.JDBCV2Suite.checkKeywordsExistsInExplain(JDBCV2Suite.scala:33)
      at org.apache.spark.sql.jdbc.JDBCV2Suite$$anonfun$$nestedInanonfun$new$76$1.applyOrElse(JDBCV2Suite.scala:502)
      at org.apache.spark.sql.jdbc.JDBCV2Suite$$anonfun$$nestedInanonfun$new$76$1.applyOrElse(JDBCV2Suite.scala:498)
      at scala.PartialFunction$Lifted.apply(PartialFunction.scala:228)
      at scala.PartialFunction$Lifted.apply(PartialFunction.scala:224)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$collect$1(TreeNode.scala:294)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$collect$1$adapted(TreeNode.scala:294)
      at org.apache.spark.sql.catalyst.trees.TreeNode.foreach(TreeNode.scala:253)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$foreach$1(TreeNode.scala:254)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$foreach$1$adapted(TreeNode.scala:254)
      at scala.collection.Iterator.foreach(Iterator.scala:943)
      at scala.collection.Iterator.foreach$(Iterator.scala:943)
      at scala.collection.AbstractIterator.foreach(Iterator.scala:1431)
      at scala.collection.IterableLike.foreach(IterableLike.scala:74)
      at scala.collection.IterableLike.foreach$(IterableLike.scala:73)
      at scala.collection.AbstractIterable.foreach(Iterable.scala:56)
      at org.apache.spark.sql.catalyst.trees.TreeNode.foreach(TreeNode.scala:254)
      at org.apache.spark.sql.catalyst.trees.TreeNode.collect(TreeNode.scala:294)
      at org.apache.spark.sql.jdbc.JDBCV2Suite.$anonfun$new$76(JDBCV2Suite.scala:498)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

#### Class: `org.apache.spark.sql.SQLQuerySuite`

- Error:

  ```
  [unresolved dependency: org.apache.hive.hcatalog#hive-hcatalog-core;2.3.9: not found]
  ```

  - Status: **Unresolved**
  - Tests (1 failure):

    - `SPARK-33084: Add jar support Ivy URI in SQL`

  - Cause: Hive `2.3.9` is not present in local Maven cache
  - Solution: **Not working** Modify test to use TDP's Hive version. See [Code changes 7.](#code-changes)
  - Stack trace:

    ```
    java.lang.RuntimeException: [unresolved dependency: org.apache.hive.hcatalog#hive-hcatalog-core;2.3.9: not found]
      at org.apache.spark.deploy.SparkSubmitUtils$.resolveMavenCoordinates(SparkSubmit.scala:1447)
      at org.apache.spark.util.DependencyUtils$.resolveMavenDependencies(DependencyUtils.scala:185)
      at org.apache.spark.util.DependencyUtils$.resolveMavenDependencies(DependencyUtils.scala:159)
      at org.apache.spark.sql.internal.SessionResourceLoader.resolveJars(SessionState.scala:162)
      at org.apache.spark.sql.internal.SessionResourceLoader.addJar(SessionState.scala:176)
      at org.apache.spark.sql.execution.command.AddJarsCommand.$anonfun$run$1(resources.scala:32)
      at org.apache.spark.sql.execution.command.AddJarsCommand.$anonfun$run$1$adapted(resources.scala:32)
      at scala.collection.immutable.Stream.foreach(Stream.scala:533)
      at org.apache.spark.sql.execution.command.AddJarsCommand.run(resources.scala:32)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult$lzycompute(commands.scala:75)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult(commands.scala:73)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.executeCollect(commands.scala:84)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.$anonfun$applyOrElse$1(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$5(SQLExecution.scala:103)
      at org.apache.spark.sql.execution.SQLExecution$.withSQLConfPropagated(SQLExecution.scala:163)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$1(SQLExecution.scala:90)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.execution.SQLExecution$.withNewExecutionId(SQLExecution.scala:64)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:93)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$transformDownWithPruning$1(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.trees.CurrentOrigin$.withOrigin(TreeNode.scala:82)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDownWithPruning(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.org$apache$spark$sql$catalyst$plans$logical$AnalysisHelper$$super$transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning(AnalysisHelper.scala:267)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning$(AnalysisHelper.scala:263)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDown(TreeNode.scala:457)
      at org.apache.spark.sql.execution.QueryExecution.eagerlyExecuteCommands(QueryExecution.scala:93)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted$lzycompute(QueryExecution.scala:80)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted(QueryExecution.scala:78)
      at org.apache.spark.sql.Dataset.<init>(Dataset.scala:219)
      at org.apache.spark.sql.Dataset$.$anonfun$ofRows$2(Dataset.scala:99)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.Dataset$.ofRows(Dataset.scala:96)
      at org.apache.spark.sql.SparkSession.$anonfun$sql$1(SparkSession.scala:618)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.SparkSession.sql(SparkSession.scala:613)
      at org.apache.spark.sql.test.SQLTestUtilsBase.$anonfun$sql$1(SQLTestUtils.scala:231)
      at org.apache.spark.sql.SQLQuerySuite.$anonfun$new$826(SQLQuerySuite.scala:3707)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

#### Class: `org.apache.spark.sql.TPCDSV1_4_PlanStabilitySuite`

- Error:

  ```
  Plans did not match: last approved simplified plan: /tdp/spark-apache/sql/core/src/test/resources/tpcds-plan-stability/approved-plans-v1_4/q4/simplified.txt last approved explain plan: /tdp/spark-apache/sql/core/src/test/resources/tpcds-plan-stability/approved-plans-v1_4/q4/explain.txt
  ```

  - Status: **Unresolved**
  - Tests (2 failures):

    - `check simplified (tpcds-v1.4/q4)`
    - `check simplified (tpcds-v1.4/q5)`

  - Cause: Unknown
  - Solution:
  - Stack trace:

    ```
    org.scalatest.exceptions.TestFailedException:
    Plans did not match:
    last approved simplified plan: /tdp/spark-apache/sql/core/src/test/resources/tpcds-plan-stability/approved-plans-v1_4/q4/simplified.txt
    last approved explain plan: /tdp/spark-apache/sql/core/src/test/resources/tpcds-plan-stability/approved-plans-v1_4/q4/explain.txt

    TakeOrderedAndProject [customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address]
      WholeStageCodegen (24)
        Project [customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address]
          BroadcastHashJoin [customer_id,customer_id,year_total,year_total,year_total,year_total]
            Project [customer_id,customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address,year_total,year_total,year_total]
              BroadcastHashJoin [customer_id,customer_id]
                Project [customer_id,customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address,year_total,year_total]
                  BroadcastHashJoin [customer_id,customer_id,year_total,year_total,year_total,year_total]
                    Project [customer_id,year_total,customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address,year_total,year_total]
                      BroadcastHashJoin [customer_id,customer_id]
                        BroadcastHashJoin [customer_id,customer_id]
                          Filter [year_total]
                            HashAggregate [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,d_year,sum,isEmpty] [sum(CheckOverflow((promote_precision(CheckOverflow((promote_precision(cast(CheckOverflow((promote_precision(cast(CheckOverflow((promote_precision(cast(ss_ext_list_price as decimal(8,2))) - promote_precision(cast(ss_ext_wholesale_cost as decimal(8,2)))), DecimalType(8,2), true) as decimal(9,2))) - promote_precision(cast(ss_ext_discount_amt as decimal(9,2)))), DecimalType(9,2), true) as decimal(10,2))) + promote_precision(cast(ss_ext_sales_price as decimal(10,2)))), DecimalType(10,2), true)) / 2.00), DecimalType(14,6), true)),customer_id,year_total,sum,isEmpty]
                              InputAdapter
                                Exchange [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,d_year] #1
                                  WholeStageCodegen (3)
                                    HashAggregate [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,d_year,ss_ext_list_price,ss_ext_wholesale_cost,ss_ext_discount_amt,ss_ext_sales_price] [sum,isEmpty,sum,isEmpty]
                                      Project [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,ss_ext_discount_amt,ss_ext_sales_price,ss_ext_wholesale_cost,ss_ext_list_price,d_year]
                                        BroadcastHashJoin [ss_sold_date_sk,d_date_sk]
                                          Project [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,ss_ext_discount_amt,ss_ext_sales_price,ss_ext_wholesale_cost,ss_ext_list_price,ss_sold_date_sk]
                                            BroadcastHashJoin [c_customer_sk,ss_customer_sk]
                                              Filter [c_customer_sk,c_customer_id]
                                                ColumnarToRow
                                                  InputAdapter
                                                    Scan parquet default.customer [c_customer_sk,c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address]
                                              InputAdapter
                                                BroadcastExchange #2
                                                  WholeStageCodegen (1)
                                                    Filter [ss_customer_sk]
                                                      ColumnarToRow
                                                        InputAdapter
                                                          Scan parquet default.store_sales [ss_customer_sk,ss_ext_discount_amt,ss_ext_sales_price,ss_ext_wholesale_cost,ss_ext_list_price,ss_sold_date_sk]
                                                            SubqueryBroadcast [d_date_sk] #1
                                                              BroadcastExchange #3
                                                                WholeStageCodegen (1)
                                                                  Filter [d_year,d_date_sk]
                                                                    ColumnarToRow
                                                                      InputAdapter
                                                                        Scan parquet default.date_dim [d_date_sk,d_year]
                                          InputAdapter
                                            ReusedExchange [d_date_sk,d_year] #3

    ...

    actual simplified plan: /tdp/spark-apache/sql/core/target/tmp/q4.actual.simplified.txt
    actual explain plan: /tdp/spark-apache/sql/core/target/tmp/q4.actual.explain.txt

    TakeOrderedAndProject [customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address]
      WholeStageCodegen (24)
        Project [customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address]
          BroadcastHashJoin [customer_id,customer_id,year_total,year_total,year_total,year_total]
            Project [customer_id,customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address,year_total,year_total,year_total]
              BroadcastHashJoin [customer_id,customer_id]
                Project [customer_id,customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address,year_total,year_total]
                  BroadcastHashJoin [customer_id,customer_id,year_total,year_total,year_total,year_total]
                    Project [customer_id,year_total,customer_id,customer_first_name,customer_last_name,customer_preferred_cust_flag,customer_birth_country,customer_login,customer_email_address,year_total,year_total]
                      BroadcastHashJoin [customer_id,customer_id]
                        BroadcastHashJoin [customer_id,customer_id]
                          Filter [year_total]
                            HashAggregate [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,d_year,sum,isEmpty] [sum(CheckOverflow((promote_precision(CheckOverflow((promote_precision(cast(CheckOverflow((promote_precision(cast(CheckOverflow((promote_precision(cast(ss_ext_list_price as decimal(8,2))) - promote_precision(cast(ss_ext_wholesale_cost as decimal(8,2)))), DecimalType(8,2), true) as decimal(9,2))) - promote_precision(cast(ss_ext_discount_amt as decimal(9,2)))), DecimalType(9,2), true) as decimal(10,2))) + promote_precision(cast(ss_ext_sales_price as decimal(10,2)))), DecimalType(10,2), true)) / 2.00), DecimalType(14,6), true)),customer_id,year_total,sum,isEmpty]
                              InputAdapter
                                Exchange [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,d_year] #1
                                  WholeStageCodegen (3)
                                    HashAggregate [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,d_year,ss_ext_list_price,ss_ext_wholesale_cost,ss_ext_discount_amt,ss_ext_sales_price] [sum,isEmpty,sum,isEmpty]
                                      Project [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,ss_ext_discount_amt,ss_ext_sales_price,ss_ext_wholesale_cost,ss_ext_list_price,d_year]
                                        BroadcastHashJoin [ss_sold_date_sk,d_date_sk]
                                          Project [c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address,ss_ext_discount_amt,ss_ext_sales_price,ss_ext_wholesale_cost,ss_ext_list_price,ss_sold_date_sk]
                                            BroadcastHashJoin [c_customer_sk,ss_customer_sk]
                                              Filter [c_customer_sk,c_customer_id]
                                                ColumnarToRow
                                                  InputAdapter
                                                    Scan parquet default.customer [c_customer_sk,c_customer_id,c_first_name,c_last_name,c_preferred_cust_flag,c_birth_country,c_login,c_email_address]
                                              InputAdapter
                                                BroadcastExchange #2
                                                  WholeStageCodegen (1)
                                                    Filter [ss_customer_sk]
                                                      ColumnarToRow
                                                        InputAdapter
                                                          Scan parquet default.store_sales [ss_customer_sk,ss_ext_discount_amt,ss_ext_sales_price,ss_ext_wholesale_cost,ss_ext_list_price,ss_sold_date_sk]
                                                            SubqueryBroadcast [d_date_sk] #1
                                                              BroadcastExchange #3
                                                                WholeStageCodegen (1)
                                                                  Filter [d_year,d_date_sk]
                                                                    ColumnarToRow
                                                                      InputAdapter
                                                                        Scan parquet default.date_dim [d_date_sk,d_year]
                                          InputAdapter
                                            ReusedExchange [d_date_sk,d_year] #3

      ...

      at org.scalatest.Assertions.newAssertionFailedException(Assertions.scala:472)
      at org.scalatest.Assertions.newAssertionFailedException$(Assertions.scala:471)
      at org.scalatest.funsuite.AnyFunSuite.newAssertionFailedException(AnyFunSuite.scala:1563)
      at org.scalatest.Assertions.fail(Assertions.scala:933)
      at org.scalatest.Assertions.fail$(Assertions.scala:929)
      at org.scalatest.funsuite.AnyFunSuite.fail(AnyFunSuite.scala:1563)
      at org.apache.spark.sql.PlanStabilitySuite.checkWithApproved(PlanStabilitySuite.scala:156)
      at org.apache.spark.sql.PlanStabilitySuite.testQuery(PlanStabilitySuite.scala:260)
      at org.apache.spark.sql.PlanStabilitySuite.testQuery$(PlanStabilitySuite.scala:248)
      at org.apache.spark.sql.TPCDSV1_4_PlanStabilitySuite.testQuery(PlanStabilitySuite.scala:265)
      at org.apache.spark.sql.TPCDSV1_4_PlanStabilitySuite.$anonfun$new$2(PlanStabilitySuite.scala:271)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.sql.execution.adaptive.DisableAdaptiveExecutionSuite.$anonfun$test$5(AdaptiveTestUtils.scala:65)
      at org.apache.spark.sql.catalyst.plans.SQLHelper.withSQLConf(SQLHelper.scala:54)
      at org.apache.spark.sql.catalyst.plans.SQLHelper.withSQLConf$(SQLHelper.scala:38)
      at org.apache.spark.sql.TPCDSV1_4_PlanStabilitySuite.org$apache$spark$sql$test$SQLTestUtilsBase$$super$withSQLConf(PlanStabilitySuite.scala:265)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withSQLConf(SQLTestUtils.scala:246)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withSQLConf$(SQLTestUtils.scala:244)
      at org.apache.spark.sql.TPCDSV1_4_PlanStabilitySuite.withSQLConf(PlanStabilitySuite.scala:265)
      at org.apache.spark.sql.execution.adaptive.DisableAdaptiveExecutionSuite.$anonfun$test$4(AdaptiveTestUtils.scala:65)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

#### Class: `org.apache.spark.sql.execution.datasources.ParquetCodecSuite`

- Error:

  ```
  java.lang.RuntimeException: native lz4 library not available
  ```

  - Status: **Resolved**
  - Tests (~~1 failure~~ 0 failure):

    - ~~`write and read - file source parquet - codec: lz4`~~

  - Cause: Tests related to LZ4 fail for Hadoop < 3.3.1 (see [apache/spark#34064](https://github.com/apache/spark/pull/34064))
  - Solution: Correct function `isHadoop3()`. See [Code changes 5.](#code-changes)
  - Stack trace:

    ```
    Cause: org.apache.spark.SparkException: Job aborted due to stage failure: Task 1 in stage 37.0 failed 1 times, most recent failure: Lost task 1.0 in stage 37.0 (TID 73) (1b904010a816 executor driver): java.lang.RuntimeException: native lz4 library not available
      at org.apache.hadoop.io.compress.Lz4Codec.getCompressorType(Lz4Codec.java:125)
      at org.apache.hadoop.io.compress.CodecPool.getCompressor(CodecPool.java:150)
      at org.apache.hadoop.io.compress.CodecPool.getCompressor(CodecPool.java:168)
      at org.apache.parquet.hadoop.CodecFactory$HeapBytesCompressor.<init>(CodecFactory.java:146)
      at org.apache.parquet.hadoop.CodecFactory.createCompressor(CodecFactory.java:208)
      at org.apache.parquet.hadoop.CodecFactory.getCompressor(CodecFactory.java:191)
      at org.apache.parquet.hadoop.ParquetRecordWriter.<init>(ParquetRecordWriter.java:152)
      at org.apache.parquet.hadoop.ParquetOutputFormat.getRecordWriter(ParquetOutputFormat.java:503)
      at org.apache.parquet.hadoop.ParquetOutputFormat.getRecordWriter(ParquetOutputFormat.java:420)
      at org.apache.parquet.hadoop.ParquetOutputFormat.getRecordWriter(ParquetOutputFormat.java:409)
      at org.apache.spark.sql.execution.datasources.parquet.ParquetOutputWriter.<init>(ParquetOutputWriter.scala:36)
      at org.apache.spark.sql.execution.datasources.parquet.ParquetFileFormat$$anon$1.newInstance(ParquetFileFormat.scala:150)
      at org.apache.spark.sql.execution.datasources.SingleDirectoryDataWriter.newOutputWriter(FileFormatDataWriter.scala:161)
      at org.apache.spark.sql.execution.datasources.SingleDirectoryDataWriter.<init>(FileFormatDataWriter.scala:146)
      at org.apache.spark.sql.execution.datasources.FileFormatWriter$.executeTask(FileFormatWriter.scala:290)
      at org.apache.spark.sql.execution.datasources.FileFormatWriter$.$anonfun$write$16(FileFormatWriter.scala:229)
      at org.apache.spark.scheduler.ResultTask.runTask(ResultTask.scala:90)
      at org.apache.spark.scheduler.Task.run(Task.scala:131)
      at org.apache.spark.executor.Executor$TaskRunner.$anonfun$run$3(Executor.scala:506)
      at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1491)
      at org.apache.spark.executor.Executor$TaskRunner.run(Executor.scala:509)
      at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
      at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
      at java.lang.Thread.run(Thread.java:748)
    ```

### spark-hive

#### Class: `org.apache.spark.sql.hive.execution.HiveCatalogedDDLSuite`

- Error:

  ```
  message:java.nio.file.InvalidPathException: Malformed input or input contains unmappable characters: /tdp/spark-apache/sql/hive/target/tmp/warehouse-84cec61f-e81f-4b6c-acb4-e65dc8f03e11/DaTaBaSe_I.db/tab_ı
  ```

  - Status: **Unresolved**
  - Tests (1 failure):

    - `basic DDL using locale tr - caseSensitive true`

  - Cause: Character set issue
  - Solution:
  - Stack trace:

    ```
    Cause: java.nio.file.InvalidPathException: Malformed input or input contains unmappable characters: /tdp/spark-apache/sql/hive/target/tmp/warehouse-84cec61f-e81f-4b6c-acb4-e65dc8f03e11/DaTaBaSe_I.db/tab_ı
      at sun.nio.fs.UnixPath.encode(UnixPath.java:147)
      at sun.nio.fs.UnixPath.<init>(UnixPath.java:71)
      at sun.nio.fs.UnixFileSystem.getPath(UnixFileSystem.java:281)
      at java.io.File.toPath(File.java:2273)
      at org.apache.hadoop.fs.RawLocalFileSystem$DeprecatedRawLocalFileStatus.getLastAccessTime(RawLocalFileSystem.java:658)
      at org.apache.hadoop.fs.RawLocalFileSystem$DeprecatedRawLocalFileStatus.<init>(RawLocalFileSystem.java:669)
      at org.apache.hadoop.fs.RawLocalFileSystem.deprecatedGetFileStatus(RawLocalFileSystem.java:639)
      at org.apache.hadoop.fs.RawLocalFileSystem.getFileLinkStatusInternal(RawLocalFileSystem.java:930)
      at org.apache.hadoop.fs.RawLocalFileSystem.getFileStatus(RawLocalFileSystem.java:631)
      at org.apache.hadoop.fs.FilterFileSystem.getFileStatus(FilterFileSystem.java:454)
      at org.apache.hadoop.hive.metastore.Warehouse.isDir(Warehouse.java:520)
      at org.apache.hadoop.hive.metastore.HiveMetaStore$HMSHandler.create_table_core(HiveMetaStore.java:1436)
      at org.apache.hadoop.hive.metastore.HiveMetaStore$HMSHandler.create_table_with_environment_context(HiveMetaStore.java:1503)
      at sun.reflect.GeneratedMethodAccessor106.invoke(Unknown Source)
      at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
      at java.lang.reflect.Method.invoke(Method.java:498)
      at org.apache.hadoop.hive.metastore.RetryingHMSHandler.invokeInternal(RetryingHMSHandler.java:148)
      at org.apache.hadoop.hive.metastore.RetryingHMSHandler.invoke(RetryingHMSHandler.java:107)
      at com.sun.proxy.$Proxy37.create_table_with_environment_context(Unknown Source)
      at org.apache.hadoop.hive.metastore.HiveMetaStoreClient.create_table_with_environment_context(HiveMetaStoreClient.java:2404)
      at org.apache.hadoop.hive.ql.metadata.SessionHiveMetaStoreClient.create_table_with_environment_context(SessionHiveMetaStoreClient.java:93)
      at org.apache.hadoop.hive.metastore.HiveMetaStoreClient.createTable(HiveMetaStoreClient.java:750)
      at org.apache.hadoop.hive.metastore.HiveMetaStoreClient.createTable(HiveMetaStoreClient.java:738)
      at sun.reflect.GeneratedMethodAccessor105.invoke(Unknown Source)
      at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
      at java.lang.reflect.Method.invoke(Method.java:498)
      at org.apache.hadoop.hive.metastore.RetryingMetaStoreClient.invoke(RetryingMetaStoreClient.java:173)
      at com.sun.proxy.$Proxy38.createTable(Unknown Source)
      at org.apache.hadoop.hive.ql.metadata.Hive.createTable(Hive.java:859)
      at org.apache.hadoop.hive.ql.metadata.Hive.createTable(Hive.java:874)
      at org.apache.spark.sql.hive.client.HiveClientImpl.$anonfun$createTable$1(HiveClientImpl.scala:555)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.sql.hive.client.HiveClientImpl.$anonfun$withHiveState$1(HiveClientImpl.scala:305)
      at org.apache.spark.sql.hive.client.HiveClientImpl.liftedTree1$1(HiveClientImpl.scala:236)
      at org.apache.spark.sql.hive.client.HiveClientImpl.retryLocked(HiveClientImpl.scala:235)
      at org.apache.spark.sql.hive.client.HiveClientImpl.withHiveState(HiveClientImpl.scala:285)
      at org.apache.spark.sql.hive.client.HiveClientImpl.createTable(HiveClientImpl.scala:553)
      at org.apache.spark.sql.hive.HiveExternalCatalog.saveTableIntoHive(HiveExternalCatalog.scala:508)
      at org.apache.spark.sql.hive.HiveExternalCatalog.createDataSourceTable(HiveExternalCatalog.scala:404)
      at org.apache.spark.sql.hive.HiveExternalCatalog.$anonfun$createTable$1(HiveExternalCatalog.scala:274)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.sql.hive.HiveExternalCatalog.withClient(HiveExternalCatalog.scala:102)
      at org.apache.spark.sql.hive.HiveExternalCatalog.createTable(HiveExternalCatalog.scala:245)
      at org.apache.spark.sql.catalyst.catalog.ExternalCatalogWithListener.createTable(ExternalCatalogWithListener.scala:94)
      at org.apache.spark.sql.catalyst.catalog.SessionCatalog.createTable(SessionCatalog.scala:376)
      at org.apache.spark.sql.execution.command.CreateDataSourceTableCommand.run(createDataSourceTables.scala:120)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult$lzycompute(commands.scala:75)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult(commands.scala:73)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.executeCollect(commands.scala:84)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.$anonfun$applyOrElse$1(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$5(SQLExecution.scala:103)
      at org.apache.spark.sql.execution.SQLExecution$.withSQLConfPropagated(SQLExecution.scala:163)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$1(SQLExecution.scala:90)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.execution.SQLExecution$.withNewExecutionId(SQLExecution.scala:64)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:93)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$transformDownWithPruning$1(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.trees.CurrentOrigin$.withOrigin(TreeNode.scala:82)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDownWithPruning(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.org$apache$spark$sql$catalyst$plans$logical$AnalysisHelper$$super$transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning(AnalysisHelper.scala:267)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning$(AnalysisHelper.scala:263)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDown(TreeNode.scala:457)
      at org.apache.spark.sql.execution.QueryExecution.eagerlyExecuteCommands(QueryExecution.scala:93)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted$lzycompute(QueryExecution.scala:80)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted(QueryExecution.scala:78)
      at org.apache.spark.sql.Dataset.<init>(Dataset.scala:219)
      at org.apache.spark.sql.Dataset$.$anonfun$ofRows$1(Dataset.scala:91)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.Dataset$.ofRows(Dataset.scala:88)
      at org.apache.spark.sql.hive.test.TestHiveSparkSession.$anonfun$sql$1(TestHive.scala:240)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.hive.test.TestHiveSparkSession.sql(TestHive.scala:238)
      at org.apache.spark.sql.test.SQLTestUtilsBase.$anonfun$sql$1(SQLTestUtils.scala:231)
      at org.apache.spark.sql.execution.command.DDLSuite.$anonfun$new$353(DDLSuite.scala:2413)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1491)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withTable(SQLTestUtils.scala:305)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withTable$(SQLTestUtils.scala:303)
      at org.apache.spark.sql.execution.command.DDLSuite.withTable(DDLSuite.scala:228)
      at org.apache.spark.sql.execution.command.DDLSuite.$anonfun$new$352(DDLSuite.scala:2412)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1491)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withDatabase(SQLTestUtils.scala:373)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withDatabase$(SQLTestUtils.scala:372)
      at org.apache.spark.sql.execution.command.DDLSuite.withDatabase(DDLSuite.scala:228)
      at org.apache.spark.sql.execution.command.DDLSuite.$anonfun$new$351(DDLSuite.scala:2407)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withLocale(SQLTestUtils.scala:403)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withLocale$(SQLTestUtils.scala:398) at org.apache.spark.sql.execution.command.DDLSuite.withLocale(DDLSuite.scala:228)
      at org.apache.spark.sql.execution.command.DDLSuite.$anonfun$new$350(DDLSuite.scala:2405)
      at org.apache.spark.sql.catalyst.plans.SQLHelper.withSQLConf(SQLHelper.scala:54)
      at org.apache.spark.sql.catalyst.plans.SQLHelper.withSQLConf$(SQLHelper.scala:38)
      at org.apache.spark.sql.execution.command.DDLSuite.org$apache$spark$sql$test$SQLTestUtilsBase$$super$withSQLConf(DDLSuite.scala:228)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withSQLConf(SQLTestUtils.scala:246)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withSQLConf$(SQLTestUtils.scala:244)
      at org.apache.spark.sql.execution.command.DDLSuite.withSQLConf(DDLSuite.scala:228)
      at org.apache.spark.sql.execution.command.DDLSuite.$anonfun$new$349(DDLSuite.scala:2405)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

#### Class: `org.apache.spark.sql.hive.execution.HiveQuerySuite`

- Error:

  ```
  [unresolved dependency: org.apache.hive.hcatalog#hive-hcatalog-core;2.3.10-TDP-0.1.0-SNAPSHOT: not found]
  ```

  - Status: **Resolved**
  - Tests (~~1 failure~~ 0 failure):

    - ~~`SPARK-33084: Add jar support Ivy URI in SQL`~~

  - Cause: Apache Ivy doesn't support comma-separated repositories lists
  - Solution: Only use the local Maven cache as `DEFAULT_ARTIFACT_REPOSITORY`. See [Code changes 4.](#code-changes)
  - Stack trace:

    ```
    java.lang.RuntimeException: [unresolved dependency: org.apache.hive.hcatalog#hive-hcatalog-core;2.3.10-TDP-0.1.0-SNAPSHOT: not found]
      at org.apache.spark.deploy.SparkSubmitUtils$.resolveMavenCoordinates(SparkSubmit.scala:1447)
      at org.apache.spark.util.DependencyUtils$.resolveMavenDependencies(DependencyUtils.scala:185)
      at org.apache.spark.util.DependencyUtils$.resolveMavenDependencies(DependencyUtils.scala:159)
      at org.apache.spark.sql.internal.SessionResourceLoader.resolveJars(SessionState.scala:162)
      at org.apache.spark.sql.hive.HiveSessionResourceLoader.addJar(HiveSessionStateBuilder.scala:130)
      at org.apache.spark.sql.execution.command.AddJarsCommand.$anonfun$run$1(resources.scala:32)
      at org.apache.spark.sql.execution.command.AddJarsCommand.$anonfun$run$1$adapted(resources.scala:32)
      at scala.collection.immutable.Stream.foreach(Stream.scala:533)
      at org.apache.spark.sql.execution.command.AddJarsCommand.run(resources.scala:32)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult$lzycompute(commands.scala:75)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult(commands.scala:73)
      at org.apache.spark.sql.execution.command.ExecutedCommandExec.executeCollect(commands.scala:84)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.$anonfun$applyOrElse$1(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$5(SQLExecution.scala:103)
      at org.apache.spark.sql.execution.SQLExecution$.withSQLConfPropagated(SQLExecution.scala:163)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$1(SQLExecution.scala:90)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.execution.SQLExecution$.withNewExecutionId(SQLExecution.scala:64)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:93)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$transformDownWithPruning$1(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.trees.CurrentOrigin$.withOrigin(TreeNode.scala:82)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDownWithPruning(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.org$apache$spark$sql$catalyst$plans$logical$AnalysisHelper$$super$transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning(AnalysisHelper.scala:267)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning$(AnalysisHelper.scala:263)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDown(TreeNode.scala:457)
      at org.apache.spark.sql.execution.QueryExecution.eagerlyExecuteCommands(QueryExecution.scala:93)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted$lzycompute(QueryExecution.scala:80)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted(QueryExecution.scala:78)
      at org.apache.spark.sql.Dataset.<init>(Dataset.scala:219)
      at org.apache.spark.sql.Dataset$.$anonfun$ofRows$1(Dataset.scala:91)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.Dataset$.ofRows(Dataset.scala:88)
      at org.apache.spark.sql.hive.test.TestHiveSparkSession.$anonfun$sql$1(TestHive.scala:240)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.hive.test.TestHiveSparkSession.sql(TestHive.scala:238)
      at org.apache.spark.sql.test.SQLTestUtilsBase.$anonfun$sql$1(SQLTestUtils.scala:231)
      at org.apache.spark.sql.hive.execution.HiveQuerySuite.$anonfun$new$159(HiveQuerySuite.scala:1512)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1491)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withTable(SQLTestUtils.scala:305)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withTable$(SQLTestUtils.scala:303)
      at org.apache.spark.sql.hive.execution.HiveQuerySuite.withTable(HiveQuerySuite.scala:52)
      at org.apache.spark.sql.hive.execution.HiveQuerySuite.$anonfun$new$158(HiveQuerySuite.scala:1506)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.sql.hive.execution.HiveQuerySuite.org$scalatest$BeforeAndAfter$$super$runTest(HiveQuerySuite.scala:52)
      at org.scalatest.BeforeAndAfter.runTest(BeforeAndAfter.scala:213)
      at org.scalatest.BeforeAndAfter.runTest$(BeforeAndAfter.scala:203)
      at org.apache.spark.sql.hive.execution.HiveQuerySuite.runTest(HiveQuerySuite.scala:52)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.sql.hive.execution.HiveQuerySuite.org$scalatest$BeforeAndAfter$$super$run(HiveQuerySuite.scala:52)
      at org.scalatest.BeforeAndAfter.run(BeforeAndAfter.scala:273)
      at org.scalatest.BeforeAndAfter.run$(BeforeAndAfter.scala:271)
      at org.apache.spark.sql.hive.execution.HiveQuerySuite.run(HiveQuerySuite.scala:52)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

#### Class: `org.apache.spark.sql.hive.execution.HiveDDLSuite`

- Error:

  ```
  java.nio.file.InvalidPathException: Malformed input or input contains unmappable characters: /tdp/spark-apache/sql/hive/target/tmp/warehouse-84cec61f-e81f-4b6c-acb4-e65dc8f03e11/tab1/尼=2
  ```

  - Status: **Unresolved**
  - Tests (1 failure):

    - `create Hive-serde table and view with unicode columns and comment`

  - Cause: Character set issue
  - Solution:
  - Stack trace:

    ```
    Cause: java.nio.file.InvalidPathException: Malformed input or input contains unmappable characters: /tdp/spark-apache/sql/hive/target/tmp/warehouse-84cec61f-e81f-4b6c-acb4-e65dc8f03e11/tab1/尼=2
      at sun.nio.fs.UnixPath.encode(UnixPath.java:147)
      at sun.nio.fs.UnixPath.<init>(UnixPath.java:71)
      at sun.nio.fs.UnixFileSystem.getPath(UnixFileSystem.java:281)
      at java.io.File.toPath(File.java:2273)
      at org.apache.hadoop.fs.RawLocalFileSystem$DeprecatedRawLocalFileStatus.getLastAccessTime(RawLocalFileSystem.java:658)
      at org.apache.hadoop.fs.RawLocalFileSystem$DeprecatedRawLocalFileStatus.<init>(RawLocalFileSystem.java:669)
      at org.apache.hadoop.fs.RawLocalFileSystem.deprecatedGetFileStatus(RawLocalFileSystem.java:639)
      at org.apache.hadoop.fs.RawLocalFileSystem.getFileLinkStatusInternal(RawLocalFileSystem.java:930)
      at org.apache.hadoop.fs.RawLocalFileSystem.getFileStatus(RawLocalFileSystem.java:631)
      at org.apache.hadoop.fs.FilterFileSystem.getFileStatus(FilterFileSystem.java:454)
      at org.apache.hadoop.hive.io.HdfsUtils$HadoopFileStatus.<init>(HdfsUtils.java:211)
      at org.apache.hadoop.hive.ql.metadata.Hive.moveFile(Hive.java:3129)
      at org.apache.hadoop.hive.ql.metadata.Hive.replaceFiles(Hive.java:3485)
      at org.apache.hadoop.hive.ql.metadata.Hive.loadPartition(Hive.java:1657)
      at org.apache.hadoop.hive.ql.metadata.Hive.loadPartition(Hive.java:1586)
      at sun.reflect.GeneratedMethodAccessor124.invoke(Unknown Source)
      at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
      at java.lang.reflect.Method.invoke(Method.java:498)
      at org.apache.spark.sql.hive.client.Shim_v2_1.loadPartition(HiveShim.scala:1276)
      at org.apache.spark.sql.hive.client.HiveClientImpl.$anonfun$loadPartition$1(HiveClientImpl.scala:895)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.sql.hive.client.HiveClientImpl.$anonfun$withHiveState$1(HiveClientImpl.scala:305)
      at org.apache.spark.sql.hive.client.HiveClientImpl.liftedTree1$1(HiveClientImpl.scala:236)
      at org.apache.spark.sql.hive.client.HiveClientImpl.retryLocked(HiveClientImpl.scala:235)
      at org.apache.spark.sql.hive.client.HiveClientImpl.withHiveState(HiveClientImpl.scala:285)
      at org.apache.spark.sql.hive.client.HiveClientImpl.loadPartition(HiveClientImpl.scala:885)
      at org.apache.spark.sql.hive.HiveExternalCatalog.$anonfun$loadPartition$1(HiveExternalCatalog.scala:924)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.sql.hive.HiveExternalCatalog.withClient(HiveExternalCatalog.scala:102)
      at org.apache.spark.sql.hive.HiveExternalCatalog.loadPartition(HiveExternalCatalog.scala:903)
      at org.apache.spark.sql.catalyst.catalog.ExternalCatalogWithListener.loadPartition(ExternalCatalogWithListener.scala:179)
      at org.apache.spark.sql.hive.execution.InsertIntoHiveTable.processInsert(InsertIntoHiveTable.scala:339)
      at org.apache.spark.sql.hive.execution.InsertIntoHiveTable.run(InsertIntoHiveTable.scala:106)
      at org.apache.spark.sql.execution.command.DataWritingCommandExec.sideEffectResult$lzycompute(commands.scala:113)
      at org.apache.spark.sql.execution.command.DataWritingCommandExec.sideEffectResult(commands.scala:111)
      at org.apache.spark.sql.execution.command.DataWritingCommandExec.executeCollect(commands.scala:125)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.$anonfun$applyOrElse$1(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$5(SQLExecution.scala:103)
      at org.apache.spark.sql.execution.SQLExecution$.withSQLConfPropagated(SQLExecution.scala:163)
      at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$1(SQLExecution.scala:90)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)      at org.apache.spark.sql.execution.SQLExecution$.withNewExecutionId(SQLExecution.scala:64)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:97)
      at org.apache.spark.sql.execution.QueryExecution$$anonfun$eagerlyExecuteCommands$1.applyOrElse(QueryExecution.scala:93)
      at org.apache.spark.sql.catalyst.trees.TreeNode.$anonfun$transformDownWithPruning$1(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.trees.CurrentOrigin$.withOrigin(TreeNode.scala:82)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDownWithPruning(TreeNode.scala:481)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.org$apache$spark$sql$catalyst$plans$logical$AnalysisHelper$$super$transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning(AnalysisHelper.scala:267)
      at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.transformDownWithPruning$(AnalysisHelper.scala:263)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.transformDownWithPruning(LogicalPlan.scala:30)
      at org.apache.spark.sql.catalyst.trees.TreeNode.transformDown(TreeNode.scala:457)
      at org.apache.spark.sql.execution.QueryExecution.eagerlyExecuteCommands(QueryExecution.scala:93)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted$lzycompute(QueryExecution.scala:80)
      at org.apache.spark.sql.execution.QueryExecution.commandExecuted(QueryExecution.scala:78)
      at org.apache.spark.sql.Dataset.<init>(Dataset.scala:219)
      at org.apache.spark.sql.Dataset$.$anonfun$ofRows$1(Dataset.scala:91)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.Dataset$.ofRows(Dataset.scala:88)
      at org.apache.spark.sql.hive.test.TestHiveSparkSession.$anonfun$sql$1(TestHive.scala:240)
      at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:775)
      at org.apache.spark.sql.hive.test.TestHiveSparkSession.sql(TestHive.scala:238)
      at org.apache.spark.sql.test.SQLTestUtilsBase.$anonfun$sql$1(SQLTestUtils.scala:231)
      at org.apache.spark.sql.hive.execution.HiveDDLSuite.$anonfun$new$66(HiveDDLSuite.scala:545)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1491)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withTable(SQLTestUtils.scala:305)
      at org.apache.spark.sql.test.SQLTestUtilsBase.withTable$(SQLTestUtils.scala:303)
      at org.apache.spark.sql.hive.execution.HiveDDLSuite.withTable(HiveDDLSuite.scala:395)
      at org.apache.spark.sql.hive.execution.HiveDDLSuite.$anonfun$new$65(HiveDDLSuite.scala:539)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

#### Class: `org.apache.spark.sql.hive.client.HadoopVersionInfoSuite`

- Error:

  ```
  [unresolved dependency: org.apache.hive#hive-metastore;2.0.1: not found, unresolved dependency: org.apache.hive#hive-exec;2.0.1: not found, unresolved dependency: org.apache.hive#hive-common;2.0.1: not found, unresolved dependency: org.apache.hive#hive-serde;2.0.1: not found, unresolved dependency: org.apache.hadoop#hadoop-client;2.7.4: not found]
  ```

  - Status: **Unresolved**
  - Tests (1 failure):

    - `SPARK-32256: Hadoop VersionInfo should be preloaded`

  - Cause: The local Maven cache does not contains the versions specified
  - Solution:
  - Stack trace:

    ```
    java.lang.RuntimeException: [unresolved dependency: org.apache.hive#hive-metastore;2.0.1: not found, unresolved dependency: org.apache.hive#hive-exec;2.0.1: not found, unresolved dependency: org.apache.hive#hive-common;2.0.1: not found, unresolved dependency: org.apache.hive#hive-serde;2.0.1: not found, unresolved dependency: org.apache.hadoop#hadoop-client;2.7.4: not found]
      at org.apache.spark.deploy.SparkSubmitUtils$.resolveMavenCoordinates(SparkSubmit.scala:1447)
      at org.apache.spark.sql.hive.client.IsolatedClientLoader$.$anonfun$downloadVersion$2(IsolatedClientLoader.scala:138)
      at org.apache.spark.sql.catalyst.util.package$.quietly(package.scala:42)
      at org.apache.spark.sql.hive.client.IsolatedClientLoader$.downloadVersion(IsolatedClientLoader.scala:138)
      at org.apache.spark.sql.hive.client.IsolatedClientLoader$.liftedTree1$1(IsolatedClientLoader.scala:76)
      at org.apache.spark.sql.hive.client.IsolatedClientLoader$.forVersion(IsolatedClientLoader.scala:64)
      at org.apache.spark.sql.hive.client.HadoopVersionInfoSuite.$anonfun$new$1(HadoopVersionInfoSuite.scala:47)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

- Error:

  ```
  org.scalatest.exceptions.TestFailedException: IsolatedClientLoader.supportsHadoopShadedClient(hadoopVersion) was false
  ```

  - Status: **Resolved**
  - Tests (1 failure):

    - ~~`SPARK-32212: built-in Hadoop version should support shaded client if it is not hadoop 2`~~

  - Cause: Hadoop `3.1.1-TDP-0.1.0-SNAPSHOT` does not support shaded client
  - Solution: Modify the test. See [Code changes 6.](#code-changes).
  - Stack trace:

    ```
    org.scalatest.exceptions.TestFailedException: IsolatedClientLoader.supportsHadoopShadedClient(hadoopVersion) was false
      at org.scalatest.Assertions.newAssertionFailedException(Assertions.scala:472)
      at org.scalatest.Assertions.newAssertionFailedException$(Assertions.scala:471)
      at org.scalatest.Assertions$.newAssertionFailedException(Assertions.scala:1231)
      at org.scalatest.Assertions$AssertionsHelper.macroAssert(Assertions.scala:1295)
      at org.apache.spark.sql.hive.client.HadoopVersionInfoSuite.$anonfun$new$9(HadoopVersionInfoSuite.scala:87)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```

### spark-hive-thriftserver

#### Class: `org.apache.spark.sql.hive.thriftserver.SparkThriftServerProtocolVersionsSuite`

- Error:

  ```
  org.scalatest.exceptions.TestFailedException: "[?](" did not equal "[�]("
  ```

  - Status: **Unresolved**
  - Tests (5 failures):

    - `HIVE_CLI_SERVICE_PROTOCOL_V1 get binary type`
    - `HIVE_CLI_SERVICE_PROTOCOL_V2 get binary type`
    - `HIVE_CLI_SERVICE_PROTOCOL_V3 get binary type`
    - `HIVE_CLI_SERVICE_PROTOCOL_V4 get binary type`
    - `HIVE_CLI_SERVICE_PROTOCOL_V5 get binary type`

  - Cause: Character set issue
  - Solution:
  - Stack trace:

    ```
    org.scalatest.exceptions.TestFailedException: "[?](" did not equal "[�]("
      at org.scalatest.Assertions.newAssertionFailedException(Assertions.scala:472)
      at org.scalatest.Assertions.newAssertionFailedException$(Assertions.scala:471)
      at org.scalatest.Assertions$.newAssertionFailedException(Assertions.scala:1231)
      at org.scalatest.Assertions$AssertionsHelper.macroAssert(Assertions.scala:1295)
      at org.apache.spark.sql.hive.thriftserver.SparkThriftServerProtocolVersionsSuite.$anonfun$new$26(SparkThriftServerProtocolVersionsSuite.scala:303)
      at org.apache.spark.sql.hive.thriftserver.SparkThriftServerProtocolVersionsSuite.$anonfun$new$26$adapted(SparkThriftServerProtocolVersionsSuite.scala:301)
      at org.apache.spark.sql.hive.thriftserver.SparkThriftServerProtocolVersionsSuite.testExecuteStatementWithProtocolVersion(SparkThriftServerProtocolVersionsSuite.scala:69)
      at org.apache.spark.sql.hive.thriftserver.SparkThriftServerProtocolVersionsSuite.$anonfun$new$24(SparkThriftServerProtocolVersionsSuite.scala:301)
      at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.java:23)
      at org.scalatest.OutcomeOf.outcomeOf(OutcomeOf.scala:85)
      at org.scalatest.OutcomeOf.outcomeOf$(OutcomeOf.scala:83)
      at org.scalatest.OutcomeOf$.outcomeOf(OutcomeOf.scala:104)
      at org.scalatest.Transformer.apply(Transformer.scala:22)
      at org.scalatest.Transformer.apply(Transformer.scala:20)
      at org.scalatest.funsuite.AnyFunSuiteLike$$anon$1.apply(AnyFunSuiteLike.scala:226)
      at org.apache.spark.SparkFunSuite.withFixture(SparkFunSuite.scala:190)
      at org.scalatest.funsuite.AnyFunSuiteLike.invokeWithFixture$1(AnyFunSuiteLike.scala:224)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTest$1(AnyFunSuiteLike.scala:236)
      at org.scalatest.SuperEngine.runTestImpl(Engine.scala:306)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest(AnyFunSuiteLike.scala:236)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTest$(AnyFunSuiteLike.scala:218)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterEach$$super$runTest(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterEach.runTest(BeforeAndAfterEach.scala:234)
      at org.scalatest.BeforeAndAfterEach.runTest$(BeforeAndAfterEach.scala:227)
      at org.apache.spark.SparkFunSuite.runTest(SparkFunSuite.scala:62)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$runTests$1(AnyFunSuiteLike.scala:269)
      at org.scalatest.SuperEngine.$anonfun$runTestsInBranch$1(Engine.scala:413)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.SuperEngine.traverseSubNodes$1(Engine.scala:401)
      at org.scalatest.SuperEngine.runTestsInBranch(Engine.scala:396)
      at org.scalatest.SuperEngine.runTestsImpl(Engine.scala:475)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests(AnyFunSuiteLike.scala:269)
      at org.scalatest.funsuite.AnyFunSuiteLike.runTests$(AnyFunSuiteLike.scala:268)
      at org.scalatest.funsuite.AnyFunSuite.runTests(AnyFunSuite.scala:1563)
      at org.scalatest.Suite.run(Suite.scala:1112)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.funsuite.AnyFunSuite.org$scalatest$funsuite$AnyFunSuiteLike$$super$run(AnyFunSuite.scala:1563)
      at org.scalatest.funsuite.AnyFunSuiteLike.$anonfun$run$1(AnyFunSuiteLike.scala:273)
      at org.scalatest.SuperEngine.runImpl(Engine.scala:535)
      at org.scalatest.funsuite.AnyFunSuiteLike.run(AnyFunSuiteLike.scala:273)
      at org.scalatest.funsuite.AnyFunSuiteLike.run$(AnyFunSuiteLike.scala:272)
      at org.apache.spark.SparkFunSuite.org$scalatest$BeforeAndAfterAll$$super$run(SparkFunSuite.scala:62)
      at org.scalatest.BeforeAndAfterAll.liftedTree1$1(BeforeAndAfterAll.scala:213)
      at org.scalatest.BeforeAndAfterAll.run(BeforeAndAfterAll.scala:210)
      at org.scalatest.BeforeAndAfterAll.run$(BeforeAndAfterAll.scala:208)
      at org.apache.spark.SparkFunSuite.run(SparkFunSuite.scala:62)
      at org.scalatest.Suite.callExecuteOnSuite$1(Suite.scala:1175)
      at org.scalatest.Suite.$anonfun$runNestedSuites$1(Suite.scala:1222)
      at scala.collection.IndexedSeqOptimized.foreach(IndexedSeqOptimized.scala:36)
      at scala.collection.IndexedSeqOptimized.foreach$(IndexedSeqOptimized.scala:33)
      at scala.collection.mutable.ArrayOps$ofRef.foreach(ArrayOps.scala:198)
      at org.scalatest.Suite.runNestedSuites(Suite.scala:1220)
      at org.scalatest.Suite.runNestedSuites$(Suite.scala:1154)
      at org.scalatest.tools.DiscoverySuite.runNestedSuites(DiscoverySuite.scala:30)
      at org.scalatest.Suite.run(Suite.scala:1109)
      at org.scalatest.Suite.run$(Suite.scala:1094)
      at org.scalatest.tools.DiscoverySuite.run(DiscoverySuite.scala:30)
      at org.scalatest.tools.SuiteRunner.run(SuiteRunner.scala:45)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13(Runner.scala:1322)
      at org.scalatest.tools.Runner$.$anonfun$doRunRunRunDaDoRunRun$13$adapted(Runner.scala:1316)
      at scala.collection.immutable.List.foreach(List.scala:431)
      at org.scalatest.tools.Runner$.doRunRunRunDaDoRunRun(Runner.scala:1316)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24(Runner.scala:993)
      at org.scalatest.tools.Runner$.$anonfun$runOptionallyWithPassFailReporter$24$adapted(Runner.scala:971)
      at org.scalatest.tools.Runner$.withClassLoaderAndDispatchReporter(Runner.scala:1482)
      at org.scalatest.tools.Runner$.runOptionallyWithPassFailReporter(Runner.scala:971)
      at org.scalatest.tools.Runner$.main(Runner.scala:775)
      at org.scalatest.tools.Runner.main(Runner.scala)
    ```
